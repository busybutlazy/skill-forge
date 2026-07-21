# Run Approved Change

Execute all explicitly auto-approved tasks in a low- or medium-risk plan, verify the completed change, produce evidence reports, and stop before independent review.

## Use This For

- A human approved the current `changes/<change-id>/IMPLEMENTATION_PLAN.md` revision with `Automation mode: supervised-auto`.
- The approved risk level is low or medium and the plan names the exact auto-approved tasks and path scope.

## Do Not Use This For

- Draft, superseded, ambiguous, or changed plans; inferred approval; or `one-task-at-a-time` mode.
- High/extreme risk, production/secret access, irreversible migration, bulk data mutation, authentication/authorization, payment, deployment, infrastructure privilege, or other required human checkpoints.
- One bounded task or review-finding repair; use `implement-task` instead.
- Independent review, human acceptance, commit, push, merge, release, or deployment.

## Required Inputs and Admission Gate

- Change ID, request/acceptance criteria, repository rules, current approved plan revision, and attributable Git state.
- Approval evidence that explicitly names `supervised-auto`, the low/medium risk level, auto-approved task IDs, path scope, and required checkpoints.
- Existing Docker/Compose/Make/container entrypoints for task-local and full verification.

Never install dependencies or run project commands directly on the host; all task and verification commands use the approved container entrypoint.

Before writing implementation, verify every admission condition with [the checklist](./references/AUTO_EXECUTION_CHECKLIST.md). A plan's existence, a broad “continue,” or approval of an earlier revision is insufficient. If any condition is missing, stop; never rewrite the plan or approve it.

## Supervised-Auto Workflow

1. Read the request, approved plan, sources of truth, acceptance criteria, task list, execution policy, rollback, and approval evidence.
2. Inspect Git state. Preserve unrelated work and stop on unexplained or overlapping edits. Never operate from `main`/`master` when work requires commits; commit remains separately prohibited.
3. Create or append `changes/<change-id>/TASK_LOG.md`. Record the admitted plan revision, mode, risk, approved tasks/paths, baseline, and each task's evidence.
4. Execute auto-approved tasks strictly in plan order. For each task:
   - restate its boundary and allowed paths;
   - make the minimum approved implementation and tests;
   - run task-local checks only through the approved container entrypoint;
   - record files, commands, exit codes, results, omissions, and deviations in the task log;
   - continue only when the task meets its approved acceptance criteria with no stop condition.
5. Ordinary implementation mistakes may be corrected within the same task boundary. Stop if correction needs a new task, path, dependency, contract decision, scope expansion, or human checkpoint.
6. After all tasks pass locally, enter an evidence-only verification phase: do not edit implementation; trace requirements and run all applicable canonical container checks.
7. Write `changes/<change-id>/VERIFICATION_REPORT.md` with requirement-to-implementation-to-test results, exact commands/exit codes/counts, environment, mocks, skipped checks, risks, and unsupported claims.
8. If full verification fails or is incomplete, record the result and stop. Do not switch back into implementation or silently create a remediation task.
9. If verification passes, inspect the attributable diff against the request and plan, then write `changes/<change-id>/CHANGE_REPORT.md` covering completed/not completed/not verified work, files, observable behavior, contract/dependency/migration impact, deviations, limitations, risks, remaining work, and rollback.
10. Stop and hand all artifacts to a separate `review-change` session or human. Do not review or approve your own completion claim.

## Mandatory Stop Conditions

Stop immediately for a changed/unapproved plan revision; high/extreme risk; an unlisted task or path; scope, requirement, contract, schema, dependency, migration, architecture, security, or data-operation deviation; missing Docker entrypoint; destructive/production/secret access; unexplained Git changes; an unmet human checkpoint; task-local failure that cannot be corrected within its boundary; or any incomplete/failed full verification.

On stop, preserve evidence, mark the current task/result accurately, explain the smallest human decision needed, and do not continue to later tasks.

## Review Handoff and Authority Boundaries

Supervised-auto authorizes execution only between an explicitly approved plan and mandatory verification. It does not authorize replanning, acceptance, review, commit, push, merge, release, deployment, or bypassing hooks/CI/sandbox controls. Absence of a failure is not approval.
