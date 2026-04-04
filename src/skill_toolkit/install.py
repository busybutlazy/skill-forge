from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

from .models import CanonicalSkill, InstalledStatus
from .render import render_skill
from .repository import load_all_skills, load_skill
from .utils import has_frontmatter, parse_toolkit_marker, read_text


def target_root(project_dir: Path, target: str) -> Path:
    if target == "codex":
        return project_dir / ".agents" / "skills"
    if target == "claude":
        return project_dir / ".claude" / "agents"
    raise ValueError(f"unsupported target: {target}")


def install_skill(repo_root: Path, project_dir: Path, skill_name: str, target: str) -> Path:
    skill = load_skill(repo_root, skill_name, target_filter={target})
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


def _source_index(repo_root: Path) -> dict[str, CanonicalSkill]:
    return {skill.name: skill for skill in load_all_skills(repo_root)}


def _codex_status(repo_root: Path, entry: Path, sources: dict[str, CanonicalSkill]) -> InstalledStatus:
    name = entry.name
    source = sources.get(name)
    if source is None:
        return InstalledStatus(name=name, target="codex", status="unmanaged", location=entry, details="not found in canonical-skills")

    skill_md = entry / "SKILL.md"
    metadata_path = entry / "metadata.json"
    if not skill_md.is_file() or not metadata_path.is_file():
        return InstalledStatus(name=name, target="codex", status="broken", location=entry, details="missing SKILL.md or metadata.json")

    try:
        metadata = json.loads(read_text(metadata_path))
    except json.JSONDecodeError as exc:
        return InstalledStatus(name=name, target="codex", status="broken", location=entry, details=f"invalid metadata.json: {exc}")

    rendered_from = metadata.get("rendered_from")
    source_hash = metadata.get("source_package_sha256")
    version = metadata.get("version")
    if rendered_from != source.source_ref or not isinstance(source_hash, str):
        return InstalledStatus(name=name, target="codex", status="unmanaged", location=entry, version=version, details="missing or foreign toolkit markers")
    if version != source.version:
        return InstalledStatus(name=name, target="codex", status="update_available", location=entry, version=version, source_package_sha256=source_hash)
    if source_hash != source.package_sha256:
        return InstalledStatus(name=name, target="codex", status="drift", location=entry, version=version, source_package_sha256=source_hash)
    return InstalledStatus(name=name, target="codex", status="up_to_date", location=entry, version=version, source_package_sha256=source_hash)


def _claude_status(repo_root: Path, entry: Path, sources: dict[str, CanonicalSkill]) -> InstalledStatus:
    name = entry.stem
    source = sources.get(name)
    if source is None:
        return InstalledStatus(name=name, target="claude", status="unmanaged", location=entry, details="not found in canonical-skills")

    content = read_text(entry)
    if not has_frontmatter(content):
        return InstalledStatus(name=name, target="claude", status="broken", location=entry, details="missing YAML frontmatter")

    marker = parse_toolkit_marker(content)
    if marker is None:
        return InstalledStatus(name=name, target="claude", status="unmanaged", location=entry, details="missing toolkit marker")

    if marker.get("rendered_from") != source.source_ref:
        return InstalledStatus(name=name, target="claude", status="unmanaged", location=entry, details="foreign rendered_from marker")

    version = marker.get("version")
    source_hash = marker.get("source_package_sha256")
    if version != source.version:
        return InstalledStatus(name=name, target="claude", status="update_available", location=entry, version=str(version) if version is not None else None, source_package_sha256=str(source_hash) if source_hash is not None else None)
    if source_hash != source.package_sha256:
        return InstalledStatus(name=name, target="claude", status="drift", location=entry, version=str(version), source_package_sha256=str(source_hash))
    return InstalledStatus(name=name, target="claude", status="up_to_date", location=entry, version=str(version), source_package_sha256=str(source_hash))


def list_installed(repo_root: Path, project_dir: Path, target: str) -> list[InstalledStatus]:
    sources = _source_index(repo_root)
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


def remove_skill(repo_root: Path, project_dir: Path, skill_name: str, target: str) -> Path:
    statuses = {status.name: status for status in list_installed(repo_root, project_dir, target)}
    status = statuses.get(skill_name)
    if status is None:
        raise FileNotFoundError(f"{skill_name} is not installed for target {target}")
    if status.status == "unmanaged":
        raise ValueError(f"{skill_name} is unmanaged for target {target}; refusing to remove it")

    if target == "codex":
        shutil.rmtree(status.location)
        return status.location

    status.location.unlink()
    assets_dir = status.location.with_name(f"{skill_name}.assets")
    if assets_dir.exists():
        shutil.rmtree(assets_dir)
    return status.location
