# Adapter Contract

這份文件定義 phase 3 renderer 必須滿足的 target output 契約。canonical package 是唯一輸入，target artifact 是衍生輸出。

## Shared Contract

所有 target adapter 都必須遵守：

- 只從 canonical package 讀資料，不讀既有 rendered artifact
- 相同輸入必須產出相同輸出
- 共享 instruction 只能來自 `instruction.md`
- target-specific 差異只能來自 `targets/<target>.frontmatter.json` 類型的 override
- renderer 必須保留 canonical package 的 `version` 與 `package_sha256` 供後續比對

## Codex Target

輸出目標：

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

`SKILL.md` contract：

- 以 YAML frontmatter 開頭
- frontmatter 來自 `targets/codex.frontmatter.json`
- frontmatter 後方直接接 `instruction.md` 的共享內容

`metadata.json` contract：

- 至少保留 `name`、`version`、`description`、`updated_at`、`tags`
- 額外加入 `source_package_sha256`
- 額外加入 `rendered_from: "canonical-skills/<skill>"`

## Claude Target

根據 Anthropic Claude Code 官方 subagents 文件，專案層級自訂 agent 目錄是 `.claude/agents/`，檔案格式為含 YAML frontmatter 的 Markdown 單檔。Phase 2 因此把 Claude target contract 固定為 project subagent，而不是 `.claude/skills/`。

輸出目標：

```text
<project>/.claude/agents/<skill>.md
```

必要輸出：

- `<skill>.md`

可選輸出：

- `<skill>.assets/`

`<skill>.md` contract：

- 以 YAML frontmatter 開頭
- frontmatter 來自 `targets/claude.frontmatter.json`
- frontmatter 後方直接接 `instruction.md` 的共享內容

`<skill>.assets/` contract：

- 僅當 canonical package 含 `examples/`、`references/`、`scripts/`、`assets/` 時才輸出
- 保留原始相對路徑
- Markdown 內若引用附件，應以相對於 `<skill>.md` 的路徑表示，例如 `./commit.assets/examples/foo.md`

## Renderer Guarantees

renderer 必須能保證：

- 不會把 Codex 專屬 metadata 夾帶到 Claude output
- 不會把 Claude 專屬 tool 權限欄位夾帶到 Codex output
- 不會重排 manifest 以外的檔案順序造成雜訊 diff
- 可以從 canonical package 重新生成 artifact，而不需要依賴既有 target 目錄內容

## Proof Target

phase 2 的 migration proof 使用 `commit` skill，驗證：

- 同一份 shared `instruction.md`
- 兩份 target override
- 可產出 Codex package 與 Claude subagent
- 共享 instruction 無需維護兩份
