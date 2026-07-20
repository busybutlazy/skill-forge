# Bootstrap Project

Create the minimum explicitly approved Docker-first development and CI baseline. Discovery is read-only; no infrastructure write is allowed until a human approves the bootstrap plan.

## Use This For

- A new or unbootstrapped repository lacks an approved Docker/Compose workflow, canonical commands, CI baseline, or project-specific agent rules.
- A human explicitly asks to establish the Docker-first prerequisite before normal implementation.

## Do Not Use This For

- Rewriting or replacing mature Docker, Compose, task-runner, or CI infrastructure.
- Application implementation, architecture invention, dependency upgrades, deployment, Kubernetes, cloud/IAM, production, or secret handling.
- Treating missing Docker as permission to install or execute project dependencies on the host.

Existing infrastructure is unmanaged architecture. If it exists or conflicts with the proposed baseline, stop and recommend adoption analysis or a separate approved `plan-change` migration; never overwrite it automatically.

## Required Inputs

- Stable `<change-id>`, bootstrap request, repository instructions, specifications/contracts/ADRs, and Git state.
- Human-confirmed stack/runtime version, base image, package manager/lock strategy, canonical commands, proposed files, CI scope, risks, and rollback.

Ambiguous versions, commands, package managers, existing infrastructure ownership, or acceptance criteria require a question, not a guess.

## D1 — Read-Only Discovery

1. Read repository rules and sources of truth.
2. Inspect Git status and record unexplained edits without altering them.
3. Inspect language/runtime indicators, lockfiles, manifests, documented commands, and existing Dockerfile/Compose/Make/task-runner/CI files.
4. Do not install dependencies or execute application tools/tests. Host tools may only inspect/write repository text, invoke Git, and invoke Docker after approval.
5. Classify the repository using [the baseline checklist](./references/DOCKER_BASELINE_CHECKLIST.md):
   - Python: use [the Python profile](./references/PYTHON_PROFILE.md).
   - Node/TypeScript: use [the Node profile](./references/NODE_PROFILE.md).
   - Generic/unknown: do not fabricate dependencies, package managers, or commands; request a stack decision or propose only an approved neutral shell/documentation baseline.
   - Existing container workflow: stop and report adoption gaps or propose a separate migration plan.

## D2 — Bootstrap Plan and Mandatory Approval Pause

Prepare a plan using [the bootstrap plan template](./references/BOOTSTRAP_PLAN_TEMPLATE.md). It must state observed evidence, proposed files, approved pinned base, package-manager/lock strategy, command surface, CI behavior, unavailable commands and reasons, risks, rollback, and this declaration:

> No project dependency will be installed or executed on the host. Agents, humans, and CI will use the same approved container entrypoint.

Present the complete plan and **stop**. Do not create or modify infrastructure until a human explicitly approves that exact plan. A request to analyze, a generated plan, silence, or prior approval of this skill is not write approval. Material deviations require a revised plan and new approval.

## D3 — Minimum Approved Infrastructure

Only after explicit approval, create only missing files listed in the approved plan:

- `Dockerfile` and optionally an approved `Dockerfile.dev` or dev stage.
- `compose.yaml` and `.dockerignore`.
- `Makefile` or the repository's approved task-runner equivalent.
- `docs/agent-rules.md` using [the template](./references/AGENT_RULES_TEMPLATE.md).
- `.github/workflows/ci.yml` using the same canonical entrypoint as local work.
- `changes/<change-id>/` artifacts using [the templates](./references/CHANGE_ARTIFACT_TEMPLATES.md).

The canonical surface covers `setup`, `format` or `format-check`, `lint`, `typecheck`, `test-unit`, optional `test-integration`, `verify`, `build`, and `run`. Unsupported commands must fail clearly or be documented as unavailable with a reason; they must never silently invoke host tools. Do not add application dependencies solely to make a command exist.

Use references as decision guidance, not universal files to copy blindly. Preserve all unrelated and pre-existing files.

## D4 — Container-Only Verification and Handoff

1. Validate Compose configuration through Docker.
2. Build the approved image and run the smallest approved smoke path.
3. Run supported canonical checks only through Docker/Compose/Make container entrypoints.
4. Record exact commands, exit codes, counts, environment, mocks, skipped/unavailable checks and reasons, ownership, and Git diff.
5. Complete `VERIFICATION_REPORT.md` and `CHANGE_REPORT.md`; identify rollback and review hotspots.
6. Stop for independent review and human acceptance. Do not implement application features, merge, deploy, or invoke the next workflow automatically.

## Stop Conditions

Stop for missing explicit approval, Docker unavailable, conflicting or unexplained infrastructure/worktree state, unapproved file or command changes, uncertain runtime/package-manager evidence, dependency or architecture expansion, data-loss risk, production/secret access, or failed verification requiring a material plan deviation. There is no host fallback.

## Evidence Standard

Separate observed evidence, approved decisions, executed results, and assumptions. Never claim bootstrap completion when required checks failed or were not run. The created baseline remains subject to independent review and CI.
