# Change Request: supervised-auto-workflow

## Goal

Support an explicit human-approved supervised-auto path for low- and medium-risk changes without weakening the existing one-task-at-a-time workflow.

## In Scope

- Add a public `run-approved-change` orchestration skill.
- Add an Execution Policy to `plan-change` output.
- Define risk/mode gates, task logging, stop conditions, verification, reporting, and independent-review handoff.
- Update managed memory, guideline, catalog, tests, and both-target render/install behavior.

## Out of Scope

- Parsing approval semantics in hooks.
- A machine-enforced workflow state engine or approval CLI.
- Automatic independent review, commit, push, merge, release, production access, or secret access.
- Weakening `implement-task` one-task-at-a-time behavior.

## Acceptance Criteria

- `implement-task` remains strict and unchanged.
- `run-approved-change` accepts only explicitly approved low/medium plans whose mode is `supervised-auto`.
- High/extreme risk, plan deviation, verification failure, and unsafe operations stop for human direction.
- Successful execution records per-task evidence, produces verification/change reports, and stops before independent review.
- Plan, memory, and guideline describe the same execution-mode contract.
- The skill renders and installs idempotently for Codex and Claude with its reference intact.
- Full Docker tests pass.
