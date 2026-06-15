# Agent-Driven Skill Install Flow

Enables installing and updating skills entirely from within a Claude or Codex session, without leaving the AI environment.

## Problem

The current path requires leaving the AI session to run the interactive TTY menu:

1. Three root causes block agent-driven installs:
   - No non-interactive CLI exit for the "available catalog" (only inside the TTY menu)
   - `skill-manager` wrapper hard-requires a live TTY (`tty: true` in compose + interactive `read`)
   - `maybe_update_repo` can block on a `y/N` prompt and `exec`-restart itself

## Design

The agent *becomes* the menu: it calls `catalog --json`, calls `list --json`, cross-references them, presents a structured multi-select to the user, and then calls `install` per selection. The TTY menu remains for non-AI users.

## Implementation Phases

### Phase 1 — `catalog` CLI subcommand + `--yes` flag

**File:** `src/skill_forge/cli.py`

- Add `catalog` subparser: `--target` (required), `--scope` (default `public` / `all`), `--json`
- Add `run_catalog(args)`: calls `load_all_skills()` with target/scope filter, outputs name/version/description/scope/tags
- Add `--yes` to `install` and `update` subparsers — passes `lambda _: True` as confirm callback, so drift overwrites succeed without stdin when the agent has already obtained user consent
- Wire `catalog` in `main()` dispatch

JSON schema emitted by `catalog --json`:
```json
[{"name": "...", "version": "...", "description": "...", "scope": "...", "tags": [...]}]
```

### Phase 2 — Non-interactive wrapper mode

**Files:** `skill-manager` (sh), `skill-manager.ps1`

**sh wrapper:**
- Detect non-interactive: auto via `[ -t 0 ]` (stdin not TTY), explicit via `--no-interactive` as first arg (consumed/stripped before Docker call)
- `maybe_update_repo`: when non-interactive, skip `y/N` + `exec` restart; emit update notice to stderr only
- `docker compose run`: add `-T` (disables pseudo-TTY, overrides `tty: true` in compose.yaml)

**ps1 wrapper:**
- Detect non-interactive: `[Console]::IsInputRedirected` and/or `--no-interactive` in args (stripped before Docker call)
- Same skip logic for `Update-RepoIfNeeded`
- Pass `-T` to `docker compose run`

Agent stable entry point: `skill-manager --no-interactive catalog --target claude --json`

### Phase 3 — `install-my-skill` canonical skill

**New directory:** `canonical-skills/regular-skills/install-my-skill/`

Files: `package.json`, `instruction.md`, `targets/claude.frontmatter.json`, `targets/codex.frontmatter.json`, `manifest.json`

Scope: `public`, tagged `shared` (automatically included in manager catalog).

`instruction.md` flow:
1. Trigger: user expresses intent to install/update/manage skills
2. Confirm target (codex/claude) and project path
3. Run `catalog --json` → available skills
4. Run `list --json` → installed status
5. Cross-reference → present structured multi-select (name / version / status badge)
6. Per selection: run `install <name> --target X --project Y`; for drift, explain then add `--force --yes`; for unmanaged, refuse and explain
7. Report results; remind user to reload/restart session

### Phase 4 — README

Add "Installing skills from within Claude / Codex" section:
- Trigger phrase and example output
- Bootstrap note: `install-my-skill` itself must be installed once via `skill-manager` (or is included in the default shared catalog)
- Known limit: reload session after install for skills to take effect

### Phase 5 — Tests

- `catalog` subcommand: JSON schema, scope/target filtering, empty result
- Wrapper non-interactive: `--no-interactive` flag strips correctly, no TTY error, no self-exec
- `install-my-skill` package validates (added to `test_all_canonical_skills_validate`)
- `install-my-skill` has `shared` tag (added to shared-tag test)
- Smoke test: `catalog --target claude --json` round-trips against `list --json` status fields

## Constraints

- No hot-reload: skills load at session start; agent must remind user to reload
- No MCP server: CLI + shell-out is sufficient
- TTY menu unchanged: existing `skill-manager` interactive flow still works
- Safety model unchanged: drift/unmanaged rules enforced as before
