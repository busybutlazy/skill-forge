# Phase B Review Report: Managed safety hooks

## Review conclusion

No Blocking or High correctness/security finding was identified in the delivered Linux/macOS native-hook path. The automated and live evidence supports the completion claims for that path. Phase B should be accepted only with the following deferred-scope items acknowledged.

## Post-review resolution (2026-07-17)

- External finding: `rm -rf *` and equivalent unresolved globs could bypass broad-root classification. **Resolved** by denying recursive forced deletion targets containing `*`, `?`, or `[`, adding regression cases, and running shared internal/runner parity fixtures. Canonical `agent-hooks` was bumped to 0.2.0.
- External finding: five B0 approval gates were not durably recorded outside chat. **Resolved procedurally** by `DECISION_RECORD.md`, which records the approved runtime, native Codex path, blocked rules, obsolete-setting migration, uninstall deferral, and consequences.
- The original Medium M1/M2 below remain accepted deferred scope, not undisclosed completion claims.

## Findings

### Medium M1 — Git fallback in the initial scope is not delivered

The verified native Codex adapter is the primary path, but an untrusted hook or `[features] hooks = false` leaves no pre-commit fallback. Status reports the project-level disablement and warns about trust, so this is disclosed rather than silent.

Recommendation: accept native-only Phase B explicitly or schedule a separate fallback change with its own ownership and coexistence design.

### Medium M2 — Automatic uninstall remains unresolved

Install/update ownership is precise, but there is no CLI/TUI removal operation for `agent-hooks`. Manual rollback is documented and can preserve unrelated handlers, but it is easier to perform incorrectly than a tested command.

Recommendation: decide whether uninstall belongs in a follow-up Phase B patch or backlog; do not reuse skill removal without structural JSON ownership tests.

### Low L1 — Windows support is intentionally unavailable

Runtime discovery recognizes `py -3`, but target installation refuses it because `commandWindows` and launcher behavior were not tested. Documentation states Linux/macOS support and the Windows limitation.

### Low L2 — Policy logic exists in two implementations

The repository policy module and standalone canonical runner duplicate deterministic rules so installed target projects do not depend on the `skill_forge` package. Overlapping fixtures reduce drift risk but cannot mechanically guarantee equivalence.

Resolution: a shared decision-fixture test now executes both implementations and requires identical rule IDs. Keep this parity test mandatory for every rule change; consider generation from shared rule data only if it preserves the dependency-free runner.

### Suggestion S1 — Project-only status cannot prove active Codex enforcement

Trust is external and command-line or higher-precedence configuration may disable hooks. The current advisory is honest. Documentation should continue avoiding claims that `up_to_date` proves execution.

## Review checks

- Scope and report claims compared against diff from `117e868`.
- Additive merge ownership inspected for Claude and Codex, including same-group user handlers.
- Atomic write and rollback tests inspected.
- Policy and standalone runner path lists compared.
- README/reference claims compared with implemented rule IDs and status behavior.
- Deferred items searched across implementation and reports for disclosure consistency.

## Human review hotspots

1. Accept or reject M1/M2 as deferred work.
2. Review the exact initial blocked rule set for project suitability.
3. Confirm Python 3.11+ Linux/macOS prerequisite is acceptable.
4. Confirm additive `guideline` JSON output is acceptable to downstream consumers.
