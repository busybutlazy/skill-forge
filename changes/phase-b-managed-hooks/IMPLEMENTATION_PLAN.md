# Phase B Implementation Plan: Managed safety hooks

## Status

Implemented through B6 on 2026-07-17. Native Claude/Codex hooks, managed lifecycle, CLI/TUI integration, documentation, and verification are complete. Git pre-commit fallback, automatic uninstall, and Windows support are documented deviations/deferred work requiring human acceptance.

## Goal

Extend the Phase A `guideline` installation flow so target projects can install deterministic safety enforcement for dangerous commands and protected files. Prefer native lifecycle hooks where the target supports them, preserve user-owned configuration, and provide explicit status, drift, and rollback behavior.

## Current state

- `agent-memory` and `agent-guideline` are single-file managed config items with HTML markers.
- Claude security defaults are additively merged into `.claude/settings.local.json` by `security_check.py`.
- The existing security defaults contain `allowManagedHooksOnly`, but current Claude Code documentation says this key is honored only in organization-managed settings. It should not be emitted into project-local settings.
- Claude Code supports project hooks in `.claude/settings.json` and `.claude/settings.local.json`, including blocking `PreToolUse` command hooks.
- Current Codex documentation exposes project lifecycle hooks in `.codex/hooks.json` as well as inline `.codex/config.toml`. Prefer the dedicated JSON file so hook ownership and additive merge do not require a TOML writer. This supersedes the earlier assumption that Codex necessarily needs a Git pre-commit-only fallback, but runtime behavior still needs a local smoke test.
- `Dockerfile.dev` does not install the package; repository commands need `PYTHONPATH=src` unless the package is installed separately.

## In scope

1. A reusable deterministic policy engine that classifies:
   - destructive shell commands;
   - writes to protected files and directories;
   - allowed operations with no false blocking result.
2. Claude `PreToolUse` integration for `Bash`, `Edit`, and `Write`.
3. Codex lifecycle-hook integration if the capability spike confirms a stable project-scoped configuration and command contract.
4. A Git pre-commit fallback for environments where native Codex hooks are unavailable or disabled.
5. Additive config merge: retain unrelated user settings and hooks.
6. Managed script installation with version, hash, drift, unmanaged-file refusal, and explicit force confirmation.
7. CLI/TUI status and install reporting under the existing project-guideline flow.
8. Unit, integration, menu, Docker, and target smoke tests.
9. User and maintainer documentation, including prerequisites and limitations.

## Out of scope

- LLM-, prompt-, or agent-based hooks.
- CI templates, reviewer agents, or Phase C workflow skills.
- Production/cloud policy deployment or organization-managed settings.
- Secret scanning of file contents.
- Automatically deleting or replacing user-owned hooks.
- Claiming that hooks replace sandbox, permissions, CI, or human approval.

## Proposed design

### 1. Separate policy from adapters

Create a pure policy module with structured input and output:

```text
HookRequest(tool_name, command, file_path)
→ HookDecision(allow | deny, rule_id, reason)
```

Adapters translate Claude/Codex hook JSON into this model. The policy must not execute the requested command, resolve secrets, access the network, or depend on an LLM.

Initial rules should be allow-by-default and narrowly block:

- destructive Git operations such as `reset --hard`, `clean -fd`, and force push;
- broad recursive deletion and deletion of repository roots;
- direct operations explicitly targeting production environments;
- writes to `.env*`, credential/secret paths, `.git/`, managed hook files, and migration history unless explicitly approved outside the hook.

Each rule needs a stable ID and table-driven tests. Parsing must account for quoting, command chains, environment assignments, and absolute versus repository-relative paths. Simple substring matching is not acceptable.

### 2. Install a managed hook bundle

The current one-body `ConfigItemSpec` is insufficient for scripts plus target configuration. Introduce a managed bundle abstraction rather than overloading Markdown rendering:

```text
canonical-configs/agent-hooks/
├── config.json
├── policy.json
├── hooks/
│   └── safety_check.py
└── adapters/
    ├── claude-settings.fragment.json
    └── codex-hooks.fragment.json
```

Bundle metadata records every rendered file and its hash. Script markers use language-appropriate comments. JSON/TOML configuration is merged structurally and tracked by a namespaced hook identity instead of appending comments that could invalidate syntax.

### 3. Claude adapter

- Install the shareable hook entry into `.claude/settings.json`, not the personal `.claude/settings.local.json`.
- Add only skill-forge-owned matcher groups/handlers; preserve unrelated keys and hooks.
- Use a stable command path rooted at the project.
- Remove `allowManagedHooksOnly` from new project-local security defaults. For an existing generated local file, report the obsolete key; do not silently delete it without an explicit migration decision.
- Treat a conflicting hook with the same skill-forge identity as drift; treat unrelated hooks as user-owned and preserve them.

### 4. Codex adapter and fallback

Start with a capability spike against the minimum supported Codex version:

1. Verify trusted-project loading of `.codex/hooks.json`.
2. Capture the actual `PreToolUse` stdin and decision-output contract.
3. Verify relative/absolute script paths, Windows override support, and behavior when hooks are disabled.
4. Verify additive JSON merge and trust-review behavior.

If all checks pass, install a native Codex `PreToolUse` adapter. If any required behavior is unstable, install only the documented Git pre-commit fallback and clearly report that it protects commits but cannot block every tool invocation.

### 5. Runtime portability decision

Recommended first implementation: a Python-standard-library policy runner with an explicit `python3` runtime preflight. This offers reliable JSON and shell parsing but introduces a target prerequisite. Before implementation, the human approver must choose one:

- require Python 3.11+ for managed hooks;
- ship separate POSIX shell and PowerShell implementations;
- narrow Phase B to Linux/macOS and schedule Windows support separately.

Do not hide this dependency behind Docker on every hook invocation because startup latency would apply to every matched tool call.

## Task breakdown

### B0. Capability and contract tests

- Record supported Claude Code and Codex versions.
- Build minimal no-op hooks for both targets in temporary projects.
- Capture input/output fixtures and path behavior.
- Decide runtime portability and native Codex versus Git fallback.
- Update this plan with the approved contracts before production implementation.

### B1. Policy engine

- Define request/decision models and stable rule IDs.
- Implement command and path normalization.
- Add table-driven allow/deny tests, including bypass attempts and false-positive controls.

### B2. Managed bundle lifecycle

- Add bundle source loading, validation, status, install, update, and rollback-safe writes.
- Implement comment-style markers for scripts and structural ownership for JSON/TOML fragments.
- Preserve the Phase A unmanaged/drift safety contract.

### B3. Claude integration

- Add additive `.claude/settings.json` hook merge.
- Add obsolete-local-security-key reporting/migration behavior.
- Test existing settings, existing unrelated hooks, invalid JSON, drift, and repeated installs.

### B4. Codex integration

- Implement the approved native-hook or Git fallback design from B0.
- Test trusted/untrusted project behavior and clearly report inactive enforcement.

### B5. CLI and TUI

- Expose `agent-hooks` in guideline status/install.
- Present per-artifact failures without aborting unrelated guideline items.
- Require confirmation for drift and configuration migrations.

### B6. Documentation and verification

- Update README and guideline reference in English and Traditional Chinese.
- Run the full suite in `skill-forge-dev`.
- Smoke-test clean install, repeated install, drift, unmanaged files, additive merge, actual blocking, allowed commands, and uninstall/rollback for both targets.

## Test cases

### Policy unit tests

- Block each named dangerous operation with its rule ID.
- Block protected paths through relative paths, absolute paths, `..`, quoting, and command chains.
- Allow benign `rm` in an isolated temporary directory, normal Git reads, source edits, tests, and builds.
- Fail closed only when a matched security request is malformed; ordinary unsupported tools pass through.

### Installation tests

- Clean target receives scripts and target configuration.
- Reinstall is idempotent.
- Existing unrelated hooks/settings survive byte-for-byte where practical and semantically otherwise.
- Invalid JSON/TOML is refused without partial writes.
- User-owned files are never overwritten, including with `--force`.
- Managed drift requires force plus confirmation.
- A failure in one bundle artifact does not corrupt or prevent status reporting for other guideline items.

### End-to-end tests

- Claude and Codex deny a dangerous command before execution.
- Claude and Codex deny writes to protected paths.
- Allowed commands and writes execute normally.
- Git fallback blocks a protected staged change and allows a safe commit.
- Windows behavior matches the approved portability scope.

## Risks and mitigations

- **False positives lock out normal work:** narrow rules, stable reasons, allow-case tests, documented manual recovery.
- **Bypass through shell syntax:** parse normalized command structure and test chains/quoting; do not rely on substring matching.
- **Config corruption:** parse before mutation, write to a temporary sibling, validate, then atomically replace.
- **User hook loss:** merge only namespaced entries and test preservation.
- **Hook API drift:** pin a tested minimum version and keep captured fixtures.
- **Runtime missing:** preflight before installation and report inactive hooks as broken, not up-to-date.
- **Git hooks are incomplete enforcement:** label fallback capability honestly and retain sandbox/CI guidance.

## Rollback

- Remove only skill-forge-owned matcher groups and managed scripts.
- Restore the previous configuration from an atomic backup if validation fails during installation.
- Never remove unrelated user hooks or settings.
- Keep a documented manual removal procedure when the CLI cannot run.

## Approval gates

Human approval is required after B0 for:

1. runtime portability choice;
2. native Codex hook versus Git fallback;
3. exact blocked command and protected-path policy;
4. migration behavior for the obsolete `allowManagedHooksOnly` local setting;
5. whether uninstall is included in Phase B or deferred.

No B1-B6 implementation should begin until these decisions are approved.

## B0 progress (2026-07-17)

See `CAPABILITY_REPORT.md`. Official contracts plus Claude Bash/`Edit`/`Write` and Codex Bash/`apply_patch` runtime behavior are verified in temporary projects. Windows portability remains open.

## B1 progress (2026-07-17)

The platform-neutral policy engine and table-driven tests are implemented. See `B1_VERIFICATION_REPORT.md`. B2-B6 remain gated on the runtime/platform and migration decisions in this plan.

## B2 progress (2026-07-17)

The generic multi-file managed bundle lifecycle is implemented and tested. See `B2_VERIFICATION_REPORT.md`. Guideline registry integration remains B5 scope; B3 now consumes the lifecycle through the Claude adapter.

## B3 progress (2026-07-17)

The Claude adapter, Python >=3.11 preflight, obsolete-setting migration, canonical runner, and live Bash/Edit/Write enforcement are implemented and verified. See `B3_VERIFICATION_REPORT.md`. Windows support remains pending; B4-B6 are not started.

## B4 progress (2026-07-17)

The native Codex `.codex/hooks.json` adapter is implemented and verified against Codex 0.144.5. It preserves unrelated hooks, reports project-level `hooks = false` as inactive, exposes the trust-review requirement, and blocks dangerous commands through the installed canonical runner. See `B4_VERIFICATION_REPORT.md`. The Git pre-commit fallback remains deferred as defense in depth; B5-B6 are not started.

## B5 progress (2026-07-17)

The `agent-hooks` bundle is exposed as a first-class guideline item in CLI status/install and the interactive guideline menu for both Codex and Claude. JSON status includes per-artifact state, text status preserves the existing one-line-per-item contract, and item-level failures do not abort unrelated guideline installs. See `B5_VERIFICATION_REPORT.md`. B6 documentation/final verification remains.

## B6 progress (2026-07-17)

English and Traditional Chinese user/maintainer documentation, canonical target guidance, the final automated matrix, fresh/repeated Codex and Claude smoke installs, and Phase B change/review/verification reports are complete. See `B6_VERIFICATION_REPORT.md`, `CHANGE_REPORT.md`, and `REVIEW_REPORT.md`. The documented deferred items remain outside the delivered native-hook path.
