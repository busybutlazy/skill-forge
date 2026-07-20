# Verify Change

Produce reproducible evidence for an implemented change. Do not fix implementation while verifying; the only permitted write is the owned report.

## Use This For

- Implementation is ready to be checked against acceptance criteria and an approved plan.

## Do Not Use This For

- Planning, implementation, debugging by editing code, change summarization without tests, or approving completion.

## Required Inputs

- Change ID, request/acceptance criteria, approved implementation plan, current diff, and task handoffs.
- Existing canonical format, lint, type, unit, integration, contract, E2E, build, and security commands where applicable.

Missing acceptance criteria or an attributable diff is a blocker. If no existing containerized verification entrypoint exists, stop and point to Phase D `bootstrap-project`; never run project commands on the host.

## Workflow

1. Inspect repository state and map each requirement to implementation locations and candidate tests.
2. Record environment, relevant versions, services, mocks, and baseline failures.
3. Run applicable existing canonical commands through Docker/Compose/Make/container wrappers in the repository-defined order.
4. Capture the exact command, exit code, passed/failed/skipped counts when available, and relevant output. Do not convert failures into success or silently omit checks.
5. Perform permitted read-only/manual observations and distinguish them from automated tests.
6. Write `changes/<change-id>/VERIFICATION_REPORT.md` using [the template](./references/VERIFICATION_REPORT_TEMPLATE.md).
7. Stop with a clear pass/fail/incomplete summary and blockers. Do not repair findings or invoke reporting/review automatically.

## Stop Conditions

Stop for destructive/production commands, secrets, migrations, dependency installation, unexplained worktree changes, missing container support, unsafe environment assumptions, or verification that would mutate persistent data without approval. Contract or scope mismatch is evidence, not permission to rewrite the plan.

## Evidence Standard

Every pass claim must link requirement, implementation, test, and observed result. List tests not run and why, mock boundaries, uncertainty, known risks, and human review hotspots.
