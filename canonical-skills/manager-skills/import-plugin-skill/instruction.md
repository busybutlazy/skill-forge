# Import Plugin Skill

用來把一個本機 plugin skill 來源先做風險審查，再轉成這個 repo 可治理的 canonical draft。

## Use This For

- 讀取一個本機 Codex plugin 目錄，或一個本機單一 skill folder
- 在 plugin 內選定單一 skill 作為匯入來源，或直接使用該單一 skill folder
- 先做 LLM review，阻擋有中高風險的內容
- 把安全的 skill 轉成 staged canonical draft
- 在使用者明確同意後，將 draft 提升到 `canonical-skills/regular-skills/`

## Do Not Use This For

- 直接從網路下載 plugin repo
- 一次匯入整個 plugin 的所有 skills
- 直接把外部 skill 安裝到 `.agents/` 或 `.claude/`
- 略過 review 直接寫入 `canonical-skills/`
- 取代 `finalize-skill`

## Workflow

### 1. Confirm the local source

先確認：

- source root path
- 這是本機目錄，不是遠端 URL
- 來源型態是以下兩者之一：
  - Codex plugin directory：存在 `.codex-plugin/plugin.json`
  - single skill folder：目錄根部存在 `SKILL.md`
- 若是 plugin directory，要匯入的 skill 名稱
- 若是 single skill folder，確認它本身就是唯一匯入來源
- 若要轉成不同 canonical 名稱，先確認目標 skill name

如果使用者只有遠端 repo URL，先要求他下載到本機，再繼續。

若來源同時不符合這兩種結構，停止並明講目前不支援該格式。

建議本機來源路徑：

- `tmp/foreign_skills/<source-name>/`

### 2. Inspect the source structure

至少讀：

- 若是 plugin directory：
  - `.codex-plugin/plugin.json`
  - 目標 skill 的 instruction 檔
  - 該 skill 直接引用的 assets、references 或 scripts
- 若是 single skill folder：
  - `SKILL.md`
  - 相鄰的 `agents/*.yaml`、`examples/`、`references/`、`templates/`、`scripts/` 或 `assets/`
  - 該 skill 直接引用的檔案

如果 plugin 內有多個 skills，不要自行整批匯入；必須要求使用者明確指定其中一個。

如果是單一 skill folder，預設只匯入該資料夾代表的這一個 skill，不要往外層遞迴搜尋其他 skill。

### 3. Run the risk review first

在產生 canonical draft 前，先做 structured review，至少回報：

- source summary
- inspected files
- extracted capabilities
- suspicious behaviors
- final verdict：`allow`、`needs_human_review` 或 `block`

預設規則：

- 只要判定為中高風險，就直接 `block`
- 有風險時不要繼續產生可安裝的 canonical package
- `needs_human_review` 可以產出 review report，但不可提升到 `canonical-skills/`

高風險訊號包括：

- 隱藏或模糊的 shell execution
- credential 或 token 蒐集
- 網路外傳或不明遠端依賴
- destructive commands
- 不透明 hooks
- 混淆過的 instruction 或 scripts

### 4. Stage a canonical draft

只有在 review verdict 為 `allow` 時才繼續。

先輸出到 staging area，例如：

- `tmp/import-candidates/<source-name>/<skill-name>/`

staged draft 至少包含：

- `package.json`
- `instruction.md`
- `manifest.json`
- `targets/codex.frontmatter.json`
- `targets/claude.frontmatter.json`
- `review-report.md`

必要規則：

- canonical body 只保留 shared instruction
- target-specific wording 放到 target frontmatter
- install paths 仍固定為 `.agents/skills/{name}/` 與 `.claude/skills/{name}/`
- 只有安全且實際被引用的 assets 才可帶入 draft
- 若來源是 `SKILL.md` 單檔格式，先把 frontmatter 與 shared body 分離，再轉成 canonical `instruction.md` 加 target frontmatter
- 無法安全映射的 hooks 或 plugin-specific runtime behavior 必須在 review report 中明講，不可偷偷轉換

### 5. Promote only with explicit approval

若使用者要正式匯入，再把 staged draft 複製到：

- `canonical-skills/regular-skills/<skill-name>/`

提升前要再次確認：

- 最終 canonical skill name
- review verdict 仍為 `allow`
- draft 內容已完成人工確認

若使用者未明確同意，保持 draft 留在 staging area，不可自動提升。

### 6. Hand off to finalize

成功提升到 `canonical-skills/regular-skills/` 後，下一步應提醒使用者執行 `finalize-skill`。

建議互動收尾：

- 問使用者是否現在就要 finalize 這個 skill
- 若使用者回答 `yes`，立即切換到 `finalize-skill`
- 若使用者回答 `no`，明確提醒之後要執行 `finalize-skill <skill-name>`

如果只是要把 canonical 狀態同步到本 repo 的 agent 目錄，不用這個 skill，改用 `install-manager-skill`。
