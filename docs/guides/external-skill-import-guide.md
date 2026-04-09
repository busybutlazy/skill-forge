# External Skill Import Guide

## English

### Purpose

This guide explains how maintainers should import downloaded external skills without bypassing the canonical governance model.

### Workspace Layout

Use this local workspace convention:

```text
tmp/
├── foreign_skills/
└── import-candidates/
```

- `tmp/foreign_skills/`: downloaded external skill sources
- `tmp/import-candidates/`: staged canonical drafts created after review

Do not place downloaded external sources directly under `canonical-skills/`.

### Supported Inputs

`import-plugin-skill` currently supports one local source at a time:

- a Codex plugin directory containing `.codex-plugin/plugin.json`
- a single skill folder whose root contains `SKILL.md`

If the source does not match either shape, stop and review it manually before attempting conversion.

### Review And Promotion Flow

1. Download the external source into `tmp/foreign_skills/<source-name>/`.
2. Use `import-plugin-skill` to inspect one skill source.
3. Produce a structured maintainer decision review in Traditional Chinese, including skill type, trigger boundary, permission model, failure modes, canonicalization guidance, maintenance cost, and a risk table.
4. If the verdict is `needs_human_review` or `block`, stop promotion and keep only review output plus remediation notes.
5. If the verdict is `allow`, stage the converted draft in `tmp/import-candidates/<source-name>/<skill-name>/`.
6. Let the user review the report and staged draft first; if changes are needed, write `change-request.md`, revise the draft, and require a reviewer pass in `draft-review.md`.
7. On explicit approval, and only after the reviewer verdict is `pass`, ask whether the skill belongs in `canonical-skills/regular-skills/<skill-name>/` or `canonical-skills/manager-skills/<skill-name>/`.
8. Promote into the chosen canonical layer, then run `refresh-metadata`, `validate`, and a Codex smoke test.
9. Delete the matching `tmp/import-candidates/...` draft only after the full flow succeeds.

### Rules

- never install foreign skills directly into `.agents/skills/` or `.claude/skills/`
- never treat downloaded external content as canonical source before review
- keep review findings with the staged draft
- treat `change-request.md` and `draft-review.md` as part of the staged review trail when a draft is revised
- unresolved `medium` or `high` risk blocks promotion
- unclear trigger boundaries, weak approval gates, or unmanageable maintenance cost can also block promotion
- blocked imports should return rewrite or restriction guidance, not only a rejection
- if the source cannot be mapped cleanly to canonical structure, stop instead of forcing a lossy conversion

## 繁體中文

### 目的

這份文件說明 maintainer 應如何匯入下載回來的外部 skill，同時不繞過 canonical 治理流程。

### 工作區結構

建議使用以下本機工作區慣例：

```text
tmp/
├── foreign_skills/
└── import-candidates/
```

- `tmp/foreign_skills/`：下載回來的外部 skill 來源
- `tmp/import-candidates/`：review 後產生的 canonical 草稿

不要把下載回來的外部來源直接放進 `canonical-skills/`。

### 支援的輸入

`import-plugin-skill` 目前一次只支援一個本機來源：

- 含有 `.codex-plugin/plugin.json` 的 Codex plugin directory
- 根目錄帶有 `SKILL.md` 的 single skill folder

若來源不符合這兩種形狀，先停下來人工檢查，不要硬轉。

### Review 與 Promotion 流程

1. 把外部來源下載到 `tmp/foreign_skills/<source-name>/`
2. 用 `import-plugin-skill` 檢查單一 skill 來源
3. 產出結構化的維護決策審查，且 `review-report.md` 必須用繁體中文撰寫，內容包含 skill 類型、trigger 邊界、permission model、failure mode、canonicalization 建議、maintenance cost 與風險表
4. 若 verdict 是 `needs_human_review` 或 `block`，就停止 promotion，只保留 review 輸出與 remediation notes
5. 若 verdict 是 `allow`，就把轉換後的 draft 放到 `tmp/import-candidates/<source-name>/<skill-name>/`
6. 先讓使用者審查 `review-report.md` 與 staged draft；若要修改，先整理 `change-request.md`、修 draft，再由 reviewer 產出 `draft-review.md`
7. 只有在使用者確認 draft 不再需要修改，且 reviewer verdict 為 `pass` 後，才詢問正式納管到 `canonical-skills/regular-skills/<skill-name>/` 還是 `canonical-skills/manager-skills/<skill-name>/`
8. 提升到選定的 canonical layer 後，直接執行 `refresh-metadata`、`validate` 與 Codex smoke test
9. 只有在整個流程都成功後，才刪除對應的 `tmp/import-candidates/...` draft

### 規則

- 不可把 foreign skill 直接安裝到 `.agents/skills/` 或 `.claude/skills/`
- 在 review 前，不可把下載內容當成 canonical source
- review findings 應與 staged draft 一起保留
- 若有修改 draft，`change-request.md` 與 `draft-review.md` 也應保留在 staging review trail
- 任何未解除的 `medium` 或 `high` 風險都不可 promote
- trigger 邊界不清、approval gate 過軟、或 maintenance cost 不可治理，也可以成為不 promote 的理由
- 被阻擋的匯入應提供改寫或限制建議，不應只有拒絕結果
- 若來源無法乾淨對應到 canonical 結構，應停止，而不是強行做有損轉換
