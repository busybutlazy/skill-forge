# Phase 1 - Stabilize the Current Codex Manager

## Goal

先把現有以 Codex 為主的 shell manager 穩定下來，解掉目前最容易踩到的可用性與安全性問題，讓後續 phase 可以在較低風險下進行。

## Decisions Locked In

- 本 phase 不做 GUI，只維持 CLI。
- 本 phase 不重寫成 Python。
- 本 phase 的唯一 target 是現有 Codex 安裝流程，也就是安裝到 `<project>/.agents/skills/`。
- 本 phase 不處理 Claude 相容輸出，只做現有 manager 的穩定化。

## Scope

- 修正 macOS 預設 shell 環境下的可用性問題。
- 移除 manager 啟動時的隱性 side effect。
- 補齊最基本的 skill package 驗證能力。
- 更新 README，讓安裝需求、限制與執行方式講清楚。

## Work Items

1. Runtime compatibility guard
   - 在 `skill-manager.sh` 啟動時檢查 bash major version。
   - 若版本小於 4，直接以清楚訊息退出。
   - README 要新增 macOS 前置需求，明確說明內建 `/bin/bash` 3.2 不可用。

2. Remove implicit repo mutation
   - 拿掉啟動即 `git pull` 的行為。
   - 改成文件說明或未來顯式子命令，不在一般 install flow 自動更新 repo。

3. Add basic validation
   - 增加一個最小 validator 能檢查：
     - skill 資料夾存在
     - `SKILL.md` 與 `metadata.json` 皆存在
     - 資料夾名、metadata `name`、frontmatter `name` 一致
   - install/list 流程遇到不合法 skill 時，要顯示錯誤並跳過，不可靜默安裝壞資料。

4. Improve install safety
   - 安裝與更新時要檢查 copy 是否成功。
   - 不再只顯示 `SKILL.md` diff 就覆蓋整包資料夾。
   - 至少補一個明確提示，告知更新是覆蓋整個 skill package。

5. Documentation refresh
   - README 補齊 shell 版本需求與已知限制。
   - README 說明 manager 目前仍是 Codex-first，Claude 相容屬於後續 phase。

## Acceptance Criteria

- 在 macOS 內建 `/bin/bash` 下執行時，會得到明確錯誤訊息，而不是 bash 語法或內建功能炸掉。
- manager 不會在啟動時自動修改 toolkit repo。
- 壞掉的 skill package 不會被正常列出或安裝。
- README 可以讓新使用者正確理解目前需求與限制。

## Out of Scope

- 非互動式 CLI
- category filter、search、preset、pager
- Claude target output
- Python 重寫
