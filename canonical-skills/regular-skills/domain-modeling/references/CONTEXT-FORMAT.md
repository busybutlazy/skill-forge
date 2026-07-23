# CONTEXT.md Format

Use a short context description followed by a `## Language` glossary. Each entry names one canonical domain term, defines it in one or two sentences, and may list discouraged synonyms under `_Avoid_`.

```md
# {Context Name}

{One or two sentence description.}

## Language

**Order**:
{Precise domain definition.}
_Avoid_: Purchase, transaction
```

Only include project-specific domain concepts. Keep implementation details and general programming vocabulary out. Group terms only when a natural domain cluster exists.

For multiple contexts, `CONTEXT-MAP.md` identifies each context's `CONTEXT.md` and their relationships. Otherwise use the root `CONTEXT.md`.
