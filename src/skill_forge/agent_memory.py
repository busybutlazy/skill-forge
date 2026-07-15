from __future__ import annotations

import json
import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from .models import InstalledStatus
from .utils import read_text, sha256_bytes, write_text

AGENT_MEMORY_NAME = "agent-memory"
MEMORY_TARGET_FILENAMES = {"codex": "AGENTS.md", "claude": "CLAUDE.md"}

# The marker may appear on any line: users commonly append notes after it, and
# that must classify as drift (recoverable) rather than unmanaged (refused).
_MARKER_RE = re.compile(
    r"^<!-- skill-forge:agent-memory version=(?P<version>\S+) sha256=(?P<sha>[0-9a-f]{64}) -->$\n?",
    re.MULTILINE,
)


def _canonical_body(text: str) -> str:
    return text.rstrip("\n") + "\n"


@dataclass(frozen=True)
class AgentMemorySource:
    root: Path
    version: str
    description: str
    updated_at: str
    body: str

    @property
    def body_sha256(self) -> str:
        return sha256_bytes(self.body.encode("utf-8"))


def agent_memory_dir(repo_root: Path) -> Path:
    return repo_root / "canonical-configs" / AGENT_MEMORY_NAME


def load_agent_memory(repo_root: Path) -> AgentMemorySource | None:
    """Load the canonical agent-memory source, or None when the repo has none."""
    source_dir = agent_memory_dir(repo_root)
    config_path = source_dir / "config.json"
    memory_path = source_dir / "memory.md"
    if not config_path.is_file() or not memory_path.is_file():
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

    body = _canonical_body(read_text(memory_path))

    return AgentMemorySource(
        root=source_dir,
        version=version,
        description=str(config.get("description", "")),
        updated_at=str(config.get("updated_at", "")),
        body=body,
    )


def memory_file_path(project_dir: Path, target: str) -> Path:
    try:
        return project_dir / MEMORY_TARGET_FILENAMES[target]
    except KeyError:
        raise ValueError(f"unsupported target: {target}") from None


def render_memory(source: AgentMemorySource) -> str:
    marker = f"<!-- skill-forge:agent-memory version={source.version} sha256={source.body_sha256} -->"
    return f"{source.body}\n{marker}\n"


def memory_status(source: AgentMemorySource, project_dir: Path, target: str) -> InstalledStatus | None:
    """Classify the installed memory file. Returns None when not installed."""
    path = memory_file_path(project_dir, target)
    if not path.is_file():
        return None

    content = read_text(path)
    match = _MARKER_RE.search(content)
    if match is None:
        return InstalledStatus(
            name=AGENT_MEMORY_NAME,
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
            name=AGENT_MEMORY_NAME,
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
            name=AGENT_MEMORY_NAME,
            target=target,
            status="update_available",
            location=path,
            version=recorded_version,
            source_package_sha256=recorded_sha,
            managed=True,
        )
    if recorded_sha != source.body_sha256:
        return InstalledStatus(
            name=AGENT_MEMORY_NAME,
            target=target,
            status="drift",
            location=path,
            version=recorded_version,
            source_package_sha256=recorded_sha,
            details="canonical memory source changed without a version bump",
            managed=True,
        )
    return InstalledStatus(
        name=AGENT_MEMORY_NAME,
        target=target,
        status="up_to_date",
        location=path,
        version=recorded_version,
        source_package_sha256=recorded_sha,
        managed=True,
    )


def install_memory(
    source: AgentMemorySource,
    project_dir: Path,
    target: str,
    *,
    force: bool = False,
    confirm: Callable[[str], bool] | None = None,
) -> Path:
    """Write the rendered memory file, honouring the managed-install safety model."""
    path = memory_file_path(project_dir, target)
    status = memory_status(source, project_dir, target)

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

    write_text(path, render_memory(source))
    return path
