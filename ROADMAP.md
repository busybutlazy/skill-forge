# Roadmap

這個檔案改為 roadmap 索引，讓後續 agent 可以依 phase 逐步完成。

## 執行順序

1. [Phase 1: 穩定現有 Codex manager](TODO/phase1.md)
2. [Phase 2: 建立中立 skill source 與 adapter](TODO/phase2.md)
3. [Phase 3: 重構 manager/validator/render pipeline](TODO/phase3.md)

## 已決定方向

- 使用者介面維持 CLI，不做 GUI。
- 一般使用者不需要學 Python；如果後續引入 Python，只限於 manager/validator 的維護層。
- 長期目標是 Claude 與 Codex 雙相容。
- 不直接維護兩套平行 skill 內容，而是建立中立 skill source，再輸出成各 target 需要的格式。
- `version` 保留做人類可讀版本；完整性檢查另外使用 package hash 或 manifest，不用 hash 取代版本號。

## Backlog

以下需求先保留，等前三個 phase 完成後再排程：

### CLI Enhancements

- [ ] 支援非互動模式，例如 `skill-manager.sh install commit --yes`
- [ ] 支援依 category 篩選 skill
- [ ] 支援以關鍵字搜尋名稱、描述與 tags
- [ ] 加入 preset 機制，一次安裝一組常用 skills
- [ ] 為大量 skill 清單加入分頁或更好的排版
- [ ] 支援維護者快速同步 repo 內 `.agents/skills/` 到個人環境

### Metadata and Validation

- [ ] 定義 canonical metadata schema 驗證
- [ ] 支援 skill 相依性欄位
- [ ] 對 major version 升級顯示更醒目的提示
- [ ] 規劃自動檢查 frontmatter 與 metadata 一致性
- [ ] 檢查 skill 名稱在 `skill-base/` 與 `.agents/skills/` 間是否衝突

### Quality

- [ ] 為 skill 建立簡單的驗證流程或 smoke tests
- [ ] 補一份公開版的貢獻指南
