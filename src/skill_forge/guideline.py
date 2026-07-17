from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from .agent_memory import (
    ConfigItemSource,
    config_file_path,
    config_status,
    install_config,
    load_all_config_items,
    load_config_item,
)
from .claude_hooks import claude_hooks_status, install_claude_hooks
from .codex_hooks import codex_hooks_status, install_codex_hooks
from .managed_bundles import ManagedBundleSource, load_managed_bundle


AGENT_HOOKS_NAME = "agent-hooks"


@dataclass(frozen=True)
class GuidelineItem:
    name: str
    version: str
    description: str
    source: ConfigItemSource | ManagedBundleSource

    @property
    def is_bundle(self) -> bool:
        return isinstance(self.source, ManagedBundleSource)


@dataclass(frozen=True)
class GuidelineItemStatus:
    name: str
    target: str
    status: str
    location: Path
    source_version: str
    version: str | None = None
    details: str | None = None
    artifacts: tuple[dict[str, object], ...] = ()

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "name": self.name,
            "target": self.target,
            "status": self.status,
            "location": str(self.location),
            "source_version": self.source_version,
        }
        if self.version is not None:
            payload["version"] = self.version
        if self.details is not None:
            payload["details"] = self.details
        if self.artifacts:
            payload["artifacts"] = list(self.artifacts)
        return payload


def load_guideline_items(repo_root: Path) -> list[GuidelineItem]:
    items = [
        GuidelineItem(source.name, source.version, source.description, source)
        for source in load_all_config_items(repo_root)
    ]
    bundle = load_managed_bundle(repo_root, AGENT_HOOKS_NAME)
    if bundle is not None:
        items.append(GuidelineItem(bundle.name, bundle.version, bundle.description, bundle))
    return items


def load_guideline_item(repo_root: Path, name: str) -> GuidelineItem | None:
    if name == AGENT_HOOKS_NAME:
        source = load_managed_bundle(repo_root, name)
    else:
        try:
            source = load_config_item(repo_root, name)
        except ValueError:
            return None
    if source is None:
        return None
    return GuidelineItem(source.name, source.version, source.description, source)


def guideline_item_status(
    item: GuidelineItem,
    repo_root: Path,
    project_dir: Path,
    target: str,
) -> GuidelineItemStatus:
    if isinstance(item.source, ConfigItemSource):
        installed = config_status(item.source, project_dir, target)
        location = config_file_path(item.source, project_dir, target)
        if installed is None:
            return GuidelineItemStatus(
                item.name, target, "not_installed", location, item.version
            )
        return GuidelineItemStatus(
            item.name,
            target,
            installed.status,
            installed.location,
            item.version,
            installed.version,
            installed.details,
        )

    aggregate = (
        claude_hooks_status(repo_root, project_dir)
        if target == "claude"
        else codex_hooks_status(repo_root, project_dir)
    )
    artifacts = tuple(
        {
            "id": artifact.artifact_id,
            "status": artifact.status,
            "location": str(artifact.location),
            **({"details": artifact.details} if artifact.details else {}),
        }
        for artifact in aggregate.bundle.artifacts
    )
    details: list[str] = []
    if aggregate.settings.details:
        details.append(aggregate.settings.details)
    if aggregate.runtime is None:
        details.append("Python 3.11 or newer is unavailable")
    if target == "codex":
        if aggregate.feature.details:
            details.append(aggregate.feature.details)
        if aggregate.trust_review_required:
            details.append("Codex hook trust review may be required for this exact definition")
    version = next(
        (artifact.version for artifact in aggregate.bundle.artifacts if artifact.version),
        None,
    )
    return GuidelineItemStatus(
        item.name,
        target,
        aggregate.status,
        aggregate.settings.path,
        item.version,
        version,
        "; ".join(details) or None,
        artifacts,
    )


def install_guideline_item(
    item: GuidelineItem,
    repo_root: Path,
    project_dir: Path,
    target: str,
    *,
    force: bool = False,
    confirm: Callable[[str], bool] | None = None,
) -> tuple[Path, ...]:
    if isinstance(item.source, ConfigItemSource):
        return (
            install_config(
                item.source, project_dir, target, force=force, confirm=confirm
            ),
        )
    if target == "claude":
        return install_claude_hooks(
            repo_root, project_dir, force=force, confirm=confirm
        )
    return install_codex_hooks(
        repo_root, project_dir, force=force, confirm=confirm
    )


def guideline_item_target_note(item: GuidelineItem, target: str) -> str:
    if isinstance(item.source, ConfigItemSource):
        return item.source.spec.target_paths[target]
    if target == "claude":
        return ".claude/hooks/skill-forge/safety_check.py + .claude/settings.json"
    return ".codex/hooks/skill-forge/safety_check.py + .codex/hooks.json"
