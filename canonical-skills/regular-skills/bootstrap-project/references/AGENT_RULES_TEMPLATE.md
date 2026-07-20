# Project Agent Rules

## Purpose and Source of Truth

- Specification:
- Contracts:
- Architecture/ADRs:
- Change artifacts:

## Docker-Only Execution

Project dependencies and project commands must run through the approved Docker/Compose/canonical task entrypoint. Do not install or run them on the host. Host use is limited to repository text operations, Git, and Docker invocation.

## Canonical Commands

| Purpose | Command | Availability/notes |
|---|---|---|
| Setup | | |
| Format check | | |
| Lint | | |
| Type check | | |
| Unit test | | |
| Integration test | | |
| Full verify | | |
| Build | | |
| Run | | |

## Architecture Boundaries

## Protected Files and Operations

## Change Workflow and Approval Gates

Non-trivial work follows request → read-only plan → human approval → one task → container verification → reports → independent review → human acceptance. Material deviations stop for approval.

## Stop Conditions

- Requirements/contracts conflict or scope must expand.
- Existing unexplained worktree changes overlap the task.
- Docker or a required container entrypoint is unavailable.
- A dependency, migration, secret, production access, destructive action, or protected-file change needs new approval.
- Required verification cannot run.

## Definition of Done

List project-specific implementation, verification, documentation, review, and CI gates. Never claim completion for unrun checks or unresolved blocking findings.
