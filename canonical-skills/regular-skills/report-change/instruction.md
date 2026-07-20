# Report Change

Describe what the change actually did, did not do, and did not prove. The only permitted write is the owned report.

## Use This For

- Implementation and verification evidence exist and need comparison with the request and approved plan.

## Do Not Use This For

- Planning, implementation, verification execution, code fixes, independent review, approval, release, or speculative release notes.

## Required Inputs

- Change ID, request, approved plan and approval evidence.
- Current Git status/diff and task handoffs.
- Verification report and available CI evidence.

If the plan, diff, or verification evidence is unavailable, mark the report incomplete and stop rather than inventing facts.

## Workflow

1. Establish the comparison base and inspect the full attributable diff, including tracked, staged, and relevant untracked files.
2. Compare each planned task and acceptance criterion with observed implementation and verification evidence.
3. Identify files added/modified/deleted; observable behavior; contract/schema, migration, dependency, configuration, and documentation effects.
4. Disclose completed, not completed, not verified, planned deviations, unplanned changes, breaking changes, remaining work, limitations, risks, uncertainty, and rollback.
5. Write `changes/<change-id>/CHANGE_REPORT.md` using [the template](./references/CHANGE_REPORT_TEMPLATE.md).
6. Stop and hand the report to an independent reviewer/human. Do not modify implementation or invoke review automatically.

## Stop Conditions and Boundaries

Do not run project commands, install dependencies, edit production code/tests/specifications, approve deviations, or hide unrelated work. Stop for an ambiguous diff base, unexplained worktree edits, missing approval evidence, or a material scope/contract discrepancy that requires a human decision. Docker-only container constraints still apply if any repository command is needed, with no host fallback; normally this workflow only performs read-only Git inspection.

## Evidence Standard

Tie statements to diff paths, commits, task handoffs, verification rows, or CI evidence. Clearly label inference. A report does not prove correctness and cannot replace verification, review, or human acceptance.
