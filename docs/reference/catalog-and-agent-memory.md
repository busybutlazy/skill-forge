# Display catalog and agent memory

This reference covers three features that live outside the canonical skill packages:

- the display catalog (`canonical-skills/catalog.json`)
- the recommended baseline prompt in the interactive menu
- the managed agent memory file (`CLAUDE.md` / `AGENTS.md`)

---

## Display catalog (`canonical-skills/catalog.json`)

Controls how the interactive menu groups, orders, and highlights skills. The file lives next to the canonical buckets but is **not** part of any skill package, so editing it never changes a `package_sha256`.

```json
{
  "schema_version": 1,
  "groups": [
    { "name": "Git & Review", "skills": ["commit", "create-pr", "code-review"] }
  ],
  "recommended": ["install-my-skill", "commit", "create-pr"],
  "highlight_keywords": ["commit", "PR", "review"]
}
```

| Key | Meaning |
|-----|---------|
| `groups` | Ordered display sections. Each entry has a `name` and an ordered `skills` list. |
| `recommended` | Skills pulled into the top `★ Recommended` section (each skill appears only once, even if it also belongs to a group). |
| `highlight_keywords` | Case-insensitive, word-boundary keywords colored inside skill descriptions. |

Rules:

- Skills not listed in any group fall into an `Others` section at the end.
- Catalog entries that do not match an available skill are ignored.
- A missing or invalid `catalog.json` degrades gracefully to a flat, ungrouped list.

The menu shipped via `skill-manager` is the same Python menu (`skill_forge.menu`), so the catalog applies to the Docker CLI/TUI path automatically. Because the runtime image bakes the repo into `/opt/skill-forge`, catalog changes reach end users the same way skill changes do: through a repo update.

---

## Recommended baseline prompt

After the target (`codex` / `claude`) is selected in the interactive menu — including after **Switch target** — the menu checks two baseline items:

- **claude only:** `.claude/settings.local.json` security defaults (missing file or missing keys)
- **both targets:** the `install-my-skill` skill (not installed, or update available)

If anything is missing it asks **one** question:

```
Write recommended baseline (security settings + install-my-skill)? [Y/n]:
```

- Empty input means **yes**.
- Security settings use the existing additive-only init/merge logic.
- `install-my-skill` is installed without `--force`; if the existing install is `unmanaged`, `drift`, or `broken`, the baseline step never overwrites it — it shows a notice and defers to the normal Install / Update flow.
- The non-interactive CLI path is unchanged: `_auto_security_check` still auto-writes security settings for claude commands, and never auto-installs skills.

---

## Agent memory (`CLAUDE.md` / `AGENTS.md`)

A single tool-neutral memory source rendered to the target project root:

```text
canonical-configs/agent-memory/
├── config.json   # schema_version, version, description, updated_at
└── memory.md     # shared body, rendered verbatim
```

Rendered filenames: `CLAUDE.md` for the `claude` target, `AGENTS.md` for `codex`.

### Managed marker

Instead of a sidecar metadata file, the rendered file ends with one marker line:

```html
<!-- skill-forge:agent-memory version=0.1.0 sha256=<hash-of-body> -->
```

The hash covers the canonical body (trailing newlines normalized), so the file is self-describing and drift detection needs no extra state.

### Status model

| Status | Condition |
|--------|-----------|
| not installed | file does not exist |
| `unmanaged` | file exists without a marker — never overwritten, not even with `--force` |
| `drift` | body no longer matches the recorded hash (edits before **or after** the marker), or the canonical source changed without a version bump |
| `update_available` | marker version differs from the canonical version |
| `up_to_date` | version and hash both match |

`drift` requires `--force` plus confirmation to overwrite, mirroring the skill install safety model.

### Where it appears

- Interactive menu: the **Configs** section at the end of *Install / Update skills*, and in *Check installed skill status*. It is never part of the recommended baseline.
- CLI:

```bash
skill-forge memory status  --target claude --project /workspace/project --json
skill-forge memory install --target claude --project /workspace/project [--force] [--yes]
```

### Maintainer flow

Edit `canonical-configs/agent-memory/memory.md`, bump `version` (and `updated_at`) in `config.json`, and installed copies report `update_available` on their next status check.
