# Phase B B5 Verification Report

## Scope

Integrated the managed `agent-hooks` bundle into the existing guideline CLI and TUI flows for Codex and Claude. Documentation beyond implementation-plan and verification records remains B6 scope.

## Requirement traceability

| Requirement | Implementation | Test | Result |
|---|---|---|---|
| List hooks beside managed guideline files | `load_guideline_items` | CLI JSON/plain and status-menu tests | Pass |
| Filter status/install to `agent-hooks` | `load_guideline_item` | filtered CLI install/status test | Pass |
| Preserve legacy memory command behavior | existing memory path remains separate | guideline/memory compatibility tests | Pass |
| Report bundle artifact state | `GuidelineItemStatus.artifacts` | JSON artifact assertion | Pass |
| Continue unrelated items after hook failure | item-level CLI error handling | invalid Codex hooks JSON test | Pass |
| Reuse drift confirmation and unmanaged refusal | `install_guideline_item` delegates to target adapters | adapter plus CLI flow tests | Pass |
| Select hooks by TUI index | `_guideline_menu` unified items | index-to-hooks menu test | Pass |
| Show inactive/broken target state | unified status facade | Codex adapter aggregate tests | Pass |

## Commands executed

```text
PYTHONPATH=src python -m unittest tests.test_skill_forge.GuidelineCliTests tests.test_skill_forge.MenuOnboardingTests -v
Exit 0 — 16 focused tests passed

docker run --rm -e PYTHONPATH=src -v /home/jett/skill-forge:/workspace -w /workspace skill-forge-dev python -m unittest discover -s tests -q
Exit 0 — 104 tests passed

Fresh `guideline install` and JSON status smoke tests into temporary Codex and Claude Git projects
Exit 0 — agent-memory, agent-guideline, and agent-hooks all reported up_to_date

python -m compileall -q src tests
Exit 0

git diff --check
Exit 0
```

## Output compatibility

- `memory` retains its legacy single-object JSON output.
- Guideline JSON remains an array and now adds `agent-hooks` with artifact details.
- Plain guideline status remains one line per item; artifact detail is available through JSON and the TUI.
- The existing config item order is unchanged; `agent-hooks` is appended as the third item.

## Tests not run

- Windows CLI/TUI install: Windows runtime support remains pending.
- Git pre-commit fallback and uninstall: deferred decisions.
- Final documentation and full Phase B end-to-end matrix: B6 scope.

## Known limitations and review hotspots

- The facade deliberately delegates installation and safety classification; it does not merge the single-file and bundle lifecycle implementations.
- Codex trust state cannot be proven from project files, so JSON/TUI status includes an advisory detail even when artifacts are current.
- A malformed canonical bundle is a repository-maintainer error and still prevents guideline registry loading.

## Rollback

- Remove `agent-hooks` from the guideline facade while leaving the target adapters and canonical bundle intact.
- Existing `agent-memory`, `agent-guideline`, and legacy `memory` paths are independent and remain usable.
