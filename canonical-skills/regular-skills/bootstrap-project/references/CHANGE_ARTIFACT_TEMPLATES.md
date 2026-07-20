# Bootstrap Change Artifact Templates

Create these under `changes/<change-id>/` only after the bootstrap plan's file list is explicitly approved. Preserve any existing artifacts.

## `REQUEST.md`

```markdown
# Request: <change-id>

## Problem and Goal
## In Scope
## Out of Scope
## Acceptance Criteria
## Constraints and Human Decisions
```

## `IMPLEMENTATION_PLAN.md`

Use `BOOTSTRAP_PLAN_TEMPLATE.md`; retain discovery evidence, the exact approved file list, canonical commands, verification, rollback, and approval evidence.

## `VERIFICATION_REPORT.md`

```markdown
# Verification Report: <change-id>

## Result and Environment
## Requirement Traceability
## Docker/Compose Commands and Exit Codes
## Canonical Checks and Counts
## Checks Not Run and Reasons
## Ownership and Git Diff Inspection
## Risks and Review Hotspots
```

## `CHANGE_REPORT.md`

```markdown
# Change Report: <change-id>

## Completed / Not Completed / Not Verified
## Files Added, Modified, Deleted
## Canonical Command and CI Behavior
## Dependency, Contract, and Configuration Impact
## Plan Deviations and Unplanned Changes
## Risks, Remaining Work, and Rollback
```

## `REVIEW_REPORT.md`

```markdown
# Review Report: <change-id>

## Scope and Independence
## Findings: Blocking / High / Medium / Low / Suggestion
## Docker-Only and CI-Parity Assessment
## Unreviewed Areas and Residual Risk
## Human Disposition Required
```

Reports must state evidence and omissions. They do not approve themselves or authorize application implementation.
