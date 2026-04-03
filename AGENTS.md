# AGENTS.md

Repository instructions for maintaining this Codex skill toolkit.

## Purpose

This repo has two distinct skill layers:

- `skill-base/` contains public skills that get installed into other projects.
- `.agents/skills/` contains maintainer-only skills used to work on this repository itself.

Do not mix these two layers.

## Rules

- Public skills belong in `skill-base/`.
- Maintainer workflows belong in `.agents/skills/`.
- `skill-manager.sh` only manages `skill-base/` contents.
- Use `metadata.json` as the source of truth for public skill versioning.
- Keep `SKILL.md` concise and explicit about trigger conditions.
- Avoid references to company-only processes, internal repositories, or other tool-specific legacy layouts.

## Codex Structure

- `AGENTS.md` is for repo rules and collaboration constraints.
- `.agents/skills/` is for repo-scoped Codex skills.
- `.codex/` is for configuration, not the primary skill directory.

## Validation

- After changing `skill-manager.sh`, run `bash -n skill-manager.sh`.
- Smoke-test installs into a temporary project directory and verify the target is `<project>/.agents/skills/`.
- When updating public skills, ensure `metadata.json.version` and `updated_at` are refreshed appropriately.
