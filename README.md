# Codex Skill Toolkit

用來維護與分發 Codex skills 的工具專案。

這個 repo 分成兩條用途明確的路徑：

- `skill-base/`：可安裝到其他專案 `.agents/skills/` 的公開 skills
- `.agents/skills/`：這個 repo 自己使用的管理者 skills

`.codex/` 不是這個專案的主要 skills 目錄。對 Codex 而言：

- `AGENTS.md` 負責規則與協作約定
- `.agents/skills/` 負責 task-specific skills
- `.codex/config.toml` 才是 config / hooks / MCP 類設定位置

## Quick Start

### 1. Clone 到本機

```bash
git clone git@github.com:busybutlazy/Skill_Merchant-.git ~/Skill_Merchant
```

如果你的正式 repo 名稱不同，把上面的 repo 名稱改成實際名稱即可。

### 2. 確認執行環境

`skill-manager.sh` 目前依賴 Bash 4+。

- `bash --version` 必須顯示 4.0 以上
- macOS 內建 `/bin/bash` 是 3.2，不能直接拿來跑這支 script
- 如果你在 macOS 上使用，先安裝新版 Bash，例如 `brew install bash`

執行前先確認目前會用到的 `bash` 是新版：

```bash
command -v bash
bash --version
```

### 3. 在目標專案根目錄執行 manager

```bash
cd /path/to/target-project
bash ~/Skill_Merchant/skill-manager.sh
```

`skill-manager.sh` 會把你選的公開 skills 安裝到目前專案的 `.agents/skills/`。

manager 不會自動更新這個 toolkit repo；如果你要取得最新內容，請手動在 toolkit repo 內執行 `git pull`。

### 4. 在這個 repo 內工作時

這個 repo 自己的管理者 skills 放在 `.agents/skills/`，用途是維護 `skill-base/`，例如建立新 skill、更新既有 skill。

## 專案結構

```text
codex-skill-toolkit/
├── AGENTS.md
├── .agents/
│   └── skills/
│       ├── create-skill/
│       │   └── SKILL.md
│       └── update-skill/
│           └── SKILL.md
├── skill-base/
│   ├── commit/
│   │   ├── SKILL.md
│   │   └── metadata.json
│   └── <other-public-skills>/
│       ├── SKILL.md
│       ├── metadata.json
│       ├── scripts/
│       ├── references/
│       ├── examples/
│       └── assets/
├── skill-manager.sh
├── README.md
├── ROADMAP.md
└── TODO/
    ├── phase1.md
    ├── phase2.md
    └── phase3.md
```

## 這個工具做什麼

`skill-manager.sh` 提供互動式 CLI，支援：

- 從 `skill-base/` 安裝公開 skills 到目標專案 `.agents/skills/`
- 更新已安裝的公開 skills
- 列出目標專案目前已安裝的公開 skills 與可用更新
- 移除目標專案中不再需要的公開 skills

CLI 不會處理這個 repo 自己的 `.agents/skills/` 管理者 skills。
目前 CLI 只支援 Codex 的 `.agents/skills/` 安裝目標；Claude 相容規劃放在後續 roadmap phase。

## Skill Format

每個 Codex skill 至少包含：

### `SKILL.md`

Codex 會先讀 frontmatter 的 `name` 與 `description` 來決定是否使用該 skill。

```yaml
---
name: commit
description: "Use this skill when the user wants help reviewing changes and creating one or more git commits."
---
```

建議：

- `name` 使用小寫加連字號
- `description` 清楚描述該觸發與不該觸發的情境
- 內容聚焦在流程、限制、輸出要求，不要塞大量背景資訊

### `metadata.json`

這份 metadata 主要給 `skill-manager.sh` 使用，用來顯示版本、分類與描述。

```json
{
  "name": "commit",
  "version": "1.0.0",
  "category": "git",
  "description": "Plan commit boundaries, review staged content, and craft concise commit messages",
  "author": "Toolkit Maintainer",
  "updated_at": "2026-04-03",
  "tags": ["git", "commit", "workflow"]
}
```

## 公開 Skills 與管理者 Skills 的差異

- `skill-base/`
  - 給其他專案安裝用
  - 由 `skill-manager.sh` 管理
  - 應保持通用、可分發、可重用
- `.agents/skills/`
  - 給這個 repo 的維護者使用
  - 不由 `skill-manager.sh` 安裝或列出
  - 用來協助建立、更新、審查 `skill-base/` 內容

## 新增公開 Skill

1. 在 `skill-base/` 下建立新資料夾
2. 加入 `SKILL.md` 與 `metadata.json`
3. 視需要加入 `scripts/`、`references/`、`examples/`、`assets/`
4. 在測試專案中執行 `skill-manager.sh` 驗證安裝與更新流程
5. 提交變更

## 維護原則

- `AGENTS.md` 放規矩，skills 放招式
- 管理者技能不放進 `skill-base/`
- 變更既有公開 skill 時，更新 `metadata.json.version`
- 避免殘留任何與其他工具或舊結構耦合的目錄與文案
