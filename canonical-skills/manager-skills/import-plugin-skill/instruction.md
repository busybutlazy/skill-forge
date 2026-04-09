# Import Plugin Skill

用來把一個本機 plugin skill 來源先做維護決策審查，再轉成這個 repo 可治理的 canonical draft。

## Use This For

- 讀取一個本機 Codex plugin 目錄，或一個本機單一 skill folder
- 在 plugin 內選定單一 skill 作為匯入來源，或直接使用該單一 skill folder
- 先做 maintainer-oriented LLM review，評估是否值得、是否適合被 canonical 化
- 把安全的 skill 轉成 staged canonical draft
- 在使用者明確同意後，將 draft 提升到 `canonical-skills/regular-skills/` 或 `canonical-skills/manager-skills/`
- 在提升後直接完成 finalize 與 smoke test，並在成功後清理 staging draft

## Do Not Use This For

- 直接從網路下載 plugin repo
- 一次匯入整個 plugin 的所有 skills
- 直接把外部 skill 安裝到 `.agents/` 或 `.claude/`
- 略過 review 直接寫入 `canonical-skills/`
- 在風險未解除時強行 promote

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

### 3. Run the maintainer review first

在產生 canonical draft 前，先做結構化的維護決策審查。`review-report.md` 必須使用繁體中文撰寫，且至少回報：

- 來源摘要
- inspected files
- extracted capabilities
- Skill 類型判定
- Trigger 邊界分析
- Permission model 分析
- Failure mode 分析
- Canonicalization 建議
- Maintenance cost
- 風險表
- final verdict：`allow`、`needs_human_review` 或 `block`
- recommended restrictions or rewrites

Skill 類型必須先從這些類別中選出主分類：

- `task skill`
- `orchestration skill`
- `policy / governance skill`
- `domain adapter`
- `meta-skill`

必要時可再補一行 secondary characterization，例如：

- `policy-governed operations meta-skill`

因為不同類型的 skill，觸發邊界、權限模型與維護標準都不同，不能跳過這一步。

`Trigger 邊界分析` 至少要明列：

- 應觸發
- 不應觸發
- 需先升級審查

`Permission model 分析` 至少要回答：

- 它預設是 read-oriented mindset 還是 act-first mindset
- 哪些操作主要落在 L1 / L2 / L3
- 是否存在 implicit escalation
- approval gate 是弱文字提示，還是流程上真的卡得住

`Failure mode 分析` 至少要回答：

- 最可能怎麼被誤用
- 最糟會造成什麼後果
- 哪些 wording 或 examples 容易導致 agent overreach
- 哪些 examples 可能被誤讀成 blanket permission

`Canonicalization 建議` 至少要回答：

- 是否應拆成兩個 skill
- 是否應抽出共用 policy section
- examples 哪些保留、哪些應降級成 controlled examples、哪些應移除
- name 是否應改得更精準
- trigger text 應如何收窄

`Maintenance cost` 至少要回答：

- `low` / `medium` / `high maintenance`
- 主要維護來源是什麼
- 哪些段落最容易 drift
- 是否需要 regression review checklist

風險表仍應保留結構化欄位，但欄位名稱用繁體中文：

- `風險`
- `證據`
- `嚴重度`
- `影響原因`
- `限制／修正建議`

預設規則：

- 任何未解除的 `medium` 或 `high` 風險都不可 promote
- `allow` 才可繼續產生 staged canonical draft，而且代表這個 skill 在可接受的維護成本下適合納管
- `needs_human_review` 用於 trigger 邊界、權限模型、canonicalization 或維護成本仍未收斂的情況
- `block` 不可產生可安裝的 canonical package，只能留下 review report 與 remediation checklist

不要把 review 只理解成安全檢查。維護不可治理、trigger 過寬、approval gate 太軟、名稱與定位模糊，也都可以成為不 promote 的理由。

高風險訊號包括：

- 隱藏或模糊的 shell execution
- credential 或 token 蒐集
- 網路外傳或不明遠端依賴
- destructive commands
- 不透明 hooks
- 混淆過的 instruction 或 scripts

若有風險或維護治理問題，不要只說「有問題」。要補上具體 remediation 建議，例如：

- 收窄 instruction 權限範圍
- 新增 destructive / production / network 操作前的人工確認
- 禁止 secret 或 credential 蒐集
- 移除危險 examples、scripts、hooks 或把它們隔離到不納管的區域
- 把高風險操作改成只允許產出 plan、checklist 或 dry-run 指令
- 把 production-adjacent examples 明確標成 controlled examples
- 把過度泛化的 trigger text 改成更窄、更可治理的觸發條件

### 4. Stage a canonical draft

只有在 review verdict 為 `allow` 時才繼續建立 staged canonical draft。

先輸出到 staging area，例如：

- `tmp/import-candidates/<source-name>/<skill-name>/`

staged draft 至少包含：

- `review-report.md`
- `package.json`
- `instruction.md`
- `manifest.json`
- `targets/codex.frontmatter.json`
- `targets/claude.frontmatter.json`

必要規則：

- canonical body 只保留 shared instruction
- target-specific wording 放到 target frontmatter
- install paths 仍固定為 `.agents/skills/{name}/` 與 `.claude/skills/{name}/`
- 只有安全且實際被引用的 assets 才可帶入 draft
- 若來源是 `SKILL.md` 單檔格式，先把 frontmatter 與 shared body 分離，再轉成 canonical `instruction.md` 加 target frontmatter
- 無法安全映射的 hooks 或 plugin-specific runtime behavior 必須在 review report 中明講，不可偷偷轉換

如果 verdict 是 `needs_human_review` 或 `block`，可在對應 staging 位置保留 `review-report.md` 與 remediation notes，但不要建立可安裝 package 檔案。

### 5. Review the staged draft before promotion

產出 `review-report.md` 與 staged draft 後，不要立刻問 promote。

先把這些內容交給使用者審查：

- `review-report.md`
- staged `instruction.md`
- target frontmatter
- 被帶入的 examples / references / assets

接著明確詢問使用者：

- 是否接受這份 review 結論
- 是否要先修改 staged draft

如果使用者要修改，先不要 promote。應依照 `update-skill` 的修改原則處理 staged draft，至少可修改：

- trigger description
- 不適用情境
- 流程步驟
- 限制與輸出要求
- target-specific wording
- canonical 名稱、description、examples 保留策略

修改完成後要重新：

- refresh staged draft metadata
- validate staged draft
- 把更新後的 draft 再交回給使用者審查

只有在使用者明確表示 draft 不再需要修改時，才進入 promote 決策。

### 6. Ask whether to promote, and where

若使用者要正式匯入，先再次確認：

- 最終 canonical skill name
- review verdict 仍為 `allow`
- draft 內容已完成人工確認
- 這次要納入哪一層：
  - `canonical-skills/regular-skills/<skill-name>/`
  - `canonical-skills/manager-skills/<skill-name>/`

不要自行推斷目的地。每次 promote 前都要明確詢問 regular 還是 manager。

若使用者未明確同意，保持 draft 留在 staging area，不可自動提升。

如果來源內容與使用者選的 layer 不匹配，要明講，例如：

- maintainer-only workflow 卻想放進 `regular-skills/`
- 一般可分發 skill 卻想放進 `manager-skills/`
- maintenance cost 很高、卻想當成低維護 public skill 直接納管

### 7. Complete the intake flow

在使用者明確同意後，應直接把 intake flow 做完，不要只停在 promote。

步驟：

- 把 staged draft 複製到使用者選定的 canonical layer
- 執行 `refresh-metadata`
- 執行 `validate`
- 至少做一個 Codex target smoke test

smoke test 規則：

- 若採納到 `regular-skills/`，用臨時專案跑 `install <skill-name> --target codex`
- 若採納到 `manager-skills/`，用臨時專案跑 `sync-manager-catalog <skill-name> --target codex`
- 若 smoke test 失敗，要明確列出失敗步驟與錯誤，不可假裝完成

### 8. Clean up staging only after full success

只有在這些步驟全部成功後，才刪除：

- `tmp/import-candidates/<source-name>/<skill-name>/`

完整成功條件：

- promote 成功
- `refresh-metadata` 成功
- `validate` 通過
- smoke test 通過

若其中任一步失敗，保留 staging draft 供排查與重跑。

### 9. Report the final result

收尾時至少回報：

- source name 與最終 canonical skill name
- 採納 layer：`regular-skills` 或 `manager-skills`
- review verdict 與主要維護決策摘要
- 最終 package hash
- validate 結果
- smoke test 結果
- staging draft 是否已清理

如果只是要把 canonical 狀態同步到本 repo 的 agent 目錄，不用這個 skill，改用 `install-manager-skill`。
