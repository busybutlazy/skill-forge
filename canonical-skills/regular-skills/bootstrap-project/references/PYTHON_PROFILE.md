# Python Bootstrap Profile

This is decision guidance, not a universal Dockerfile.

## Evidence Required

- Determine supported Python range from `pyproject.toml`, runtime files, CI, documentation, and dependency metadata.
- Select pip/venv, Poetry, uv, PDM, or another manager only from existing manifest/lock evidence.
- If lockfiles disagree or no compatible Python version is established, stop for a human decision.

## Approved Plan Considerations

- Pin an approved Python base compatible with the declared project range; do not default blindly to the agent's own runtime.
- Restore dependencies inside the image/container and use frozen/locked behavior when the existing manager supports it.
- Keep build-only tooling out of the runtime stage when a runtime image is needed.
- Define the project package/import strategy from existing packaging evidence; do not fabricate a package layout.
- Run formatter, linter, type checker, tests, build, and application only through the canonical container surface.
- If Ruff, Black, mypy, pytest, or build tooling is absent, mark its command unavailable or request a separately approved dependency change. Do not add it merely to complete the matrix.

## Verification Evidence

Record Compose validation, image build, Python version inside the image, dependency restore mode, smallest smoke command, supported canonical checks, exit codes/counts, cache/mount behavior, and resulting file ownership.

Never install Python packages or execute project Python/test commands directly on the host.
