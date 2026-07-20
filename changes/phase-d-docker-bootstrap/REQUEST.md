# Phase D Request: Docker-First Project Bootstrap

## Problem

The guideline mandates Docker execution, but a new project may lack Dockerfile, Compose, canonical commands, CI, and project-specific agent rules. Missing infrastructure must not become permission to install dependencies or execute project work on the host.

## Goal

Deliver a `bootstrap-project` public skill that creates the minimum approved Docker-first development and CI skeleton before normal implementation.

## In scope

- Read-only stack/repository discovery and a mandatory approval pause.
- Stack-appropriate Dockerfile, Compose, `.dockerignore`, and canonical Make/task entrypoints.
- Containerized format/lint/type/test/build commands or explicitly unavailable placeholders.
- Minimal CI using the same canonical entrypoint.
- `docs/agent-rules.md` and `changes/<change-id>/` artifact templates.
- Container build/smoke/verification evidence.
- Catalog/guideline availability updates and both-target skill smoke tests.

## Out of scope

- Host dependency installation or host project tests.
- Production deployment, Kubernetes, cloud infrastructure, secrets, or IAM.
- Exhaustive framework templates or automatic architecture design.
- Rewriting mature existing container/CI stacks without a separate approved migration.
- Adding application dependencies merely to satisfy bootstrap.

## Non-negotiable constraints

- Dockerization is the standard baseline, not optional.
- Host tools may inspect/write repository text, invoke Git, and invoke Docker; they may not install or execute project dependencies.
- Stop for approval after analysis and before infrastructure writes.
- Existing Docker/Compose/CI files are unmanaged architecture and never overwritten automatically.
- Agents, humans, and CI share one canonical command surface.

## Acceptance criteria

- `bootstrap-project` validates and renders/installs for Codex and Claude with all references.
- Its workflow cannot proceed from analysis to writes without explicit approval.
- It contains no host fallback.
- Python, Node/TypeScript, generic/unknown, and existing-infrastructure cases are explicit and evidence-driven.
- Conflicting existing infrastructure causes refusal/stop rather than overwrite.
- Minimum outputs, verification, rollback, and review hotspots are defined.
- Guideline availability changes only after validation.
