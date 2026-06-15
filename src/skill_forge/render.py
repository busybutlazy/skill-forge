from __future__ import annotations

import json
import shutil
from pathlib import Path

from .models import CanonicalSkill
from .utils import dump_frontmatter, write_text


def _copy_assets(skill: CanonicalSkill, destination: Path) -> None:
    for asset_dir in skill.asset_dirs:
        src = skill.root / asset_dir
        dest = destination / asset_dir
        # symlinks=True preserves symlinks as symlinks instead of following them.
        shutil.copytree(src, dest, dirs_exist_ok=True, symlinks=True)


def _metadata_payload(skill: CanonicalSkill) -> dict[str, object]:
    return {
        "name": skill.name,
        "version": skill.version,
        "description": skill.description,
        "updated_at": skill.updated_at,
        "tags": skill.tags,
        "source_package_sha256": skill.package_sha256,
        "rendered_from": skill.source_ref,
    }


def render_skill(skill: CanonicalSkill, target: str, output_root: Path) -> Path:
    if target not in skill.targets:
        raise ValueError(f"skill {skill.name} does not define target {target}")

    config = skill.targets[target]
    relative_path = Path(config.install_path.format(name=skill.name))
    target_path = output_root / relative_path

    if target == "codex":
        target_path.mkdir(parents=True, exist_ok=True)
        skill_md = dump_frontmatter(config.frontmatter) + skill.instruction
        metadata = _metadata_payload(skill)
        write_text(target_path / "SKILL.md", skill_md)
        write_text(target_path / "metadata.json", json.dumps(metadata, ensure_ascii=False, indent=2) + "\n")
        _copy_assets(skill, target_path)
        return target_path

    if target == "claude":
        target_path.mkdir(parents=True, exist_ok=True)
        metadata = _metadata_payload(skill)
        content = dump_frontmatter(config.frontmatter) + skill.instruction
        write_text(target_path / "SKILL.md", content)
        write_text(target_path / "metadata.json", json.dumps(metadata, ensure_ascii=False, indent=2) + "\n")
        _copy_assets(skill, target_path)
        return target_path

    raise ValueError(f"unsupported target: {target}")
