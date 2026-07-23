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

1. Read the user's goal, repository policy, existing project documents, code, relevant `CONTEXT.md` or `CONTEXT-MAP.md`, and ADRs.
2. Apply `grilling` to inventory every unresolved choice within the current project or change scope and classify its ownership. Prioritize Load-Bearing Decisions without omitting smaller choices that affect observable behavior, failure handling, data semantics, operations, or acceptance.
3. Investigate facts from repository evidence. Resolve user-owned decisions through explicit confirmation. Record implementation-owned defaults without presenting them as product decisions.
4. Apply `domain-modeling` whenever confirmed answers change terminology, entities, relationships, boundaries, ownership, or invariants. Record only qualifying ADRs.
5. Apply the Safe Deferral Gate to every proposed deferred decision.
6. Maintain decision artifacts inline and finish with the Decision Readiness Summary.

## Safe Deferral Gate

A decision is `intentionally deferred` only when all conditions hold:

1. No current specification, Externally Observable Contract, Walking Skeleton, or included near-term Phase requires an assumed answer.
2. Deferral does not change the meaning of current acceptance criteria.
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

Every completion or stop must output exactly these sections:

```markdown
## Resolved Decisions

## Intentionally Deferred Decisions

## Blocking Open Decisions

## Conflicts or Assumptions Found

## Updated Artifacts

## Recommended Next Workflow
```

Record every deferred decision as:

```markdown
- Decision:
- Why Safe Now:
- Affected Scope:
- Decision Owner:
- Becomes Blocking When:
```

`Recommended Next Workflow` must name one concrete route: `define-project`, `plan-change`, `continue grill-with-docs`, or `return to human decision owner`.

Only when `Blocking Open Decisions: None` may the summary declare `Ready for define-project`. If any blocking decision remains, do not soften the block with “mostly ready,” an implementation assumption, or a recommendation presented as a decision.

## Exit Criteria

Every unresolved choice in the current scope has an owner and readiness classification. Every user-owned decision required now is resolved, every deferred decision passes the Safe Deferral Gate, and no Blocking Decision remains.

## Handoff

Return the Decision Readiness Summary and stop. The named next workflow requires its own Admission Criteria and authority.
