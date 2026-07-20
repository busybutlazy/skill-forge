from __future__ import annotations

import json
import os
import subprocess
import tempfile
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from .managed_bundles import (
    ManagedBundleStatus,
    install_managed_bundle,
    load_managed_bundle,
    managed_bundle_status,
)


SKILL_FORGE_HOOK_SCRIPT = "${CLAUDE_PROJECT_DIR}/.claude/hooks/skill-forge/safety_check.py"


@dataclass(frozen=True)
class PythonRuntime:
    command: tuple[str, ...]
    version: tuple[int, int, int]


@dataclass(frozen=True)
class ClaudeHookSettingsStatus:
    status: str
    path: Path
    details: str | None = None


@dataclass(frozen=True)
class ClaudeHooksStatus:
    status: str
    settings: ClaudeHookSettingsStatus
    bundle: ManagedBundleStatus
    runtime: PythonRuntime | None


def find_python_runtime(
    *,
    candidates: Sequence[tuple[str, ...]] | None = None,
    run: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> PythonRuntime | None:
    """Find a host Python >= 3.11 without imposing an upper version bound."""
    commands = candidates or (("python3",), ("py", "-3"))
    probe = "import sys; print('.'.join(map(str, sys.version_info[:3])))"
    for command in commands:
        try:
            result = run(
                [*command, "-c", probe],
                text=True,
                capture_output=True,
                check=False,
                timeout=5,
            )
        except (OSError, subprocess.TimeoutExpired):
            continue
        if result.returncode != 0:
            continue
        try:
            version = tuple(int(part) for part in result.stdout.strip().split("."))
        except ValueError:
            continue
        if len(version) == 3 and version >= (3, 11, 0):
            return PythonRuntime(command=tuple(command), version=version)
    return None


def claude_hook_settings_status(project_dir: Path) -> ClaudeHookSettingsStatus:
    path = project_dir / ".claude" / "settings.json"
    if not path.exists():
        return ClaudeHookSettingsStatus("not_installed", path)
    if path.is_symlink() or not path.is_file():
        return ClaudeHookSettingsStatus("unmanaged", path, "settings target is not a regular file")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return ClaudeHookSettingsStatus("unmanaged", path, f"invalid Claude settings JSON: {exc}")
    if not isinstance(payload, dict):
        return ClaudeHookSettingsStatus("unmanaged", path, "Claude settings root must be an object")

    try:
        owned = _owned_handlers(payload)
    except ValueError as exc:
        return ClaudeHookSettingsStatus("unmanaged", path, str(exc))
    if not owned:
        return ClaudeHookSettingsStatus("not_installed", path)
    if owned != _expected_matcher_groups():
        return ClaudeHookSettingsStatus("drift", path, "skill-forge Claude hook settings differ from canonical")
    return ClaudeHookSettingsStatus("up_to_date", path)


def install_claude_hook_settings(
    project_dir: Path,
    *,
    force: bool = False,
    confirm: Callable[[str], bool] | None = None,
    runtime: PythonRuntime | None = None,
) -> Path:
    runtime = runtime or find_python_runtime()
    if runtime is None:
        raise RuntimeError("Python 3.11 or newer is required to install managed safety hooks.")
    if runtime.command != ("python3",):
        raise RuntimeError(
            "Claude hook installation currently requires a Python 3.11+ runtime available as python3; "
            "Windows launcher support is pending validation."
        )

    status = claude_hook_settings_status(project_dir)
    if status.status == "unmanaged":
        raise ValueError(f"{status.path}: {status.details}; refusing to modify")
    if status.status == "drift":
        if not force:
            raise ValueError("Claude hook settings have drifted; rerun install with --force")
        if confirm is None:
            raise ValueError("Claude hook settings have drifted and require confirmation")
        if not confirm("Claude hook settings have drifted. Replace only skill-forge-owned entries? [y/N]: "):
            raise RuntimeError("Update aborted by user.")

    path = status.path
    if path.exists():
        payload = json.loads(path.read_text(encoding="utf-8"))
    else:
        payload = {}
    hooks = payload.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise ValueError("Claude settings hooks must be an object; refusing to modify")
    pre_tool_use = hooks.setdefault("PreToolUse", [])
    if not isinstance(pre_tool_use, list):
        raise ValueError("Claude settings hooks.PreToolUse must be a list; refusing to modify")

    retained = _without_owned_handlers(pre_tool_use)
    hooks["PreToolUse"] = [*retained, *_expected_matcher_groups()]
    _write_json_atomic(path, payload)
    return path


def claude_hooks_status(repo_root: Path, project_dir: Path) -> ClaudeHooksStatus:
    source = load_managed_bundle(repo_root, "agent-hooks")
    if source is None:
        raise ValueError("No canonical agent-hooks bundle found.")
    bundle = managed_bundle_status(source, project_dir, "claude")
    settings = claude_hook_settings_status(project_dir)
    runtime = find_python_runtime()

    if bundle.status == "not_installed" and settings.status == "not_installed":
        status = "not_installed"
    elif "unmanaged" in {bundle.status, settings.status}:
        status = "unmanaged"
    elif "drift" in {bundle.status, settings.status}:
        status = "drift"
    elif bundle.status == "update_available":
        status = "update_available"
    elif bundle.status != "up_to_date" or settings.status != "up_to_date" or runtime is None:
        status = "broken"
    else:
        status = "up_to_date"
    return ClaudeHooksStatus(status, settings, bundle, runtime)


def install_claude_hooks(
    repo_root: Path,
    project_dir: Path,
    *,
    force: bool = False,
    confirm: Callable[[str], bool] | None = None,
    runtime: PythonRuntime | None = None,
) -> tuple[Path, ...]:
    runtime = runtime or find_python_runtime()
    if runtime is None:
        raise RuntimeError("Python 3.11 or newer is required to install managed safety hooks.")
    source = load_managed_bundle(repo_root, "agent-hooks")
    if source is None:
        raise ValueError("No canonical agent-hooks bundle found.")

    settings_status = claude_hook_settings_status(project_dir)
    if settings_status.status == "unmanaged":
        raise ValueError(f"{settings_status.path}: {settings_status.details}; refusing to modify")

    def install_settings() -> None:
        install_claude_hook_settings(
            project_dir,
            force=force,
            confirm=confirm,
            runtime=runtime,
        )

    artifacts = install_managed_bundle(
        source,
        project_dir,
        "claude",
        force=force,
        confirm=confirm,
        post_install=install_settings,
    )
    return (*artifacts, settings_status.path)


def _expected_matcher_groups() -> list[dict[str, object]]:
    return [_expected_matcher_group("Bash"), _expected_matcher_group("Edit|Write|NotebookEdit")]


def _expected_matcher_group(matcher: str) -> dict[str, object]:
    return {
        "matcher": matcher,
        "hooks": [
            {
                "type": "command",
                "command": "python3",
                "args": [SKILL_FORGE_HOOK_SCRIPT],
                "timeout": 10,
                "statusMessage": "Checking skill-forge safety policy",
            }
        ],
    }


def _owned_handlers(payload: dict[str, object]) -> list[object]:
    hooks = payload.get("hooks", {})
    if not isinstance(hooks, dict):
        raise ValueError("Claude settings hooks must be an object")
    groups = hooks.get("PreToolUse", [])
    if not isinstance(groups, list):
        raise ValueError("Claude settings hooks.PreToolUse must be a list")
    return [group for group in groups if _group_is_owned(group)]


def _group_is_owned(group: object) -> bool:
    if not isinstance(group, dict):
        return False
    handlers = group.get("hooks", [])
    if not isinstance(handlers, list):
        return False
    for handler in handlers:
        if not isinstance(handler, dict):
            continue
        args = handler.get("args", [])
        command = handler.get("command")
        if isinstance(args, list) and SKILL_FORGE_HOOK_SCRIPT in args:
            return True
        if isinstance(command, str) and SKILL_FORGE_HOOK_SCRIPT in command:
            return True
    return False


def _without_owned_handlers(groups: list[object]) -> list[object]:
    retained_groups: list[object] = []
    for group in groups:
        if not isinstance(group, dict):
            retained_groups.append(group)
            continue
        handlers = group.get("hooks")
        if not isinstance(handlers, list):
            retained_groups.append(group)
            continue
        retained_handlers = [handler for handler in handlers if not _handler_is_owned(handler)]
        if retained_handlers:
            retained_group = dict(group)
            retained_group["hooks"] = retained_handlers
            retained_groups.append(retained_group)
    return retained_groups


def _handler_is_owned(handler: object) -> bool:
    if not isinstance(handler, dict):
        return False
    args = handler.get("args", [])
    command = handler.get("command")
    return (
        isinstance(args, list)
        and SKILL_FORGE_HOOK_SCRIPT in args
        or isinstance(command, str)
        and SKILL_FORGE_HOOK_SCRIPT in command
    )


def _write_json_atomic(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    original_mode = path.stat().st_mode & 0o777 if path.is_file() else 0o644
    content = (json.dumps(payload, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
            temp_path = Path(handle.name)
        temp_path.chmod(original_mode)
        os.replace(temp_path, path)
        temp_path = None
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
