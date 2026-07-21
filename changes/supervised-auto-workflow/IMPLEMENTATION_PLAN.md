# Implementation Plan: supervised-auto-workflow

## Objective

Add an explicit supervised-auto workflow between human plan approval and independent review while retaining strict task execution for high-risk or narrowly bounded work.

## In Scope

- `plan-change` Execution Policy contract and template.
- New public `run-approved-change` package.
- Managed memory/guideline/catalog consistency.
- Focused contract, render/install, and regression verification.

## Out of Scope

- Stateful approval enforcement in hooks or a new workflow CLI.
- Automatic review, acceptance, commit, push, merge, or release.

## Current-State Evidence

- `implement-task` requires exactly one task and a stopping handoff.
- Installed agents may nevertheless infer and execute later workflow stages from broad user prompts.
- Existing hooks enforce deterministic safety boundaries, not semantic plan approval.

## Acceptance Criteria

See `REQUEST.md`.

## Tasks

### Task 1 — Define planning and execution contracts

- Add risk, automation mode, task/path scope, checkpoints, and approval evidence to the plan template.
- Define the supervised-auto trigger, refusal cases, workflow, task log, verification boundary, and final handoff.

### Task 2 — Integrate canonical governance sources

- Update memory, guideline, and catalog without changing hook behavior or recommended installs.

### Task 3 — Finalize and verify

- Refresh/validate canonical package metadata.
- Add focused tests, both-target repeated-install smoke, and full Docker regression.

## Verification Strategy

- Structural contracts for risk/mode gates, stopping behavior, companion artifacts, and catalog order.
- Canonical validation for new/updated skills.
- Fresh and repeated Codex/Claude installs preserving references and reporting `up_to_date`.
- Full `unittest` discovery in `skill-forge-dev`.

## Risks and Rollback

- Risk: Agent treats supervised-auto as universal permission. Mitigation: explicit low/medium gate, approved task list, and refusal conditions.
- Risk: Verification silently becomes implementation. Mitigation: evidence-only verification phase; failure stops.
- Rollback: remove the new package/tests/catalog entry and revert plan/memory/guideline versions and wording.

## Human Decisions and Approval

- Plan revision: 1
- Risk level: medium
- Automation mode: supervised-auto
- Approval evidence: user explicitly requested canonical implementation after approving this design in the active session on 2026-07-21.
