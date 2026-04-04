from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .repository import OPTIONAL_ASSET_DIRS, resolve_skill_dir
from .utils import compute_package_sha, read_text, sha256_file, write_text


@dataclass(frozen=True)
class RefreshMetadataResult:
    skill: str
    package_sha256: str
    updated_fields: list[str]
    manifest_files: list[str]


def _manifest_paths(skill_dir: Path) -> list[str]:
    paths = ["instruction.md"]
    targets_dir = skill_dir / "targets"
    if targets_dir.is_dir():
        for path in sorted(item for item in targets_dir.rglob("*") if item.is_file()):
            paths.append(str(path.relative_to(skill_dir)))
    for asset_dir in OPTIONAL_ASSET_DIRS:
        root = skill_dir / asset_dir
        if not root.is_dir():
            continue
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            paths.append(str(path.relative_to(skill_dir)))
    return paths


def refresh_skill_metadata(
    repo_root: Path,
    skill: str | Path,
    *,
    version: str | None = None,
    updated_at: str | None = None,
    use_today: bool = False,
) -> RefreshMetadataResult:
    skill_dir = resolve_skill_dir(repo_root, skill)
    package_path = skill_dir / "package.json"
    manifest_path = skill_dir / "manifest.json"

    package_data = json.loads(read_text(package_path))
    manifest_paths = _manifest_paths(skill_dir)
    file_entries = [(rel_path, sha256_file(skill_dir / rel_path)) for rel_path in manifest_paths]
    package_sha = compute_package_sha(file_entries)

    manifest_data = {
        "files": [{"path": rel_path, "sha256": digest} for rel_path, digest in file_entries],
        "package_sha256": package_sha,
    }

    fields: list[str] = []
    if version is not None and package_data["identity"].get("version") != version:
        package_data["identity"]["version"] = version
        fields.append("identity.version")

    next_updated_at = updated_at
    if use_today and updated_at is None:
        next_updated_at = date.today().isoformat()
    if next_updated_at is not None and package_data["identity"].get("updated_at") != next_updated_at:
        package_data["identity"]["updated_at"] = next_updated_at
        fields.append("identity.updated_at")

    if package_data["integrity"].get("package_sha256") != package_sha:
        package_data["integrity"]["package_sha256"] = package_sha
        fields.append("integrity.package_sha256")

    write_text(manifest_path, json.dumps(manifest_data, ensure_ascii=False, indent=2) + "\n")
    write_text(package_path, json.dumps(package_data, ensure_ascii=False, indent=2) + "\n")

    return RefreshMetadataResult(
        skill=package_data["identity"]["name"],
        package_sha256=package_sha,
        updated_fields=fields,
        manifest_files=manifest_paths,
    )
