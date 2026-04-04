# Roadmap

這個檔案作為 roadmap 索引，讓後續工作依 phase 逐步落地。

## 執行順序

1. [Phase 1: 穩定現有 Codex manager](TODO/phase1.md)
2. [Phase 2: 建立中立 skill source 與 adapter](TODO/phase2.md)
3. [Phase 3: 重構 manager/validator/render pipeline](TODO/phase3.md)
4. [Phase 3.5: 收斂 pipeline 缺口並固定 CLI 契約](TODO/phase3.5.md)
5. [Phase 3.6: 補齊 install safety 與 phase 完成紀錄](TODO/phase3.6.md)
6. [Phase 4: 容器化開發與測試環境](TODO/phase4.md)
7. [Phase 5: 將 toolkit 發布為容器化 CLI](TODO/phase5.md)
8. [Phase 6: 恢復 project-local UX 與互動式 skill manager](TODO/phase6.md)

## 完成狀態

- Phase 1: 已完成（歷史 shell manager 穩定化；目前已由 Python CLI 與 `skill-manager` wrapper 取代）
- Phase 2: 已完成
- Phase 3: 已完成
- Phase 3.5: 已完成
- Phase 3.6: 已完成
- Phase 4: 已完成
- Phase 5: 已完成
- Phase 6: 已完成

## 已決定方向

- 使用者介面維持 CLI，不做 GUI。
- 公開 skill 的唯一來源是 `canonical-skills/`。
- Codex 與 Claude 都視為 canonical source 的 rendered target。
- `version` 保留做人類可讀版本；完整性檢查由 manifest 與 package hash 負責。
- phase 3 後以 Python CLI 為主入口。

## Backlog

以下需求保留到前六個 phase 完成後再排程：

### CLI Enhancements

- [ ] 支援非互動模式，例如 `skill-toolkit install commit --yes`
- [ ] 支援依 tag 或 target 篩選 skill
- [ ] 支援以關鍵字搜尋名稱、描述與 tags
- [ ] 加入 preset 機制，一次安裝一組常用 skills
- [ ] 為大量 skill 清單加入分頁或更好的排版
- [ ] 支援維護者快速同步 repo 內 `.agents/skills/` 到個人環境

### Metadata and Validation

- [ ] 定義更完整的 canonical metadata schema 驗證
- [ ] 支援 skill 相依性欄位
- [ ] 對 major version 升級顯示更醒目的提示
- [ ] 規劃自動檢查 frontmatter 與 identity / rendered metadata 一致性
- [ ] 檢查 public skill 名稱與 maintainer skill 名稱是否衝突

### Quality

- [ ] 補更完整的 integration tests
- [ ] 補公開版貢獻指南
- [ ] 補 phase 4 / phase 5 的 CI 驗證流程
