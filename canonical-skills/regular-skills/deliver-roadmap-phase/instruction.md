# Deliver Roadmap Phase

## Objective

Deliver one approved Roadmap Phase as bounded governed Changes, then stop for Human Phase Acceptance.

## Admission Criteria

- The user wants to deliver one named phase or milestone from an existing Roadmap.
- The project has enough specifications, contracts, architecture decisions, and containerized verification commands to plan the phase without inventing requirements.
- The user wants a single entry point instead of invoking each change-workflow skill manually.

Reject admission for:

- “Continue the Roadmap,” multiple phases, or an ambiguous heading. Require the Roadmap path and one uniquely matching phase ID or heading.
- Product discovery, changing Roadmap scope, or filling missing requirements by assumption.
- A single already-planned task or change; use the underlying workflow skill directly.
- Commit, push, merge, release, deployment, production/secret access, or self-approval.

## Required Inputs

- Roadmap path and exact phase ID/heading.
- Requested execution mode: `one-task-at-a-time` or `supervised-auto` (default to the safer mode when omitted).
- Repository rules and applicable sources of truth.
- Existing Docker/Compose/Make/container entrypoints for verification.

Read [the phase delivery packet template](./references/PHASE_DELIVERY_PACKET_TEMPLATE.md) before planning. Never install dependencies or run project commands directly on the host.

## Phase Readiness Gate

A phase must have an approved observable outcome, scope, acceptance criteria,
and Decision Gates. Read every gate before planning. A Phase cannot enter
planning when any decision required before Phase start remains unresolved.

If a gate or phase scope still contains an undecided external contract, data ownership rule, security boundary, or major architecture alternative, stop and route to `grill-with-docs`. Do not conduct a full interview or resolve the choice by assumption inside phase delivery.

## Phase Workflow

1. Resolve exactly one Roadmap phase. Quote its stable ID/heading, boundaries, and Decision Gates in `changes/<phase-run-id>/PHASE_REQUEST.md`. Stop if it is absent, ambiguous, already complete, or has an unresolved decision required before Phase start.
2. Perform read-only discovery. Read applicable specifications, contracts, ADR index/entries, project rules, current Git state, tests, and container commands. Do not modify production code during discovery.
3. Decompose the phase into the smallest independently verifiable child Changes. Define dependency order, acceptance criteria, risk, execution mode, allowed paths, rollback, and the Roadmap outcomes covered by each child. Convert every non-start Decision Gate into an explicit human checkpoint in the Phase Execution Plan.
4. Write `changes/<phase-run-id>/PHASE_EXECUTION_PLAN.md` using the template. Map each gate to the child or Phase event it blocks, its owner, and current status. Create draft child `REQUEST.md` and `IMPLEMENTATION_PLAN.md` artifacts under distinct `changes/<change-id>/` directories. Planning artifacts are the only writes allowed before approval.
5. Present one Phase Delivery Packet approval gate. Approval must identify the current plan revision, exact phase, child Changes, dependency order, risks/modes, auto-approved tasks/paths, and checkpoints. A vague “continue” or approval of an older revision is insufficient.
6. After approval, execute child Changes in dependency order:
   - low/medium-risk `supervised-auto` children follow the installed `run-approved-change` contract;
   - `one-task-at-a-time` and high-risk children use `implement-task` and stop at every approved checkpoint;
   - extreme-risk or prohibited operations require manual handling and cannot be auto-executed;
   - a child Change cannot start while a Decision Gate required before that child remains unresolved;
   - dependent work remains blocked until the named decision owner resolves the gate;
   - a failed or blocked child prevents dependent children from starting.
7. Do not silently repair a failed evidence-only verification. Record the result and stop for a new approved remediation plan.
8. After all children complete their verification and Change Reports, confirm every Decision Gate required before Phase completion is resolved, then run phase-level container verification against the Roadmap outcomes. The Phase cannot complete while such a gate remains unresolved. Write `PHASE_VERIFICATION_REPORT.md` and `PHASE_CHANGE_REPORT.md`, including incomplete, unverified, deferred, and blocked outcomes.
9. Hand the phase packet and child artifacts to a genuinely separate `review-change` session/subagent or a human reviewer. Never review or approve the implementation in the same execution context.
10. Stop for final human acceptance. Only after explicit acceptance may a separately authorized action update Roadmap completion state. Never commit, push, merge, release, or deploy implicitly.

## Mandatory Stop Conditions

Stop for ambiguous phase identity; missing sources of truth or container entrypoint; plan revision drift; unexplained Git changes; scope/contract/schema/dependency/architecture/security deviation; new task or path; unmet checkpoint; failed/incomplete verification; high/extreme risk not assigned to the safe mode; production/secret/destructive access; or any attempt to include another Roadmap phase.

On stop, preserve evidence, name the blocked child/outcome, and request the smallest human decision required. Do not advance the Roadmap state.

## Authority Boundary

| Capability | Authority |
|---|---|
| Coordinate installed atomic workflow skills | Allowed within the approved Phase Delivery Packet |
| Weaken an atomic skill's Admission Criteria | Denied |
| Expand scope, paths, tasks, or execution mode | Denied without revised approval |
| Review or self-approve implementation | Denied |
| Commit, push, merge, release, or deploy | Denied |

Planning approval, independent review, Human Phase Acceptance, and Git/release actions remain distinct authorities.
