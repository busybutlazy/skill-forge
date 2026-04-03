# Canonical Skill Package Spec

Phase 2 定義的 canonical package 是 skill 的唯一 source of truth。Codex 與 Claude 的安裝內容都必須由這份 source render 出來，不可反向手改 target artifact。

## Goals

- 共享內容只維護一份
- target-specific 差異集中在 override 檔案
- render 輸出可重現
- phase 3 可直接依此實作 validator 與 renderer

## Canonical Layout

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

必要檔案只有 `package.json`、`instruction.md`、`manifest.json` 與至少一個 target override。其餘資料夾皆為選用。

## Required Fields

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

- `schema_version`: canonical package schema 版本
- `identity.*`: shared identity；不得由 target override 覆寫 `name` 或 `version`
- `content.instruction_file`: shared instruction 主體
- `targets.<target>.frontmatter_file`: target wrapper 定義
- `targets.<target>.install_path`: renderer 要輸出的目標路徑樣板
- `integrity.*`: package-level 完整性資訊

## Shared Content Rules

`instruction.md` 只放共享 instruction 主體，不放 target-specific frontmatter，也不放 target 專屬安裝說明。

允許放在 shared body 的內容：

- skill 的角色與目標
- 執行流程
- 通用限制與品質標準
- 可被多個 target 共用的範例或參考資料連結

不得直接寫進 shared body 的內容：

- 只屬於單一 target 的 trigger wording
- 只屬於單一 target 的 wrapper/frontmatter 欄位
- 只屬於單一 target 的安裝路徑或工具權限設定

## Target Override Rules

每個 target override 至少要能表達：

- `name`
- `description`
- 可選的 target-specific fields
- render 時要不要附帶 asset projection

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

## Integrity Rules

`manifest.json` 是 canonical package 的穩定清單，至少要列出 render-driving content：

- 每個受管檔案的相對路徑
- 每個檔案的 `sha256`
- 穩定排序後計算出的 `package_sha256`

phase 2 proof 先把 hash 範圍收斂為 shared instruction 與 target override，避免 `package.json` / `manifest.json` 自我參照。phase 3 若要把 metadata 也納入雜湊，必須先定義 normalization 規則。

`package_sha256` 的計算輸入必須固定：

1. 以 manifest 內的 `files[].path` 做字典序排序
2. 對每個檔案產生一行 `path:sha256`
3. 以 LF (`\n`) 串接所有行，最後一行也保留 LF
4. 對串接結果再計算一次 `sha256`

這份規則要讓 phase 3 可以穩定辨識 update、drift 與 broken package。

## Non-Goals

- 不要求 phase 2 就完成所有 skill 遷移
- 不要求 phase 2 就導入完整自動 renderer
- 不要求 target override 能承載獨立業務邏輯
