# AGENTS.md

Repository instructions for maintaining skill-forge.

## Purpose

This repo has two distinct skill layers:

- `canonical-skills/` contains public skills and is the only editable public source.
- `.agents/skills/` contains maintainer-only skills used to work on this repository itself.

Do not mix these two layers.

## Rules

- Public skills belong in `canonical-skills/`.
- Maintainer workflows belong in `.agents/skills/`.
- Rendered Codex / Claude artifacts are derived output, not source.
- Use `package.json` and `manifest.json` in each canonical skill as the source of truth for public skill versioning and integrity.
- Keep `instruction.md` concise and explicit about trigger conditions.
- Avoid references to company-only processes, internal repositories, or other tool-specific legacy layouts.

## Codex Structure

- `AGENTS.md` is for repo rules and collaboration constraints.
- `.agents/skills/` is for repo-scoped Codex skills.
- `.codex/` is for configuration, not the primary skill directory.

## Validation

- After changing Python CLI code, run the phase 3 test suite.
- Smoke-test installs into a temporary project directory for both Codex and Claude targets.
- When updating public skills, ensure `package.json.identity.version`, `updated_at`, `manifest.json`, and `package_sha256` stay in sync.
