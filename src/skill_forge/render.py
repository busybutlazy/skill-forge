from __future__ import annotations

import json
import shutil
from pathlib import Path

from .models import CanonicalSkill
from .utils import dump_frontmatter, make_forge_marker, write_text


def _copy_assets(skill: CanonicalSkill, destination: Path) -> None:
    for asset_dir in skill.asset_dirs:
        src = skill.root / asset_dir
        dest = destination / asset_dir
        shutil.copytree(src, dest, dirs_exist_ok=True)


def render_skill(skill: CanonicalSkill, target: str, output_root: Path) -> Path:
    if target not in skill.targets:
        raise ValueError(f"skill {skill.name} does not define target {target}")

    config = skill.targets[target]
    relative_path = Path(config.install_path.format(name=skill.name))
    target_path = output_root / relative_path

    if target == "codex":
        target_path.mkdir(parents=True, exist_ok=True)
        skill_md = dump_frontmatter(config.frontmatter) + skill.instruction
        metadata = {
            "name": skill.name,
            "version": skill.version,
            "description": skill.description,
            "updated_at": skill.updated_at,
            "tags": skill.tags,
            "source_package_sha256": skill.package_sha256,
            "rendered_from": skill.source_ref,
        }
        write_text(target_path / "SKILL.md", skill_md)
        write_text(target_path / "metadata.json", json.dumps(metadata, ensure_ascii=False, indent=2) + "\n")
        _copy_assets(skill, target_path)
        return target_path

    if target == "claude":
        target_path.parent.mkdir(parents=True, exist_ok=True)
        marker = make_forge_marker(
            {
                "name": skill.name,
                "version": skill.version,
                "source_package_sha256": skill.package_sha256,
                "rendered_from": skill.source_ref,
            }
        )
        content = dump_frontmatter(config.frontmatter) + marker + "\n" + skill.instruction
        write_text(target_path, content)
        if skill.asset_dirs:
            assets_root = target_path.with_name(f"{skill.name}.assets")
            _copy_assets(skill, assets_root)
        return target_path

    raise ValueError(f"unsupported target: {target}")
