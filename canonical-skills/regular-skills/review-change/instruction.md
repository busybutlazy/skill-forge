# Review Change

Try to disprove the completion claim. The only permitted write is the owned review report; never repair or approve the implementation.

## Use This For

- A change has implementation, verification, and change-report evidence ready for adversarial review.

## Do Not Use This For

- Implementing fixes, authoring the plan under review, running a self-approval gate, merging, releasing, or replacing human review.

## Required Inputs

- Change ID, request/acceptance criteria, approved plan and approval evidence.
- Full attributable diff, tests, task handoffs, verification report, change report, and relevant CI/contract history.

If core artifacts are missing, report the evidence gap as a finding. If the reviewer shares the implementation session/context, disclose reduced independence and recommend a separate reviewer or human.

## Workflow

1. Establish scope, comparison base, review independence, and claimed outcome.
2. Trace every acceptance criterion through implementation and tests; challenge unsupported or mock-only claims.
3. Inspect normal and failure paths for correctness, error handling, authorization/security, data consistency, backward compatibility, and hidden contract/dependency/migration effects.
4. Look for out-of-scope edits, over-abstraction, missing rollback, skipped tests, misleading reports, and untracked/generated artifacts.
5. Classify findings as Blocking, High, Medium, Low, or Suggestion. Give evidence, impact, and a bounded remediation direction; do not edit code.
6. Write `changes/<change-id>/REVIEW_REPORT.md` using [the checklist/template](./references/REVIEW_REPORT_TEMPLATE.md).
7. Stop for human disposition. Do not approve, implement findings, merge, release, or silently call another workflow.

## Stop Conditions and Boundaries

Use read-only inspection and existing containerized checks only when necessary to challenge evidence. Never install dependencies or run project commands directly on the host. Stop before destructive commands, production/secret access, migrations, implementation edits, or scope decisions. Unexplained worktree state and missing container entrypoints must be recorded, not bypassed.

## Evidence Standard

Distinguish verified defects, evidence gaps, and suggestions. Cite paths, symbols, commands, outputs, and report contradictions. Absence of findings is not proof of correctness; state unreviewed areas and residual risk.
