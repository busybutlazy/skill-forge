# Phase B B2 Verification Report

## Scope

Implemented a generic multi-file managed bundle lifecycle. It is not registered as a guideline item and does not yet modify Claude or Codex hook configuration.

## Requirement traceability

| Requirement | Implementation | Test | Result |
|---|---|---|---|
| Validate bundle metadata and contained paths | `src/skill_forge/managed_bundles.py` | unsafe paths, duplicate targets, missing sources | Pass |
| Render per-artifact version/hash markers | `render_bundle_artifact` | both-target lifecycle | Pass |
| Report not-installed, up-to-date, update, drift, unmanaged, and broken bundles | `managed_bundle_status` | lifecycle, version, partial, mode, drift tests | Pass |
| Never overwrite user-owned artifacts | `install_managed_bundle` | unmanaged and symlink tests | Pass |
| Require force plus confirmation for drift | `install_managed_bundle` | drift confirmation test | Pass |
| Repair partial bundles and executable modes | `install_managed_bundle` | partial and mode repair tests | Pass |
| Write artifacts atomically and roll back cross-file failures | `_atomic_write`, `_restore_originals` | simulated second-write failure | Pass |
| Support target-specific paths and modes | bundle artifact specs | Codex/Claude lifecycle test | Pass |

## Commands executed

```text
PYTHONPATH=src python -m unittest tests.test_managed_bundles -v
Exit 0 — 10 tests passed

docker run --rm -e PYTHONPATH=src -v /home/jett/skill-forge:/workspace -w /workspace skill-forge-dev python -m unittest discover -s tests
Exit 0 — 72 tests passed in 61.447s

Existing install + guideline smoke test in fresh Codex and Claude temporary projects
Exit 0 — both targets installed and all guideline items reported up_to_date

git diff --check
Exit 0
```

## Safety properties

- Bundle source and target paths must remain relative and cannot contain `..`.
- Duplicate artifact IDs and duplicate per-target destinations are rejected before installation.
- Symlink targets are classified as unmanaged and never followed or replaced.
- A preflight checks every artifact before any write.
- Every artifact is written through a same-directory temporary file plus `os.replace`.
- If any write fails, prior artifacts are restored to their original bytes and modes.
- Executable artifacts are `0755`; ordinary artifacts are `0644`.

## Tests not run

- Claude/Codex settings merge: B3/B4 scope.
- Real `agent-hooks` canonical bundle: not created in B2.
- Windows filesystem/mode behavior: no Windows environment is available.
- Uninstall: still an approval-gate decision.

## Known limitations and review hotspots

- B2 supports marker-managed text/script artifacts. Structurally merged JSON belongs to target adapters and must use namespaced ownership rather than comment markers.
- Rollback removes newly created files but intentionally leaves harmless empty parent directories.
- POSIX executable-mode status is meaningful on Linux/macOS; Windows activation must be validated through adapter commands rather than mode bits.
- Bundle status currently reports one aggregate state; B5 must expose artifact details so partial or inactive enforcement is not hidden.

## Rollback

Remove `src/skill_forge/managed_bundles.py` and `tests/test_managed_bundles.py`. B2 is not connected to any command or target project.
