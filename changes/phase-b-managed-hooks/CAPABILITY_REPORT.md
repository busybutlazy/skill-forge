# Phase B B0 Capability Report

## Status

Claude and Codex Linux runtime contracts are verified. Windows portability remains open. No production code was modified by B0.

## Environment

| Target | Result |
|---|---|
| Claude Code | CLI present, version `2.1.212` |
| Codex | Official CLI `0.144.5` installed under `/tmp` for this spike |
| Codex manual | Fresh official manual fetched on `2026-07-17` |

## Confirmed contracts

### Claude Code

- Project hooks may be configured in `.claude/settings.json` (shared) or `.claude/settings.local.json` (personal).
- `PreToolUse` command hooks receive JSON on stdin and can deny a tool call through `hookSpecificOutput.permissionDecision = "deny"`.
- `Bash`, `Edit`, and `Write` are supported matcher targets.
- `${CLAUDE_PROJECT_DIR}` is available for stable project-relative script paths.
- `allowManagedHooksOnly` is valid only in organization-managed settings; emitting it into project-local settings is obsolete and ineffective.

### Codex

- Hooks are stable and enabled by default.
- Trusted projects may load `.codex/hooks.json` or inline hooks from `.codex/config.toml`; untrusted projects skip project-local hooks.
- Prefer `.codex/hooks.json` for Phase B to avoid TOML mutation.
- Matching hooks from multiple sources all run; a project hook does not replace user or system hooks.
- Non-managed hooks require review and trust. Trust is tied to the exact hook definition hash, so an update requires review again.
- Current command hooks support `PreToolUse` and match `Bash`, `apply_patch`, plus `Edit|Write` aliases for patch operations.
- Hooks receive JSON on stdin, run with the session cwd, and support `commandWindows`.
- Project hook commands should resolve scripts from the Git root because Codex may start in a subdirectory.
- Hooks can be disabled by `[features] hooks = false`; status must not claim active enforcement in that case.

## Attempted runtime tests

### Claude

A temporary Git project with a `.claude/settings.json` `PreToolUse` hook was created under `/tmp`. The hook would capture stdin and deny a sentinel Bash command before it writes a sentinel file.

Result:

- Claude authentication is present.
- The first account attempt stopped before tool execution with an HTTP 429 session limit.
- A later run with an available account loaded `.claude/settings.json`, invoked the `PreToolUse` hook, and captured stdin.
- Returning `hookSpecificOutput.permissionDecision = "deny"` blocked the Bash command before execution; the sentinel file was not created.
- The captured payload contained `cwd`, `effort`, `hook_event_name`, `permission_mode`, `prompt_id`, `session_id`, `tool_input`, `tool_name`, `tool_use_id`, and `transcript_path`.
- `tool_input.command` contained the shell command and `tool_input.description` contained the model-provided description.

### Codex

The official `@openai/codex` package was installed under `/tmp` without changing the system installation. Runtime tests used a temporary trusted Git project and an ephemeral session.

Verified results:

- `.codex/hooks.json` loaded and received `PreToolUse` events.
- A Bash hook returned `permissionDecision: deny`; Codex blocked the command before execution and the sentinel file remained absent.
- Starting Codex from a nested repository directory still loaded the project hook when its command resolved the script with `git rev-parse --show-toplevel`.
- `--disable hooks` skipped the hook and allowed the sentinel command, confirming that installed files alone do not prove active enforcement.
- Without `--dangerously-bypass-hook-trust`, the unreviewed hook was skipped and the command ran. Non-interactive JSON output did not include a clear hook-review warning, so status/install output must tell users to review hooks explicitly.
- Matcher `Edit|Write` triggered for Codex `apply_patch`.
- The captured `apply_patch` request used `tool_name: "apply_patch"` and placed the complete patch text in `tool_input.command` (not `tool_input.patch`). After adapting to that actual payload, the hook denied the edit before the target file was created.

Captured Bash and `apply_patch` fixtures include `cwd`, `hook_event_name`, `model`, `permission_mode`, `session_id`, `tool_input`, `tool_name`, `tool_use_id`, `transcript_path`, and `turn_id`.

## Remaining B0 tests

1. Test Codex `commandWindows` on Windows, or explicitly narrow the supported platform scope.
2. Test the selected shared runtime on Windows or explicitly narrow the supported platform scope.

## Preliminary design decisions

- Use `.claude/settings.json` for shared Claude hooks.
- Use `.codex/hooks.json` for shared Codex hooks.
- Keep Git pre-commit as defense in depth or fallback, not the primary Codex adapter.
- Share one deterministic policy implementation across adapters where runtime portability permits.
- Do not start B1 until the runtime choice and remaining approval gates are resolved.

## Evidence classification

- **Verified locally:** installed versions, Claude Bash/`Edit`/`Write` and Codex Bash/`apply_patch` payloads, denial behavior, Codex disabled/untrusted behavior, nested-directory path resolution, sentinel file results.
- **Verified from current official documentation/manual:** config locations, event names, trust model, matcher coverage, input channel, feature disable behavior.
- **Not yet verified locally:** Windows invocation and interactive Codex `/hooks` trust UX.

### Claude Edit and Write fixtures

- `Write` uses `tool_input.file_path` and `tool_input.content`.
- `Edit` uses `tool_input.file_path`, `old_string`, `new_string`, and `replace_all`.
- A live deny test prevented `Write` from creating a new file and prevented `Edit` from changing an existing file.
- A second live E2E installed the canonical `agent-hooks` bundle plus generated `.claude/settings.json`; the installed policy denied a `Write` to `.env` and left the file absent.

### B4 native Codex adapter verification

- The production adapter installs the canonical runner plus additive `.codex/hooks.json` matcher groups.
- Codex 0.144.5 loaded the installed configuration and denied `git reset --hard HEAD` before execution with rule `git.reset-hard`.
- Project `.codex/config.toml` with `[features] hooks = false` is reported as inactive rather than up to date.
- Hook trust cannot be inferred safely from repository files, so installed status retains an explicit trust-review signal.
