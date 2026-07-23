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
- every Load-Bearing Decision required by the Project Definition, Walking Skeleton, or included Roadmap phases is resolved;
- every other deferred decision has a safe-deferral rationale, named owner, and explicit blocking trigger;
- known constraints;
- a Decision Readiness Summary, or equivalent evidence that satisfies [DECISION_READINESS_EVIDENCE.md](./references/DECISION_READINESS_EVIDENCE.md).

Validate readiness evidence using the referenced contract, then read relevant `CONTEXT.md` or `CONTEXT-MAP.md`, ADRs, existing project documents, repository policy, and current repository structure.

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
   - prefer an independently acceptable Vertical Slice;
   - define included scope and acceptance criteria;
   - state dependencies, risks, Decision Gates, and deferred work;
   - avoid a horizontal technical layer unless it is a qualifying enabling Phase.
   An enabling Phase is allowed only when it produces an independently verifiable capability, is required by later outcome slices, and cannot be safely folded into the first dependent slice.
7. Map every deferred decision to the Roadmap Phase or condition where it becomes blocking. Each Decision Gate names the owner, required timing, and current status.
8. Cross-reference `CONTEXT.md`, ADRs, and readiness evidence instead of copying them wholesale.
9. Write project-definition artifacts using [PROJECT_DEFINITION_FORMAT.md](./references/PROJECT_DEFINITION_FORMAT.md), then assemble the Project Approval Packet using [PROJECT_APPROVAL_PACKET_TEMPLATE.md](./references/PROJECT_APPROVAL_PACKET_TEMPLATE.md).
10. Stop and wait for explicit human project approval.

## Outputs

- `docs/SPEC.md`
- conditional `docs/CONTRACTS.md`
- `docs/ROADMAP.md`, including per-phase Decision Gates
- Project Approval Packet

The formats and conditional creation rules are defined in the referenced templates. Silence or approval of earlier decisions is not Project Approval.

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
