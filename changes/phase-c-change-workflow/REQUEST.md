# Phase C Request: Change Workflow Skills

## Problem

The managed guideline defines a gated change lifecycle, but target projects receive only prose. The named workflow skills are absent from the public catalog, so agents cannot reliably re-enter planning, task implementation, verification, reporting, or review after context changes.

## Goal

Deliver Docker-first public skills that turn the guideline lifecycle into repeatable, separately triggered workflows while preserving human approval gates and role separation.

## In scope

1. `plan-change`: read-only analysis and an approval-ready plan.
2. `implement-task`: execute exactly one approved task and stop.
3. `verify-change`: run canonical containerized verification and create traceability.
4. `report-change`: compare approved plan with diff and disclose deviations.
5. `review-change`: read-only adversarial review of completion claims.
6. Per-skill reference templates, a `Change Workflow` catalog group, and accurate guideline availability labels.
7. Canonical validation plus Codex and Claude render/install smoke tests.

## Out of scope

- Docker/project initialization (`bootstrap-project` is Phase D).
- Hooks, CI engine changes, deployment, production access, or secrets.
- Automatically chaining all skills or approving plans, deviations, reviews, merge, or release.
- Target-specific business logic or company-internal processes.

## Non-negotiable constraints

- Public source lives only in `canonical-skills/regular-skills/`.
- Every skill has a narrow trigger and explicit non-trigger cases.
- `plan-change` and `review-change` are read-only.
- `implement-task` performs one named approved task, never the next task.
- No skill installs dependencies or runs project commands directly on the host.
- If no canonical container entry exists, work stops and points to Phase D bootstrap; there is no host fallback.
- Human approval is required between planning and implementation and for material deviations.

## Acceptance criteria

- All five skills validate and render/install for both targets with references preserved.
- Catalog grouping is correct and not automatically recommended.
- Each workflow specifies inputs, outputs, stop conditions, prohibited actions, and a stopping handoff.
- Templates use consistent terminology for implementation, verification, change, and review reports.
- Full tests pass; fresh Codex/Claude installs report `up_to_date`.
- The guideline distinguishes delivered skills from roadmap items.

## Human decisions

- Dockerization is mandatory; missing Docker is not permission for host project execution.
- Implementation is delegated to an implementation agent; the primary session is reviewer.
