# Plan Change

## Objective

Produce an approval-ready Implementation Plan without implementing the Change. The Write Set is limited to the owned plan artifact.

## Admission Criteria

- Planning a non-trivial feature, fix, migration, contract change, or refactor before implementation.
- Re-planning when approved scope or repository evidence has materially changed.

Reject admission for:

- Implementing code, changing configuration, installing dependencies, running migrations, or approving a plan.
- A trivial documentation or formatting edit whose scope and validation are already explicit.

## Required Inputs

- Change request or problem statement and a stable `<change-id>`.
- Repository instructions, specifications, contracts, ADRs, and acceptance criteria.
- Git status/diff, relevant code and tests, canonical container commands, and known baseline failures.

If the request, acceptance criteria, or change identifier is missing, stop and request it. Treat conflicting sources of truth as a blocker.

## Decision Readiness Gate

If load-bearing product, domain, externally observable contract, security,
data-model, data-ownership, or major architecture decisions remain unresolved,
stop and route to `grill-with-docs`. Do not resolve them by assumption inside
planning or present a recommended option as an approved decision.

## Workflow

1. Read repository rules and sources of truth before examining implementation details.
2. Inspect Git state and record unexplained edits or pre-existing failures; do not alter them.
3. Trace relevant modules, symbols, contracts, tests, data/control flow, and error boundaries.
4. Define objective, in scope, out of scope, observable acceptance criteria, risks, unknowns, and rollback.
5. Classify risk and propose an execution policy: `one-task-at-a-time` for any risk level, or `supervised-auto` only for low/medium risk. List the exact auto-approved tasks, allowed paths, human checkpoints, and stop conditions; the human must approve the mode explicitly.
6. Divide work into independently verifiable tasks. Identify contract, dependency, migration, security, and data-loss approval points.
7. Define normal, boundary, failure, compatibility, and security tests. Verification commands must use existing Docker/Compose/Make/container wrappers only.
8. Write `changes/<change-id>/IMPLEMENTATION_PLAN.md` using [the template](./references/IMPLEMENTATION_PLAN_TEMPLATE.md).
9. Present unresolved decisions and stop for explicit human approval. Do not invoke implementation. A plan's existence, proposed mode, or prior approval of another revision is not approval.

## Stop Conditions

Stop for conflicting requirements, unexplained worktree changes, missing canonical container entrypoints, required production/secret access, irreversible data operations, unapproved dependencies/migrations, or scope/contract changes. Missing Docker support points to the separate `bootstrap-project` workflow; it never permits host project execution.

## Exit Criteria and Handoff

Separate observed facts from assumptions. Cite files, symbols, baseline commands, and results precisely. The handoff is the plan path, task list, risks, and questions awaiting human approval. A written plan is not approval.
