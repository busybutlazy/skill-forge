# Change Report: Roadmap Phase Delivery Facade

## Completed

- Added `deliver-roadmap-phase` as the primary user-facing Roadmap workflow.
- Added optional canonical `dependencies.skills` metadata and dependency-first cycle-safe resolution.
- CLI and TUI disclose and install required skills before the requested facade.
- Kept the six Change Workflow skills independently installable and usable.
- Updated catalog, managed guideline/memory, package specification, README, and tests.

## Observable Behavior

Selecting or installing `deliver-roadmap-phase` installs `plan-change`, `implement-task`, `run-approved-change`, `verify-change`, `report-change`, and `review-change`, then the facade itself. Packages without dependencies behave as before.

## Not Included

- Dependency-aware `update` or `remove`; dependency expansion applies to installation only.
- Automatic Roadmap status mutation, Git actions, release, deployment, or self-review.

## Risks and Rollback

- A dependency with drift/unmanaged state retains the existing per-skill safety refusal and may leave earlier bundle members installed before stopping; installation is ordered but not transactional.
- Rollback removes the new facade/dependency field and resolver, restoring one-package installation behavior.
