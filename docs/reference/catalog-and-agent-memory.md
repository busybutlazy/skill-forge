# Display catalog and project guideline

This reference covers three features that live outside the canonical skill packages:

- the display catalog (`canonical-skills/catalog.json`)
- the recommended baseline prompt in the interactive menu
- the project guideline: managed config items rendered into the target project (`CLAUDE.md` / `AGENTS.md` and `docs/agent-guideline.md`)

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

## Project guideline (managed config items)

The project guideline is a set of **managed config items**: tool-neutral canonical sources rendered into the target project, each with its own marker-based drift detection. Every item lives under `canonical-configs/<item-name>/`:

```text
canonical-configs/<item-name>/
├── config.json   # schema_version, version, description, updated_at
└── <body>.md     # shared body, rendered verbatim
```

An item whose canonical source directory is missing is simply unavailable and skipped.

### Items

| Item | Body file | Rendered path (`codex`) | Rendered path (`claude`) |
|------|-----------|-------------------------|--------------------------|
| `agent-memory` | `memory.md` | `AGENTS.md` | `CLAUDE.md` |
| `agent-guideline` | `guideline.md` | `docs/agent-guideline.md` | `docs/agent-guideline.md` |

`agent-memory` holds the short always-applicable rules at the project root; `agent-guideline` holds the full governance guideline under `docs/` (parent directories are created on install).

### Managed marker

Instead of a sidecar metadata file, each rendered file ends with one marker line naming its item:

```html
<!-- skill-forge:agent-memory version=0.1.0 sha256=<hash-of-body> -->
<!-- skill-forge:agent-guideline version=0.1.0 sha256=<hash-of-body> -->
```

The hash covers the canonical body (trailing newlines normalized), so the file is self-describing and drift detection needs no extra state. The `skill-forge:agent-memory` marker format is unchanged from the pre-guideline releases, so already-installed files stay recognized.

### Status model

| Status | Condition |
|--------|-----------|
| not installed | file does not exist |
| `unmanaged` | file exists without a marker — never overwritten, not even with `--force` |
| `drift` | body no longer matches the recorded hash (edits before **or after** the marker), or the canonical source changed without a version bump |
| `update_available` | marker version differs from the canonical version |
| `up_to_date` | version and hash both match |

`drift` requires `--force` plus confirmation to overwrite, mirroring the skill install safety model. Each item applies the model independently.

### Where it appears

- Interactive menu: the **Install / Update project guideline** action on the main menu (right after *Install / Update skills*) lists all available items with multi-select install; *Check installed skill status* shows every item under a **Guideline** section, including not-yet-installed ones. It is never part of the recommended baseline.
- CLI:

```bash
skill-forge guideline status  [--item NAME] --target claude --project /workspace/project [--json]
skill-forge guideline install [--item NAME] --target claude --project /workspace/project [--force] [--yes]
```

By default both commands cover **all** available items; `--item` narrows to one. On install, a refusal on one item (for example an `unmanaged` file) is reported but does not abort the remaining items; the exit code is 1 if any item failed.

`memory status` / `memory install` remain compatibility commands for the `agent-memory` item. They install and classify the same file with the same marker, while preserving the legacy CLI output shape (notably, `memory status --json` emits one object and `guideline status --item agent-memory --json` emits a one-element array).

### Maintainer flow

Edit the item body (for example `canonical-configs/agent-memory/memory.md`), bump `version` (and `updated_at`) in that item's `config.json`, and installed copies report `update_available` on their next status check.
