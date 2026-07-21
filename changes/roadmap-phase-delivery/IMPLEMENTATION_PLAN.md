# Implementation Plan: Roadmap Phase Delivery Facade

## Scope

1. Add canonical package dependency metadata and dependency-first resolution.
2. Apply dependency expansion consistently to CLI and interactive installs with disclosure.
3. Create and finalize `deliver-roadmap-phase` with one-phase, one-approval, independent-review boundaries.
4. Add catalog/config documentation and contract tests.
5. Validate both target installs and the full Docker test suite.

## Risk and Rollback

- Risk: medium; installer behavior expands only for packages declaring dependencies.
- Existing packages without dependency metadata retain current behavior.
- Rollback removes the dependency field/resolver and the new canonical package.

## Approval

Approved by the user on 2026-07-21 by requesting the Roadmap facade and agreeing that it install its companion workflow skills as a bundle.
