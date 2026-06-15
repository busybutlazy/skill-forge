# Import Plugin Skill

用來把一個本機 plugin skill 來源先做維護決策審查，再經過 `skillkeeper`、`imitator`、`reviewer` 與 `skill-review-packet` 的流程，轉成可治理的 canonical draft。

## Use This For

- 讀取一個本機 Codex plugin 目錄，或一個本機單一 skill folder
- 在 plugin 內選定單一 skill 作為匯入來源，或直接使用該單一 skill folder
- 先做前置準入審查，判斷這個 skill 是否值得 canonicalize
- 在值得匯入時，以高保真方式產生 staged canonical draft
- 用功能保真 reviewer 驗證 draft 是否把 skill 改壞
- 在人工審核前，用標準化 review packet 整理整個 intake 結論

## Do Not Use This For

- 直接從網路下載 plugin repo
- 一次匯入整個 plugin 的所有 skills
- 直接把外部 skill 安裝到 `.agents/` 或 `.claude/`
- 略過 `skillkeeper` 直接進入改寫
- 略過 `reviewer` 直接 promote draft
- 把 `skill-review-packet` 當成新的准入判斷者

## Roles

### `skillkeeper`

負責兩次決策：

- 初次準入：判斷這個 skill 是否值得花 token canonicalize
- 最終準入：在 reviewer 通過後，確認 final draft 仍值得納管

固定 prompt 位置：

- `./references/agent-prompts/skillkeeper-initial.prompt.md`
- `./references/agent-prompts/skillkeeper-final.prompt.md`

### `imitator`

負責依據 `source-inventory.md` 高保真改寫 staged canonical draft。

固定 prompt 位置：

- `./references/agent-prompts/imitator.prompt.md`

### `reviewer`

負責拿原始 source、`source-inventory.md` 與 staged draft 做功能對照，找出功能流失、引用斷點與使用時機遺失。

固定 prompt 位置：

- `./references/agent-prompts/reviewer.prompt.md`

### `skill-review-packet`

負責把 `skillkeeper`、`reviewer`、`change-request.md` 等結果整理成給人工審核的標準化資料包；它不負責新增政策判斷。

`skill-review-packet` 自己是可重用 skill，不是這裡的 agent prompt 檔之一。

## Fixed Prompt Files

agent prompt 不應直接內嵌在 `instruction.md`。

這個 skill 固定使用以下可人工編輯的 prompt 檔：

- `./references/agent-prompts/skillkeeper-initial.prompt.md`
- `./references/agent-prompts/skillkeeper-final.prompt.md`
- `./references/agent-prompts/imitator.prompt.md`
- `./references/agent-prompts/reviewer.prompt.md`

這些檔案屬於 canonical reference material，Codex 與 Claude 都應投影到各自的 skill 目錄中相同的相對位置。

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

### 2. Inspect the source structure

至少讀：

- 若是 plugin directory：
  - `.codex-plugin/plugin.json`
  - 目標 skill 的 instruction 檔
  - 該 skill 直接引用的 assets、references、templates 或 scripts
- 若是 single skill folder：
  - `SKILL.md`
  - 相鄰的 `agents/*.yaml`、`examples/`、`references/`、`templates/`、`scripts/` 或 `assets/`
  - 該 skill 直接引用的檔案

必須整理來源中的顯式線索，例如：

- 核心 capabilities
- trigger points
- do-not-use boundaries
- output contract
- 何時要查看 `examples/`
- 何時要套用 `templates/`
- 何時要查 `references/`
- 哪些 `scripts/` 或 `assets/` 是流程的一部分

如果 plugin 內有多個 skills，不要自行整批匯入；必須要求使用者明確指定其中一個。

### 3. Run `skillkeeper` initial screening

在任何改寫之前，先做一次前置準入審查。這一步的目標是避免把 token 花在：

- 高風險且不適合納管的 skill
- 維護成本過高的 skill
- 對 repo 幫助不大、沒有必要 canonicalize 的 skill

執行時應使用：

- `./references/agent-prompts/skillkeeper-initial.prompt.md`

`skillkeeper` 初次審查至少要輸出：

- `skillkeeper-initial.md`
- `source-inventory.md`

`skillkeeper-initial.md` 必須使用繁體中文，至少包含：

- 來源摘要
- source utility / 為什麼值得或不值得納管
- 風險摘要
- 維護成本
- canonicalization constraints
- must-preserve list
- removable-only-if-justified list
- verdict：`allow`、`needs_human_review` 或 `block`

`source-inventory.md` 必須至少包含：

- capability list
- trigger list
- do-not-use boundaries
- explicit support-file references
- when to consult those support files
- important workflow order / section structure
- output contract
- external dependencies
- permission-sensitive behaviors

預設規則：

- verdict 是 `block` 或 `needs_human_review` 時，不可啟動 `imitator`
- 只有 verdict 是 `allow` 時，才能建立 staged canonical draft

### 4. Run `imitator` to stage the canonical draft

只有在 `skillkeeper` verdict 為 `allow` 時才繼續。

執行時應使用：

- `./references/agent-prompts/imitator.prompt.md`

先輸出到 staging area，例如：

- `tmp/import-candidates/<source-name>/<skill-name>/`

staged draft 至少包含：

- `skillkeeper-initial.md`
- `source-inventory.md`
- `package.json`
- `instruction.md`
- `manifest.json`
- `targets/codex.frontmatter.json`
- `targets/claude.frontmatter.json`

必要規則：

- `source-inventory.md` 是 binding contract，不是可有可無的參考
- canonical body 應盡量保留來源 skill 的共享 instruction 結構與能力線索
- target-specific wording 放到 target frontmatter
- install paths 仍固定為 `.agents/skills/{name}/` 與 `.claude/skills/{name}/`
- 來源 instruction 只要顯式提到 `examples/`、`templates/`、`references/`、`scripts/` 或 `assets/`，就必須：
  - 帶入該檔案或資料夾
  - 或在 canonical instruction 中補上等價且明確的引用方式
  - 或在後續審查中被明講為安全導向的刻意刪減
- 若來源有明確的 template / example 使用時機，canonical draft 也必須保留「何時要去看這些檔案」的指引
- 不可默默刪除功能、引用、workflow cues 或 output contract

### 5. Run `reviewer`

`reviewer` 不是只看 diff，而是必須拿：

- 原始 source
- `source-inventory.md`
- 最新 staged canonical draft

做功能對照。

執行時應使用：

- `./references/agent-prompts/reviewer.prompt.md`

`reviewer` 必須產出 `reviewer-report.md`，至少包含：

- preserved behaviors
- remapped behaviors
- dropped behaviors
- source-only behaviors
- canonical-only behaviors
- missing reference hooks
- missing invocation cues
- safety-regression warnings
- verdict：`pass` 或 `revise`
- required fixes for next round

預設規則：

- reviewer 主要檢查功能保真
- 若看到明顯新增安全退化，必須標記，但不取代 `skillkeeper` 的最終判斷
- 只要發現未明講且未被接受的功能差異，預設判 `revise`
- 顯式引用的 `examples/`、`templates/`、`references/`、`scripts/`、`assets/` 若在 canonical 中遺失或失去使用時機說明，預設判 `revise`

### 6. Control the `imitator -> reviewer` loop

初次 candidate 階段允許 `imitator -> reviewer` 來回最多 3 次。

規則：

- reviewer 判 `revise` 時，必須回到 `imitator`
- reviewer 判 `pass` 時，才可進入最終準入
- 若同一階段連續 3 次仍未通過 reviewer，停止自動往返，改交人工審查

### 7. Run `skillkeeper` final admission

當 `reviewer` 通過後，`skillkeeper` 必須再次審查 final draft，而不是直接沿用第一次 verdict。

執行時應使用：

- `./references/agent-prompts/skillkeeper-final.prompt.md`

這次要回答的是：

- 經過改寫後，這個 skill 是否仍值得納管
- 是否有未解除的高風險治理問題
- reviewer 容許通過的功能差異是否可接受

`skillkeeper` 最終審查要產出 `skillkeeper-final.md`，至少包含：

- final utility judgment
- remaining risks
- accepted tradeoffs
- unresolved concerns requiring human attention
- verdict：`admit`、`needs_human_review` 或 `reject`

### 8. Generate the human review packet

在交給人工之前，必須呼叫 `skill-review-packet`，輸出：

- `skill-review-packet.md`

這份 packet 要整理：

- source overview
- `skillkeeper` 初次準入結果
- `reviewer` 的功能保真結論
- `skillkeeper` 最終準入結果
- preserved / narrowed / dropped 區塊
- unresolved risks
- 需要人工決定的點

review packet 與相關 review artifacts 在 promote 後不應留在 public canonical skill 目錄中。若流程成功完成，應把 review trail 保留到 repo 內的固定 maintainer 路徑，例如：

- `reviews/<skill-name>/skillkeeper-initial.md`
- `reviews/<skill-name>/source-inventory.md`
- `reviews/<skill-name>/reviewer-report.md`
- `reviews/<skill-name>/skillkeeper-final.md`
- `reviews/<skill-name>/skill-review-packet.md`

若有 revision，也一併保留：

- `reviews/<skill-name>/change-request.md`
- `reviews/<skill-name>/draft-review.md`

### 9. Handle human feedback

若使用者要修改 staged draft，先不要 promote。

在 importer 動手修改前，先整理成 `change-request.md`。至少包含：

- 修改目標
- 不可改動的部分
- 預期要收窄、保留或移除的方向
- 哪些 capabilities / references / templates / examples 必須保留或等價映射
- 哪些 wording 必須保留
- 完成條件

接著進入新的 revision phase：

- `imitator`
- `reviewer`
- 最多 3 次 loop
- `skillkeeper` final admission
- `skill-review-packet`

必要時可額外產出 `draft-review.md`，作為這一輪修改的摘要。

### 10. Ask whether to promote, and where

只有在以下條件同時成立時，才可詢問 promote：

- 最新 `skillkeeper-initial.md` verdict 為 `allow`
- 最新 `reviewer-report.md` verdict 為 `pass`
- 最新 `skillkeeper-final.md` verdict 為 `admit`
- 使用者明確表示 draft 不再需要修改

promote 前仍要再次確認：

- 最終 canonical skill name
- 這次要納入哪一層：
  - `canonical-skills/regular-skills/<skill-name>/`
  - `canonical-skills/manager-skills/<skill-name>/`

### 11. Complete the intake flow

在使用者明確同意後，應直接把 intake flow 做完，不要只停在 promote。

步驟：

- 把 staged draft 複製到使用者選定的 canonical layer
- 把 review artifacts 複製到 `reviews/<skill-name>/`
- 呼叫 `finalize-skill` 對新採納的 canonical skill 執行 `refresh-metadata` 與 `validate`
- 至少做一個 Codex target smoke test
- 只有在上述步驟都成功後，才刪除對應的 `tmp/import-candidates/<source-name>/<skill-name>/`

review artifacts 預設至少包含：

- `skillkeeper-initial.md`
- `source-inventory.md`
- `reviewer-report.md`
- `skillkeeper-final.md`
- `skill-review-packet.md`

若存在，也要一併搬移：

- `change-request.md`
- `draft-review.md`

smoke test 規則：

- 若採納到 `regular-skills/`，用臨時專案跑 `install <skill-name> --target codex`
- 若採納到 `manager-skills/`，用臨時專案跑 `sync-manager-catalog <skill-name> --target codex`

### 12. Report the final result

收尾時至少回報：

- source name 與最終 canonical skill name
- 採納 layer：`regular-skills` 或 `manager-skills`
- `skillkeeper-initial.md` 結論
- `reviewer-report.md` 結論
- `skillkeeper-final.md` 結論
- `skill-review-packet.md` 是否已更新
- review artifacts 是否已保存到 `reviews/<skill-name>/`
- 若 draft 曾修改過，`change-request.md` 與 `draft-review.md` 的結論
- 最終 package hash
- validate 結果
- smoke test 結果
