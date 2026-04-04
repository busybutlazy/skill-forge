# Phase 6 - Restore Project-Local UX with an Interactive Skill Manager

## Goal

讓一般使用者可以在自己的專案根目錄直接啟動 skill manager，不需要先理解 toolkit repo 路徑、`docker run` 參數或底層 CLI 子命令，並以互動式文字介面完成常見的 install / update / remove / status 檢查。

## Decisions Locked In

- phase 6 建立在 phase 5 的 runtime image 上，不重做 container model。
- 一般使用者主入口不是 `make up`，而是 project-local wrapper script。
- 一般使用者主流程以 interactive menu 為主，不以 shell 指令為主。
- expert terminal 仍保留，但只作為進階入口。
- target project 以啟動時的目前目錄為準，這是 phase 6 的預設模式。

## Scope

- 新增 project-local wrapper script。
- 新增 interactive menu。
- 讓 runtime container 預設進入 menu。
- 把文件改成 end-user 優先。

## Work Items

1. Add project-local wrapper
   - 提供 `skill-manager` wrapper script。
   - 使用者在 target project 根目錄執行時，自動把 `PWD` 掛載成 target project。
   - 自動處理 host user 權限對映。

2. Add interactive menu
   - 啟動後先選 `codex` 或 `claude`。
   - 主畫面至少提供：
     - 檢查已安裝 skill 狀態
     - 安裝 skill
     - 更新 / 修復 skill
     - 移除 skill
     - 切換 target
     - 進入 expert terminal

3. Reuse existing status and safety rules
   - menu 必須直接沿用 phase 3.5 / 3.6 的狀態模型與 install safety 規則。
   - 不可在 menu 中實作另一套獨立判定邏輯。

4. Refocus documentation
   - README 先講一般使用者如何從 target project 啟動 `skill-manager`。
   - `make up` 與 compose 保留給 maintainer / advanced workflow。

## Acceptance Criteria

- 使用者在 target project 根目錄執行 `skill-manager` 後，會直接進入互動式 menu。
- 使用者不需要手動輸入 project path 或 `UID/GID`。
- menu 可正確反映 `up_to_date`、`update_available`、`drift`、`broken`、`unmanaged`。
- menu 觸發的 install / update / remove 與既有 CLI 行為一致。
- runtime container 仍保留 direct CLI 與 expert shell 入口。

## Out of Scope

- GUI
- 第三種 target
- 完整桌面安裝器
- phase 6 內重做 canonical source model
