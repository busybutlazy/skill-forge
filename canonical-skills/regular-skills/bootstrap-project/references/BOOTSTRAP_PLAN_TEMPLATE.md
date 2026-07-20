# Bootstrap Plan: <change-id>

## Objective and Acceptance Criteria

## Read-Only Discovery Evidence

- Repository/Git state:
- Rules, specs, contracts, and ADRs:
- Runtime indicators and version evidence:
- Manifests and lockfiles:
- Existing Docker/Compose/task-runner/CI files:
- Documented commands and baseline limitations:

## Classification

- Profile: Python / Node-TypeScript / Generic-Unknown / Existing Infrastructure
- Confidence and unresolved questions:

## Git Initialization Decision

- Existing Git repository: Yes / No
- Run `git init`: Yes / No / Not approved
- Approved initial working branch:
- Checkpoint commit authorized: Yes / No
- Exact checkpoint file set and approval evidence:
- Git author identity evidence:

Git initialization, branch naming, staging, and committing are separate decisions. Leave them unperformed unless explicitly approved.

## Proposed Approved Files

| Path | Create/leave unchanged | Purpose and evidence |
|---|---|---|

## Runtime and Dependency Decisions

- Pinned base image and rationale:
- Package manager and lock strategy:
- Dependency changes: **None unless separately approved.**

## Canonical Command Surface

| Command | Container entrypoint | Available? | Evidence/reason |
|---|---|---|---|
| setup | | | |
| format / format-check | | | |
| lint | | | |
| typecheck | | | |
| test-unit | | | |
| test-integration | | | |
| verify | | | |
| build | | | |
| run | | | |

## CI and Local Parity

## Verification Plan

## Risks, Review Hotspots, and Rollback

## Explicit No-Host-Execution Statement

No project dependency will be installed or executed on the host. Agents, humans, and CI will use the same approved container entrypoint.

## Human Approval

- Exact plan approved by:
- Approval evidence/date:
- **Status: Not approved until explicitly completed by a human. Stop before writes.**
