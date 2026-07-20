# Phase C Implementation Plan: Change Workflow Skills

## Objective and current state

Create five composable public skills that operationalize the guideline without allowing one agent role to plan, implement, verify, review, and approve itself. The guideline names these workflows today, but matching canonical packages and catalog grouping do not exist. The renderer already preserves bundled `references/` for both targets.

## Shared contract

Every skill defines:

1. Trigger and explicit non-trigger cases.
2. Required inputs and missing-input behavior.
3. Read/write/command boundaries.
4. Docker-only execution through existing canonical wrapper/Make/Compose commands.
5. Stop conditions for scope, contract, dependency, data-loss, environment, and unexplained-worktree issues.
6. One owned output or bounded task result.
7. Evidence requirements; no unsupported pass/completion claims.
8. A handoff that stops instead of silently invoking the next workflow.

Shared logic stays in `instruction.md`; target frontmatter differs only for accurate triggering.

## Skill contracts

### C1 — `plan-change`

- Trigger: planning a non-trivial change before implementation.
- Inputs: request, repository rules, specifications/contracts/ADRs, Git state, test baseline.
- Read-only analysis identifies scope, files/symbols, risks, contracts, tests, rollback, and small tasks.
- Owns `changes/<change-id>/IMPLEMENTATION_PLAN.md` using its template.
- Stops for human approval.
- Forbids production edits, installs, migrations, implementation, and inferred approval.

### C2 — `implement-task`

- Trigger: one exact task from an explicitly approved plan.
- Inputs: approved plan/change ID and task identifier.
- Restates boundary, makes minimum edits, updates local tests, runs safe task-local container verification, reports evidence/deviations, then stops.
- Forbids scope expansion, spec rewrite, unapproved dependency/migration changes, next-task execution, and whole-change completion claims.

### C3 — `verify-change`

- Trigger: implementation is ready for evidence-based verification.
- Inputs: acceptance criteria, approved plan, diff, canonical commands.
- Builds requirement→implementation→test traceability; runs existing format/lint/type/unit/integration/contract/E2E/build/security commands only through container entrypoints.
- Records exact commands, exit codes, counts, environment, mocks, omissions, and reasons in `VERIFICATION_REPORT.md`.
- Missing container verification is a blocker pointing to Phase D, never permission for host execution.
- Forbids fixing code while verifying.

### C4 — `report-change`

- Trigger: implementation and verification evidence exist.
- Compares request, approved plan, diff, and verification report.
- Owns `CHANGE_REPORT.md`: completed/not completed/not verified, observable behavior, files, contract/migration/dependency changes, deviations, remaining work, risks, rollback.
- Makes no production-code changes.

### C5 — `review-change`

- Trigger: a completion claim needs adversarial review.
- Reads request, plan, diff, tests, verification, and change reports; tries to disprove correctness, coverage, compatibility, security, and scope claims.
- Owns `REVIEW_REPORT.md` with Blocking/High/Medium/Low/Suggestion findings and evidence.
- Never modifies implementation or approves itself. Same-session reviewers disclose lack of independence and recommend a separate reviewer/human.

## Package layout

All packages use version `0.1.0`, date `2026-07-20`, public distribution, and both target overrides:

```text
canonical-skills/regular-skills/<name>/
├── package.json
├── instruction.md
├── manifest.json
├── targets/{codex.frontmatter.json,claude.frontmatter.json}
└── references/<owned-template-or-checklist>.md
```

References:

- `plan-change/references/IMPLEMENTATION_PLAN_TEMPLATE.md`
- `implement-task/references/TASK_HANDOFF_CHECKLIST.md`
- `verify-change/references/VERIFICATION_REPORT_TEMPLATE.md`
- `report-change/references/CHANGE_REPORT_TEMPLATE.md`
- `review-change/references/REVIEW_REPORT_TEMPLATE.md`

## Catalog and guideline

- Add `Change Workflow` after `Git & Review`, ordered plan→implement→verify→report→review.
- Do not add these to the automatic recommended baseline.
- Split guideline skills into Available and Planned.
- Mark the five Phase C skills Available only after validation; keep `bootstrap-project` Planned until Phase D.
- Bump `agent-guideline` because rendered content changes.

## Delegated implementation sequence

1. Scaffold five packages using `create-skill` conventions.
2. Draft instructions and concise owned references.
3. Update catalog and guideline availability/version.
4. Run `refresh-metadata` and `validate` for every package (`finalize-skill`).
5. Add focused tests only where current coverage does not pin contracts.
6. Render/install all packages into fresh Codex and Claude temporary Git projects; verify references and repeated install.
7. Run the full Docker suite.
8. Produce Phase C `VERIFICATION_REPORT.md` and `CHANGE_REPORT.md`.
9. Stop for reviewer inspection; do not commit or begin Phase D.

## Verification matrix

- Identity, version/date, targets, manifests, and package hashes agree.
- Every reference appears at the same relative path for both targets.
- Catalog/menu grouping loads and trigger descriptions remain distinct.
- Docker-only, stop, forbidden, evidence, and handoff rules are present.
- Fresh installs are `up_to_date`; repeated installs are idempotent.
- Full `skill-forge-dev` suite passes.

## Risks and rollback

- Overlapping triggers: use narrow descriptions/non-trigger sections.
- Monolithic auto-mode: enforce stop boundaries.
- Verbose templates: retain only review-critical fields.
- False independent review: require disclosure.
- Unbootstrapped projects remain non-executable by design; Phase D is the sanctioned path.

Rollback removes the five packages and catalog group, then reverts guideline availability/version. No persistent target, dependency, database, production, or generated local-agent mutation is authorized outside temporary smoke projects.

## Reviewer checkpoints

- Check package boundaries and contradictory ownership.
- Verify no host-execution fallback or implicit auto-chaining.
- Verify metadata and both-target smoke evidence.
- Confirm the implementation agent stopped before Phase D and did not commit.
