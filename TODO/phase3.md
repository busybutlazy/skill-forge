# Phase 3 - Rebuild the Manager, Validator, and Renderer Pipeline

## Goal

在 phase 1 穩定既有 shell manager、phase 2 定好 canonical package spec 後，把 manager/validator/render 核心重構成更可靠的工具鏈，並正式支援 Codex 與 Claude 雙 target。

## Decisions Locked In

- 本 phase 採用 Python CLI 作為 manager、validator、renderer 的主要實作語言。
- 一般使用者仍然使用 CLI，不需要理解 Python 語法。
- 可以保留 `skill-manager.sh` 作為薄包裝 entrypoint，但核心邏輯不再放在 shell 中。
- `version` 保留做人類可讀版本，完整性檢查改由 package hash 或 manifest 負責。

## Why Python in This Phase

- JSON、frontmatter、manifest parsing 會比 shell 穩定。
- 更容易做可測試的 validator 與 renderer。
- 後續要做 search、filter、non-interactive mode、schema validation 時，維護成本較低。
- 對一般使用者沒有額外語法門檻，因為他們只會使用 CLI 入口。

## Scope

- 建立 Python CLI 核心。
- 導入 canonical package validation。
- 導入 target rendering。
- 導入 package integrity check。
- 讓 install/list/remove/update 都基於新的 render pipeline 運作。

## Planned CLI Responsibilities

新的 CLI 至少支援：

- `validate`
  - 驗證 canonical package 結構、metadata、frontmatter mapping、hash/manifest
- `render`
  - 依 target 輸出 Codex 或 Claude package
- `install`
  - 把 rendered package 安裝到指定專案目錄
- `list`
  - 列出已安裝 package、版本、完整性狀態、是否有更新
- `remove`
  - 移除指定 target 目錄中的已安裝 package

## Integrity Strategy

優先採用 package-level integrity 機制：

- 保留 `version`
- 新增 `package_sha256` 或等價欄位
- hash 範圍至少涵蓋整個 canonical skill package
- 計算時必須有固定排序，避免相同內容算出不同結果

若 phase 3 實作時需要更細的診斷，再擴充為 manifest：

- 每個檔案的相對路徑
- 每個檔案的 sha256
- 必要檔案與可選檔案定義

## Install Status Rules

manager 至少要辨識以下狀態：

- version 不同，表示有可更新版本
- version 相同但 package hash 不同，表示本地內容被修改或 package 不一致
- 缺少必要檔案，表示 package broken
- target package 不屬於當前 source，表示 unmanaged or foreign install

## Acceptance Criteria

- 使用同一份 canonical source，可以 render 並安裝到 Codex 與 Claude 目標路徑。
- CLI 可以明確區分 update、drift、broken 三種狀態。
- 至少有自動化測試覆蓋 validate、render、install、list 的基本情境。
- `skill-manager.sh` 若保留，只作為薄包裝，不再承擔主要邏輯。

## Out of Scope

- GUI
- 雙平台以外的第三種 target
- 在 phase 3 一次完成所有進階 UX 功能
