# Skill Review Packet

用來把 skill 審查流程中各階段的結論整理成標準化、可交給人工審核的資料包。

## Use This For

- 已經有審查輸入材料，需要產生一致格式的 skill review packet
- 要把 `skillkeeper`、`reviewer`、`change-request.md` 等結果彙整給人工審核
- 想把 skill intake / revision 的審查結果包裝成可重用的 maintainer review artifact

## Do Not Use This For

- 代替 `skillkeeper` 做準入判斷
- 代替 `reviewer` 做功能保真比對
- 在沒有上游審查材料時憑空產生政策判斷
- 直接修改 canonical skill 內容

## Required Inputs

這些材料通常由 `import-plugin-skill` 工作流程產生。至少應具備下列材料中的三份核心材料（`skillkeeper-initial.md`、`source-inventory.md`、`reviewer-report.md`），其餘為補充材料：

- `skillkeeper-initial.md`（核心）
- `source-inventory.md`（核心）
- `reviewer-report.md`（核心）
- `skillkeeper-final.md`
- 若有人工回饋，另含 `change-request.md`
- 若有 revision summary，另含 `draft-review.md`

## Workflow

### 1. Read the upstream review artifacts

先確認目前有哪些可用材料，並辨識它們分別回答了什麼問題：

- `skillkeeper-initial.md`：為什麼值得或不值得進入改寫
- `source-inventory.md`：原始 skill 的功能與引用基線
- `reviewer-report.md`：draft 是否保留了 source 的功能性
- `skillkeeper-final.md`：final draft 是否可准入
- `change-request.md`：人工要求的修改方向
- `draft-review.md`：某一輪 revision 的摘要

如果缺少關鍵材料，要在 packet 中明講缺口，而不是自行補判斷。

### 2. Normalize the review story

把輸入材料整理成固定敘事：

- source 是什麼
- 為什麼考慮納管
- 有哪些 must-preserve capabilities / references
- draft 保留了什麼
- draft 收窄了什麼
- 哪些問題被 reviewer 打回過
- final admission 是什麼

### 3. Produce the packet

以對話回覆的形式輸出 `skill-review-packet.md` 的完整內容（不另存為獨立檔案，除非 maintainer 明確要求）。packet 至少包含：

- source overview
- intake decision summary
- preserved areas
- narrowed or remapped areas
- reviewer findings
- final admission status
- unresolved risks
- open questions for human review

`skill-review-packet.md` 應使用繁體中文撰寫。若上游材料含有英文欄位名稱、verdict 或檔名，可保留原始識別字，但敘述、摘要、判讀與給人工審核者看的說明都應以繁體中文為主。

若存在多輪 revision（即有 `change-request.md` 或多份 `draft-review.md`），應補一段 revision history，整理：

- 這一輪是第幾次 revision phase
- 是否有 `change-request.md`
- reviewer 是否曾要求 revise
- 哪些點是這一輪新修正的

## Rules

- 這個 skill 只整理和包裝上游結論，不新增新的政策判斷
- 若上游 verdict 互相衝突，要在 packet 中明講矛盾，而不是自行裁決
- packet 重點是幫人工快速審核，不是重寫整份 review
- packet 完成的標準：所有八個必要欄位都有內容，缺口以「材料不足，無法判斷」明確標注，不留空白欄位
