# Grill with Docs

## Objective

Reach Decision Readiness before project definition or change planning. Use `grilling` for the interview and `domain-modeling` for terminology, boundaries, invariants, and ADR-worthy choices.

## Admission Criteria

Admit when any of these are true:

- a new project has only an initial idea;
- a major feature has multiple viable directions;
- domain terminology is inconsistent;
- the user, documents, code, or ADRs conflict;
- requirements affect external contracts, data ownership or models, authorization, security boundaries, acceptance, or major architecture;
- `define-project` or `plan-change` cannot proceed without guessing.

Reject admission for a clear bounded change, approved task execution, verification or review alone, or a local fix with a known root cause.

## Workflow

1. Read the user's goal, repository policy, existing project documents, code, relevant `CONTEXT.md` or `CONTEXT-MAP.md`, ADRs, [DECISION_INVENTORY_FORMAT.md](./references/DECISION_INVENTORY_FORMAT.md), and [READINESS_SUMMARY_FORMAT.md](./references/READINESS_SUMMARY_FORMAT.md).
2. Apply `grilling` to inventory every unresolved choice within the current project or change scope and classify its ownership. Prioritize Load-Bearing Decisions without omitting smaller choices that affect observable behavior, failure handling, data semantics, operations, or acceptance.
3. Investigate facts from repository evidence. Resolve user-owned decisions through explicit confirmation. Record implementation-owned defaults without presenting them as product decisions.
4. Apply `domain-modeling` whenever confirmed answers change terminology, entities, relationships, boundaries, ownership, or invariants. Record only qualifying ADRs.
5. Apply the Safe Deferral Gate to every proposed deferred decision.
6. Maintain the required Decision Inventory artifact and finish with the Decision Readiness Summary. If the session stops before inventory and readiness assessment are complete, mark both outputs as partial and use the incomplete status.

## Safe Deferral Gate

A decision is `intentionally deferred` only when all conditions hold:

1. The next downstream artifact can be completed coherently without assuming an answer.
2. The decision does not change the meaning of proposed scope, Externally Observable Contracts, Walking Skeleton, acceptance criteria, or any work authorized before the recorded blocking trigger.
3. A named decision owner or authority is recorded.
4. The exact phase, event, date, or condition that makes the decision blocking is recorded.

Otherwise classify it as `blocking unresolved`.

## Authority Boundary

| Capability | Authority |
|---|---|
| Read repository, documents, code, context, and ADRs | Allowed |
| Write confirmed glossary terms and qualifying ADRs | Allowed by repository policy |
| Write dedicated decision notes or session summary | Allowed by repository policy |
| Write production code, dependencies, migrations, runtime, deployment, or implementation tasks | Denied |
| Approve a decision | Denied |
| Start implementation, commit, push, merge, or invoke a higher-authority workflow | Denied |

## Decision Readiness Summary

Every completion or stop must produce the Decision Inventory and summary defined by the referenced formats. The summary must use exactly one status: `Ready`, `Stopped With Blocking Decisions`, or `Incomplete — Session Stopped Before Readiness Assessment`.

Only `Ready` with `Blocking Open Decisions: None` may declare `Ready for define-project` or `Ready for plan-change`. A stopped session cannot claim readiness, and known blockers cannot be softened with an assumption or recommendation.

## Exit Criteria

For `Ready`, the complete inventory covers the current scope, every choice has an owner and readiness classification, every required user-owned decision is resolved, every deferred decision passes the Safe Deferral Gate, and no Blocking Decision remains.

## Handoff

Return the Decision Inventory and Decision Readiness Summary, then stop. The named next workflow requires its own Admission Criteria and authority.
