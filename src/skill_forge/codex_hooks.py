from __future__ import annotations

import json
import os
import tempfile
import tomllib
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from .claude_hooks import PythonRuntime, find_python_runtime
from .managed_bundles import (
    ManagedBundleStatus,
    install_managed_bundle,
    load_managed_bundle,
    managed_bundle_status,
)


SKILL_FORGE_HOOK_SCRIPT = ".codex/hooks/skill-forge/safety_check.py"
SKILL_FORGE_COMMAND = (
    'python3 "$(git rev-parse --show-toplevel)/.codex/hooks/skill-forge/safety_check.py"'
)


@dataclass(frozen=True)
class CodexHookSettingsStatus:
    status: str
    path: Path
    details: str | None = None


@dataclass(frozen=True)
class CodexFeatureStatus:
    enabled: bool | None
    path: Path
    details: str | None = None


@dataclass(frozen=True)
class CodexHooksStatus:
    status: str
    settings: CodexHookSettingsStatus
    bundle: ManagedBundleStatus
    runtime: PythonRuntime | None
    feature: CodexFeatureStatus
    trust_review_required: bool


def codex_hook_settings_status(project_dir: Path) -> CodexHookSettingsStatus:
    path = project_dir / ".codex" / "hooks.json"
    if not path.exists():
        return CodexHookSettingsStatus("not_installed", path)
    if path.is_symlink() or not path.is_file():
        return CodexHookSettingsStatus("unmanaged", path, "hooks target is not a regular file")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return CodexHookSettingsStatus("unmanaged", path, f"invalid Codex hooks JSON: {exc}")
    if not isinstance(payload, dict):
        return CodexHookSettingsStatus("unmanaged", path, "Codex hooks root must be an object")
    try:
        owned = _owned_handlers(payload)
    except ValueError as exc:
        return CodexHookSettingsStatus("unmanaged", path, str(exc))
    if not owned:
        return CodexHookSettingsStatus("not_installed", path)
    if owned != _expected_matcher_groups():
        return CodexHookSettingsStatus("drift", path, "skill-forge Codex hooks differ from canonical")
    return CodexHookSettingsStatus("up_to_date", path)


def codex_feature_status(project_dir: Path) -> CodexFeatureStatus:
    path = project_dir / ".codex" / "config.toml"
    if not path.exists():
        return CodexFeatureStatus(True, path)
    if path.is_symlink() or not path.is_file():
        return CodexFeatureStatus(None, path, "Codex config target is not a regular file")
    try:
        payload = tomllib.loads(path.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, OSError) as exc:
        return CodexFeatureStatus(None, path, f"cannot determine hooks feature state: {exc}")
    features = payload.get("features", {})
    if not isinstance(features, dict):
        return CodexFeatureStatus(None, path, "Codex config features must be a table")
    enabled = features.get("hooks", True)
    if not isinstance(enabled, bool):
        return CodexFeatureStatus(None, path, "Codex features.hooks must be a boolean")
    details = None if enabled else "Codex hooks are disabled by project config"
    return CodexFeatureStatus(enabled, path, details)


def install_codex_hook_settings(
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
            "Codex hook installation currently requires a Python 3.11+ runtime available as python3; "
            "Windows launcher support is pending validation."
        )

    status = codex_hook_settings_status(project_dir)
    if status.status == "unmanaged":
        raise ValueError(f"{status.path}: {status.details}; refusing to modify")
    if status.status == "drift":
        if not force:
            raise ValueError("Codex hook settings have drifted; rerun install with --force")
        if confirm is None:
            raise ValueError("Codex hook settings have drifted and require confirmation")
        if not confirm("Codex hook settings have drifted. Replace only skill-forge-owned entries? [y/N]: "):
            raise RuntimeError("Update aborted by user.")

    path = status.path
    payload = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    hooks = payload.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise ValueError("Codex hooks must be an object; refusing to modify")
    pre_tool_use = hooks.setdefault("PreToolUse", [])
    if not isinstance(pre_tool_use, list):
        raise ValueError("Codex hooks.PreToolUse must be a list; refusing to modify")
    hooks["PreToolUse"] = [*_without_owned_handlers(pre_tool_use), *_expected_matcher_groups()]
    _write_json_atomic(path, payload)
    return path


def codex_hooks_status(repo_root: Path, project_dir: Path) -> CodexHooksStatus:
    source = load_managed_bundle(repo_root, "agent-hooks")
    if source is None:
        raise ValueError("No canonical agent-hooks bundle found.")
    bundle = managed_bundle_status(source, project_dir, "codex")
    settings = codex_hook_settings_status(project_dir)
    runtime = find_python_runtime()
    feature = codex_feature_status(project_dir)

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
    elif feature.enabled is None:
        status = "broken"
    elif feature.enabled is False:
        status = "inactive"
    else:
        status = "up_to_date"
    return CodexHooksStatus(status, settings, bundle, runtime, feature, settings.status == "up_to_date")


def install_codex_hooks(
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
    settings_status = codex_hook_settings_status(project_dir)
    if settings_status.status == "unmanaged":
        raise ValueError(f"{settings_status.path}: {settings_status.details}; refusing to modify")

    def install_settings() -> None:
        install_codex_hook_settings(
            project_dir, force=force, confirm=confirm, runtime=runtime
        )

    artifacts = install_managed_bundle(
        source,
        project_dir,
        "codex",
        force=force,
        confirm=confirm,
        post_install=install_settings,
    )
    return (*artifacts, settings_status.path)


def _expected_matcher_groups() -> list[dict[str, object]]:
    return [_expected_matcher_group("Bash"), _expected_matcher_group("Edit|Write")]


def _expected_matcher_group(matcher: str) -> dict[str, object]:
    return {
        "matcher": matcher,
        "hooks": [
            {
                "type": "command",
                "command": SKILL_FORGE_COMMAND,
                "timeout": 10,
                "statusMessage": "Checking skill-forge safety policy",
            }
        ],
    }


def _owned_handlers(payload: dict[str, object]) -> list[object]:
    hooks = payload.get("hooks", {})
    if not isinstance(hooks, dict):
        raise ValueError("Codex hooks must be an object")
    groups = hooks.get("PreToolUse", [])
    if not isinstance(groups, list):
        raise ValueError("Codex hooks.PreToolUse must be a list")
    return [group for group in groups if _group_is_owned(group)]


def _group_is_owned(group: object) -> bool:
    if not isinstance(group, dict):
        return False
    handlers = group.get("hooks", [])
    return isinstance(handlers, list) and any(_handler_is_owned(handler) for handler in handlers)


def _handler_is_owned(handler: object) -> bool:
    return (
        isinstance(handler, dict)
        and isinstance(handler.get("command"), str)
        and SKILL_FORGE_HOOK_SCRIPT in handler["command"]
    )


def _without_owned_handlers(groups: list[object]) -> list[object]:
    retained_groups: list[object] = []
    for group in groups:
        if not isinstance(group, dict) or not isinstance(group.get("hooks"), list):
            retained_groups.append(group)
            continue
        retained_handlers = [handler for handler in group["hooks"] if not _handler_is_owned(handler)]
        if retained_handlers:
            retained_group = dict(group)
            retained_group["hooks"] = retained_handlers
            retained_groups.append(retained_group)
    return retained_groups


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
