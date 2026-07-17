#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shlex
import sys
from pathlib import Path


PATCH_FILE_RE = re.compile(r"^\*\*\* (?:Add|Update|Delete) File: (?P<path>.+)$", re.MULTILINE)
SHELL_SEPARATORS = {";", "&&", "||", "&", "|", "\n"}


def main() -> int:
    if sys.version_info < (3, 11):
        return deny("runtime.python-version", "Managed safety hooks require Python 3.11 or newer.")
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError, TypeError):
        return deny("hook.invalid-json", "Hook input is not valid JSON.")
    if not isinstance(payload, dict):
        return deny("hook.invalid-payload", "Hook input must be a JSON object.")

    tool_name = payload.get("tool_name")
    tool_input = payload.get("tool_input", {})
    if not isinstance(tool_name, str) or not isinstance(tool_input, dict):
        return deny("hook.invalid-payload", "Hook input is missing tool_name or tool_input.")
    cwd = Path(str(payload.get("cwd", "."))).resolve(strict=False)
    project_root = find_project_root(cwd)

    decision = None
    if tool_name == "Bash":
        decision = evaluate_shell(str(tool_input.get("command", "")), cwd, project_root)
    elif tool_name == "apply_patch":
        decision = evaluate_patch(str(tool_input.get("command", "")), project_root)
    elif tool_name in {"Edit", "Write"}:
        file_path = tool_input.get("file_path")
        if not isinstance(file_path, str) or not file_path:
            decision = ("write.malformed", "File-write request is missing file_path.")
        elif is_protected_path(file_path, project_root):
            decision = ("path.protected-write", f"Write targets protected project path: {file_path}")

    if decision is None:
        return 0
    return deny(*decision)


def find_project_root(cwd: Path) -> Path:
    current = cwd
    while True:
        if (current / ".git").exists():
            return current
        if current.parent == current:
            return cwd
        current = current.parent


def evaluate_shell(command: str, cwd: Path, project_root: Path) -> tuple[str, str] | None:
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|\n")
        lexer.whitespace = " \t\r"
        lexer.whitespace_split = True
        lexer.commenters = ""
        tokens = list(lexer)
    except ValueError:
        return ("shell.malformed", "Malformed shell command cannot be safely classified.")

    segments: list[list[str]] = [[]]
    for token in tokens:
        if token in SHELL_SEPARATORS:
            if segments[-1]:
                segments.append([])
        else:
            segments[-1].append(token)
    for segment in (item for item in segments if item):
        executable, arguments = command_and_arguments(segment)
        if executable in {"bash", "sh", "zsh"} and "-c" in arguments:
            index = arguments.index("-c") + 1
            if index < len(arguments):
                decision = evaluate_shell(arguments[index], cwd, project_root)
                if decision:
                    return decision
        elif executable == "git":
            decision = evaluate_git(arguments)
            if decision:
                return decision
        elif executable == "rm":
            decision = evaluate_rm(arguments, cwd, project_root)
            if decision:
                return decision
    return None


def command_and_arguments(tokens: list[str]) -> tuple[str | None, list[str]]:
    remaining = list(tokens)
    while remaining and is_assignment(remaining[0]):
        remaining.pop(0)
    if remaining and remaining[0] in {"command", "env", "sudo"}:
        remaining.pop(0)
        while remaining and (remaining[0].startswith("-") or is_assignment(remaining[0])):
            remaining.pop(0)
    if not remaining:
        return None, []
    return Path(remaining[0]).name, remaining[1:]


def is_assignment(token: str) -> bool:
    name, separator, _ = token.partition("=")
    return bool(separator and name and (name[0].isalpha() or name[0] == "_") and name.replace("_", "a").isalnum())


def evaluate_git(arguments: list[str]) -> tuple[str, str] | None:
    index = git_subcommand_index(arguments)
    if index is None:
        return None
    subcommand = arguments[index]
    options = arguments[index + 1 :]
    if subcommand == "reset" and "--hard" in options:
        return ("git.reset-hard", "git reset --hard can discard uncommitted work.")
    if (
        subcommand == "clean"
        and not has_option(options, "n", "--dry-run")
        and has_option(options, "f", "--force")
        and has_option(options, "d", "--directories")
    ):
        return ("git.clean-force", "git clean with force and directory removal can delete untracked work.")
    if subcommand == "push" and any(
        option in {"-f", "--force", "--force-with-lease", "--force-if-includes"}
        for option in options
    ):
        return ("git.force-push", "Force-pushing can rewrite shared history.")
    return None


def git_subcommand_index(arguments: list[str]) -> int | None:
    options_with_values = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}
    index = 0
    while index < len(arguments):
        value = arguments[index]
        if value in options_with_values:
            index += 2
        elif any(value.startswith(f"{option}=") for option in options_with_values if option.startswith("--")):
            index += 1
        elif value.startswith("-"):
            index += 1
        else:
            return index
    return None


def has_option(options: list[str], short: str, long: str) -> bool:
    return any(
        option == long or option.startswith("-") and not option.startswith("--") and short in option[1:]
        for option in options
    )


def evaluate_rm(arguments: list[str], cwd: Path, project_root: Path) -> tuple[str, str] | None:
    if not (has_option(arguments, "r", "--recursive") and has_option(arguments, "f", "--force")):
        return None
    for target in (argument for argument in arguments if not argument.startswith("-")):
        if contains_glob(target):
            return (
                "shell.unresolved-recursive-delete",
                f"Recursive forced deletion contains an unresolved glob target: {target}",
            )
        if broad_delete_target(target, cwd, project_root):
            return (
                "shell.broad-recursive-delete",
                f"Recursive forced deletion targets a broad or protected root: {target}",
            )
    return None


def contains_glob(target: str) -> bool:
    return any(character in target for character in "*?[")


def broad_delete_target(target: str, cwd: Path, project_root: Path) -> bool:
    if target in {"/", ".", "..", "~", "$HOME", "${HOME}"} or "$" in target or "`" in target:
        return True
    candidate = Path(target)
    if not candidate.is_absolute():
        candidate = cwd / candidate
    normalized = candidate.resolve(strict=False)
    root = project_root.resolve(strict=False)
    return normalized in {root, root.parent}


def evaluate_patch(command: str, project_root: Path) -> tuple[str, str] | None:
    paths = [match.group("path").strip() for match in PATCH_FILE_RE.finditer(command)]
    if not paths and command.strip():
        return ("patch.malformed", "Patch target paths cannot be safely classified.")
    for path in paths:
        if is_protected_path(path, project_root):
            return ("path.protected-write", f"Patch targets protected project path: {path}")
    return None


def is_protected_path(raw_path: str, project_root: Path) -> bool:
    candidate = Path(raw_path)
    if not candidate.is_absolute():
        candidate = project_root / candidate
    normalized = candidate.resolve(strict=False)
    root = project_root.resolve(strict=False)
    try:
        parts = normalized.relative_to(root).parts
    except ValueError:
        return False
    if not parts:
        return False
    filename = parts[-1]
    return (
        filename == ".env"
        or filename.startswith(".env.")
        or parts[0] in {".git", "secrets"}
        or parts == ("config", "credentials.json")
        or parts[:2] in {(".claude", "hooks"), (".codex", "hooks")}
    )


def deny(rule_id: str, reason: str) -> int:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": f"[{rule_id}] {reason}",
        }
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
