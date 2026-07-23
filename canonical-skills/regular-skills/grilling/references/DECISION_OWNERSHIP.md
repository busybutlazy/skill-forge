# Decision Ownership

Classify a choice from evidence and authority, not from how technical it sounds.

## Fact

Use `fact` when repository, environment, existing contract, or authoritative documentation can establish the answer. Investigate it before asking the user.

## User-Owned Decision

Use `user-owned decision` when the answer changes product meaning, externally observable behavior, acceptance, business or domain semantics, risk tolerance, or an authority boundary. A recommendation is not confirmation.

## Implementation-Owned Gate

Classify a choice as `implementation-owned decision` only when all conditions hold:

1. It does not change observable behavior, Externally Observable Contracts, acceptance criteria, security boundaries, authorization semantics, data ownership, or domain invariants.
2. It is reversible within the approved implementation boundary.
3. It requires no new dependency, migration, major architecture choice, or irreversible operation.
4. The calling workflow grants the implementer authority to choose it.

Record the selected default and rationale. If any condition fails, or classification remains uncertain, use `user-owned decision` or `blocking unresolved decision`.

## Intentionally Deferred and Blocking

The calling workflow defines whether a decision may be safely deferred. A decision that fails that gate, lacks an authorized owner, or is required for downstream readiness is `blocking unresolved decision`.
