# Domain Modeling

## Purpose

Internal method for actively changing a project's ubiquitous language, boundaries, relationships, ownership, or invariants. Reading existing vocabulary alone does not invoke this method.

## Method

- Read the relevant `CONTEXT.md`, `CONTEXT-MAP.md`, ADRs, project documents, and code before proposing definitions.
- Surface overloaded, vague, inconsistent, or contradictory terms immediately.
- Give each important concept a precise canonical name and definition.
- Define relevant entities, relationships, boundaries, ownership, and invariants.
- Test definitions with concrete scenarios and edge cases.
- When the stated model conflicts with documentation or code, present the conflict for resolution rather than silently choosing a side.
- Never promote an unconfirmed inference into the canonical model.

### Canonical Glossary

When a term is confirmed, update the applicable `CONTEXT.md` inline using [CONTEXT-FORMAT.md](./references/CONTEXT-FORMAT.md). If `CONTEXT-MAP.md` exists, use the context it identifies; ask when the correct context is genuinely ambiguous. Create the glossary lazily when the first term is confirmed.

`CONTEXT.md` is canonical glossary and domain context only. It is not a full specification, work log, implementation plan, ADR collection, or scratchpad.

### Sparse ADRs

Create or offer an ADR only when all three conditions hold:

1. The decision is hard to reverse or expensive to change.
2. A future maintainer lacking the context would find it surprising.
3. It represents a real trade-off rather than an implementation detail.

Use [ADR-FORMAT.md](./references/ADR-FORMAT.md), and create `docs/adr/` lazily. If any criterion is missing, do not create an ADR.

## Authority Adapter

| Capability | Authority |
|---|---|
| Read context, ADRs, documents, and code | Allowed |
| Update confirmed glossary terms | Allowed when the caller permits |
| Create an ADR meeting all three criteria | Allowed when the caller permits |
| Record an unconfirmed inference as canonical | Denied |
| Modify production code, dependencies, migrations, runtime, or deployment | Denied |
| Approve, commit, push, or merge | Denied |

## Return Contract

Return control when the calling workflow has the confirmed terminology, boundaries, invariants, glossary changes, and any genuinely necessary ADRs it needs. Identify unresolved contradictions explicitly.
