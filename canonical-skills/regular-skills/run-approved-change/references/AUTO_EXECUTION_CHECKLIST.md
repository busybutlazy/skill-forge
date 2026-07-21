# Supervised-Auto Execution Checklist

## Admission

- [ ] Stable change ID and request/acceptance criteria exist.
- [ ] Current plan revision is explicitly marked Approved.
- [ ] Human approval evidence names that revision, low/medium risk, and `supervised-auto`.
- [ ] Auto-approved task IDs, allowed paths, checkpoints, verification, and rollback are explicit.
- [ ] No high/extreme-risk, production, secret, irreversible migration, bulk data, auth/payment/deployment, or privilege operation is included.
- [ ] Git state is attributable and canonical container entrypoints exist.

If any box is false or ambiguous, stop before implementation.

## Task Log Header

```markdown
# Task Log: <change-id>

- Plan revision:
- Approval evidence:
- Risk level:
- Automation mode: supervised-auto
- Auto-approved tasks:
- Approved path scope:
- Baseline Git state and tests:
```

## Per-Task Entry

```markdown
## <task-id> — <bounded outcome>

- Boundary and allowed paths:
- Files changed:
- Tests added/modified:
- Container commands and exit codes:
- Acceptance criteria demonstrated:
- Tests not run and why:
- Deviations: None / <stop and describe>
- Result: Pass / Fail / Incomplete
```

## Continue Decision

Continue only when the current task is Pass, has no deviation, uses only approved paths, and triggers no human checkpoint. In-scope correction of an ordinary implementation mistake is allowed before the task is declared complete; new scope or a new task is not.

## Completion Boundary

- [ ] All auto-approved tasks passed in order.
- [ ] Full verification ran in evidence-only mode.
- [ ] Verification Report accurately records failures, skips, mocks, and uncertainty.
- [ ] Failed/incomplete verification stopped the run without implementation repair.
- [ ] Passing verification is followed by a Change Report.
- [ ] Independent review, acceptance, commit, push, merge, release, and deployment remain unperformed.
