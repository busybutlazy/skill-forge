---
name: create-skill
description: "Use this skill when the user wants to create a new public Codex skill in this repository's skill-base, scaffold its folder, or draft the first version of its metadata and instructions."
---

# Create Public Skill

用來在這個 repo 的 `skill-base/` 中建立新的公開 Codex skill。

## Use This For

- 新增一個可分發的公開 skill
- 草擬 `SKILL.md` 與 `metadata.json`
- 建立 skill 所需的基本資料夾結構

## Do Not Use This For

- 修改 repo 維護者專用的 `.agents/skills/`
- 安裝 skill 到其他專案
- 只做小幅文字修正或版本調整

## Workflow

### 1. Gather the definition

先確認：

- skill 名稱
- 使用情境
- 不該觸發的情境
- 分類
- 主要 workflow
- 是否需要 `scripts/`、`references/`、`examples/`、`assets/`

### 2. Check repository conventions

讀取：

- `AGENTS.md`
- `README.md`
- 至少一個 `skill-base/` 既有 skill 作為結構參考

### 3. Create the public skill

在 `skill-base/<skill-name>/` 建立：

- `SKILL.md`
- `metadata.json`
- 視需要建立輔助目錄

`SKILL.md` 應包含：

- 明確的 Codex frontmatter
- 觸發時機
- 不適用情境
- 執行流程
- 必要限制與輸出要求

`metadata.json` 應包含：

- `name`
- `version`
- `category`
- `description`
- `author`
- `updated_at`
- `tags`

### 4. Validate consistency

確認：

- 目錄名稱、frontmatter `name`、metadata `name` 一致
- `description` 足以讓 Codex 判斷是否該觸發
- `metadata.json` 的版本與日期合理
- 內容屬於公開可分發 skill，而不是 repo 管理技能

### 5. Prepare for manager install flow

提醒自己或使用者：

- 這個 skill 之後會由 `skill-manager.sh` 安裝到其他專案 `.agents/skills/`
- 因此內容不應依賴這個 repo 自己的特殊維護流程
