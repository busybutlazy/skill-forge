# Define Project

## Objective

Synthesize resolved decisions into an approval-ready Project Definition and outcome-based Roadmap. This workflow organizes decisions; it does not choose unresolved alternatives.

## Admission Criteria

Required evidence:

- project goal;
- target users or actors;
- observable success criteria;
- confirmed scope boundaries;
- confirmed domain terminology;
- every load-bearing decision is resolved or explicitly deferred;
- known constraints;
- a Decision Readiness Summary or equivalent evidence.

Read the Decision Readiness Summary, relevant `CONTEXT.md` or `CONTEXT-MAP.md`, ADRs, existing project documents, repository policy, and current repository structure.

Admission fails when readiness evidence is missing or any Blocking Decision remains in product, domain, contract, security, data ownership, data model, acceptance, or major architecture:

1. do not infer an answer;
2. do not turn a recommendation into an approved decision;
3. identify the exact blocking decisions;
4. stop and route to `grill-with-docs`.

## Workflow

1. Define the problem, users and actors, observable outcomes, success criteria, in-scope work, and out-of-scope work.
2. Consolidate confirmed domain invariants without duplicating the canonical glossary.
3. Define externally observable contracts, including only relevant APIs, events, authorization invariants, error behavior, data-ownership boundaries, and compatibility requirements.
4. Confirm major system boundaries and external dependencies from resolved evidence.
5. Define the minimum Walking Skeleton: executable, crossing the primary system boundaries, and testing the highest-risk assumption. A structural scaffold does not qualify.
6. Build Roadmap phases in dependency order. Each phase must:
   - produce an observable outcome;
   - be independently acceptable;
   - define included scope and acceptance criteria;
   - state dependencies, risks, and deferred work;
   - form an independently acceptable Vertical Slice, not a horizontal technical layer.
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

| Capability | Authority |
|---|---|
| Read readiness evidence, context, ADRs, documents, and repository structure | Allowed |
| Write `SPEC.md`, conditional `CONTRACTS.md`, `ROADMAP.md`, and approval packet | Allowed |
| Write production code or runtime implementation | Denied |
| Add dependencies, run migrations, or establish deployment | Denied |
| Approve the project or start `bootstrap-project` | Denied |
| Commit, push, or merge | Denied |

Do not silently fill gaps in the definition. Material new ambiguity discovered while synthesizing is a stop condition and routes back to `grill-with-docs`.

## Exit Criteria

The specification, necessary contracts, Roadmap, and Project Approval Packet are internally consistent and ready for review.

## Handoff

Present the Project Approval Packet and stop. Only explicit Human Project Approval can admit a later `bootstrap-project` workflow.
