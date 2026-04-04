---
name: "update-skill"
description: "Canonical skill maintenance specialist for this repository. Use when a maintainer needs to revise an existing public canonical skill package."
tools: "Bash, Read, Grep, Glob, Edit"
---
<!-- skill-toolkit: {"name": "update-skill", "rendered_from": "canonical-skills/manager-skills/update-skill", "source_package_sha256": "a510c844ead72488699990a86edfa231bc975d806d40afdd4b24ca363a4b5310", "version": "1.0.0"} -->

# Update Public Skill

用來修改 `canonical-skills/regular-skills/` 中既有的公開 skill。

## Use This For

- 更新 skill workflow
- 調整 trigger description
- 修正 canonical package metadata
- 升級 skill 版本
- 視需要調整 `shared` tag，控制 manager install flow 是否應納入某個 regular skill

## Do Not Use This For

- 修改 `.agents/skills/` 的管理者技能
- 安裝或移除其他專案的 skills
- 建立全新的 skill
- 把 skill 同步到本 repo 的 `.agents/` 或 `.claude/`

## Workflow

### 1. Inspect the current skill

先讀：

- `canonical-skills/regular-skills/<skill-name>/instruction.md`
- `canonical-skills/regular-skills/<skill-name>/package.json`
- `canonical-skills/regular-skills/<skill-name>/manifest.json`
- `canonical-skills/regular-skills/<skill-name>/targets/`
- 必要時對照 `docs/reference/canonical-package-spec.md` 與 `docs/reference/adapter-contract.md`

搞清楚：

- 現在的行為是什麼
- 哪些部分要改
- 變更是否屬於 patch / minor / major 等級

### 2. Revise the skill

更新必要內容：

- 觸發描述
- 不適用情境
- 流程步驟
- 限制與輸出要求
- target-specific frontmatter
- 受管 asset 目錄中的引用與路徑

只改真正需要改的部分，避免把 skill 改成另一個任務。

shared `instruction.md` 不應混入 target-specific frontmatter、Claude tools、安裝路徑或 maintainer-only 流程。

### 3. Update metadata

同步調整：

- `package.json.identity.version`
- `package.json.identity.updated_at`
- 必要時調整 `package.json.identity.description`、`package.json.identity.tags`
- `manifest.json`
- `package.json.integrity.package_sha256`

版本規則：

- 小修正：patch
- 新增能力或顯著流程調整：minor
- 不相容重寫或定位改變：major

如果修改了 render-driving content，必須同步更新：

- `manifest.json.files[*].sha256`
- `manifest.json.package_sha256`
- `package.json.integrity.package_sha256`

### 4. Validate publishability

確認：

- skill 仍屬於公開可分發內容
- 目錄名稱、`identity.name`、target override `name` 一致
- package metadata 與 target override 沒有互相矛盾
- 說明不依賴舊工具或已淘汰目錄
- `distribution.scope` 仍符合預期
- `content.instruction_file` 仍為 `instruction.md`
- Codex install path 仍為 `.agents/skills/{name}/`
- Claude install path 仍為 `.claude/agents/{name}.md`

更新完 canonical source 後，下一步應提醒使用者執行 `finalize-skill`。

建議互動收尾：

- 問使用者是否現在就要 finalize 這個 skill
- 若使用者回答 `yes`，立即切換到 `finalize-skill`
- 若使用者回答 `no`，明確提醒之後要執行 `finalize-skill <skill-name>`

如果只是要把 canonical 狀態同步到本 repo 的 agent 目錄，不用這個 skill，改用 `install-manager-skill`。

### 5. Check manager impact

如果這次修改會影響 render / install 流程，記得一起檢查：

- Python CLI
- `README.md`
- target render output 與狀態顯示是否仍合理

若變更牽涉 canonical 結構、hash、renderer 或 installer 契約，再補做：

- phase 3 test suite
- 用暫時目錄 smoke-test Codex install
- 用暫時目錄 smoke-test Claude install
