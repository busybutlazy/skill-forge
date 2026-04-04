# Phase 8 - Canonicalize Maintainer Workflows and Improve Maintainer UX

## Goal

把 repo 自己使用的 maintainer workflows 從 `.agents/skills/` 的手工來源，收斂成同樣受 canonical governance 管理的 package，並補上維護者真正可用的 terminal/manual 操作體驗。

phase 8 的重點不是擴大 consumer surface，而是讓 maintainer path 也變成清楚、可驗證、可手動更新的正式流程。

## Why This Phase Exists

phase 7 完成後，consumer workflow 已經相對清楚：

- target project 中用 `skill-manager`
- 透過 menu 安裝、更新、移除 skill
- 用 canonical source 管理 public skill

但 maintainer workflow 仍有幾個缺口：

- repo 自用的 `create-skill`、`update-skill` 還沒有 canonical package
- `.agents/skills/` 仍同時扮演來源與工作目錄，邊界不乾淨
- maintainer 修改 skill 後，缺少統一的 manifest / hash 更新工具
- terminal 版功能存在，但 maintainer 很難快速理解每個命令的適用時機

如果這些問題不補齊，repo 雖然有 public governance story，自己的 maintainer 流程仍然不夠一致。

## Decisions Locked In

- `canonical-skills/` 仍是唯一 canonical source tree。
- 目錄上再明確分成 `regular-skills/` 與 `manager-skills/`。
- canonical package 仍保留 `distribution.scope` 作為第二層防呆。
- `.agents/skills/` 不再被視為來源，只是 rendered Codex artifact。
- maintainer-only skills 預設不出現在 consumer menu / public install path。
- metadata 更新先採手動觸發工具，不做自動 release pipeline。

## Scope

- 將 repo 自用 maintainer skills 整理成 canonical package。
- 新增 CLI 工具以手動更新 manifest / package hash。
- 新增 CLI 工具把 maintainer skills sync 到 repo 本地工作目錄。
- 撰寫 maintainer terminal 操作手冊。
- 對 README / roadmap / package spec 補齊 maintainer workflow 說明。

## Work Items

1. Canonicalize maintainer skills
   - 新增 `canonical-skills/manager-skills/create-skill/`
   - 新增 `canonical-skills/manager-skills/update-skill/`
   - 在 `package.json` 中標示 `distribution.scope: "maintainer"`
   - 保留 `.agents/skills/` 作為 render output，不再當 source

2. Add manual metadata refresh tooling
   - 新增 `skill-toolkit refresh-metadata <skill>`
   - 自動重建 `manifest.json.files`
   - 同步更新 `manifest.json.package_sha256`
   - 同步更新 `package.json.integrity.package_sha256`
   - 視需要更新 `identity.version` 與 `identity.updated_at`

3. Add maintainer sync tooling
   - 新增 `skill-toolkit sync-maintainer --project .`
   - 讓 maintainer 可以手動把 maintainer-only canonical skills render/install 到 repo 本地 `.agents/skills/`
   - 支援 `--force`，用於從舊 unmanaged 內容遷移到受管輸出

4. Document the terminal surface
   - 撰寫完整 maintainer terminal guide
   - 清楚解釋 `skill-manager`、expert terminal、core CLI commands、status model 與 safety rules
   - 區分 consumer 與 maintainer 的使用心智模型

5. Update roadmap and repo story
   - 更新 README 對 maintainer workflow 的描述
   - 更新 canonical package spec，納入 `distribution.scope`
   - 將 phase 8 納入 `ROADMAP.md`

## Acceptance Criteria

- repo 自用 maintainer skills 有 canonical package，可被 validate。
- maintainer 修改 canonical skill 後，可用單一 CLI 命令刷新 manifest/hash。
- maintainer 可用單一 CLI 命令把 maintainer skills sync 回 repo 工作目錄。
- `.agents/skills/` 在文件中明確被描述為 rendered output，不再被描述為 source。
- 至少有一份完整 terminal/manual 文件能說清楚 maintainer 與 consumer 的差異。

## Out of Scope

- GUI 或 dashboard
- signing / audit backend
- 非 maintainer 角色權限系統
- private registry
