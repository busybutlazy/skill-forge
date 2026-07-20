from __future__ import annotations

import re
import shlex
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class HookRequest:
    tool_name: str
    command: str
    cwd: Path
    project_root: Path
    file_path: str | None = None


@dataclass(frozen=True)
class HookDecision:
    allowed: bool
    rule_id: str | None = None
    reason: str | None = None


_ALLOW = HookDecision(allowed=True)
_PATCH_FILE_RE = re.compile(r"^\*\*\* (?:Add|Update|Delete) File: (?P<path>.+)$", re.MULTILINE)
_SHELL_SEPARATORS = {";", "&&", "||", "&", "|", "\n"}


def evaluate_hook_request(request: HookRequest) -> HookDecision:
    """Evaluate one normalized hook request without performing side effects."""
    if request.tool_name == "Bash":
        return _evaluate_shell(request)
    if request.tool_name == "apply_patch":
        return _evaluate_patch(request)
    if request.tool_name in {"Edit", "Write", "NotebookEdit"}:
        return _evaluate_file_write(request)
    return _ALLOW


def _evaluate_shell(request: HookRequest) -> HookDecision:
    try:
        tokens = _shell_tokens(request.command)
    except ValueError:
        return HookDecision(
            allowed=False,
            rule_id="shell.malformed",
            reason="Refusing a malformed shell command that cannot be safely classified.",
        )

    for segment in _command_segments(tokens):
        executable, arguments = _command_and_arguments(segment)
        if executable is None:
            continue

        if executable in {"bash", "sh", "zsh"} and "-c" in arguments:
            command_index = arguments.index("-c") + 1
            if command_index < len(arguments):
                decision = _evaluate_shell(
                    HookRequest(
                        tool_name="Bash",
                        command=arguments[command_index],
                        cwd=request.cwd,
                        project_root=request.project_root,
                    )
                )
                if not decision.allowed:
                    return decision
        elif executable == "git":
            decision = _evaluate_git(arguments, request)
            if not decision.allowed:
                return decision
        elif executable == "rm":
            decision = _evaluate_rm(arguments, request)
            if not decision.allowed:
                return decision
        else:
            decision = _evaluate_host_dependency_install(executable, arguments)
            if not decision.allowed:
                return decision
    return _ALLOW


def _shell_tokens(command: str) -> list[str]:
    lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|\n")
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    lexer.commenters = ""
    return list(lexer)


def _command_segments(tokens: list[str]) -> list[list[str]]:
    segments: list[list[str]] = [[]]
    for token in tokens:
        if token in _SHELL_SEPARATORS:
            if segments[-1]:
                segments.append([])
            continue
        segments[-1].append(token)
    return [segment for segment in segments if segment]


def _command_and_arguments(tokens: list[str]) -> tuple[str | None, list[str]]:
    remaining = list(tokens)
    while remaining and _is_environment_assignment(remaining[0]):
        remaining.pop(0)
    if remaining and remaining[0] in {"command", "env", "sudo"}:
        remaining.pop(0)
        while remaining and (remaining[0].startswith("-") or _is_environment_assignment(remaining[0])):
            remaining.pop(0)
    if not remaining:
        return None, []
    return Path(remaining[0]).name, remaining[1:]


def _is_environment_assignment(token: str) -> bool:
    name, separator, _ = token.partition("=")
    return bool(separator and name and (name[0].isalpha() or name[0] == "_") and name.replace("_", "a").isalnum())


def _evaluate_git(arguments: list[str], request: HookRequest) -> HookDecision:
    subcommand_index = _git_subcommand_index(arguments)
    if subcommand_index is None:
        return _ALLOW
    subcommand = arguments[subcommand_index]
    options = arguments[subcommand_index + 1 :]

    if subcommand == "reset" and "--hard" in options:
        return HookDecision(False, "git.reset-hard", "git reset --hard can discard uncommitted work.")
    if (
        subcommand == "clean"
        and not _has_short_or_long_option(options, "n", "--dry-run")
        and _has_short_or_long_option(options, "f", "--force")
        and _has_short_or_long_option(options, "d", "--directories")
    ):
        return HookDecision(False, "git.clean-force", "git clean with force and directory removal can delete untracked work.")
    if subcommand == "push" and any(
        option in {"-f", "--force", "--force-with-lease", "--force-if-includes"}
        for option in options
    ):
        return HookDecision(False, "git.force-push", "Force-pushing can rewrite shared history.")
    if subcommand == "commit":
        branch = _current_git_branch(_git_worktree(arguments, subcommand_index, request))
        if branch in {"main", "master"}:
            return HookDecision(False, "git.protected-branch-commit", f"Direct commits on {branch} are not allowed; create a working branch first.")
    return _ALLOW


def _git_worktree(arguments: list[str], subcommand_index: int, request: HookRequest) -> Path:
    worktree = request.cwd
    changed_directory = False
    index = 0
    while index < subcommand_index:
        if arguments[index] == "-C" and index + 1 < subcommand_index:
            candidate = Path(arguments[index + 1])
            worktree = candidate if candidate.is_absolute() else worktree / candidate
            worktree = worktree.resolve(strict=False)
            changed_directory = True
            index += 2
        else:
            index += 1
    return worktree if changed_directory else request.project_root


def _current_git_branch(worktree: Path) -> str | None:
    git_entry = worktree / ".git"
    git_dir = git_entry
    if git_entry.is_file():
        try:
            marker, value = git_entry.read_text(encoding="utf-8").strip().split(":", 1)
        except (OSError, ValueError):
            return None
        if marker != "gitdir":
            return None
        candidate = Path(value.strip())
        git_dir = candidate if candidate.is_absolute() else (worktree / candidate).resolve(strict=False)
    try:
        head = (git_dir / "HEAD").read_text(encoding="utf-8").strip()
    except OSError:
        return None
    prefix = "ref: refs/heads/"
    return head.removeprefix(prefix) if head.startswith(prefix) else None


def _evaluate_host_dependency_install(executable: str | None, arguments: list[str]) -> HookDecision:
    if executable is None:
        return _ALLOW
    install = False
    if executable == "uv":
        install = any(argument in {"add", "remove", "sync"} for argument in arguments) or ("pip" in arguments and "install" in arguments)
    elif executable == "poetry":
        install = any(argument in {"add", "install", "update"} for argument in arguments)
    elif executable == "npm":
        install = any(argument in {"i", "install", "ci", "add", "update"} for argument in arguments)
    elif executable == "pnpm":
        install = any(argument in {"i", "install", "add", "update"} for argument in arguments)
    elif executable == "yarn":
        query_only = bool(arguments) and all(argument in {"--version", "-v", "--help", "-h"} for argument in arguments)
        install = not query_only and (not arguments or any(argument in {"add", "install", "upgrade"} for argument in arguments) or all(argument.startswith("-") for argument in arguments))
    elif executable == "pip" or re.fullmatch(r"pip\d+(?:\.\d+)?", executable):
        install = "install" in arguments
    elif re.fullmatch(r"python\d*(?:\.\d+)?", executable):
        install = "-m" in arguments and "pip" in arguments and "install" in arguments
    if install:
        return HookDecision(False, "dependency.host-install", "Project dependencies must be installed through the approved Docker/container entrypoint.")
    return _ALLOW


def _git_subcommand_index(arguments: list[str]) -> int | None:
    options_with_values = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}
    index = 0
    while index < len(arguments):
        value = arguments[index]
        if value in options_with_values:
            index += 2
            continue
        if any(value.startswith(f"{option}=") for option in options_with_values if option.startswith("--")):
            index += 1
            continue
        if value.startswith("-"):
            index += 1
            continue
        return index
    return None


def _has_short_or_long_option(options: list[str], short: str, long: str) -> bool:
    for option in options:
        if option == long:
            return True
        if option.startswith("-") and not option.startswith("--") and short in option[1:]:
            return True
    return False


def _evaluate_rm(arguments: list[str], request: HookRequest) -> HookDecision:
    recursive = _has_short_or_long_option(arguments, "r", "--recursive")
    forced = _has_short_or_long_option(arguments, "f", "--force")
    if not (recursive and forced):
        return _ALLOW

    targets = [argument for argument in arguments if not argument.startswith("-")]
    for target in targets:
        if _contains_glob(target):
            return HookDecision(
                False,
                "shell.unresolved-recursive-delete",
                f"Recursive forced deletion contains an unresolved glob target: {target}",
            )
        if _is_broad_delete_target(target, request):
            return HookDecision(
                False,
                "shell.broad-recursive-delete",
                f"Recursive forced deletion targets a broad or protected root: {target}",
            )
    return _ALLOW


def _contains_glob(target: str) -> bool:
    return any(character in target for character in "*?[")


def _is_broad_delete_target(target: str, request: HookRequest) -> bool:
    if target in {"/", ".", "..", "~", "$HOME", "${HOME}"}:
        return True
    if "$" in target or "`" in target:
        return True
    candidate = Path(target)
    if not candidate.is_absolute():
        candidate = request.cwd / candidate
    normalized = candidate.resolve(strict=False)
    project_root = request.project_root.resolve(strict=False)
    return normalized == project_root or normalized == project_root.parent


def _evaluate_patch(request: HookRequest) -> HookDecision:
    paths = [match.group("path").strip() for match in _PATCH_FILE_RE.finditer(request.command)]
    if not paths and request.command.strip():
        return HookDecision(
            False,
            "patch.malformed",
            reason="Refusing an apply_patch request whose target paths cannot be classified.",
        )
    for raw_path in paths:
        if _is_protected_project_path(raw_path, request.project_root):
            return HookDecision(
                False,
                "path.protected-write",
                f"The patch targets a protected project path: {raw_path}",
            )
    return _ALLOW


def _evaluate_file_write(request: HookRequest) -> HookDecision:
    if not request.file_path:
        return HookDecision(
            False,
            "write.malformed",
            "Refusing a file-write request whose target path is missing.",
        )
    if _is_protected_project_path(request.file_path, request.project_root):
        return HookDecision(
            False,
            "path.protected-write",
            f"The write targets a protected project path: {request.file_path}",
        )
    return _ALLOW


def _is_protected_project_path(raw_path: str, project_root: Path) -> bool:
    candidate = Path(raw_path)
    if not candidate.is_absolute():
        candidate = project_root / candidate
    normalized = candidate.resolve(strict=False)
    root = project_root.resolve(strict=False)
    try:
        relative = normalized.relative_to(root)
    except ValueError:
        return False

    parts = relative.parts
    if not parts:
        return False
    filename = parts[-1]
    if filename == ".env" or filename.startswith(".env."):
        return True
    if parts[0] in {".git", "secrets"}:
        return True
    if parts == ("config", "credentials.json"):
        return True
    return parts[:2] in {(".claude", "hooks"), (".codex", "hooks")}
