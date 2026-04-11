# Phase Archive Summary

這份摘要用來保留 `archive/phases/` 的最小必要脈絡，方便在不保留每個 phase 細節文件時，仍能快速理解專案演進。

## Overall Progress

- Phase 1 到 Phase 7 已完成
- Phase 8 仍為目前 maintainer workflow 收斂階段
- 主軸已從單一工具 manager，收斂成 `canonical-skills/` 為唯一 source of truth、可 render 到 Codex 與 Claude 的 `skill-forge`

## Phase Summary

### Phase 1

- 主題：穩定現有 Codex manager
- 產出重點：修正 shell 可用性、移除啟動 side effects、補基本 package 驗證、釐清 README
- 邊界：只處理 Codex，不做 GUI、不做 Python 重寫、不做 Claude

### Phase 2

- 主題：建立中立 canonical source 與 target adapters
- 產出重點：定義 canonical package model、定義 Codex/Claude adapter 契約、完成最小雙 target migration proof
- 代表產物：`docs/reference/canonical-package-spec.md`、`docs/reference/adapter-contract.md`、`docs/reference/drift-policy.md`

### Phase 3

- 主題：重建 manager、validator、renderer pipeline
- 產出重點：改以 Python CLI 為主入口，建立 validate/render/install/list/remove 流程，引入 package integrity 與 install status 規則
- 結果：`canonical-skills/` 成為唯一公開來源，舊 shell-centered model 退場

### Phase 3.5

- 主題：在容器化前補齊 CLI 契約
- 產出重點：補完 `update`、重新定義 install/update/remove safety model、補足狀態判定與測試、讓 README 與 CLI 行為對齊
- 結果：固定 phase 4/5 可依賴的 CLI 行為

### Phase 3.6

- 主題：收緊 install safety，補 phase completion record
- 產出重點：install 不再對既有目標做靜默覆蓋、補各狀態測試、讓 README 與實作重新一致
- 結果：把 phase 3.5 的安全模型落成為可測行為

### Phase 4

- 主題：容器化維護與測試環境
- 產出重點：開發用 Dockerfile、可重現的容器測試流程、容器內可跑 CLI 與 smoke tests
- 邊界：不是最終對外 runtime image

### Phase 5

- 主題：把 `skill-forge` 發布為容器化 CLI
- 產出重點：正式 runtime image、entrypoint、mount/path/permission 規則、容器使用文件
- 結果：可用 `docker run` 執行與本地一致的 CLI

### Phase 6

- 主題：恢復 project-local UX
- 產出重點：`skill-manager` wrapper、interactive menu、runtime 預設進入 menu、end-user 優先文件
- 結果：一般使用者主入口從低階命令改為專案內互動式操作

### Phase 7

- 主題：明確化 enterprise governance 定位與 adoption foundation
- 產出重點：README 首屏敘事、quickstart/demo、governance/trust story、adoption guide、與官方能力的分工說明
- 結果：產品定位收斂為 governance / portability / supply chain，而不是 marketplace

### Phase 8

- 主題：canonicalize maintainer workflows，改善 maintainer UX
- 產出重點：maintainer skills 收斂進 `canonical-skills/manager-skills/`、手動 metadata refresh 工具、repo-local sync 工具、maintainer terminal guide
- 目前狀態：進行中

## Stable Decisions Across Phases

- `canonical-skills/` 是唯一 canonical source tree
- Codex 與 Claude 都是 rendered targets，不是 source
- CLI / TUI 優先，不以 GUI 為近期重點
- 維護者工作流與一般使用者路徑必須分離
- package integrity 與 validation 是核心治理能力

## If You Remove Detailed Phase Files Later

至少建議保留這份摘要與根目錄 `ROADMAP.md`，因為：

- `ROADMAP.md` 保留目前方向與 backlog
- 這份摘要保留歷史 phase 的背景、結果與決策脈絡
