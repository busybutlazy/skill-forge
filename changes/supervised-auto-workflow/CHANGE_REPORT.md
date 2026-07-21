# Change Report: supervised-auto-workflow

## Outcome

Added an explicit supervised-auto workflow for human-approved low/medium-risk plans while preserving the strict one-task-at-a-time path.

## Completed

- Added public `run-approved-change` `0.1.0` with an execution checklist and both target frontmatters.
- Updated `plan-change` to `0.2.0` with risk/mode/path/checkpoint/approval fields.
- Updated agent memory to `0.5.0` and guideline to `0.6.0`.
- Added the skill to Change Workflow after `implement-task`, without adding it to recommended installs.
- Added focused contracts, both-target idempotent install coverage, and full regression verification.

## Not Completed / Not Verified

- No machine-enforced approval state or hook parsing of Markdown was added.
- No live model behavior evaluation was performed.
- Independent review and human acceptance remain outstanding.

## Observable Behavior

- Users can choose strict `implement-task` or explicitly approved `run-approved-change`.
- Supervised-auto executes only listed tasks/paths, records `TASK_LOG.md`, verifies in evidence-only mode, produces reports, and stops before review/commit.

## Contract and Compatibility Impact

- `plan-change` output gains a required Execution Policy and explicit approval revision fields.
- Existing strict workflow remains available and unchanged.
- No hook, dependency, schema, migration, production, deployment, or recommended-baseline change.

## Deviations

- None from the approved design.

## Rollback

Remove the new package/test/catalog entry and revert `plan-change`, memory, guideline, reference documentation, and their versions/hashes.
