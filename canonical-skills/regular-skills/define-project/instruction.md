# Define Project

Synthesize decisions that have already been resolved into a project definition that a human can approve, decompose into a Roadmap, and use to begin project bootstrap. This workflow organizes decisions; it does not choose among unresolved product or architecture alternatives.

## Admission

Before writing, confirm evidence for all of the following:

- project goal;
- target users or actors;
- observable success criteria;
- confirmed scope boundaries;
- confirmed domain terminology;
- every load-bearing decision is resolved or explicitly deferred;
- known constraints;
- a Decision Readiness Summary or equivalent evidence.

Read the Decision Readiness Summary, relevant `CONTEXT.md` or `CONTEXT-MAP.md`, ADRs, existing project documents, repository policy, and current repository structure.

If decision-readiness evidence is missing, or any blocking product, domain, contract, security, data-ownership, data-model, acceptance, or major architecture decision remains:

1. do not infer an answer;
2. do not turn a recommendation into an approved decision;
3. identify the exact blocking decisions;
4. stop and route to `grill-with-docs`.

## Process

1. Define the problem, users and actors, observable outcomes, success criteria, in-scope work, and out-of-scope work.
2. Consolidate confirmed domain invariants without duplicating the canonical glossary.
3. Define externally observable contracts, including only relevant APIs, events, authorization invariants, error behavior, data-ownership boundaries, and compatibility requirements.
4. Confirm major system boundaries and external dependencies from resolved evidence.
5. Define the minimum Walking Skeleton. It must be genuinely executable, cross the project's principal system boundaries, and verify the most important project assumption. A blank scaffold does not qualify.
6. Build Roadmap phases in dependency order. Each phase must:
   - produce an observable outcome;
   - be independently acceptable;
   - define included scope and acceptance criteria;
   - state dependencies, risks, and deferred work;
   - form a vertical outcome slice rather than a horizontal technical layer.
7. Preserve intentionally deferred decisions and state when they become blocking.
8. Cross-reference `CONTEXT.md`, ADRs, and readiness evidence instead of copying them wholesale.
9. Assemble the Project Approval Packet using [PROJECT_APPROVAL_PACKET_TEMPLATE.md](./references/PROJECT_APPROVAL_PACKET_TEMPLATE.md).
10. Stop and wait for explicit human project approval.

## Outputs

Create project-definition artifacts only as needed:

### `docs/SPEC.md`

```markdown
# Project Specification

## Problem
## Users and Actors
## Observable Outcomes
## Success Criteria
## In Scope
## Out of Scope
## Domain Invariants
## System Boundaries
## Non-Functional Requirements
## Known Constraints
## Intentionally Deferred Decisions
```

### `docs/CONTRACTS.md`

Create this only when the project has an externally observable contract, such as an API or event contract, authorization invariant, error contract, data-ownership boundary, or compatibility requirement. Do not describe internal implementation details as contracts.

### `docs/ROADMAP.md`

```markdown
# Roadmap

## Walking Skeleton

## Phase N

### Observable Outcome
### Included Scope
### Acceptance Criteria
### Dependencies
### Risks
### Deferred Work
```

### Project Approval Packet

The packet must identify the artifacts being approved, readiness evidence, Walking Skeleton, Roadmap outcomes, deferred decisions, risks, unresolved non-blocking concerns, and the exact approval requested. It must make clear that silence or approval of earlier decisions is not project approval.

## Authority Boundary

This workflow may write project-definition artifacts only. It must not write production code, create runtime implementation, add dependencies, run migrations, establish a deployment, approve the project, commit, push, merge, or start `bootstrap-project`.

Do not silently fill gaps in the definition. Material new ambiguity discovered while synthesizing is a stop condition and routes back to `grill-with-docs`.

## Completion

Completion means the specification, any necessary contracts, Roadmap, and Project Approval Packet are internally consistent and ready for human review. Present them and stop. Only explicit human project approval can admit a later `bootstrap-project` workflow.
