# Phase B Decision Record

## Status

The human approver confirmed these decisions through the phased implementation conversation and explicitly authorized the post-review resolution on 2026-07-17. This record makes those approvals durable outside chat history.

## D1 — Runtime portability

**Decision:** Managed hooks require a `python3` command running Python 3.11 or newer, with no upper version cap. Linux/macOS is the supported Phase B path; Windows launcher behavior is deferred until tested.

**Rationale:** A standard-library Python runner provides deterministic JSON and shell parsing without Docker startup on every hook invocation.

## D2 — Codex enforcement path

**Decision:** Use native project `.codex/hooks.json` as the primary Codex adapter. Git pre-commit fallback is deferred as a separate defense-in-depth change.

**Consequence:** Disabled or untrusted native hooks have no automatic fallback. Status reports explicit project disablement and advises that trust review may be required.

## D3 — Initial blocked rule set

**Decision:** Accept the narrow deterministic rules implemented and tested in Phase B:

- `git reset --hard`;
- forced directory-removing `git clean` without dry-run;
- force push variants;
- recursive forced deletion of broad/protected roots;
- recursive forced deletion containing unresolved glob characters (`*`, `?`, `[`);
- writes to `.env*`, `secrets/`, `config/credentials.json`, `.git/`, and managed hook directories;
- fail-closed handling for malformed matched security requests.

Production-specific commands and migration-history rules remain project-specific and are not generalized by this bundle.

## D4 — Obsolete Claude setting migration

**Decision:** Stop emitting project-local `allowManagedHooksOnly` and automatically remove only that exact obsolete top-level key from existing `.claude/settings.local.json`, with a visible report. Preserve all other content and refuse invalid JSON.

**Rationale:** Claude honors this key only in organization-managed settings; retaining it locally implies protection that is not active.

## D5 — Uninstall scope

**Decision:** Automatic uninstall is deferred. Phase B documents manual removal of only skill-forge-owned matcher handlers and marker-managed runner files.

**Consequence:** A future uninstall command must receive separate approval and prove structural preservation of unrelated user hooks/settings.

## Deferred items accepted

- Git pre-commit fallback.
- Automatic uninstall command.
- Windows `commandWindows` / `py -3` execution support.
- Project-specific production and migration policy.
