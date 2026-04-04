---
name: create-skill
description: "Public canonical skill creation specialist. Use proactively when the user wants to add a new skill under canonical-skills/, scaffold package.json and manifest.json, or define Codex and Claude target overrides."
tools: Bash, Read, Grep, Glob
---

# Create Public Skill

用來在這個 repo 的 `canonical-skills/` 中建立新的公開 skill。

## Use This For

- 新增一個可分發的公開 skill
- 草擬 `package.json`、`manifest.json`、`instruction.md` 與 target overrides
- 建立 skill 所需的基本資料夾結構

## Do Not Use This For

- 修改 repo 維護者專用的 `.agents/skills/` 或 `.claude/agents/`
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
- `docs/phase2/canonical-package-spec.md`
- `docs/phase2/adapter-contract.md`
- 至少一個 `canonical-skills/` 既有 skill 作為結構參考

### 3. Create the public skill

在 `canonical-skills/<skill-name>/` 建立：

- `package.json`
- `manifest.json`
- `instruction.md`
- `targets/codex.frontmatter.json`
- `targets/claude.frontmatter.json`
- 視需要建立輔助目錄

`package.json` 必須遵守目前 canonical schema：

- `schema_version: 1`
- `identity.name`
- `identity.version`
- `identity.description`
- `identity.updated_at`
- `identity.tags`
- `content.instruction_file`，固定為 `instruction.md`
- `targets.codex.frontmatter_file`
- `targets.codex.install_path`，固定為 `.agents/skills/{name}/`
- `targets.claude.frontmatter_file`
- `targets.claude.install_path`，固定為 `.claude/agents/{name}.md`
- `integrity.manifest_file`，固定為 `manifest.json`
- `integrity.package_sha256`

`instruction.md` 應包含：

- 觸發時機
- 不適用情境
- 執行流程
- 必要限制與輸出要求

shared `instruction.md` 只放共用 instruction 主體，不放 target-specific frontmatter、工具權限、安裝路徑或單一 target 的觸發文案。

target override 要求：

- `targets/codex.frontmatter.json` 至少包含 `name` 與 `description`
- `targets/claude.frontmatter.json` 至少包含 `name` 與 `description`
- Claude 如需 target-specific 欄位，例如 `tools`，只能放在 Claude frontmatter

`manifest.json` 必須列出 render-driving content：

- `instruction.md`
- `targets/codex.frontmatter.json`
- `targets/claude.frontmatter.json`
- 若有其他會影響 render 的受管檔案，也要一併納入

`manifest.json` 與 `package.json.integrity.package_sha256` 必須同步對應同一個 package hash。

### 4. Validate consistency

確認：

- 目錄名稱、`identity.name`、兩個 target override 的 `name` 一致
- `description` 足以讓 target 判斷是否該觸發
- `package.json` 結構符合目前 validator 契約
- `manifest.json`、`integrity.package_sha256`、版本與日期彼此一致
- 內容屬於公開可分發 skill，而不是 repo 管理技能

建立完後一定要跑：

- `PYTHONPATH=src python -m skill_toolkit --repo-root . validate <skill-name>`

若 validate 失敗，先修 canonical package，不要跳過。

### 5. Smoke-check target behavior

至少確認 render / install 心智模型沒有寫錯：

- 這個 skill 之後會由 Python CLI render 並安裝到其他專案
- Codex 目標是 `.agents/skills/<name>/`
- Claude 目標是 `.claude/agents/<name>.md`
- 因此 canonical source 不應依賴這個 repo 自己的 maintainer workflow

如果這次建立的 skill 使用了 `examples/`、`references/`、`scripts/`、`assets/`，要再檢查它們在 Codex 與 Claude output 的相對路徑是否合理。
