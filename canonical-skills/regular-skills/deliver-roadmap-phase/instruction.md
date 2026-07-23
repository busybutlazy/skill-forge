# Deliver Roadmap Phase

Turn one exact Roadmap phase into bounded governed changes, obtain one execution approval, coordinate the approved work, and stop for final human acceptance.

## Use This For

- The user wants to deliver one named phase or milestone from an existing Roadmap.
- The project has enough specifications, contracts, architecture decisions, and containerized verification commands to plan the phase without inventing requirements.
- The user wants a single entry point instead of invoking each change-workflow skill manually.

## Do Not Use This For

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
and resolved blocking decisions. If it still contains an undecided external
contract, data ownership rule, security boundary, or major architecture
alternative, stop and route to `grill-with-docs`. Do not conduct a full
interview or resolve the choice by assumption inside phase delivery.

## Phase Workflow

1. Resolve exactly one Roadmap phase. Quote its stable ID/heading and boundaries in `changes/<phase-run-id>/PHASE_REQUEST.md`. Stop if it is absent, ambiguous, already complete, or depends on unresolved product decisions.
2. Perform read-only discovery. Read applicable specifications, contracts, ADR index/entries, project rules, current Git state, tests, and container commands. Do not modify production code during discovery.
3. Decompose the phase into the smallest independently verifiable child Changes. Define dependency order, acceptance criteria, risk, execution mode, allowed paths, checkpoints, rollback, and the Roadmap outcomes covered by each child.
4. Write `changes/<phase-run-id>/PHASE_EXECUTION_PLAN.md` using the template. Create draft child `REQUEST.md` and `IMPLEMENTATION_PLAN.md` artifacts under distinct `changes/<change-id>/` directories. Planning artifacts are the only writes allowed before approval.
5. Present one Phase Delivery Packet approval gate. Approval must identify the current plan revision, exact phase, child Changes, dependency order, risks/modes, auto-approved tasks/paths, and checkpoints. A vague “continue” or approval of an older revision is insufficient.
6. After approval, execute child Changes in dependency order:
   - low/medium-risk `supervised-auto` children follow the installed `run-approved-change` contract;
   - `one-task-at-a-time` and high-risk children use `implement-task` and stop at every approved checkpoint;
   - extreme-risk or prohibited operations require manual handling and cannot be auto-executed;
   - a failed or blocked child prevents dependent children from starting.
7. Do not silently repair a failed evidence-only verification. Record the result and stop for a new approved remediation plan.
8. After all children complete their verification and Change Reports, run phase-level container verification against the Roadmap outcomes. Write `PHASE_VERIFICATION_REPORT.md` and `PHASE_CHANGE_REPORT.md`, including incomplete, unverified, deferred, and blocked outcomes.
9. Hand the phase packet and child artifacts to a genuinely separate `review-change` session/subagent or a human reviewer. Never review or approve the implementation in the same execution context.
10. Stop for final human acceptance. Only after explicit acceptance may a separately authorized action update Roadmap completion state. Never commit, push, merge, release, or deploy implicitly.

## Mandatory Stop Conditions

Stop for ambiguous phase identity; missing sources of truth or container entrypoint; plan revision drift; unexplained Git changes; scope/contract/schema/dependency/architecture/security deviation; new task or path; unmet checkpoint; failed/incomplete verification; high/extreme risk not assigned to the safe mode; production/secret/destructive access; or any attempt to include another Roadmap phase.

On stop, preserve evidence, name the blocked child/outcome, and request the smallest human decision required. Do not advance the Roadmap state.

## Authority Boundary

This skill is an orchestrating facade over the installed atomic workflow skills. It does not weaken their admission gates or grant authority beyond the approved Phase Delivery Packet. Planning approval, independent review, final acceptance, and Git/release actions remain distinct authorities.
