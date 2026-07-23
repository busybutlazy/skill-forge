# Decision Inventory Format

The Decision Inventory is a required project or change artifact. Keep it complete enough to resume later and concise enough to audit.

```markdown
# Decision Inventory

## Scope

## Decision Dependency Map

## Decisions

### <Decision ID and title>
- Classification: fact | user-owned | implementation-owned | intentionally deferred | blocking unresolved
- Owner or authority:
- Depends on:
- Affected scope:
- Evidence:
- Current status:
- Resolution or implementation default:
- Rationale:
- Safe-deferral rationale:
- Becomes blocking when:

## Inventory Coverage
- Areas examined:
- Known gaps:
- Last checked against repository and documents:
```

Omit fields that do not apply to a decision, but never omit classification, owner or authority, dependencies, affected scope, evidence, and current status. Implementation-owned entries must record their default and rationale. Deferred entries must record the complete Safe Deferral Gate evidence.

When a session ends before inventory is complete, preserve the partial inventory, list known gaps under `Inventory Coverage`, and do not claim readiness.
