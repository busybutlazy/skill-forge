from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

from .models import CanonicalSkill, InstalledStatus
from .render import render_skill
from .repository import load_all_skills, load_manager_catalog_skill, load_manager_catalog_skills, load_skill
from .utils import has_frontmatter, read_text, sha256_file


def target_root(project_dir: Path, target: str) -> Path:
    if target == "codex":
        return project_dir / ".agents" / "skills"
    if target == "claude":
        return project_dir / ".claude" / "skills"
    raise ValueError(f"unsupported target: {target}")


def _safe_remove(path: Path) -> None:
    """Remove a file, directory, or symlink without following symlinks."""
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def _materialize_install(skill: CanonicalSkill, project_dir: Path, target: str) -> Path:
    destination = Path(skill.targets[target].install_path.format(name=skill.name))
    final_path = project_dir / destination

    # [HIGH-1] Path containment: reject absolute install_paths and .. traversals.
    # pathlib silently discards project_dir when destination is absolute, so we
    # must resolve and verify before touching the filesystem.
    resolved_final = final_path.resolve()
    resolved_project = project_dir.resolve()
    if not resolved_final.is_relative_to(resolved_project):
        raise ValueError(
            f"install_path '{skill.targets[target].install_path}' for skill '{skill.name}' "
            f"resolves outside the project directory"
        )

    final_path.parent.mkdir(parents=True, exist_ok=True)

    if not os.access(final_path.parent, os.W_OK):
        try:
            current_mode = final_path.parent.stat().st_mode
            os.chmod(final_path.parent, current_mode | 0o700)
        except PermissionError:
            raise RuntimeError(
                f"Skills directory '{final_path.parent}' is not writable and permissions could not be fixed automatically. "
                f"Please run: chmod -R u+w {final_path.parent}"
            )

    # [HIGH-2] Render into a temp dir on the same filesystem as the destination
    # so that shutil.move can use os.rename (atomic) instead of copy+delete.
    with tempfile.TemporaryDirectory(prefix=".skill-forge-render-", dir=final_path.parent) as tmp_dir:
        temp_root = Path(tmp_dir)
        rendered_path = render_skill(skill, target, temp_root)

        # Move rendered output to a staging path adjacent to the destination.
        staging = final_path.with_name(f".skill-forge-stage-{final_path.name}")
        _safe_remove(staging)
        shutil.move(str(rendered_path), str(staging))
    # tmp_dir (and any empty scaffold dirs left by render_skill) is cleaned up here.

    # Atomic swap: rename old → backup, put new in place, then discard backup.
    # The old skill is never absent during this window.
    backup = final_path.with_name(f".skill-forge-bak-{final_path.name}")
    _safe_remove(backup)

    if final_path.is_symlink() or final_path.exists():
        os.rename(str(final_path), str(backup))

    try:
        os.rename(str(staging), str(final_path))
    except Exception:
        # Rollback: restore backup so the installed skill is not lost.
        if backup.is_symlink() or backup.exists():
            os.rename(str(backup), str(final_path))
        _safe_remove(staging)
        raise

    _safe_remove(backup)
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
    if not entry.is_dir():
        return {}
    return {
        str(path.relative_to(entry)): sha256_file(path)
        for path in sorted(item for item in entry.rglob("*") if item.is_file())
    }


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
    with tempfile.TemporaryDirectory(prefix="skill-forge-status-") as tmp_dir:
        rendered = render_skill(skill, "codex", Path(tmp_dir))
        return _snapshot_directory(rendered)


def _expected_claude_snapshot(skill: CanonicalSkill) -> dict[str, str]:
    with tempfile.TemporaryDirectory(prefix="skill-forge-status-") as tmp_dir:
        rendered = render_skill(skill, "claude", Path(tmp_dir))
        return _snapshot_claude_bundle(rendered)


def _load_metadata(entry: Path, target: str) -> tuple[dict[str, object] | None, InstalledStatus | None]:
    metadata_path = entry / "metadata.json"
    if not metadata_path.is_file():
        return None, InstalledStatus(name=entry.name, target=target, status="broken", location=entry, details="missing metadata.json")

    try:
        return json.loads(read_text(metadata_path)), None
    except json.JSONDecodeError as exc:
        return None, InstalledStatus(name=entry.name, target=target, status="broken", location=entry, details=f"invalid metadata.json: {exc}")


def _codex_status(repo_root: Path, entry: Path, sources: dict[str, CanonicalSkill]) -> InstalledStatus:
    name = entry.name
    source = sources.get(name)
    if source is None:
        return InstalledStatus(name=name, target="codex", status="unmanaged", location=entry, details="not found in canonical-skills")

    skill_md = entry / "SKILL.md"
    metadata, metadata_error = _load_metadata(entry, "codex")
    if metadata_error is not None:
        return metadata_error

    rendered_from = metadata.get("rendered_from")
    source_hash = metadata.get("source_package_sha256")
    version = metadata.get("version")
    if rendered_from != source.source_ref or not isinstance(source_hash, str):
        return InstalledStatus(name=name, target="codex", status="unmanaged", location=entry, version=version, details="missing or foreign skill-forge metadata")
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
    name = entry.name
    source = sources.get(name)
    if source is None:
        return InstalledStatus(name=name, target="claude", status="unmanaged", location=entry, details="not found in canonical-skills")

    skill_md = entry / "SKILL.md"
    if not skill_md.is_file():
        return InstalledStatus(name=name, target="claude", status="broken", location=entry, details="missing SKILL.md")

    content = read_text(skill_md)
    metadata, metadata_error = _load_metadata(entry, "claude")
    if metadata_error is not None:
        return metadata_error

    rendered_from = metadata.get("rendered_from")
    source_hash = metadata.get("source_package_sha256")
    version = metadata.get("version")
    managed = rendered_from == source.source_ref and isinstance(source_hash, str)
    if not has_frontmatter(content):
        return InstalledStatus(name=name, target="claude", status="broken", location=entry, version=str(version) if version is not None else None, source_package_sha256=str(source_hash) if source_hash is not None else None, details="missing YAML frontmatter", managed=managed)
    if not managed:
        return InstalledStatus(name=name, target="claude", status="unmanaged", location=entry, version=str(version) if version is not None else None, details="missing or foreign skill-forge metadata")
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
        for entry in sorted(path for path in root.iterdir() if path.is_dir()):
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
            if status.status == "broken" and force:
                # broken + no metadata means we can't confirm ownership, but the user
                # has explicitly passed --force so allow the overwrite to proceed.
                pass
            else:
                raise ValueError(
                    f"{skill_name} already exists for target {target} but is unmanaged; refusing to overwrite it"
                )
        elif status.status == "drift":
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

    if "scripts" in skill.asset_dirs:
        print(
            f"notice: {skill_name} includes a scripts/ directory with executable content "
            f"that will be installed to {target} and may run automatically.",
            file=sys.stderr,
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
        raise ValueError(f"{skill_name} is not a managed skill-forge install for target {target}; refusing to update it")
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
        if status.status != "broken":
            raise ValueError(f"{skill_name} is not a managed skill-forge install for target {target}; refusing to remove it")
        # broken with no readable metadata — allow removal so the user can reinstall cleanly

    _safe_remove(status.location)
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
                unmanaged_path = project_dir / ".claude" / "skills" / skill_name
            if unmanaged_path.is_dir():
                shutil.rmtree(unmanaged_path)
            elif unmanaged_path.exists():
                unmanaged_path.unlink()
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
