from __future__ import annotations

import json
from pathlib import Path

from .models import SecurityCheckResult

SECURITY_DEFAULTS: dict = {
    "$schema": "https://json.schemastore.org/claude-code-settings.json",
    "permissions": {
        "deny": [
            "Read(./.env)",
            "Read(./.env.*)",
            "Read(./secrets/**)",
            "Read(./config/credentials.json)",
            "Read(~/.aws/credentials)",
            "Read(~/.ssh/id_*)",
            "Read(~/.npmrc)",
        ],
    },
    "env": {
        "CLAUDE_CODE_SUBPROCESS_ENV_SCRUB": "1",
    },
    "disableBypassPermissionsMode": "disable",
    "allowManagedHooksOnly": True,
    "allowedHttpHookUrls": [],
    "httpHookAllowedEnvVars": [],
    "sandbox": {
        "enabled": True,
        "autoAllowBashIfSandboxed": True,
        "excludedCommands": [
            "docker *",
        ],
        "filesystem": {
            "denyRead": [
                "~/.aws/credentials",
                "~/.ssh",
                "~/.gnupg",
            ],
            "denyWrite": [
                "/etc",
                "/usr/local/bin",
                "~/.ssh",
                "~/.aws",
                "~/.gnupg",
            ],
        },
    },
}

_RESET = "\033[0m"
_BOLD = "\033[1m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"


def _settings_path(project_dir: Path) -> Path:
    return project_dir / ".claude" / "settings.local.json"


def check_security_settings(project_dir: Path) -> SecurityCheckResult:
    """Check whether the project has a complete settings.local.json."""
    path = _settings_path(project_dir)
    if not path.is_file():
        return SecurityCheckResult(settings_path=path, exists=False, missing_keys=[])

    try:
        existing = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return SecurityCheckResult(settings_path=path, exists=True, missing_keys=["(file is invalid JSON)"])

    missing = _find_missing(existing, SECURITY_DEFAULTS)
    return SecurityCheckResult(settings_path=path, exists=True, missing_keys=missing)


def init_security_settings(project_dir: Path) -> Path:
    """Create a default settings.local.json. Raises if the file already exists."""
    path = _settings_path(project_dir)
    if path.is_file():
        raise FileExistsError(f"settings.local.json already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(SECURITY_DEFAULTS, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path


def merge_security_defaults(project_dir: Path) -> list[str]:
    """Merge missing security defaults into an existing settings.local.json.

    Strategy: additive only — never removes or overwrites existing values.
    Returns the list of keys/items that were actually added.
    """
    path = _settings_path(project_dir)
    try:
        existing = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

    applied: list[str] = []
    _merge_dict(existing, SECURITY_DEFAULTS, applied, prefix="")

    if applied:
        path.write_text(
            json.dumps(existing, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return applied


def format_applied_report(applied_keys: list[str], settings_path: Path | None = None) -> str:
    """Format a report of items that were auto-applied."""
    lines = [f"{_YELLOW}{_BOLD}[security]{_RESET} Auto-applied missing security defaults:"]
    for key in applied_keys:
        lines.append(f"  {_GREEN}+{_RESET} {key}")
    if settings_path is not None:
        lines.append(f"  File: {settings_path}")
    return "\n".join(lines)


def format_created_report(settings_path: Path) -> str:
    """Format a report when a new default file was created."""
    return f"{_GREEN}{_BOLD}[security]{_RESET} Created default security settings: {settings_path}"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _find_missing(existing: dict, defaults: dict, prefix: str = "") -> list[str]:
    """Find keys/items in defaults that are absent from existing."""
    missing: list[str] = []

    for key, default_value in defaults.items():
        key_path = f"{prefix}{key}" if not prefix else f"{prefix}.{key}"

        if key not in existing:
            missing.append(key_path)
            continue

        existing_value = existing[key]

        if isinstance(default_value, dict) and isinstance(existing_value, dict):
            missing.extend(_find_missing(existing_value, default_value, key_path))
        elif isinstance(default_value, list) and isinstance(existing_value, list):
            existing_set = set(existing_value)
            for item in default_value:
                if item not in existing_set:
                    missing.append(f"{key_path}: {item}")

    return missing


def _merge_dict(target: dict, defaults: dict, applied: list[str], prefix: str) -> None:
    """Recursively merge defaults into target (additive only)."""
    for key, default_value in defaults.items():
        key_path = f"{prefix}{key}" if not prefix else f"{prefix}.{key}"

        if key not in target:
            target[key] = _deep_copy_json(default_value)
            applied.append(key_path)
            continue

        existing_value = target[key]

        if isinstance(default_value, dict) and isinstance(existing_value, dict):
            _merge_dict(existing_value, default_value, applied, key_path)
        elif isinstance(default_value, list) and isinstance(existing_value, list):
            existing_set = set(existing_value)
            for item in default_value:
                if item not in existing_set:
                    existing_value.append(item)
                    applied.append(f"{key_path}: {item}")


def _deep_copy_json(value: object) -> object:
    """Deep copy a JSON-compatible value."""
    if isinstance(value, dict):
        return {k: _deep_copy_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_deep_copy_json(item) for item in value]
    return value
