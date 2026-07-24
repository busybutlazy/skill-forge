from __future__ import annotations

import os
from pathlib import Path


class UnsafeProjectDir(ValueError):
    """Raised when a project directory is too broad to install into."""


def host_project_dir(project_dir: Path) -> Path:
    """Return the path the user sees.

    Inside the runtime container the project is always bind-mounted at
    /workspace/project, so the container path never looks unsafe. The wrapper
    exports the real host directory; validate that instead when it is present.
    """
    host = os.environ.get("SKILL_FORGE_PROJECT_HOST_DIR")
    if not host:
        return project_dir
    return Path(host)


def check_project_dir(project_dir: Path) -> None:
    """Reject project directories that would scatter agent config too widely.

    Running skill-manager from $HOME or / installs hooks into the user-level
    ~/.claude/settings.json, which then applies to every project while
    ${CLAUDE_PROJECT_DIR} resolves elsewhere and the hook script is missing.
    """
    candidate = host_project_dir(project_dir)
    if candidate.parent == candidate:
        raise UnsafeProjectDir(
            f"Refusing to use the filesystem root as a project directory: {candidate}\n"
            "cd into the project you want to manage and rerun."
        )

    home = Path(os.environ.get("HOME") or Path.home())
    if candidate == home:
        raise UnsafeProjectDir(
            f"Refusing to use your home directory as a project directory: {candidate}\n"
            "Installing there writes hooks into the user-level ~/.claude/settings.json, "
            "which then breaks every other project.\n"
            "cd into the project you want to manage and rerun."
        )


def project_dir_warnings(project_dir: Path) -> list[str]:
    """Return non-fatal notes about a project directory."""
    candidate = host_project_dir(project_dir)
    if (project_dir / ".git").exists():
        return []
    return [f"note: {candidate} is not a git repository; double-check this is the project you meant."]
