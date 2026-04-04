# Canonical Skill Package Spec

## English

A canonical package is the only source of truth for a skill. Codex and Claude installable content must be rendered from that source, not edited back through target artifacts.

### Goals

- maintain one shared source of instruction content
- keep target-specific differences in override files
- make rendered outputs reproducible
- provide a stable contract for validators and renderers

### Canonical Layout

```text
canonical-skills/<skill>/
├── package.json
├── instruction.md
├── manifest.json
├── targets/
│   ├── codex.frontmatter.json
│   └── claude.frontmatter.json
├── examples/
├── references/
├── scripts/
└── assets/
```

Only `package.json`, `instruction.md`, `manifest.json`, and at least one target override are required. The other directories are optional.

### Required Fields

`package.json` must contain:

```json
{
  "schema_version": 1,
  "identity": {
    "name": "commit",
    "version": "1.0.0",
    "description": "Plan commit boundaries, review staged content, and craft concise commit messages",
    "updated_at": "2026-04-03",
    "tags": ["git", "commit", "workflow"]
  },
  "content": {
    "instruction_file": "instruction.md"
  },
  "targets": {
    "codex": {
      "frontmatter_file": "targets/codex.frontmatter.json",
      "install_path": ".agents/skills/{name}/"
    },
    "claude": {
      "frontmatter_file": "targets/claude.frontmatter.json",
      "install_path": ".claude/agents/{name}.md"
    }
  },
  "integrity": {
    "manifest_file": "manifest.json",
    "package_sha256": "<sha256>"
  }
}
```

Field rules:

- `schema_version`: version of the canonical package schema
- `identity.*`: shared identity; target overrides must not replace `name` or `version`
- `content.instruction_file`: shared instruction body
- `targets.<target>.frontmatter_file`: target wrapper definition
- `targets.<target>.install_path`: output path template used by the renderer
- `integrity.*`: package-level integrity metadata

### Shared Content Rules

`instruction.md` contains only the shared instruction body. It must not include target-specific frontmatter or target-specific installation guidance.

Allowed in the shared body:

- the role and goal of the skill
- workflow steps
- general constraints and quality standards
- examples or references that can be shared across targets

Not allowed in the shared body:

- target-specific trigger wording
- target-specific wrapper or frontmatter fields
- target-specific install paths or tool permission settings

### Target Override Rules

Every target override must be able to express at least:

- `name`
- `description`
- optional target-specific fields
- whether asset projection should be included during rendering

Codex override example:

```json
{
  "name": "commit",
  "description": "Use this skill when the user wants help reviewing local changes, deciding commit boundaries, or creating one or more git commits."
}
```

Claude override example:

```json
{
  "name": "commit",
  "description": "Git commit planning specialist. Use proactively when the user asks to review local changes, separate commit boundaries, or prepare one or more commits.",
  "tools": "Bash, Read, Grep, Glob"
}
```

### Integrity Rules

`manifest.json` is the stable package inventory. It must include at least the render-driving content:

- the relative path of each managed file
- the `sha256` of each file
- the final `package_sha256` computed over the stable file list

The current hash scope is limited to shared instruction content and target overrides so that `package.json` and `manifest.json` do not self-reference. If metadata is added to the hash in the future, normalization rules must be defined first.

The `package_sha256` input must be computed in a fixed way:

1. sort manifest `files[].path` values lexicographically
2. generate one line per file as `path:sha256`
3. join all lines with LF (`\n`), keeping a trailing LF on the final line
4. compute `sha256` over the resulting text

These rules exist so the system can consistently detect updates, drift, and broken packages.

### Non-Goals

- completing every skill migration in one step
- requiring a fully automated renderer from day one
- allowing target overrides to carry independent business logic

## 繁體中文

canonical package 是 skill 的唯一 source of truth。Codex 與 Claude 的可安裝內容都必須由這份 source render 出來，不可反向手改 target artifact。

### 目標

- 共享 instruction 內容只維護一份
- target-specific 差異集中在 override 檔案
- 讓 render 輸出可重現
- 提供 validator 與 renderer 可依賴的穩定契約

### Canonical Layout

```text
canonical-skills/<skill>/
├── package.json
├── instruction.md
├── manifest.json
├── targets/
│   ├── codex.frontmatter.json
│   └── claude.frontmatter.json
├── examples/
├── references/
├── scripts/
└── assets/
```

只有 `package.json`、`instruction.md`、`manifest.json` 與至少一個 target override 是必要檔案，其餘目錄皆為選用。

### 必要欄位

`package.json` 必須包含：

```json
{
  "schema_version": 1,
  "identity": {
    "name": "commit",
    "version": "1.0.0",
    "description": "Plan commit boundaries, review staged content, and craft concise commit messages",
    "updated_at": "2026-04-03",
    "tags": ["git", "commit", "workflow"]
  },
  "content": {
    "instruction_file": "instruction.md"
  },
  "targets": {
    "codex": {
      "frontmatter_file": "targets/codex.frontmatter.json",
      "install_path": ".agents/skills/{name}/"
    },
    "claude": {
      "frontmatter_file": "targets/claude.frontmatter.json",
      "install_path": ".claude/agents/{name}.md"
    }
  },
  "integrity": {
    "manifest_file": "manifest.json",
    "package_sha256": "<sha256>"
  }
}
```

欄位規則：

- `schema_version`：canonical package schema 版本
- `identity.*`：共享 identity；target override 不得覆寫 `name` 或 `version`
- `content.instruction_file`：共享 instruction 主體
- `targets.<target>.frontmatter_file`：target wrapper 定義
- `targets.<target>.install_path`：renderer 使用的輸出路徑樣板
- `integrity.*`：package-level 完整性資訊

### Shared Content Rules

`instruction.md` 只放共享 instruction 主體，不放 target-specific frontmatter，也不放 target-specific 安裝說明。

允許放在 shared body 的內容：

- skill 的角色與目標
- 執行流程
- 通用限制與品質標準
- 可被多個 target 共用的範例或參考資料

不得直接寫進 shared body 的內容：

- 單一 target 專屬的 trigger wording
- 單一 target 專屬的 wrapper 或 frontmatter 欄位
- 單一 target 專屬的安裝路徑或工具權限設定

### Target Override Rules

每個 target override 至少要能表達：

- `name`
- `description`
- 可選的 target-specific 欄位
- render 時是否要附帶 asset projection

Codex override 範例：

```json
{
  "name": "commit",
  "description": "Use this skill when the user wants help reviewing local changes, deciding commit boundaries, or creating one or more git commits."
}
```

Claude override 範例：

```json
{
  "name": "commit",
  "description": "Git commit planning specialist. Use proactively when the user asks to review local changes, separate commit boundaries, or prepare one or more commits.",
  "tools": "Bash, Read, Grep, Glob"
}
```

### Integrity Rules

`manifest.json` 是穩定的 package 清單。它至少要列出 render-driving content：

- 每個受管檔案的相對路徑
- 每個檔案的 `sha256`
- 依穩定檔案清單計算出的最終 `package_sha256`

目前的 hash 範圍只包含共享 instruction 內容與 target override，避免 `package.json` 與 `manifest.json` 自我參照。若未來要把 metadata 納入雜湊，必須先定義 normalization 規則。

`package_sha256` 的輸入必須以固定方式計算：

1. 以 manifest 內的 `files[].path` 做字典序排序
2. 對每個檔案產生一行 `path:sha256`
3. 以 LF (`\n`) 串接所有行，最後一行也保留 LF
4. 對串接結果再計算一次 `sha256`

這些規則的目的是讓系統可以穩定辨識 update、drift 與 broken package。

### Non-Goals

- 不要求一次完成所有 skill 遷移
- 不要求從第一天就具備完整自動 renderer
- 不允許 target override 承載獨立業務邏輯
