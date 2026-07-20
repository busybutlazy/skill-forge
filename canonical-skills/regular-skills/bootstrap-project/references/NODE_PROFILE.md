# Node and TypeScript Bootstrap Profile

This is decision guidance, not a universal Dockerfile.

## Evidence Required

- Determine Node compatibility from `package.json` engines, runtime files, existing CI, and documentation.
- Select exactly one package manager from lockfile/package-manager evidence:
  - `package-lock.json` → npm
  - `pnpm-lock.yaml` → pnpm
  - `yarn.lock` → Yarn, with version confirmed from project evidence
- Multiple/conflicting lockfiles or missing runtime evidence require a human decision.

## Approved Plan Considerations

- Pin an approved Node base line; do not use mutable `latest`.
- Use the manager's frozen install mode inside the image/container (`npm ci`, an approved frozen pnpm install, or an approved immutable Yarn install).
- Preserve existing scripts as the source for format, lint, typecheck, test, build, and run commands.
- Do not invent scripts, switch package managers, regenerate lockfiles, or add ESLint/Prettier/TypeScript/test dependencies merely to fill the command matrix.
- Document absent scripts as unavailable or request a separately approved dependency/tooling change.
- Consider non-root execution and ownership of bind-mounted/generated files.

## Verification Evidence

Record Compose validation, image build, Node and package-manager versions inside the image, frozen restore result, smallest smoke command, supported scripts, exit codes/counts, cache/mount behavior, and resulting file ownership.

Never install Node packages or execute project Node/TypeScript scripts directly on the host.
