# Phase 7 - Clarify Enterprise Skill Governance Positioning and Adoption Foundations

## Goal

把這個 repo 從「能管理 canonical skills 的 toolkit」進一步收斂成一個清楚可理解的開源定位：企業可控、可審核、可移植的 AI coding skill 管理基礎設施。

phase 7 的重點不是新增漂亮 UI，而是把產品敘事、信任模型、導入路徑與後續擴充方向講清楚，讓更多開發者與團隊知道這個 repo 解的是什麼問題。

## Why This Phase Exists

phase 1 到 phase 6 已經完成了核心技術骨架：

- `canonical-skills/` 作為唯一 source of truth
- Codex / Claude 雙 target renderer
- validate / render / install / update / remove pipeline
- project-local `skill-manager` wrapper 與 interactive menu

但目前 repo 對外仍偏向「工具實作」，還沒有把以下價值清楚表達出來：

- 為什麼團隊不該讓工程師各自安裝來路不明的 skill
- 為什麼 canonical model 可以降低 vendor lock-in
- 這個 repo 和官方 skills / subagents / marketplace 的差異在哪裡
- 對一般開發者來說，第一個成功體驗應該是什麼

如果這些沒有講清楚，即使功能存在，也不容易被理解、採用或貢獻。

## Decisions Locked In

- phase 7 不把重點放在漂亮 GUI 或完整 web console。
- phase 7 優先改善 README、demo、敘事、治理模型與 adoptability。
- 產品定位偏向 enterprise skill governance / skill supply chain，不是公開 marketplace。
- `canonical-skills/` 仍是唯一公開 source of truth。
- 新 AI target 的支援策略仍以新增 adapter 為主，不回退到多份平行 skill 維護。

## Scope

- 重寫 repo 對外定位與 README 首屏敘事。
- 補齊這個專案和官方平台能力的分工說明。
- 定義更清楚的 trust / governance roadmap。
- 強化「canonical source -> 多 target」的示範與 quickstart。
- 釐清後續 phase 是否需要管理型 UI，但不在本 phase 正式開發。

## Work Items

1. Rewrite the public positioning
   - 把 README 首屏改成先回答：
     - 這個 repo 解什麼問題
     - 適合誰用
     - 為什麼不是另一個 skill marketplace
     - 為什麼 canonical model 對團隊有價值
   - 補一句話定位、短版價值主張與使用情境

2. Explain the governance story
   - 補文件說明：
     - approved skill source
     - version / manifest / package hash 的角色
     - maintainer 與 consumer workflow 的差異
     - 為什麼這能降低第三方 skill 風險
   - 明確區分：
     - 官方平台原生 skills 能力
     - 本 repo 的 canonical governance 層

3. Strengthen adoption materials
   - 補 quickstart，讓新使用者能在短時間內理解：
     - canonical skill 長什麼樣
     - render 到 Codex / Claude 後有何差異
     - 如何在自己的專案中使用
   - 補 demo、流程圖、範例截圖或 asciinema

4. Prepare future governance capabilities
   - 定義下一階段候選能力：
     - private catalog / approved registry
     - signing 或等價 provenance 機制
     - policy enforcement
     - audit trail
     - target capability matrix
   - 先形成設計方向，不要求 phase 7 全部落地

5. Evaluate management UI only as a later layer
   - 文件中明確說明：
     - 目前優先級不在漂亮 UI
     - 若未來做 UI，應先做 catalog / approval / audit 類管理面板
     - CLI / TUI 仍是近期主要操作面

## Acceptance Criteria

- README 首屏能在短時間內讓新讀者理解這不是 skill marketplace，而是 canonical skill governance toolkit。
- repo 文件能清楚說明安全控管與 vendor portability 的價值主張。
- 至少有一份 quickstart 或 demo 能直觀展示 canonical source 與雙 target render。
- 後續 governance 能力有明確 backlog 或設計方向，不再只停留在口頭概念。
- phase 7 完成時，仍不需要正式 web UI 才能讓專案對外成立。

## Out of Scope

- 正式實作 web UI 或 dashboard
- 新增第三種 target 的完整支援
- 完整 RBAC / signing / audit backend
- 商業化包裝或銷售流程
