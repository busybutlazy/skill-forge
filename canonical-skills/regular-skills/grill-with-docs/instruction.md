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
2. Build the current decision tree and classify known nodes.
3. Identify load-bearing unresolved decisions: choices that affect scope, observable contracts, the domain model, major architecture, acceptance, security, data ownership, or costly implementation direction.
4. Resolve them in dependency order using `grilling`. Ask one primary question at a time and wait for the user's answer.
5. For each question provide:
   - the decision;
   - why it must be decided now;
   - a concrete recommended answer and rationale;
   - the meaningful alternatives;
   - the costs and trade-offs of each option.
6. Verify facts from the repository instead of asking the user. Never treat a recommendation or inference as a confirmed decision.
7. Pressure-test answers with concrete scenarios, failure cases, and boundary cases. Challenge ambiguous, contradictory, or conflicting answers.
8. Apply `domain-modeling` when terminology, entities, relationships, boundaries, ownership, or invariants change. Write only confirmed terms to the canonical glossary.
9. Record an ADR only when the decision is hard to reverse, surprising without context, and a real trade-off.
10. Continue until no blocking decisions remain, or the user explicitly asks to stop.
11. Produce the Decision Readiness Summary below.

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

`Recommended Next Workflow` must name one concrete route: `define-project`, `plan-change`, `continue grill-with-docs`, or `return to human decision owner`.

Only when `Blocking Open Decisions: None` may the summary declare `Ready for define-project`. If any blocking decision remains, do not soften the block with “mostly ready,” an implementation assumption, or a recommendation presented as a decision.

## Exit Criteria

Every Load-Bearing Decision affecting scope, Externally Observable Contracts, domain model, major architecture, acceptance, security, data ownership, or costly implementation direction is resolved or intentionally deferred.

## Handoff

Return the Decision Readiness Summary and stop. The named next workflow requires its own Admission Criteria and authority.
