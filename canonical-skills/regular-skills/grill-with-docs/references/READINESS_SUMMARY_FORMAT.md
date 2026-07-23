# Decision Readiness Summary Format

Every completion or stop produces this summary:

```markdown
# Decision Readiness Summary

Status: Ready | Stopped With Blocking Decisions | Incomplete — Session Stopped Before Readiness Assessment

## Decision Inventory Reference

## Resolved Decisions

## Implementation-Owned Defaults

## Intentionally Deferred Decisions

## Blocking Open Decisions

## Conflicts or Assumptions Found

## Updated Artifacts

## Recommended Next Workflow
```

Each deferred decision records:

```markdown
- Decision:
- Why Safe Now:
- Affected Scope:
- Decision Owner:
- Becomes Blocking When:
```

## Status Rules

- `Ready`: inventory and readiness assessment are complete, every deferred decision passes the Safe Deferral Gate, and `Blocking Open Decisions: None`. The final declaration is exactly `Ready for define-project` or `Ready for plan-change`.
- `Stopped With Blocking Decisions`: inventory is sufficiently complete for readiness assessment and at least one blocking decision is identified. Route to `continue grill-with-docs` or `return to human decision owner`.
- `Incomplete — Session Stopped Before Readiness Assessment`: the user stopped, evidence is missing, or inventory coverage is incomplete before readiness could be assessed. List known gaps and route to `continue grill-with-docs`.

Never infer that undiscovered decisions are non-blocking.
