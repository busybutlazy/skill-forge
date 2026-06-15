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

### 3. Draft the PR content

如果專案有 `.github/PULL_REQUEST_TEMPLATE.md`，優先沿用。沒有的話，自行產生簡潔結構，例如：

```markdown
## Summary

## Key Changes

## Validation

## Notes
```

`## Notes` 用於記錄已知限制、後續追蹤事項或遷移注意點；若無則省略。

Title 應該短、明確、可掃描；body 要聚焦在 reviewer 真正需要知道的事。

### 4. Review with the user

把 title 與 body 先給使用者看，允許調整方向、語氣或細節。確認後才進下一步。

### 5. Create the PR

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

### 6. Branch cleanup (optional)

PR 合併後，如果使用者要刪除 source branch，**只使用 `git branch -d`**（小寫）：

```bash
git branch -d <source>
```

`-d` 會在 branch 尚未合併時拒絕刪除，防止意外丟失 commit。
不要使用 `git branch -D`（大寫）——它會跳過合併檢查，提早執行可能靜默丟失未合併的 commit。

若 `-d` 回傳 "not fully merged" 錯誤，先確認 PR 已在 GitHub 上完成 merge，再重試。

## Quality Bar

- reviewer 應能在幾十秒內理解這個 PR 做了什麼
- 測試方式與已知限制要清楚
- 不要把不確定的推論寫成既定事實
