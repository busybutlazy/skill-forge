# Project Lifecycle Guide

This guide explains how an end user should select and invoke the project-lifecycle skills. The managed [agent guideline](../../canonical-configs/agent-guideline/guideline.md) remains the governance source of truth.

## Recommended Skill Set

In the catalog, find the `Project Lifecycle` group and install the entrypoints appropriate to the project:

- `grill-with-docs`
- `define-project`
- `bootstrap-project`
- `deliver-roadmap-phase`

The installer automatically includes method and workflow dependencies. Users should invoke the four entrypoints above, not internal methods such as `grilling` or `domain-modeling`.

Reload the Claude or Codex session after installation so the new skills are available.

## Choose the Entry Point

| Current state | Entry point | Expected result |
|---------------|-------------|-----------------|
| Project idea or major change has unresolved choices, including product, domain, contract, security, data, architecture, failure-behavior, operations, or acceptance decisions | `grill-with-docs` | Decision Readiness Summary |
| Decisions are ready but have not been synthesized into an approval-ready project definition | `define-project` | SPEC, conditional CONTRACTS, Roadmap, and Project Approval Packet |
| An approved greenfield Project Definition exists, but development, container, canonical-command, or CI baselines do not | `bootstrap-project` | Approved engineering baseline |
| One exact approved Roadmap Phase has satisfied its Decision Gates | `deliver-roadmap-phase` | Governed delivery evidence for that Phase |
| An existing project needs one clear bounded change | `plan-change` | Change plan and approval request |

Do not start downstream merely because an upstream document exists. Use the relevant approval and readiness evidence: `Status: Ready` with no Blocking Open Decisions for project definition, explicit Human Project Approval for greenfield bootstrap, and satisfied Phase-start Decision Gates for Phase delivery.

## Typical Greenfield Sequence

```text
ambiguous project idea
→ grill-with-docs
→ Decision Readiness Summary
→ define-project
→ Human Project Approval
→ bootstrap-project
→ approved Roadmap Phase
→ deliver-roadmap-phase
→ Human Phase Acceptance
→ commit
→ create-pr
```

`commit` and `create-pr` are separate, explicitly invoked workflows. Project or Phase approval does not authorize Git or release actions.

## Example Prompts

### 1. Resolve project decisions

```text
Use grill-with-docs for this project idea.

Goal: <what the project should achieve>
Users: <known users or actors>
Existing evidence: <documents, repository paths, or constraints>

Inventory unresolved choices, investigate facts from the repository, ask me
one user-owned decision at a time, and finish with a Decision Readiness Summary.
```

The workflow always preserves a required Decision Inventory and reports one status:

- `Ready`: readiness assessment is complete with `Blocking Open Decisions: None`; route to `define-project` or `plan-change`.
- `Stopped With Blocking Decisions`: assessment is complete and named blockers remain.
- `Incomplete — Session Stopped Before Readiness Assessment`: the user stopped or inventory coverage is incomplete.

A deferred decision is valid only when the next artifact and all work authorized before its trigger can proceed without assuming the answer, and its rationale, owner, affected scope, and blocking trigger are recorded.

### 2. Create the Project Definition

```text
Use define-project.

Decision readiness: <summary path>
Context and ADRs: <paths>

Create the approval-ready Project Definition and stop for Human Project Approval.
Do not implement or infer unresolved decisions.
```

Expected artifacts:

- `docs/SPEC.md`
- `docs/CONTRACTS.md` when externally observable contracts exist
- `docs/ROADMAP.md`, including Walking Skeleton and per-Phase Decision Gates
- Project Approval Packet

### 3. Establish the engineering baseline

```text
Use bootstrap-project.

Approved Project Definition: <path>
Approval evidence: <reference>

Discover the repository, propose the Docker-first development and CI baseline,
and stop for the required bootstrap approval before writing it.
```

For an existing repository that only lacks an engineering baseline, `bootstrap-project` may be used independently. It must not invent product, domain, Roadmap, runtime, or toolchain decisions.

### 4. Deliver one Roadmap Phase

```text
Use deliver-roadmap-phase.

Roadmap: docs/ROADMAP.md
Phase: <exact phase ID or heading>
Mode: one-task-at-a-time
```

The Phase must have an approved observable outcome, scope, acceptance criteria, and satisfied Decision Gates required before Phase start. Later gates become explicit human checkpoints: they block the named child Change, dependent work, or Phase completion until resolved. The workflow delivers only that Phase and stops for independent review and Human Phase Acceptance.

## When to Skip Steps

- Skip `grill-with-docs` when repository evidence already establishes all decisions needed by the current definition or change.
- Skip `define-project` for a clear bounded change in an existing approved project; use `plan-change`.
- Use `bootstrap-project` independently when an existing project only needs a governed engineering baseline.
- Do not invoke `deliver-roadmap-phase` for an ambiguous Phase, multiple phases, or a Phase whose start gates remain unresolved.

## 繁體中文摘要

全新專案通常依下列順序進行：

```text
模糊專案想法
→ grill-with-docs
→ Decision Readiness Summary
→ define-project
→ 人類批准 Project Definition
→ bootstrap-project
→ deliver-roadmap-phase
→ 人類驗收 Phase
→ commit
→ create-pr
```

入口依目前狀態選擇，不必無條件從頭執行：

- 有未決策事項：使用 `grill-with-docs`。
- 決策已收斂但缺正式專案文件：使用 `define-project`。
- Project Definition 已批准但缺工程基線：使用 `bootstrap-project`。
- 一個明確 Phase 已批准且 Decision Gates 已滿足：使用 `deliver-roadmap-phase`。
- 既有專案只有明確且有限的 Change：使用 `plan-change`。

`grill-with-docs` 必須保存 Decision Inventory。只有 `Status: Ready` 可以進入 `define-project` 或 `plan-change`；已知 blockers 使用 `Stopped With Blocking Decisions`，尚未完成 inventory 或使用者中途停止則使用 `Incomplete — Session Stopped Before Readiness Assessment`。

每個 workflow 的批准權限彼此獨立。Project Approval 不等於 bootstrap、implementation、Git 或 release 授權；Phase Acceptance 也不會自動觸發 commit 或 create-pr。
