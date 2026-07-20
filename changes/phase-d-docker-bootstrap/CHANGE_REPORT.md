# Phase D Change Report: Docker-First Project Bootstrap

## Outcome

Delivered the `bootstrap-project` public skill as the sanctioned path from a repository without an approved container workflow to a human-approved Docker-first development and CI baseline. The workflow has no host dependency execution fallback and refuses automatic overwrite of existing infrastructure.

## Completed

- Added canonical `bootstrap-project` package version `0.1.0`, dated 2026-07-20, for Codex and Claude.
- Added read-only discovery, mandatory plan/approval pause, bounded infrastructure creation, container-only verification, reporting, and review handoff.
- Added explicit Python, Node/TypeScript, generic/unknown, and existing-infrastructure paths.
- Added six references for planning, baseline review, stack evidence, project agent rules, and change artifacts.
- Added `Project Bootstrap` catalog group immediately after `Change Workflow`; automatic recommendations are unchanged.
- Moved `bootstrap-project` from Phase D roadmap wording to Available in the guideline and bumped `agent-guideline` from `0.3.0` to `0.4.0`.
- Added focused tests, finalized metadata, validated both target installs, and completed the Docker full suite.

## Files Added

```text
canonical-skills/regular-skills/bootstrap-project/
├── package.json
├── instruction.md
├── manifest.json
├── targets/
│   ├── codex.frontmatter.json
│   └── claude.frontmatter.json
└── references/
    ├── AGENT_RULES_TEMPLATE.md
    ├── BOOTSTRAP_PLAN_TEMPLATE.md
    ├── CHANGE_ARTIFACT_TEMPLATES.md
    ├── DOCKER_BASELINE_CHECKLIST.md
    ├── NODE_PROFILE.md
    └── PYTHON_PROFILE.md
```

- `tests/test_phase_d_bootstrap.py`
- `changes/phase-d-docker-bootstrap/VERIFICATION_REPORT.md`
- This report.

## Files Modified

- `canonical-skills/catalog.json`: added non-recommended `Project Bootstrap` group.
- `canonical-configs/agent-guideline/config.json`: version `0.4.0`.
- `canonical-configs/agent-guideline/guideline.md`: marks bootstrap Available and preserves Docker-only as the sole sanctioned bootstrap path.
- `tests/test_phase_c_workflow.py`: approved narrow delivery-state transition; retains all five Phase C Available assertions and removes only the obsolete Phase D roadmap-literal assertion.

## Files Deleted

- None.

## Observable Behavior

- Codex and Claude users can discover/install `bootstrap-project` with all six references.
- The skill first performs read-only discovery and must stop for explicit human approval before any infrastructure write.
- Missing Docker is a blocker, not permission for host dependency installation or project execution.
- Existing Docker/Compose/task-runner/CI files cause refusal or a separate migration recommendation rather than overwrite.
- Python and Node decisions come from repository/runtime/lock evidence; generic/unknown projects stop for decisions instead of receiving fabricated dependencies.

## Contract, Dependency, Migration, and CI Impact

- Public catalog gains one package and group.
- Managed guideline source version changes from `0.3.0` to `0.4.0`; managed target copies will report an available update normally.
- No skill is added to `recommended`.
- No application/runtime dependency, repository CLI, schema, migration, hook, production CI engine, deployment, cloud, IAM, or secret handling was changed.
- The skill describes target-project CI generation; this repository's own CI files are unchanged.

## Plan Deviations and Unplanned Changes

- No functional deviation from the Phase D plan.
- The first full suite revealed a predictable delivery-state conflict: the accepted Phase C test required the literal “Phase D roadmap; unavailable” after Phase D had made the skill Available. With primary reviewer approval, only that obsolete assertion was replaced; Phase C package sources and all remaining Phase C contracts were untouched. The new Phase D test owns the Available/no-roadmap assertion.

## Not Completed / Not Verified

- No target repository was bootstrapped; references are evidence-driven guidance, not blindly copied Dockerfiles.
- No application feature, production deployment, Kubernetes/cloud/IAM, secret, dependency upgrade, or existing-infrastructure migration was implemented.
- No live model-behavior evaluation was performed.
- No automatic approval, workflow chaining, merge, or release action was introduced.

## Known Risks and Limitations

- The human approval boundary depends on agent compliance plus external controls; the skill cannot itself prove authorization.
- Stack profiles cannot cover every framework and intentionally stop when evidence is insufficient.
- Existing infrastructure adoption may require a separately approved migration and can leave bootstrap incomplete by design.
- A target's initial baseline quality depends on explicit runtime/base/package-manager decisions and independent review.

## Rollback

Remove `canonical-skills/regular-skills/bootstrap-project/` and `tests/test_phase_d_bootstrap.py`, remove the `Project Bootstrap` catalog group, revert the guideline text/config version to the pre-Phase-D state, and restore the historical Phase C roadmap assertion only if bootstrap is again unavailable. No database, dependency, generated repository-local agent artifact, or persistent production state needs rollback.

Target-project bootstrap rollback must use the target's approved Git diff and must never delete pre-existing infrastructure.

## Reviewer Hotspots

- Approval pause occurs before every infrastructure write and material deviation.
- No host project/dependency execution path exists.
- Existing infrastructure is treated as unmanaged and protected.
- Runtime/package-manager selection is evidence-driven and does not invent dependencies.
- Canonical local/CI command parity and explicit unavailable commands.
- Six-reference render/install integrity and package hash.
- No Phase C package source mutation.
