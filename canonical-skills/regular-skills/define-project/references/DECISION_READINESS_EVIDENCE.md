# Decision Readiness Evidence

A `Decision Readiness Summary` with `Status: Ready` is the normal admission evidence.

Existing projects may provide equivalent evidence only when it satisfies the same contract:

- a complete Decision Inventory or canonical reference for the requested scope;
- decision ownership and dependencies;
- resolved decisions and implementation-owned defaults;
- safely deferred decisions with rationale, affected scope, owner, and blocking trigger;
- Blocking Open Decisions;
- conflicts and assumptions;
- confirmation that no Blocking Decision remains.

Equivalent evidence must also pass:

## Scope

It covers the current Project Definition, proposed Walking Skeleton, included Roadmap phases, contracts, and requested outcomes. Uncovered areas are not implicitly ready.

## Freshness

It has been checked against the current repository, specifications, contracts, glossary or context, and ADRs. Superseded decisions and material repository changes invalidate readiness until reconciled.

## Conflict

Contradictions between the user, evidence, code, contracts, or ADRs are resolved or classified as blocking. Silence does not resolve a conflict.

If completeness, scope, freshness, or conflict status cannot be established, admission fails and routes to `grill-with-docs`.
