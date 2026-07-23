# Agent Working Agreement

適用於 Claude Code 與 Codex 的共用工作準則。此檔由 skill-forge 管理，請勿直接手改；要調整內容請修改 `canonical-configs/agent-memory/memory.md` 後重新安裝。

## 溝通

- 回覆使用繁體中文；程式碼、識別字、commit message 使用英文。
- 先講結論，再講細節；不確定時直接說不確定。

## Source of Truth

以下文件若存在，以其為準，不要憑記憶或自行推測：

```text
開發流程規範：docs/agent-guideline.md
專案特定規則：docs/agent-rules.md
需求與驗收：docs/SPEC.md
Contract：docs/CONTRACTS.md
技術決策：docs/ADR/
變更紀錄：changes/<change-id>/
```

## 開發流程

非 trivial 的修改必須依序：

1. 唯讀分析現況（不改 code、不裝 dependency）。
2. 產生 implementation plan（含 scope、測試案例、rollback）。
3. 取得人類批准後才實作。
4. 依 Plan 明確批准的 Execution Policy 執行：預設一次一個 Task；只有低／中風險且人類明確批准 `supervised-auto` 時，才能連續執行列出的 auto-approved Tasks。
5. 執行驗證並如實記錄命令與結果。
6. 產生變更報告，揭露完成、未完成與偏差。
7. 接受獨立審查。

依目前 readiness 選擇 lifecycle 入口：

- 有未決選擇的新專案或重大 Change：使用 `grill-with-docs`，不得在 planning 中自行猜測。
- 決策已具備 readiness evidence，但缺正式 Project Definition：使用 `define-project`。
- Greenfield Project Definition 已獲人類批准，但缺工程基線：使用 `bootstrap-project`。
- 已批准一個明確 Roadmap Phase，且 Phase-start Decision Gates 已滿足：使用 `deliver-roadmap-phase`，並指定 Roadmap 路徑與唯一 Phase ID／標題。

不得用「繼續 Roadmap」推定下一階段，也不得一次涵蓋多個 Phase。Project Approval、bootstrap approval、Phase Acceptance 與 Git／release authority 彼此獨立。

完整流程、風險分級與報告格式見 `docs/agent-guideline.md`。

### Stop Conditions（遇到即停止並回報，不得自行決定）

- 規格衝突，或需要修改 Out of Scope 的內容。
- 必須改變已批准的 Contract。
- 必要測試無法執行。
- 可能造成資料遺失或擴大權限。
- 需要新增 production dependency。
- Git 工作區已有無法辨識的修改。
- `supervised-auto` 需要新增 Task／路徑、偏離批准 Plan、觸發人工 checkpoint，或完整驗證失敗。

### Definition of Done（同時符合才能宣稱完成）

- 已批准範圍全部實作，測試已實際執行且通過。
- CI 通過（或如實回報未執行的項目與原因）。
- 變更報告已產生，無未揭露偏差。
- 相關文件已同步，無 blocking review finding。

## 環境與執行（Docker based）

- 一律以 Docker 為執行環境：不要在 host 上 `pip install` 或全域安裝套件。
- 執行 CLI、測試、腳本時，優先使用專案既有的容器化入口（compose service、Makefile、wrapper script）；不要自行發明新的執行方式。
- 若專案沒有現成容器流程，先跟使用者確認再建立，不要直接在 host 執行。

## Python 專案慣例

- 以 `pyproject.toml` 為唯一設定來源：依賴、建置、工具設定（lint/format/test）都收斂在 toml，不新增 `setup.py`、`requirements.txt` 等平行設定檔。
- 修改需與 CI/CD 相容：變更後 pipeline 必須仍能通過；重要邏輯要附上可在 CI 內執行的自動化測試，不要引入只能在本機手動操作的驗證步驟。

## Git 管控

- **每次 commit 前，必須先檢查目前分支**（`git branch --show-current`）。
- **嚴禁在 `main`（或 `master`）分支直接 commit**；若目前在 main 上，先建立或切換到工作分支。
- 檢查分支名稱是否與當前任務相符；若目前的工作是一個獨立任務，先提醒使用者選擇：切換到新分支，或延後這次 commit。
- 未經使用者要求，不要自行 commit 或 push。
- Commit message 使用 Conventional Commits（`feat:` / `fix:` / `docs:` / `chore:` …）。

## 撰寫程式時的說明義務

- 撰寫或修改程式時，向使用者清楚解釋執行邏輯：這段程式在做什麼、為什麼這樣設計、影響範圍在哪裡。
- 重大設計決策（架構、資料流、介面契約）先說明並取得同意，再動手實作。
- 解釋以使用者能複述為標準：避免只貼 code 不說明，也避免堆術語。

## 修改原則

- 優先重用專案既有的函式與模式，避免重複造輪子。
- 先做最小可行的修改（YAGNI），不要順手重構無關的程式碼。
- 不要手改由工具 render 出來的產物（例如 `.claude/skills/`、`.agents/skills/`）。

## 專案特定規則與常用指令

- 本檔只放跨專案通用準則。專案特定規則與常用指令由各專案自行維護，寫在專案根目錄的 `docs/agent-rules.md`。
- 開始工作前，若 `docs/agent-rules.md` 存在，必須先閱讀並遵循；其內容與本檔衝突時，以專案規則優先。
- 不要把專案特定內容直接補寫進本檔 render 出的 `CLAUDE.md` / `AGENTS.md`：該檔由 skill-forge 納管，會被判定為 drift，更新時可能被覆蓋。
