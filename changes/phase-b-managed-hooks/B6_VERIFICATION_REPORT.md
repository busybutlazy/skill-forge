# Phase B B6 Verification Report

## Result

The delivered Linux/macOS native-hook path is verified for Claude and Codex. No Blocking or High review finding remains. Git fallback, automatic uninstall, and Windows support were not delivered and are explicitly documented.

## Requirement traceability

| Requirement | Implementation | Evidence | Result |
|---|---|---|---|
| Deterministic policy with stable denial reasons | internal policy + standalone runner | table-driven policy and payload fixtures | Pass |
| Managed multi-file lifecycle | `managed_bundles.py` | clean/repeat/drift/unmanaged/rollback tests | Pass |
| Additive Claude native hooks | `claude_hooks.py` | preservation, drift, rollback, live Bash/Edit/Write E2E | Pass |
| Additive Codex native hooks | `codex_hooks.py` | preservation, inactive/trust status, live Bash/apply_patch E2E | Pass |
| Guideline CLI/TUI exposure | `guideline.py`, CLI, menu | filtered/all-item and menu-index tests | Pass |
| Failure isolation | guideline install loop | invalid/OSError per-item continuation tests | Pass |
| Python 3.11+ without upper cap | runtime preflight | version table and target smoke tests | Pass |
| English and Traditional Chinese documentation | README, terminal guide, reference, canonical guideline | final diff review | Pass |
| Git pre-commit fallback | not implemented | review finding M1 | Deferred |
| Automatic uninstall | not implemented | review finding M2 | Deferred |
| Windows runtime/command hooks | not implemented | review finding L1 | Deferred |

## Commands executed

```text
PYTHONPATH=src python -m unittest tests.test_hook_policy tests.test_managed_bundles tests.test_security_check tests.test_claude_hooks tests.test_codex_hooks tests.test_agent_hooks_bundle tests.test_skill_forge.GuidelineConfigTests tests.test_skill_forge.GuidelineCliTests tests.test_skill_forge.MenuOnboardingTests -q
Exit 0 — 68 focused tests passed in 10.464s

docker run --rm -e PYTHONPATH=src -v /home/jett/skill-forge:/workspace -w /workspace skill-forge-dev python -m unittest discover -s tests -q
Exit 0 — 106 tests passed after the post-review patch

Fresh and repeated `guideline install` into temporary Codex and Claude Git projects
Exit 0 — both installs were idempotent

`guideline status` for both smoke projects
Exit 0 — post-review fresh Codex and Claude projects report agent-memory 0.4.0, agent-guideline 0.2.0, and agent-hooks 0.2.0 all up_to_date

git diff --check 117e868
Exit 0
```

## Live target evidence retained from this branch

- Claude Code 2.1.212 invoked the installed canonical runner for Bash, Edit, and Write. Protected `.env` writes were denied before mutation.
- Codex 0.144.5 invoked the installed canonical runner and denied `git reset --hard HEAD` with `git.reset-hard` before execution.
- Codex starting below the Git root resolved the same runner; disabled and untrusted hook behavior was separately verified in B0.

The live tests were not repeated during B6 because the installed runner and adapters did not change after B3/B4, and repeating Claude would consume account quota without adding contract coverage.

## Matrix summary

| Scenario | Claude | Codex |
|---|---|---|
| Fresh install | Pass | Pass |
| Repeated install | Pass | Pass |
| Managed drift requires force + confirmation | Pass | Pass |
| Unmanaged/invalid config refused | Pass | Pass |
| Unrelated hook/settings preserved | Pass | Pass |
| Settings failure rolls bundle back | Pass | Pass |
| Dangerous Bash denied | Pass | Pass |
| Protected file mutation denied | Pass (`Edit`/`Write`) | Pass (`apply_patch`) |
| Allowed fixture passes | Pass | Pass |
| Missing runtime reported non-current | Pass | Pass |
| Explicit hooks disable reported inactive | N/A | Pass |
| Windows | Not run | Not run |

## Environment

- Host: Linux, Asia/Taipei
- Date: 2026-07-17
- Hook runtime: `python3` >=3.11
- Full suite: `skill-forge-dev` image with repository mounted at `/workspace`

## Remaining risks

- Native hooks can be disabled, skipped before trust, or bypassed by higher-precedence configuration outside project-only status visibility.
- The deterministic parser intentionally covers a narrow rule set, not arbitrary shell semantics.
- No read-time secret protection is provided by this bundle.
- See `REVIEW_REPORT.md` for deferred scope and duplication risk.

## Post-review patch verification

```text
PYTHONPATH=src python -m unittest tests.test_hook_policy tests.test_agent_hooks_bundle -v
Exit 0 — 21 tests passed
```

The shared parity fixture verifies that both internal policy and the standalone installed runner deny `rm -rf *`, `./*`, `build/*.tmp`, and `$DIR/*` with `shell.unresolved-recursive-delete`, while allowing explicit `rm -rf build/cache`.
