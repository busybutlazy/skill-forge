---
name: "install-manager-skill"
description: "Manager skill catalog installer for this repository. Use when a maintainer needs to select manager skills and shared regular skills and sync them into local agent targets."
tools: "Bash, Read, Grep, Glob, Edit"
---
<!-- skill-toolkit: {"name": "install-manager-skill", "rendered_from": "canonical-skills/manager-skills/install-manager-skill", "source_package_sha256": "ef194de32f8331be487e6c00681c1b62aec86fa8b380f7b9457b7b52e2affc83", "version": "1.0.0"} -->

# Install Manager Skill

用來把管理者工作流需要的 skills 同步到這個 repo 本地的 agent 目錄。

## Use This For

- 列出目前可供管理者同步的 skills
- 從 `manager-skills/` 中挑選 manager-only skills
- 額外納入帶有 `shared` tag 的 regular skills
- 讓管理者選擇要同步到 `.agents/skills/`、`.claude/agents/` 或兩者都同步
- 呼叫 repo CLI 完成 install、refresh 或 update

## Do Not Use This For

- 建立新的 canonical skill
- 修改既有 canonical skill 的內容
- 手動編輯 `.agents/skills/` 或 `.claude/agents/`
- 取代 `create-skill` 或 `update-skill`

## Workflow

### 1. Inspect the available manager catalog

先整理兩類可安裝 skill：

- `canonical-skills/manager-skills/` 內全部 skills
- `canonical-skills/regular-skills/` 內帶有 `shared` tag 的 skills

向使用者清楚列出：

- skill 名稱
- 來源是 `manager-skills` 還是 `regular-skills [shared]`
- 簡短描述
- 若已安裝，顯示目前狀態

### 2. Confirm the sync target

詢問要同步到哪裡：

- Codex：`.agents/skills/`
- Claude：`.claude/agents/`
- All：兩者都同步

### 3. Choose what to sync

讓使用者選擇：

- 要同步哪些 skills
- 是否要一口氣同步全部 manager catalog
- 若有 drift 或舊的 unmanaged install，是否接受覆蓋

如果使用者沒有指定清單，預設可同步整個 manager catalog。

### 4. Execute through the toolkit CLI

不要自己重寫安裝邏輯，直接呼叫 repo CLI：

- `PYTHONPATH=src python -m skill_toolkit --repo-root . sync-manager-catalog ...`

必要時加入：

- `--project .`
- `--target codex|claude|all`
- `--force`
- 指定的 skill 名單

### 5. Report the outcome

同步完成後要回報：

- 哪些 skills 已同步
- 同步到哪些 target
- 是否有任何 skip、repair、force overwrite
- 若某 skill 不在 manager catalog，直接明講原因

## Rules

- manager catalog 只包含：
  - `manager-skills/` 內全部 skills
  - `regular-skills/` 中帶 `shared` tag 的 skills
- 不要把其他 regular skills 混進 manager install flow
- 只同步已經 finalize 完成的 canonical skills
- 不要在這個 skill 內修改 canonical source
- 若需要新增或修改 source，應改用 `create-skill` 或 `update-skill`
