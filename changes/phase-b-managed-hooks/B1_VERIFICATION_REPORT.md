# Phase B B1 Verification Report

## Scope

Implemented only the deterministic policy engine and its unit tests. No hook adapter, installer, CLI/TUI integration, or target-project file mutation is included.

## Requirement traceability

| Requirement | Implementation | Test | Result |
|---|---|---|---|
| Block destructive Git history/worktree operations | `src/skill_forge/hook_policy.py` | `test_blocks_dangerous_git_commands_in_chains` | Pass |
| Preserve Git dry-run and normal read/write operations | `src/skill_forge/hook_policy.py` | `test_allows_non_destructive_git_commands` | Pass |
| Block broad recursive forced deletion | `src/skill_forge/hook_policy.py` | `test_blocks_broad_recursive_deletes_but_allows_scoped_temp_cleanup` | Pass |
| Protect explicit sensitive project paths from patch writes | `src/skill_forge/hook_policy.py` | `test_blocks_apply_patch_for_protected_paths` | Pass |
| Allow ordinary source and documentation patches | `src/skill_forge/hook_policy.py` | `test_allows_apply_patch_for_normal_source_and_docs` | Pass |
| Fail closed for malformed matched payloads | `src/skill_forge/hook_policy.py` | malformed shell and patch tests | Pass |
| Ignore unsupported tools | `src/skill_forge/hook_policy.py` | `test_unsupported_tools_are_allowed` | Pass |

## Commands executed

```text
PYTHONPATH=src python -m unittest tests.test_hook_policy -v
Exit 0 — 8 tests passed

docker run --rm -e PYTHONPATH=src -v /home/jett/skill-forge:/workspace -w /workspace skill-forge-dev python -m unittest discover -s tests
Exit 0 — 62 tests passed in 62.132s

git diff --check
Exit 0
```

## Implemented rule IDs

- `git.reset-hard`
- `git.clean-force`
- `git.force-push`
- `shell.broad-recursive-delete`
- `shell.malformed`
- `path.protected-write`
- `patch.malformed`

Protected patch paths currently cover `.env`, `.env.*`, `secrets/`, `config/credentials.json`, `.git/`, `.claude/hooks/`, and `.codex/hooks/`.

## Tests not run

- Claude adapter and live Claude hook execution: adapter is not implemented and the B0 account remains rate-limited until reset.
- Windows runtime: no Windows environment is available.
- Target installer lifecycle: B2 has not started.

## Known limitations and review hotspots

- This is a narrow allow-by-default policy, not a complete shell parser or sandbox.
- Dynamic execution through `eval`, `xargs`, generated scripts, aliases, or custom binaries is not classified yet.
- Production-environment and migration rules are intentionally deferred because their safe definitions need project-specific policy and human approval.
- Read operations are not covered by B1; existing Claude permission/sandbox settings remain responsible for secret-read restrictions.
- Symlink behavior must be reviewed again in the final standalone hook runtime, where filesystem context may differ.
- Runtime adapters must map actual target payloads into `HookRequest`; Codex B0 proved that `apply_patch` content arrives in `tool_input.command`.

## Rollback

Delete `src/skill_forge/hook_policy.py` and `tests/test_hook_policy.py`. No target project or persistent configuration was changed by B1.
