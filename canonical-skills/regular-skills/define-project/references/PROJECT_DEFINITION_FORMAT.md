# Project Definition Format

## `docs/SPEC.md`

```markdown
# Project Specification

## Problem
## Users and Actors
## Observable Outcomes
## Success Criteria
## In Scope
## Out of Scope
## Domain Invariants
## System Boundaries
## Non-Functional Requirements
## Known Constraints
## Intentionally Deferred Decisions
```

Each deferred decision records:

```markdown
- Decision:
- Why Safe Now:
- Affected Scope:
- Decision Owner:
- Becomes Blocking When:
```

## `docs/CONTRACTS.md`

Create this file only when the project has an Externally Observable Contract, such as an API or event contract, authorization invariant, error contract, data-ownership boundary, or compatibility requirement. Internal implementation details are not contracts.

## `docs/ROADMAP.md`

```markdown
# Roadmap

## Walking Skeleton

## Phase N

### Observable Outcome
### Included Scope
### Acceptance Criteria
### Dependencies
### Decision Gates
### Risks
### Deferred Work
```

Every Decision Gate uses:

```markdown
- Decision:
- Required Before:
- Owner:
- Current Status:
```

`Required Before` names phase start, phase completion, or another explicit
event. A decision deferred in `SPEC.md` must appear in the first Phase whose
scope requires an answer. A non-start gate becomes an explicit execution
checkpoint; dependent work remains blocked until its owner resolves it.
