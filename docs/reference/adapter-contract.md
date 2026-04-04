# Adapter Contract

## English

This document defines the target output contract that every renderer must satisfy. A canonical package is the only input. Target artifacts are derived outputs.

### Shared Contract

Every target adapter must follow these rules:

- read only from the canonical package, never from previously rendered artifacts
- produce the same output for the same input
- source shared instructions only from `instruction.md`
- source target-specific differences only from override files such as `targets/<target>.frontmatter.json`
- preserve the canonical package `version` and `package_sha256` for later comparison

### Codex Target

Output location:

```text
<project>/.agents/skills/<skill>/
```

Required outputs:

- `SKILL.md`
- `metadata.json`

Optional outputs:

- `examples/`
- `references/`
- `scripts/`
- `assets/`

`SKILL.md` contract:

- begins with YAML frontmatter
- frontmatter comes from `targets/codex.frontmatter.json`
- the shared body comes directly from `instruction.md`

`metadata.json` contract:

- must keep at least `name`, `version`, `description`, `updated_at`, and `tags`
- must include `source_package_sha256`
- must include `rendered_from: "canonical-skills/<skill>"`

### Claude Target

According to the Anthropic Claude Code subagents format, the project-level custom agent directory is `.claude/agents/`, and each agent is a Markdown file with YAML frontmatter. The Claude target contract therefore uses project subagents rather than `.claude/skills/`.

Output location:

```text
<project>/.claude/agents/<skill>.md
```

Required outputs:

- `<skill>.md`

Optional outputs:

- `<skill>.assets/`

`<skill>.md` contract:

- begins with YAML frontmatter
- frontmatter comes from `targets/claude.frontmatter.json`
- the shared body comes directly from `instruction.md`

`<skill>.assets/` contract:

- render only when the canonical package contains `examples/`, `references/`, `scripts/`, or `assets/`
- preserve the original relative paths
- use paths relative to `<skill>.md` for Markdown asset references, for example `./commit.assets/examples/foo.md`

### Renderer Guarantees

The renderer must guarantee:

- Codex-only metadata is not leaked into Claude output
- Claude-only tool permission fields are not leaked into Codex output
- file ordering outside the manifest is not arbitrarily reshuffled into noisy diffs
- artifacts can be regenerated from the canonical package without depending on existing target directories

### Example Validation Target

Using the `commit` skill as a validation example, the system should confirm:

- one shared `instruction.md`
- two target overrides
- successful Codex package output and Claude subagent output
- no need to maintain duplicate editable copies of the shared instruction

## 繁體中文

這份文件定義每個 renderer 都必須滿足的 target output 契約。canonical package 是唯一輸入，target artifact 是衍生輸出。

### 共用契約

所有 target adapter 都必須遵守以下規則：

- 只從 canonical package 讀資料，不讀既有 rendered artifact
- 相同輸入必須產出相同輸出
- 共享 instruction 只能來自 `instruction.md`
- target-specific 差異只能來自 `targets/<target>.frontmatter.json` 這類 override 檔案
- 必須保留 canonical package 的 `version` 與 `package_sha256` 供後續比對

### Codex Target

輸出位置：

```text
<project>/.agents/skills/<skill>/
```

必要輸出：

- `SKILL.md`
- `metadata.json`

可選輸出：

- `examples/`
- `references/`
- `scripts/`
- `assets/`

`SKILL.md` 契約：

- 以 YAML frontmatter 開頭
- frontmatter 來自 `targets/codex.frontmatter.json`
- 共享主體直接來自 `instruction.md`

`metadata.json` 契約：

- 至少保留 `name`、`version`、`description`、`updated_at`、`tags`
- 必須加入 `source_package_sha256`
- 必須加入 `rendered_from: "canonical-skills/<skill>"`

### Claude Target

根據 Anthropic Claude Code 的 subagents 格式，專案層級自訂 agent 目錄是 `.claude/agents/`，每個 agent 是一個帶 YAML frontmatter 的 Markdown 檔。因此 Claude target contract 採用 project subagent，而不是 `.claude/skills/`。

輸出位置：

```text
<project>/.claude/agents/<skill>.md
```

必要輸出：

- `<skill>.md`

可選輸出：

- `<skill>.assets/`

`<skill>.md` 契約：

- 以 YAML frontmatter 開頭
- frontmatter 來自 `targets/claude.frontmatter.json`
- 共享主體直接來自 `instruction.md`

`<skill>.assets/` 契約：

- 只有在 canonical package 包含 `examples/`、`references/`、`scripts/` 或 `assets/` 時才輸出
- 保留原始相對路徑
- Markdown 內若引用附件，應使用相對於 `<skill>.md` 的路徑，例如 `./commit.assets/examples/foo.md`

### Renderer Guarantees

renderer 必須保證：

- 不會把 Codex 專屬 metadata 帶進 Claude output
- 不會把 Claude 專屬 tool 權限欄位帶進 Codex output
- 不會任意重排 manifest 以外的檔案順序造成雜訊 diff
- 可以直接從 canonical package 重新生成 artifact，而不依賴既有 target 目錄內容

### 驗證範例

以 `commit` skill 作為驗證範例時，系統應能確認：

- 只有一份共享的 `instruction.md`
- 存在兩份 target override
- 能成功產出 Codex package 與 Claude subagent
- 不需要維護兩份可編輯的 shared instruction
