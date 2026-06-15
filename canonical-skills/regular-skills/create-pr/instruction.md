# Pull Request Writer

協助使用者把 branch 上的工作整理成 reviewer 看得懂的 Pull Request。

## Operating Principles

- 先理解變更，再寫 PR
- PR body 重點是決策、影響與驗證，不是把 diff 重貼一遍
- 若要執行 `git push` 或 `gh pr create`，必須先取得確認
- 如果缺少 `gh`、登入狀態、或 upstream branch，先處理阻塞點

## Workflow

### 1. Determine the branch pair

先確認：

- source branch
- target branch

如果使用者沒有特別指定，可預設目前 branch 對 `main`。

### 2. Read the change set

優先看 branch 的提交與摘要差異：

- `git log <target>..<source> --oneline`
- `git diff <target>...<source> --stat`

必要時再深入看檔案差異，釐清：

- 這個 PR 的主要目的
- 重要實作決策
- 潛在風險、限制或遷移成本

### 3. Pre-flight severity check

在產生 PR 內容之前，對 diff 做一次快速自我審查，依嚴重度分級：

**P0（擋 PR，必須先修）：**
- 硬編碼的 secret / token / password（直接出現在程式碼中）
- `console.log`、`debugger`、`print("debug")` 等明顯的 debug artifact 留在非 debug 路徑
- 會讓核心功能無法運作的明顯 logic error
- 已知 code-review 報告中未解決的 CRITICAL 或 HIGH 項目（若 `docs/codereview_report/` 有對應 commit 的報告且仍有未打勾的 CRITICAL/HIGH）

**P1（自動帶進 PR Notes，不擋 PR）：**
- 已知的技術債或 TODO，可在此 PR 範圍內接受
- 效能疑慮但不阻塞功能
- 非完整的邊界條件處理（low-risk path）
- code-review 報告中未解決的 MEDIUM 項目

**Cosmetic（忽略，不提）：**
- 風格偏好、命名慣例
- 單行格式差異
- LOW 等級發現

**處理規則：**
- 若有 P0 → 列出具體問題，告知使用者必須先修再建 PR；若使用者明確說要繼續，允許繼續，但在 PR body 中標記「⚠️ 已知 P0 問題尚未修復」
- 若有 P1 → 彙整成條列，自動加入後續 Step 3 的 `## Notes` 區塊
- 若無 P0/P1 → 直接繼續，不需說明

### 4. Draft the PR content

如果專案有 `.github/PULL_REQUEST_TEMPLATE.md`，優先沿用。沒有的話，自行產生簡潔結構，例如：

```markdown
## Summary

## Key Changes

## Validation

## Notes
```

`## Notes` 用於記錄已知限制、後續追蹤事項或遷移注意點；若無則省略。

Title 應該短、明確、可掃描；body 要聚焦在 reviewer 真正需要知道的事。

### 5. Review with the user

把 title 與 body 先給使用者看，允許調整方向、語氣或細節。確認後才進下一步。

每個步驟只問一個問題，不要把多個決策合併在同一則訊息中。

### 6. Confirm post-merge cleanup

內容確認後，獨立詢問使用者：

> PR merge 後是否要刪除 source branch？
>
> 1. Yes — merge 後刪除
> 2. No — 保留 branch

記住使用者的回答，PR 建立後根據選擇提供對應指引。

### 7. Create the PR

若使用者要直接建立 PR，再視情況執行：

- `git push -u origin <source>`，若 branch 尚未推送
- 用 heredoc 傳入 body，避免多行內容在 shell 中斷行或跳脫問題：

```bash
gh pr create --base <target> --head <source> --title "<title>" --body "$(cat <<'EOF'
<body>
EOF
)"
```

如果使用者要求 reviewer，再補 `--reviewer <username>`。

### 8. Post-merge guidance

PR 建立完成後，根據使用者在 Step 6 的選擇提供指引：

**若選擇刪除 branch（在 GitHub merge 後於本地執行）：**

```bash
git checkout <target>
git pull origin <target>
git branch -d <source>
```

使用 `git branch -d`（小寫）——它會在 branch 尚未合併時拒絕刪除，防止意外丟失 commit。
不要使用 `git branch -D`（大寫），它會跳過合併檢查。

若 `-d` 回傳 "not fully merged" 錯誤，先確認 PR 已在 GitHub 上完成 merge，再重試。

**若選擇保留 branch：** 無需額外操作。

不要提供 `gh pr merge` 指令，merge 應由 reviewer 在 GitHub 上操作。

## Quality Bar

- reviewer 應能在幾十秒內理解這個 PR 做了什麼
- 測試方式與已知限制要清楚
- 不要把不確定的推論寫成既定事實
