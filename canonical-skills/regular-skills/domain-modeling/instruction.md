# Domain Modeling

Use this internal method when a calling workflow must actively clarify or change a project's domain language, boundaries, relationships, or invariants. Merely reading `CONTEXT.md` for existing vocabulary does not require this method.

## Discover the model

- Read the relevant `CONTEXT.md`, `CONTEXT-MAP.md`, ADRs, project documents, and code before proposing definitions.
- Surface overloaded, vague, inconsistent, or contradictory terms immediately.
- Give each important concept a precise canonical name and definition.
- Define relevant entities, relationships, boundaries, ownership, and invariants.
- Test definitions with concrete scenarios and edge cases.
- When the stated model conflicts with documentation or code, present the conflict for resolution rather than silently choosing a side.
- Never promote an unconfirmed inference into the canonical model.

## Maintain the glossary

When a term is confirmed, update the applicable `CONTEXT.md` inline using [CONTEXT-FORMAT.md](./references/CONTEXT-FORMAT.md). If `CONTEXT-MAP.md` exists, use the context it identifies; ask when the correct context is genuinely ambiguous. Create the glossary lazily when the first term is confirmed.

`CONTEXT.md` is canonical glossary and domain context only. It is not a full specification, work log, implementation plan, ADR collection, or scratchpad.

## Record ADRs sparsely

Create or offer an ADR only when all three conditions hold:

1. The decision is hard to reverse or expensive to change.
2. A future maintainer lacking the context would find it surprising.
3. It represents a real trade-off rather than an implementation detail.

Use [ADR-FORMAT.md](./references/ADR-FORMAT.md), and create `docs/adr/` lazily. If any criterion is missing, do not create an ADR.

## Authority

Only update project-definition artifacts permitted by the calling workflow and repository policy. This method never grants production-code authority.

It also never grants dependency, migration, runtime-configuration, deployment, approval, commit, push, or merge authority.

## Completion

Return control when the calling workflow has the confirmed terminology, boundaries, invariants, glossary changes, and any genuinely necessary ADRs it needs. Identify unresolved contradictions explicitly.
