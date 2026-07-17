from __future__ import annotations

import json
import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from .models import InstalledStatus
from .utils import read_text, sha256_bytes, write_text

AGENT_MEMORY_NAME = "agent-memory"
AGENT_GUIDELINE_NAME = "agent-guideline"


@dataclass(frozen=True)
class ConfigItemSpec:
    name: str
    body_filename: str
    target_paths: dict[str, str]


CONFIG_ITEMS: dict[str, ConfigItemSpec] = {
    AGENT_MEMORY_NAME: ConfigItemSpec(
        name=AGENT_MEMORY_NAME,
        body_filename="memory.md",
        target_paths={"codex": "AGENTS.md", "claude": "CLAUDE.md"},
    ),
    AGENT_GUIDELINE_NAME: ConfigItemSpec(
        name=AGENT_GUIDELINE_NAME,
        body_filename="guideline.md",
        target_paths={"codex": "docs/agent-guideline.md", "claude": "docs/agent-guideline.md"},
    ),
}

MEMORY_TARGET_FILENAMES = CONFIG_ITEMS[AGENT_MEMORY_NAME].target_paths


def _marker_re(name: str) -> re.Pattern[str]:
    # The marker may appear on any line: users commonly append notes after it, and
    # that must classify as drift (recoverable) rather than unmanaged (refused).
    return re.compile(
        rf"^<!-- skill-forge:{re.escape(name)} version=(?P<version>\S+) sha256=(?P<sha>[0-9a-f]{{64}}) -->$\n?",
        re.MULTILINE,
    )


def _canonical_body(text: str) -> str:
    return text.rstrip("\n") + "\n"


@dataclass(frozen=True)
class ConfigItemSource:
    spec: ConfigItemSpec
    root: Path
    version: str
    description: str
    updated_at: str
    body: str

    @property
    def name(self) -> str:
        return self.spec.name

    @property
    def body_sha256(self) -> str:
        return sha256_bytes(self.body.encode("utf-8"))


# Backwards-compatible alias for the pre-registry single-item API.
AgentMemorySource = ConfigItemSource


def config_item_dir(repo_root: Path, name: str) -> Path:
    return repo_root / "canonical-configs" / name


def load_config_item(repo_root: Path, name: str) -> ConfigItemSource | None:
    """Load a canonical config item source, or None when the repo has none."""
    try:
        spec = CONFIG_ITEMS[name]
    except KeyError:
        raise ValueError(f"unknown config item: {name}") from None

    source_dir = config_item_dir(repo_root, name)
    config_path = source_dir / "config.json"
    body_path = source_dir / spec.body_filename
    if not config_path.is_file() or not body_path.is_file():
        return None

    try:
        config = json.loads(read_text(config_path))
    except json.JSONDecodeError:
        return None
    if not isinstance(config, dict) or config.get("schema_version") != 1:
        return None

    version = config.get("version")
    if not isinstance(version, str):
        return None

    body = _canonical_body(read_text(body_path))

    return ConfigItemSource(
        spec=spec,
        root=source_dir,
        version=version,
        description=str(config.get("description", "")),
        updated_at=str(config.get("updated_at", "")),
        body=body,
    )


def load_all_config_items(repo_root: Path) -> list[ConfigItemSource]:
    """Load every available config item; items without a canonical source are skipped."""
    sources: list[ConfigItemSource] = []
    for name in CONFIG_ITEMS:
        source = load_config_item(repo_root, name)
        if source is not None:
            sources.append(source)
    return sources


def load_agent_memory(repo_root: Path) -> ConfigItemSource | None:
    """Load the canonical agent-memory source, or None when the repo has none."""
    return load_config_item(repo_root, AGENT_MEMORY_NAME)


def config_file_path(source: ConfigItemSource, project_dir: Path, target: str) -> Path:
    try:
        return project_dir / source.spec.target_paths[target]
    except KeyError:
        raise ValueError(f"unsupported target: {target}") from None


def memory_file_path(project_dir: Path, target: str) -> Path:
    try:
        return project_dir / MEMORY_TARGET_FILENAMES[target]
    except KeyError:
        raise ValueError(f"unsupported target: {target}") from None


def render_config(source: ConfigItemSource) -> str:
    marker = f"<!-- skill-forge:{source.name} version={source.version} sha256={source.body_sha256} -->"
    return f"{source.body}\n{marker}\n"


def config_status(source: ConfigItemSource, project_dir: Path, target: str) -> InstalledStatus | None:
    """Classify the installed config file. Returns None when not installed."""
    path = config_file_path(source, project_dir, target)
    if not path.is_file():
        return None

    content = read_text(path)
    match = _marker_re(source.name).search(content)
    if match is None:
        return InstalledStatus(
            name=source.name,
            target=target,
            status="unmanaged",
            location=path,
            details="missing skill-forge marker; file was not installed by skill-forge",
        )

    recorded_version = match.group("version")
    recorded_sha = match.group("sha")
    body = _canonical_body(content[: match.start()] + content[match.end() :])
    actual_sha = sha256_bytes(body.encode("utf-8"))

    if actual_sha != recorded_sha:
        return InstalledStatus(
            name=source.name,
            target=target,
            status="drift",
            location=path,
            version=recorded_version,
            source_package_sha256=recorded_sha,
            details="installed content differs from the recorded hash",
            managed=True,
        )
    if recorded_version != source.version:
        return InstalledStatus(
            name=source.name,
            target=target,
            status="update_available",
            location=path,
            version=recorded_version,
            source_package_sha256=recorded_sha,
            managed=True,
        )
    if recorded_sha != source.body_sha256:
        return InstalledStatus(
            name=source.name,
            target=target,
            status="drift",
            location=path,
            version=recorded_version,
            source_package_sha256=recorded_sha,
            details="canonical config source changed without a version bump",
            managed=True,
        )
    return InstalledStatus(
        name=source.name,
        target=target,
        status="up_to_date",
        location=path,
        version=recorded_version,
        source_package_sha256=recorded_sha,
        managed=True,
    )


def install_config(
    source: ConfigItemSource,
    project_dir: Path,
    target: str,
    *,
    force: bool = False,
    confirm: Callable[[str], bool] | None = None,
) -> Path:
    """Write the rendered config file, honouring the managed-install safety model."""
    path = config_file_path(source, project_dir, target)
    status = config_status(source, project_dir, target)

    if status is not None:
        if not status.managed:
            raise ValueError(
                f"{path.name} already exists but was not installed by skill-forge; "
                f"refusing to overwrite it (merge or remove it manually first)"
            )
        if status.status == "drift":
            if not force:
                raise ValueError(
                    f"{path.name} has drifted from canonical source for target {target}; "
                    f"rerun install with --force to overwrite local changes"
                )
            if confirm is None:
                raise ValueError(
                    f"{path.name} has drifted from canonical source for target {target}"
                )
            if not confirm(
                f"{path.name} has drifted from canonical source for target {target}. "
                f"Install will overwrite local changes. Continue? [y/N]: "
            ):
                raise RuntimeError("Update aborted by user.")

    write_text(path, render_config(source))
    return path
