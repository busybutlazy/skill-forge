# Phase B B3 Verification Report

## Scope

Implemented the Claude adapter, canonical `agent-hooks` bundle, Python runtime preflight, obsolete local-setting migration, and real Claude `PreToolUse` enforcement. CLI/TUI guideline registration remains B5 scope.

## Requirement traceability

| Requirement | Implementation | Test | Result |
|---|---|---|---|
| Accept Python 3.11 and newer without an upper bound | `find_python_runtime` | runtime version table | Pass |
| Stop emitting obsolete local managed-hook policy | `security_check.py` | new-default test | Pass |
| Remove obsolete key while preserving other local settings | `remove_obsolete_security_settings` | migration, invalid JSON, atomic failure, smoke tests | Pass |
| Preserve unrelated Claude settings and hooks | `claude_hooks.py` | additive merge and same-group ownership tests | Pass |
| Refuse invalid/symlink settings and confirm drift | `claude_hooks.py` | unmanaged and drift tests | Pass |
| Install bundle and settings transactionally | `install_claude_hooks` + B2 callback | settings failure rollback test | Pass |
| Protect Bash, Edit, and Write through native Claude hooks | canonical runner + settings matchers | fixture tests and live E2E | Pass |
| Report inactive/missing runtime as non-current | `claude_hooks_status` | aggregate status tests | Pass |

## Commands executed

```text
PYTHONPATH=src python -m unittest tests.test_hook_policy tests.test_managed_bundles tests.test_security_check tests.test_claude_hooks tests.test_agent_hooks_bundle -v
Exit 0 — 38 focused tests passed

docker run --rm -e PYTHONPATH=src -v /home/jett/skill-forge:/workspace -w /workspace skill-forge-dev python -m unittest discover -s tests
Exit 0 — 92 tests passed in 62.688s

Fresh Codex and Claude existing-install smoke tests
Exit 0 — both targets installed; existing guideline items reported up_to_date

Claude Code 2.1.212 live Write E2E against installed B3 bundle
Success — path.protected-write denied `.env`; target file remained absent

git diff --check
Exit 0
```

## Runtime fixtures

- Claude Bash: command in `tool_input.command`.
- Claude Write: path/content in `tool_input.file_path` and `tool_input.content`.
- Claude Edit: path/replacement data in `file_path`, `old_string`, `new_string`, and `replace_all`.
- Canonical runner exits successfully with no output for allow, or emits Claude-compatible `permissionDecision: deny` JSON for block.

## Safety properties

- Runtime preflight happens before any hook file or setting is written.
- B3 currently requires a `python3` command resolving to Python >=3.11; upper versions are accepted.
- `.claude/settings.json` updates are atomic and preserve mode.
- Only handlers referencing the namespaced skill-forge script path are owned and replaced.
- Bundle installation rolls back if the settings update fails.
- Invalid JSON and symlink settings are never overwritten, including with force.
- Obsolete `allowManagedHooksOnly` removal is limited to that exact top-level local key.

## Tests not run

- Windows Python launcher and Claude command-hook behavior: no Windows environment is available.
- Codex adapter using the canonical runner: B4 scope.
- CLI/TUI status/install path: B5 scope.
- Uninstall: pending the plan approval decision.

## Known limitations and review hotspots

- The canonical standalone runner and internal policy module intentionally duplicate deterministic logic so target projects do not need the `skill_forge` package. Their shared behavior is pinned by overlapping table/E2E tests; future policy changes must update both.
- Linux/macOS `python3` support is active. Windows remains explicitly unsupported until its launcher contract is tested.
- This policy is defense in depth, not a complete shell parser, sandbox, CI gate, or replacement for human approval.
- Status can prove configuration/runtime presence but cannot prove a user has not disabled hooks after the check.

## Rollback

- Remove only the skill-forge-owned matcher groups from `.claude/settings.json`.
- Remove the marker-managed `.claude/hooks/skill-forge/safety_check.py` artifact.
- Preserve all unrelated settings and hook handlers.
