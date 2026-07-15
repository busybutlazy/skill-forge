from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

CATALOG_FILENAME = "catalog.json"


@dataclass(frozen=True)
class CatalogGroup:
    name: str
    skills: list[str]


@dataclass(frozen=True)
class CatalogConfig:
    groups: list[CatalogGroup] = field(default_factory=list)
    recommended: list[str] = field(default_factory=list)
    highlight_keywords: list[str] = field(default_factory=list)


def catalog_path(repo_root: Path) -> Path:
    return repo_root / "canonical-skills" / CATALOG_FILENAME


def load_catalog(repo_root: Path) -> CatalogConfig:
    """Load the display catalog. A missing or invalid file degrades to an empty config."""
    path = catalog_path(repo_root)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return CatalogConfig()
    if not isinstance(data, dict):
        return CatalogConfig()

    groups: list[CatalogGroup] = []
    for entry in data.get("groups") or []:
        if not isinstance(entry, dict):
            continue
        name = entry.get("name")
        skills = entry.get("skills")
        if not isinstance(name, str) or not isinstance(skills, list):
            continue
        groups.append(CatalogGroup(name=name, skills=[item for item in skills if isinstance(item, str)]))

    recommended = [item for item in (data.get("recommended") or []) if isinstance(item, str)]
    keywords = [item for item in (data.get("highlight_keywords") or []) if isinstance(item, str)]
    return CatalogConfig(groups=groups, recommended=recommended, highlight_keywords=keywords)


def group_skill_names(
    names: list[str],
    catalog: CatalogConfig,
    *,
    recommended_label: str = "Recommended",
    others_label: str = "Others",
) -> list[tuple[str, list[str]]]:
    """Partition skill names into ordered display sections.

    Recommended skills always appear (once) in the recommended section, even if
    they also belong to a catalog group. Remaining names follow catalog group
    order; anything left over lands in the others section. Catalog entries that
    do not match an available name are ignored.
    """
    available = set(names)
    placed: set[str] = set()
    sections: list[tuple[str, list[str]]] = []

    recommended = [name for name in catalog.recommended if name in available and name not in placed]
    placed.update(recommended)
    if recommended:
        sections.append((recommended_label, recommended))

    for group in catalog.groups:
        members = [name for name in group.skills if name in available and name not in placed]
        placed.update(members)
        if members:
            sections.append((group.name, members))

    others = [name for name in names if name not in placed]
    if others:
        sections.append((others_label, others))
    return sections
