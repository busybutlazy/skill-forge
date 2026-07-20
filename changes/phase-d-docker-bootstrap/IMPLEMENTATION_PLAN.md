# Phase D Implementation Plan: Docker-First Project Bootstrap

## Dependency and objective

Phase D starts only after Phase C review/acceptance. Create one public `bootstrap-project` skill that turns a repository without an approved container workflow into a minimally executable Docker-first baseline, with human approval between discovery and mutation.

## Workflow contract

### D1 — Read-only discovery

Without installing or executing project dependencies, inspect rules/spec/contracts/ADRs, Git state, language indicators, lockfiles, existing Docker/Compose/Make/task runner/CI, and documented commands.

Classify as Python, Node/TypeScript, generic/unknown, or existing container workflow requiring adoption/separate migration.

### D2 — Bootstrap plan and approval

Present detected evidence, proposed files/commands, base version, package-manager/lock strategy, CI, risks, rollback, and an explicit no-host-execution statement. Stop for approval. Ask rather than guess ambiguous versions, package manager, or commands.

### D3 — Minimum infrastructure

After approval, create only missing approved files:

```text
Dockerfile
Dockerfile.dev or an approved dev stage
compose.yaml
.dockerignore
Makefile or existing task-runner equivalent
docs/agent-rules.md
.github/workflows/ci.yml
changes/<change-id>/
├── REQUEST.md
├── IMPLEMENTATION_PLAN.md
├── VERIFICATION_REPORT.md
├── CHANGE_REPORT.md
└── REVIEW_REPORT.md
```

Canonical command surface: `setup`, `format`/`format-check`, `lint`, `typecheck`, `test-unit`, optional `test-integration`, `verify`, `build`, and `run`. A command may be explicitly unavailable with a reason; it must not silently use host tools.

### D4 — Container-only verification

Validate Compose, build the approved image, run the smallest smoke path and supported canonical checks, record commands/exit codes/counts/environment/skips, inspect ownership and diff, produce verification/change reports, and stop for review.

## Stack profiles

- Python: approved pinned base compatible with `pyproject.toml`; use existing lock/package manager; install/test only in containers.
- Node/TypeScript: approved pinned Node base; select npm/pnpm/yarn only from lockfile evidence; frozen install in containers.
- Generic/unknown: do not fabricate dependencies or commands; create only an approved neutral shell/documentation or stop for a stack decision.
- Existing infrastructure: do not overwrite; report gaps and recommend a separate `plan-change` migration.

## Canonical package

Version `0.1.0`, date `2026-07-20`, public, both targets:

```text
canonical-skills/regular-skills/bootstrap-project/
├── package.json
├── instruction.md
├── manifest.json
├── targets/{codex.frontmatter.json,claude.frontmatter.json}
└── references/
    ├── BOOTSTRAP_PLAN_TEMPLATE.md
    ├── DOCKER_BASELINE_CHECKLIST.md
    ├── PYTHON_PROFILE.md
    ├── NODE_PROFILE.md
    ├── AGENT_RULES_TEMPLATE.md
    └── CHANGE_ARTIFACT_TEMPLATES.md
```

References are decision guidance/templates, not blindly copied universal Dockerfiles.

## Catalog and guideline

- Add `Project Bootstrap` after `Change Workflow`; do not add automatic recommendation without separate approval.
- Move `bootstrap-project` from Planned to Available only after validation/smoke.
- Preserve Docker-only as the standard and bootstrap as the sanctioned path, never a host fallback.
- Bump `agent-guideline`.

## Delegated implementation sequence

1. Re-read accepted Phase C outputs and this plan.
2. Scaffold the package via `create-skill` conventions.
3. Draft instruction and six references with explicit trigger/non-trigger, approval pause, and no-host fallback.
4. Update catalog/guideline availability/version.
5. Finalize metadata and validate.
6. Add focused contract tests where needed.
7. Render/install into fresh Codex and Claude Git projects; verify every reference and repeated install.
8. Run the full Docker suite.
9. Produce Phase D verification/change reports and stop; do not commit.

## Verification matrix

- Metadata/integrity validate and target triggers are narrow.
- Instruction contains discovery, approval pause, no-host execution, unmanaged refusal, evidence, and review handoff.
- Profiles do not invent package managers/dependencies.
- Both targets preserve all references and install `up_to_date` idempotently.
- Catalog/menu and guideline availability/version are accurate.
- Full Docker suite passes.

## Risks and rollback

- Insecure generic containers: require evidence/approval, not blind templates.
- Mutation of mature infrastructure: explicit non-trigger/refusal.
- Docker unavailable: hard environment blocker, never host fallback.
- CI/local drift: CI invokes the same canonical entrypoint.
- Deployment scope creep: exclude production/cloud concerns.

Rollback removes the canonical package/catalog group and reverts guideline availability/version. Target bootstrap rollback follows its approved Git diff and never deletes pre-existing infrastructure.

## Reviewer checkpoints

- Docker-only is never weakened.
- Workflow pauses before mutation and never auto-overwrites infrastructure.
- Profiles are evidence-driven and dependency-neutral.
- Implementation agent does not alter accepted Phase C packages unless reporting a reviewed defect.
