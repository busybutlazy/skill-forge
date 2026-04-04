from __future__ import annotations

import json
import shutil
import tempfile
from collections.abc import Callable
from pathlib import Path

from .models import CanonicalSkill, InstalledStatus
from .render import render_skill
from .repository import load_all_skills, load_manager_catalog_skill, load_manager_catalog_skills, load_skill
from .utils import has_frontmatter, parse_toolkit_marker, read_text, sha256_file


def target_root(project_dir: Path, target: str) -> Path:
    if target == "codex":
        return project_dir / ".agents" / "skills"
    if target == "claude":
        return project_dir / ".claude" / "agents"
    raise ValueError(f"unsupported target: {target}")


def _materialize_install(skill: CanonicalSkill, project_dir: Path, target: str) -> Path:
    destination = Path(skill.targets[target].install_path.format(name=skill.name))
    final_path = project_dir / destination

    with tempfile.TemporaryDirectory(prefix="skill-toolkit-render-") as tmp_dir:
        temp_root = Path(tmp_dir)
        rendered_path = render_skill(skill, target, temp_root)
        if final_path.exists():
            if final_path.is_dir():
                shutil.rmtree(final_path)
            else:
                final_path.unlink()
        final_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(rendered_path), str(final_path))

        if target == "claude":
            assets_dir = temp_root / ".claude" / "agents" / f"{skill.name}.assets"
            final_assets = final_path.with_name(f"{skill.name}.assets")
            if final_assets.exists():
                shutil.rmtree(final_assets)
            if assets_dir.exists():
                shutil.move(str(assets_dir), str(final_assets))

    return final_path


def _source_index(repo_root: Path, *, scopes: set[str] | None = None) -> dict[str, CanonicalSkill]:
    return {skill.name: skill for skill in load_all_skills(repo_root, scopes=scopes)}


def _manager_catalog_index(repo_root: Path, *, target_filter: set[str] | None = None) -> dict[str, CanonicalSkill]:
    return {skill.name: skill for skill in load_manager_catalog_skills(repo_root, target_filter=target_filter)}


def _snapshot_directory(root: Path) -> dict[str, str]:
    if not root.exists():
        return {}
    return {
        str(path.relative_to(root)): sha256_file(path)
        for path in sorted(item for item in root.rglob("*") if item.is_file())
    }


def _snapshot_claude_bundle(entry: Path) -> dict[str, str]:
    bundle: dict[str, str] = {}
    if entry.is_file():
        bundle[entry.name] = sha256_file(entry)
    assets_dir = entry.with_name(f"{entry.stem}.assets")
    if assets_dir.is_dir():
        for path in sorted(item for item in assets_dir.rglob("*") if item.is_file()):
            rel_path = path.relative_to(assets_dir)
            bundle[str(Path(assets_dir.name) / rel_path)] = sha256_file(path)
    return bundle


def _classify_snapshot_diff(expected: dict[str, str], actual: dict[str, str]) -> tuple[str, str] | None:
    missing_files = sorted(path for path in expected if path not in actual)
    if missing_files:
        return ("broken", f"missing rendered files: {', '.join(missing_files)}")

    changed_files = sorted(path for path, digest in expected.items() if actual.get(path) != digest)
    if changed_files:
        return ("drift", f"installed files differ from rendered output: {', '.join(changed_files)}")

    extra_files = sorted(path for path in actual if path not in expected)
    if extra_files:
        return ("drift", f"unexpected installed files: {', '.join(extra_files)}")

    return None


def _expected_codex_snapshot(skill: CanonicalSkill) -> dict[str, str]:
    with tempfile.TemporaryDirectory(prefix="skill-toolkit-status-") as tmp_dir:
        rendered = render_skill(skill, "codex", Path(tmp_dir))
        return _snapshot_directory(rendered)


def _expected_claude_snapshot(skill: CanonicalSkill) -> dict[str, str]:
    with tempfile.TemporaryDirectory(prefix="skill-toolkit-status-") as tmp_dir:
        rendered = render_skill(skill, "claude", Path(tmp_dir))
        return _snapshot_claude_bundle(rendered)


def _codex_status(repo_root: Path, entry: Path, sources: dict[str, CanonicalSkill]) -> InstalledStatus:
    name = entry.name
    source = sources.get(name)
    if source is None:
        return InstalledStatus(name=name, target="codex", status="unmanaged", location=entry, details="not found in canonical-skills")

    skill_md = entry / "SKILL.md"
    metadata_path = entry / "metadata.json"
    if not metadata_path.is_file():
        return InstalledStatus(name=name, target="codex", status="broken", location=entry, details="missing metadata.json")

    try:
        metadata = json.loads(read_text(metadata_path))
    except json.JSONDecodeError as exc:
        return InstalledStatus(name=name, target="codex", status="broken", location=entry, details=f"invalid metadata.json: {exc}")

    rendered_from = metadata.get("rendered_from")
    source_hash = metadata.get("source_package_sha256")
    version = metadata.get("version")
    if rendered_from != source.source_ref or not isinstance(source_hash, str):
        return InstalledStatus(name=name, target="codex", status="unmanaged", location=entry, version=version, details="missing or foreign toolkit markers")
    if not skill_md.is_file():
        return InstalledStatus(name=name, target="codex", status="broken", location=entry, version=version, source_package_sha256=source_hash, details="missing SKILL.md", managed=True)
    if version != source.version:
        return InstalledStatus(name=name, target="codex", status="update_available", location=entry, version=version, source_package_sha256=source_hash, managed=True)
    if source_hash != source.package_sha256:
        return InstalledStatus(name=name, target="codex", status="drift", location=entry, version=version, source_package_sha256=source_hash, details="source package hash differs from canonical source", managed=True)

    diff = _classify_snapshot_diff(_expected_codex_snapshot(source), _snapshot_directory(entry))
    if diff is not None:
        status, details = diff
        return InstalledStatus(name=name, target="codex", status=status, location=entry, version=version, source_package_sha256=source_hash, details=details, managed=True)

    return InstalledStatus(name=name, target="codex", status="up_to_date", location=entry, version=version, source_package_sha256=source_hash, managed=True)


def _claude_status(repo_root: Path, entry: Path, sources: dict[str, CanonicalSkill]) -> InstalledStatus:
    name = entry.stem
    source = sources.get(name)
    if source is None:
        return InstalledStatus(name=name, target="claude", status="unmanaged", location=entry, details="not found in canonical-skills")

    content = read_text(entry)
    marker = None
    managed = False
    try:
        marker = parse_toolkit_marker(content)
    except json.JSONDecodeError as exc:
        return InstalledStatus(name=name, target="claude", status="broken", location=entry, details=f"invalid toolkit marker: {exc}")

    if marker and marker.get("rendered_from") == source.source_ref:
        managed = True

    if not has_frontmatter(content):
        return InstalledStatus(name=name, target="claude", status="broken", location=entry, details="missing YAML frontmatter", managed=managed)

    if marker is None:
        return InstalledStatus(name=name, target="claude", status="unmanaged", location=entry, details="missing toolkit marker")

    if marker.get("rendered_from") != source.source_ref:
        return InstalledStatus(name=name, target="claude", status="unmanaged", location=entry, details="foreign rendered_from marker")

    version = marker.get("version")
    source_hash = marker.get("source_package_sha256")
    if version != source.version:
        return InstalledStatus(name=name, target="claude", status="update_available", location=entry, version=str(version) if version is not None else None, source_package_sha256=str(source_hash) if source_hash is not None else None, managed=True)
    if source_hash != source.package_sha256:
        return InstalledStatus(name=name, target="claude", status="drift", location=entry, version=str(version), source_package_sha256=str(source_hash), details="source package hash differs from canonical source", managed=True)

    diff = _classify_snapshot_diff(_expected_claude_snapshot(source), _snapshot_claude_bundle(entry))
    if diff is not None:
        status, details = diff
        return InstalledStatus(name=name, target="claude", status=status, location=entry, version=str(version), source_package_sha256=str(source_hash), details=details, managed=True)

    return InstalledStatus(name=name, target="claude", status="up_to_date", location=entry, version=str(version), source_package_sha256=str(source_hash), managed=True)


def list_installed(
    repo_root: Path,
    project_dir: Path,
    target: str,
    *,
    source_scopes: set[str] | None = None,
) -> list[InstalledStatus]:
    sources = _source_index(repo_root, scopes=source_scopes or {"public"})
    root = target_root(project_dir, target)
    if not root.exists():
        return []

    statuses: list[InstalledStatus] = []
    if target == "codex":
        for entry in sorted(path for path in root.iterdir() if path.is_dir()):
            statuses.append(_codex_status(repo_root, entry, sources))
    elif target == "claude":
        for entry in sorted(path for path in root.iterdir() if path.is_file() and path.suffix == ".md"):
            statuses.append(_claude_status(repo_root, entry, sources))
    else:
        raise ValueError(f"unsupported target: {target}")

    return statuses


def _confirm_overwrite(prompt: str, confirm: Callable[[str], bool] | None) -> None:
    if confirm is None:
        raise ValueError(prompt)
    if not confirm(prompt):
        raise RuntimeError("Update aborted by user.")


def install_skill(
    repo_root: Path,
    project_dir: Path,
    skill_name: str,
    target: str,
    *,
    force: bool = False,
    confirm: Callable[[str], bool] | None = None,
    allowed_scopes: set[str] | None = None,
) -> Path:
    scopes = allowed_scopes or {"public"}
    skill = load_skill(repo_root, skill_name, target_filter={target}, allowed_scopes=scopes)
    statuses = {
        status.name: status
        for status in list_installed(repo_root, project_dir, target, source_scopes=scopes)
    }
    status = statuses.get(skill_name)

    if status is not None:
        if not status.managed:
            raise ValueError(
                f"{skill_name} already exists for target {target} but is unmanaged; refusing to overwrite it"
            )
        if status.status == "drift":
            if not force:
                raise ValueError(
                    f"{skill_name} has drifted from canonical source for target {target}; rerun install with --force to overwrite local changes"
                )
            _confirm_overwrite(
                f"{skill_name} has drifted from canonical source for target {target}. Install will overwrite local changes. Continue? [y/N]: ",
                confirm,
            )
        elif status.status == "broken":
            _confirm_overwrite(
                f"{skill_name} is broken for target {target}. Install will repair it by overwriting the installed files. Continue? [y/N]: ",
                confirm,
            )

    return _materialize_install(skill, project_dir, target)


def update_skill(
    repo_root: Path,
    project_dir: Path,
    skill_name: str,
    target: str,
    *,
    force: bool = False,
    confirm: Callable[[str], bool] | None = None,
    allowed_scopes: set[str] | None = None,
) -> Path:
    scopes = allowed_scopes or {"public"}
    statuses = {
        status.name: status
        for status in list_installed(repo_root, project_dir, target, source_scopes=scopes)
    }
    status = statuses.get(skill_name)
    if status is None:
        raise FileNotFoundError(f"{skill_name} is not installed for target {target}")
    if not status.managed:
        raise ValueError(f"{skill_name} is not a managed toolkit install for target {target}; refusing to update it")
    if status.status == "up_to_date":
        return status.location
    if status.status == "drift":
        if not force:
            raise ValueError(f"{skill_name} has drifted from canonical source for target {target}; rerun update with --force to overwrite local changes")
        _confirm_overwrite(
            f"{skill_name} has drifted from canonical source for target {target}. This will overwrite local changes. Continue? [y/N]: ",
            confirm,
        )
    elif status.status == "broken":
        _confirm_overwrite(
            f"{skill_name} is broken for target {target}. This will repair it by overwriting the installed files. Continue? [y/N]: ",
            confirm,
        )

    skill = load_skill(repo_root, skill_name, target_filter={target}, allowed_scopes=scopes)
    return _materialize_install(skill, project_dir, target)


def remove_skill(repo_root: Path, project_dir: Path, skill_name: str, target: str) -> Path:
    statuses = {status.name: status for status in list_installed(repo_root, project_dir, target)}
    status = statuses.get(skill_name)
    if status is None:
        raise FileNotFoundError(f"{skill_name} is not installed for target {target}")
    if not status.managed:
        raise ValueError(f"{skill_name} is not a managed toolkit install for target {target}; refusing to remove it")

    if target == "codex":
        shutil.rmtree(status.location)
        return status.location

    status.location.unlink()
    assets_dir = status.location.with_name(f"{skill_name}.assets")
    if assets_dir.exists():
        shutil.rmtree(assets_dir)
    return status.location


def sync_manager_catalog(
    repo_root: Path,
    project_dir: Path,
    target: str,
    *,
    skill_names: list[str] | None = None,
    force: bool = False,
    confirm: Callable[[str], bool] | None = None,
) -> list[Path]:
    target_filter = {target}
    catalog = _manager_catalog_index(repo_root, target_filter=target_filter)
    selected_names = skill_names or sorted(catalog)
    if not selected_names:
        return []

    installed_paths: list[Path] = []
    for skill_name in selected_names:
        if skill_name not in catalog:
            raise FileNotFoundError(f"{skill_name} is not available in the manager catalog")
        skill = load_manager_catalog_skill(repo_root, skill_name, target_filter=target_filter)
        allowed_scopes = {skill.scope}
        try:
            path = install_skill(
                repo_root,
                project_dir,
                skill_name,
                target,
                force=force,
                confirm=confirm,
                allowed_scopes=allowed_scopes,
            )
        except ValueError as exc:
            if "is unmanaged; refusing to overwrite it" not in str(exc) or not force:
                raise
            if target == "codex":
                unmanaged_path = project_dir / ".agents" / "skills" / skill_name
            else:
                unmanaged_path = project_dir / ".claude" / "agents" / f"{skill_name}.md"
            if unmanaged_path.is_dir():
                shutil.rmtree(unmanaged_path)
            elif unmanaged_path.exists():
                unmanaged_path.unlink()
            assets_dir = unmanaged_path.with_name(f"{skill_name}.assets")
            if assets_dir.exists():
                shutil.rmtree(assets_dir)
            path = install_skill(
                repo_root,
                project_dir,
                skill_name,
                target,
                force=force,
                confirm=confirm,
                allowed_scopes=allowed_scopes,
            )
        installed_paths.append(path)
    return installed_paths
