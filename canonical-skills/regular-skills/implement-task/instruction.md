# Implement One Task

Execute exactly one named task from an explicitly approved implementation plan, then stop.

## Use This For

- A human has approved `changes/<change-id>/IMPLEMENTATION_PLAN.md` and named one task to execute.

## Do Not Use This For

- Unapproved plans, vague requests such as “finish the phase,” planning, whole-change verification/reporting/review, or automatic execution of later tasks.

## Required Inputs

- Change ID and approved plan path.
- Exact task identifier and approval evidence.
- Repository rules, task acceptance criteria, allowed files/symbols, and existing canonical container command.

If approval or task identity is ambiguous, stop. Never infer approval from a plan's existence.

## Workflow

1. Read the approved plan and restate the task boundary, prohibited areas, expected result, and local verification.
2. Check Git state and stop on unexplained overlapping edits or baseline failures that prevent attribution.
3. Modify only the minimum files/symbols needed by the named task. Preserve unrelated user work.
4. Add or update tests directly required by this task.
5. Run only task-local checks through existing Docker/Compose/Make/container wrappers. Never install dependencies or run project commands directly on the host.
6. Compare the result with the approved task. Record changed files, commands, exit codes, tests, omissions, and deviations using [the handoff checklist](./references/TASK_HANDOFF_CHECKLIST.md).
7. Stop. Hand the bounded result back for the next human decision; do not begin another task or claim the entire change complete.

## Prohibited Actions and Stop Conditions

Do not rewrite requirements, expand scope, modify an approved public contract, add/update production dependencies, run migrations, access production/secrets, discard worktree changes, or approve deviations. Stop if any is required; also stop for data-loss risk, missing container entrypoints, incompatible environment, unexplained edits, or a task that cannot be completed independently. Missing Docker support belongs to the `bootstrap-project` workflow, not a host fallback.

## Evidence and Handoff

Report facts, not “tests passed” without commands and results. Label unrun tests and reasons. A local task check is not full change verification, independent review, or human acceptance.
