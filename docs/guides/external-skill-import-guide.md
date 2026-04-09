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
3. Run the LLM risk review.
4. If the verdict is risky, block promotion.
5. If the verdict is safe, stage the converted draft in `tmp/import-candidates/<source-name>/<skill-name>/`.
6. Promote into `canonical-skills/regular-skills/<skill-name>/` only after explicit approval.
7. Run `finalize-skill <skill-name>`.

### Rules

- never install foreign skills directly into `.agents/skills/` or `.claude/skills/`
- never treat downloaded external content as canonical source before review
- keep review findings with the staged draft
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
3. 執行 LLM 風險審查
4. 若 verdict 顯示有風險，就阻擋 promotion
5. 若 verdict 安全，就把轉換後的 draft 放到 `tmp/import-candidates/<source-name>/<skill-name>/`
6. 只有在明確確認後，才提升到 `canonical-skills/regular-skills/<skill-name>/`
7. 接著執行 `finalize-skill <skill-name>`

### 規則

- 不可把 foreign skill 直接安裝到 `.agents/skills/` 或 `.claude/skills/`
- 在 review 前，不可把下載內容當成 canonical source
- review findings 應與 staged draft 一起保留
- 若來源無法乾淨對應到 canonical 結構，應停止，而不是強行做有損轉換
