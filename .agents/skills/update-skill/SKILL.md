---
name: update-skill
description: "Use this skill when the user wants to modify an existing public skill in this repository's skill-base, revise its workflow, or update its metadata and version."
---

# Update Public Skill

用來修改 `skill-base/` 中既有的公開 Codex skill。

## Use This For

- 更新 skill workflow
- 調整 trigger description
- 修正 metadata
- 升級 skill 版本

## Do Not Use This For

- 修改 `.agents/skills/` 的管理者技能
- 安裝或移除其他專案的 skills
- 建立全新的 skill

## Workflow

### 1. Inspect the current skill

先讀：

- `skill-base/<skill-name>/SKILL.md`
- `skill-base/<skill-name>/metadata.json`

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

只改真正需要改的部分，避免把 skill 改成另一個任務。

### 3. Update metadata

同步調整：

- `version`
- `updated_at`
- 必要時調整 `description`、`tags`

版本規則：

- 小修正：patch
- 新增能力或顯著流程調整：minor
- 不相容重寫或定位改變：major

### 4. Validate publishability

確認：

- skill 仍屬於公開可分發內容
- 名稱與資料夾一致
- metadata 與 `SKILL.md` 沒有互相矛盾
- 說明不依賴舊工具或已淘汰目錄

### 5. Check manager impact

如果這次修改會影響安裝與更新流程，記得一起檢查：

- `skill-manager.sh`
- `README.md`
- 版本顯示與更新提示是否仍合理
