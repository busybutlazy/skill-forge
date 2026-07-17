# Phase B Change Report: Managed safety hooks

## Completed

- Added deterministic classification for destructive Git operations, broad recursive deletion, malformed matched requests, and protected project-path writes.
- Added a marker-managed standalone Python safety runner requiring Python 3.11 or newer with no upper cap.
- Added transactional multi-file bundle status/install with unmanaged refusal, drift confirmation, atomic writes, and rollback.
- Added additive Claude `.claude/settings.json` and Codex `.codex/hooks.json` adapters that preserve unrelated user content.
- Removed the obsolete project-local `allowManagedHooksOnly` default and added an exact-key migration that preserves all other settings.
- Added runtime, inactive, broken, and Codex trust-review status reporting.
- Exposed `agent-hooks` through guideline CLI/TUI status and install flows.
- Updated English and Traditional Chinese documentation and bumped `agent-guideline` from 0.1.0 to 0.2.0.

## External observable behavior

- `guideline status/install` now includes `agent-hooks` by default; `--item agent-hooks` filters to it.
- Installing all guideline items creates the instruction file, governance document, runner, and target-native hook configuration.
- Guideline JSON contains bundle artifact details; plain output remains one line per item.
- Codex current status includes a trust-review advisory and reports explicit project hook disablement as `inactive`.
- Claude project-local security initialization no longer writes ineffective `allowManagedHooksOnly`.

## Files and components

- New canonical source: `canonical-configs/agent-hooks/`.
- New implementation modules: `hook_policy.py`, `managed_bundles.py`, `claude_hooks.py`, `codex_hooks.py`, and `guideline.py`.
- Updated integration: `cli.py`, `menu.py`, and `security_check.py`.
- Added/updated automated tests for policy, lifecycle, adapters, bundle runner, CLI, TUI, migration, and rollback.
- Added Phase B capability, implementation, verification, change, and review records.

No files were deleted. No production dependency, database migration, public API contract, network access, secret access, or production operation was added.

## Plan deviations and remaining work

- Git pre-commit fallback was listed in the initial scope but deferred after native Codex hooks were verified. Environments with native hooks disabled/untrusted do not receive fallback enforcement.
- Automatic uninstall remained an approval gate and was not implemented. Manual recovery is documented.
- Windows command invocation and `py -3` behavior were not verified or enabled.
- Production-specific operations and migration-history policy were deliberately not generalized; safe definitions require project-specific approval.

## Breaking changes

- No intended breaking CLI change. The legacy `memory` command and its JSON shape remain unchanged.
- `guideline` all-item output now includes a third item, which is an additive machine-output change consumers should tolerate.
- Existing installed `agent-guideline` 0.1.0 files will report `update_available` because the canonical content is now 0.2.0.

## Rollback

1. Remove only skill-forge-owned matcher handlers referencing the namespaced runner.
2. Remove the marker-managed `.claude/hooks/skill-forge/safety_check.py` or `.codex/hooks/skill-forge/safety_check.py`.
3. Preserve unrelated settings and handlers.
4. Revert Phase B commits in reverse order if repository-level rollback is required.

## Most uncertain

The largest residual uncertainty is cross-platform and external state: Windows command hooks were not tested, and project files cannot prove Codex trust or higher-precedence feature overrides.
