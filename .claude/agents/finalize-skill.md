---
name: "finalize-skill"
description: "Canonical skill finalizer for this repository. Use when a maintainer needs to refresh metadata and validate a skill after source edits."
tools: "Bash, Read, Grep, Glob, Edit"
---
<!-- skill-toolkit: {"name": "finalize-skill", "rendered_from": "canonical-skills/manager-skills/finalize-skill", "source_package_sha256": "16cafa011c2222808b6f11b104ad95abb675f4d783d262616484bbb53951cca2", "version": "1.0.0"} -->

# Finalize Skill

用來把某個 canonical skill 收尾到可驗證狀態。

## Use This For

- 對單一 canonical skill 執行 `refresh-metadata`
- 對同一個 canonical skill 執行 `validate`
- 回報 package hash、manifest 與 validate 結果
- 作為 `create-skill` 與 `update-skill` 的最後一步

## Do Not Use This For

- 建立新的 canonical skill
- 修改 canonical instruction 內容
- 同步 `.agents/skills/` 或 `.claude/agents/`
- 取代 `install-manager-skill`

## Workflow

### 1. Confirm the target skill

先確認：

- skill 名稱
- 它位於 `canonical-skills/regular-skills/` 或 `canonical-skills/manager-skills/`
- 剛剛的 source 變更是否已經完成

### 2. Refresh metadata

直接呼叫 repo CLI：

- `PYTHONPATH=src python -m skill_toolkit --repo-root . refresh-metadata <skill-name>`

如果這次也要更新日期或版本，可以加上：

- `--today`
- `--updated-at`
- `--version`

### 3. Validate the canonical package

接著執行：

- `PYTHONPATH=src python -m skill_toolkit --repo-root . validate <skill-name>`

若 validate 失敗，要明確列出 validator issues，不要假裝完成。

### 4. Report the result

至少要回報：

- skill 名稱
- 最終 package hash
- 是否 validate 通過
- 若沒有通過，哪些問題需要回去修

## Rules

- `finalize-skill` 只做 canonical package metadata refresh 與 validation
- 不直接同步本 repo 的 `.agents/` 或 `.claude/`
- 如果使用者下一步要同步到本地 agent targets，應改用 `install-manager-skill`
