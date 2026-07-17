# Phase B B4 Verification Report

## Scope

Implemented the native Codex `.codex/hooks.json` adapter selected by the B0 capability spike. CLI/TUI registration remains B5 scope. The Git pre-commit fallback remains a later defense-in-depth option rather than the primary adapter.

## Requirement traceability

| Requirement | Implementation | Test | Result |
|---|---|---|---|
| Preserve unrelated Codex hooks and settings | `install_codex_hook_settings` | additive merge and same-group handler tests | Pass |
| Protect managed entries from drift and unmanaged files | `codex_hook_settings_status` | drift, force confirmation, invalid JSON, symlink tests | Pass |
| Resolve the runner from the Git root | canonical Codex command | installed settings assertion and live nested-root contract from B0 | Pass |
| Install bundle and settings transactionally | `install_codex_hooks` | simulated settings-write rollback | Pass |
| Report explicitly disabled hooks as inactive | `codex_feature_status` | `features.hooks = false` aggregate test | Pass |
| Surface trust-review uncertainty | `CodexHooksStatus.trust_review_required` | installed aggregate status test | Pass |
| Block dangerous operations through the native hook | installed canonical runner | Codex 0.144.5 live E2E | Pass |
| Accept Python 3.11 and newer without an upper bound | shared runtime preflight | B3 runtime table plus B4 adapter tests | Pass |

## Commands executed

```text
PYTHONPATH=src python -m unittest tests.test_codex_hooks tests.test_agent_hooks_bundle -v
Exit 0 — 14 focused tests passed

docker run --rm -e PYTHONPATH=src -v /home/jett/skill-forge:/workspace -w /workspace skill-forge-dev python -m unittest discover -s tests -q
Exit 0 — 101 tests passed in 64.102s

Codex 0.144.5 live E2E against a temporary Git project with the installed B4 bundle
Success — git.reset-hard denied `git reset --hard HEAD` before execution

git diff --check
Exit 0
```

## Safety properties

- Installation refuses invalid JSON, symlinks, and user-owned conflicting files.
- Drift requires `--force` plus confirmation and replaces only skill-forge-owned handlers.
- Unrelated handlers in the same matcher group survive repair.
- The canonical runner is resolved from `git rev-parse --show-toplevel`, so sessions launched below the repository root use the same policy.
- Missing Python makes the aggregate status broken; project-level feature disablement makes it inactive.
- Installed hooks retain a trust-review signal because Codex trust is external to the repository and tied to the exact hook definition.

## Tests not run

- Windows `commandWindows` and Python launcher behavior: no Windows environment is available.
- Git pre-commit fallback: deferred; native hooks are the approved primary adapter.
- CLI/TUI status and install flow: B5 scope.
- Uninstall: pending the Phase B plan decision.

## Known limitations and review hotspots

- `trust_review_required` means the repository cannot prove approval state; it does not assert that every invocation is currently untrusted.
- A user can disable hooks through a higher-precedence or command-line feature override that repository-only status cannot observe.
- The command uses POSIX shell substitution and is intentionally limited to the verified Linux/macOS path until Windows support is tested.
- Native hooks are defense in depth and do not replace sandbox, CI, permissions, or human approval.

## Rollback

- Remove only handlers whose command references `.codex/hooks/skill-forge/safety_check.py`.
- Remove the marker-managed runner artifact.
- Preserve all unrelated `.codex/hooks.json` content.
