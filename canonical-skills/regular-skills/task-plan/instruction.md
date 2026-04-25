# Task Plan

幫使用者建立、更新、查詢與管理專案任務清單，任務以巢狀階層組織，資料持久化於 `docs/task-plan/task-plan.json`。

## When to Use

- 使用者提到要管理、追蹤或規劃專案任務
- 使用者明確呼叫 `task-plan` 指令
- 使用者想查看目前任務進度或完成狀況
- 在新對話開始時，若使用者提到有進行中的專案，主動確認是否有 `docs/task-plan/task-plan.json`

## Do Not Use

- 管理 Claude Code 自身 session 內的暫存任務（那是內建 TaskCreate 工具的職責）
- 替其他服務（GitHub Issues、Linear、Jira）操作遠端任務
- 對 `docs/task-plan/task-plan.json` 直接讀寫 JSON，**一律透過 script**

## Script Location

Script 安裝在與這份 SKILL.md 相同目錄下的 `scripts/` 子目錄，從 **專案根目錄** 執行。

路徑慣例（依安裝的 target 決定）：

- Claude Code：`./scripts/` 解析為 `.claude/skills/task-plan/scripts/`
- Codex：`./scripts/` 解析為 `.agents/skills/task-plan/scripts/`

### 偵測作業系統

在呼叫 script 前，先執行以下指令判斷環境：

```bash
uname -s 2>/dev/null
```

| 結果 | 環境 | 使用 script |
|------|------|-------------|
| `Linux` 或 `Darwin` | Linux / macOS | `bash <skill-root>/scripts/task-plan.sh <cmd>` |
| 指令失敗或無輸出 | Windows | `powershell -File <skill-root>\scripts\task-plan.ps1 <cmd>` |

`<skill-root>` 替換為對應 target 的安裝路徑（例如 `.claude/skills/task-plan`）。

> **zsh 注意**：不要把完整指令存成字串變數再展開。
> zsh 不做 word splitting，`SCRIPT="bash ..."; $SCRIPT cmd` 會把整個字串當成單一指令名稱而失敗。
> 正確寫法：直接呼叫 `bash <skill-root>/scripts/task-plan.sh <cmd>`，
> 或用 array：`SCRIPT=(bash <skill-root>/scripts/task-plan.sh); "${SCRIPT[@]}" <cmd>`

若 `docs/task-plan/task-plan.json` 不存在，第一次執行 `add` 時會自動建立。

## Task Structure

每個任務節點包含：

| 欄位 | 說明 |
|------|------|
| `id` | 自動產生的 8 碼英數 ID，不可重複 |
| `order` | 點分隔的階層位置，例如 `1`、`1.2`、`1.2.3` |
| `title` | 任務名稱 |
| `description` | 詳細描述或完成目標 |
| `status` | `todo` / `in_progress` / `done` / `blocked` / `skipped` |
| `completion_note` | 完成時記錄的簡述 |
| `created_at` | 建立日期 (ISO 8601) |
| `updated_at` | 最後更新日期 |
| `subtasks` | 子任務陣列（最多 3 層） |

階層最多 **3 層**：`1` → `1.1` → `1.1.1`。

**深度使用原則**：depth 3 只適用於 depth-2 subtask 預計跨越多個 session、或由不同人分工執行的情況。一般情況下保持 depth 2，細節放 `description` 欄位或外部設計 doc，不要為了完整而強行展開到 depth 3。

## Commands

### ls — 列出所有任務

```
task-plan ls
```

輸出：order、id、status symbol、title（依階層縮排）。

---

### add — 新增任務

```
task-plan add -id <order> <title> [description]
```

- `order`：目標位置（點分隔整數，例如 `2.1`）
- `title`：任務名稱
- `description`（選填）：詳細描述

**若目標位置已有任務，不會寫入，會輸出 warning 並建議使用 `check` 或 `update -o` 先移動舊任務。**

若要新增子任務，父節點必須先存在（例如要新增 `1.2`，`1` 必須已建立）。

---

### done — 標記完成

```
task-plan done -id <task_id> [completion_note]
```

把任務標記為 `done` 並寫入完成備註。

---

### check — 查看狀態

```
task-plan check
```

列出所有任務的 order、id、status、title，最後顯示整體完成進度與最後一筆完成任務的備註。

```
task-plan check -id <task_id>
```

顯示單一任務的完整資訊（包含 description、completion_note、時間戳記）。

---

### detail — 更新描述

```
task-plan detail -id <task_id> <description>
```

覆蓋該任務的 description 欄位。

---

### del — 刪除任務

```
task-plan del -id <task_id>
```

刪除該任務及其所有子任務。

---

### update — 修改任務

```
task-plan update -id <task_id> [-o <order>] [-state <status>] [-detail <description>]
```

`-id` 必填，其餘選填可組合使用：

| 旗標 | 說明 |
|------|------|
| `-o <order>` | 移動到新的位置（collision check 同 add） |
| `-state <status>` | 設定 status |
| `-detail <description>` | 更新 description |

---

### help

```
task-plan help
```

顯示完整 usage 說明。

## Workflow

### 1. 確認 script 可執行

在使用任何指令前，確認 script 存在且 Python 3 可用（script 會自行檢查）。

### 2. 接續既有工作（新 session）

在新 session 開始、且使用者提到有進行中的工作時，先執行 `check` 確認當前狀態：

- `in_progress` 的任務是接續起點
- `todo` 中 order 最小的任務是下一步
- 最後一筆 completion_note 提供前次工作的脈絡

`in_progress` 同時是給使用者看的進度標記與 session 間的接續線索；標記 `in_progress` 代表「已開工但未完成」，在完成前不要清掉。

### 3. 操作任務

完全依靠 script 執行 CRUD，不直接讀寫 `docs/task-plan/task-plan.json`。

### 4. 呈現結果

- 每次操作後，根據輸出向使用者摘要結果
- 若 script 回傳 warning（如 position collision），清楚說明問題並提供建議指令

### 5. 階段驗收

當某個頂層任務的所有子任務都完成時，在執行 `done` 標記父任務之前，進行階段驗收：

1. 回顧這個 phase 有哪些計畫外的發現或調整
2. 確認下一個 phase 的任務描述與順序是否仍然適用
3. 若有需要，先用 `update` 或 `detail` 修正後續任務，再執行 `done`

這個步驟讓計畫在每個里程碑有機會修正，而非事後補救。

### 6. 規劃大型任務

當使用者要規劃全新專案時，建議先討論任務切割方式，確認頂層任務後逐層建立，避免事後大量移動 order。

## Quality Bar

- 所有資料異動都透過 script，不直接操作 JSON
- 呼叫 script 時一律從專案根目錄執行
- 在使用 `add` 之前，先用 `ls` 確認當前狀態，避免 position collision
- 任務刪除前提醒使用者，因為會連同子任務一起移除
- **task-plan 管狀態與順序，設計 doc 管理由與決策**：`description` 欄位只記錄「要做什麼」，不重複外部 doc 的內容
- 已有詳細設計 doc 時，task-plan 只維護頂層任務與順序排列，depth-2 的 description 保持簡短；task-plan 作為 checklist，doc 作為 source of truth
