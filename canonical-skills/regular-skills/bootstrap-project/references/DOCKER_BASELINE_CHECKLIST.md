# Docker Baseline Checklist

Use this during read-only discovery and plan review. Do not turn unchecked assumptions into generated infrastructure.

## Evidence and Classification

- [ ] Repository rules, specification, contracts, ADRs, and Git status inspected.
- [ ] Runtime files, manifests, lockfiles, and documented commands inventoried.
- [ ] Existing `Dockerfile*`, Compose files, `.dockerignore`, task runners, and CI inventoried.
- [ ] Profile classified as Python, Node/TypeScript, generic/unknown, or existing infrastructure.
- [ ] Ambiguous runtime version, package manager, commands, or ownership raised for human decision.

## Approval Gate

- [ ] Exact proposed file list and files that must remain untouched are explicit.
- [ ] Pinned base image and compatibility evidence are explicit.
- [ ] Dependency/lock strategy and canonical commands are explicit.
- [ ] CI calls the same canonical container entrypoint as local work.
- [ ] Unavailable commands have honest reasons rather than fabricated tools.
- [ ] Risks, verification, rollback, and no-host-execution statement are explicit.
- [ ] A human approved this exact plan before any infrastructure write.

## Minimum Baseline Review

- [ ] Image runs as an appropriate non-root user where feasible.
- [ ] Build context excludes secrets, Git data, caches, dependencies, and build outputs.
- [ ] Runtime/base versions are pinned to an approved stable line; mutable `latest` is avoided.
- [ ] Dependency restore uses existing lock evidence and container-only execution.
- [ ] Compose service, working directory, mounts, environment, and command are minimal and documented.
- [ ] Canonical entrypoints cover or explicitly mark unavailable: setup, format-check, lint, typecheck, test-unit, integration, verify, build, run.
- [ ] CI does not duplicate a divergent tool invocation path.
- [ ] No secret values, production access, deployment, or cloud/IAM configuration is introduced.

## Refusal Conditions

Stop instead of overwriting existing infrastructure, guessing a stack, adding application dependencies, executing project tools on the host, or proceeding when Docker is unavailable. Existing infrastructure changes require a separately approved migration.
