# Roadmap

這個檔案作為 roadmap 索引，讓後續工作依 phase 逐步落地。

phase 1 到 phase 6 已經把這個 repo 從單一工具導向的 manager，收斂成以 `canonical-skills/` 為唯一 canonical source tree、可 render 到 Codex 與 Claude 的 toolkit。

接下來的方向不再只是「把 skill 裝進工具」，而是把這個 repo 往更清楚的產品定位收斂：

- 企業可控的 AI coding skill 管理
- 避免工程師各自安裝來源不明的第三方 skill
- 用 canonical source 降低 vendor lock-in
- 未來可透過新增 adapter 支援新的開發 AI 工具

目前的判斷是：

- 近期重點不是做漂亮 GUI
- 近期重點是把 trust、governance、portability、adoption story 講清楚並逐步落地
- 介面層維持 CLI / TUI 優先；若未來要做 UI，也應先做管理面板型 UI，而不是純展示型前端

## 執行順序

1. [Phase 1: 穩定現有 Codex manager](archive/phases/phase1.md)
2. [Phase 2: 建立中立 skill source 與 adapter](archive/phases/phase2.md)
3. [Phase 3: 重構 manager/validator/render pipeline](archive/phases/phase3.md)
4. [Phase 3.5: 收斂 pipeline 缺口並固定 CLI 契約](archive/phases/phase3.5.md)
5. [Phase 3.6: 補齊 install safety 與 phase 完成紀錄](archive/phases/phase3.6.md)
6. [Phase 4: 容器化開發與測試環境](archive/phases/phase4.md)
7. [Phase 5: 將 toolkit 發布為容器化 CLI](archive/phases/phase5.md)
8. [Phase 6: 恢復 project-local UX 與互動式 skill manager](archive/phases/phase6.md)
9. [Phase 7: 明確化 enterprise skill governance 定位並補齊 adoption 基礎](archive/phases/phase7.md)
10. [Phase 8: Canonicalize Maintainer Workflows and Improve Maintainer UX](archive/phases/.md)

## 完成狀態

- Phase 1: 已完成（歷史 shell manager 穩定化；目前已由 Python CLI 與 `skill-manager` wrapper 取代）
- Phase 2: 已完成
- Phase 3: 已完成
- Phase 3.5: 已完成
- Phase 3.6: 已完成
- Phase 4: 已完成
- Phase 5: 已完成
- Phase 6: 已完成
- Phase 7: 已完成（確立對外定位、治理敘事、adoption guide、quickstart/demo，作為 `1.0.0` 文件基線）
- Phase 8: 進行中（把 maintainer skills 納入 canonical source、補 maintainer terminal 文件、加入手動 metadata/sync 工具）

## 已決定方向

- 使用者介面近期維持 CLI / TUI，不優先做 GUI。
- 公開 skill 的唯一來源是 `canonical-skills/regular-skills/`。
- 管理者工作流 skill 應收斂在 `canonical-skills/manager-skills/`，不可混入一般 user path。
- Codex 與 Claude 都視為 canonical source 的 rendered target。
- `version` 保留做人類可讀版本；完整性檢查由 manifest 與 package hash 負責。
- phase 3 後以 Python CLI 為主入口。
- 產品定位偏向 enterprise skill governance / supply chain，而不是 skill marketplace。
- 核心價值之一是保留 AI vendor portability；canonical source 應可透過新增 adapter 擴展到更多 target。
- 若未來做 UI，優先順序應是管理型 UI，例如 catalog、approval、audit、compatibility，而不是單純漂亮首頁。

## 產品定位

目前最合理的定位是：

- `Canonical source for enterprise AI development skills`
- `Secure skill supply chain for coding agents`
- `Write skills once, govern centrally, deploy to multiple coding AI targets`

換句話說，這個 repo 不是要做另一個公開 skill marketplace，而是要讓團隊或公司能：

- 用單一 canonical source 管理內部 skill
- 驗證來源、版本與完整性
- 集中控管分發
- 降低對單一 AI coding tool 的綁定

## Phase 7 之後的優先順序

phase 7 起，優先處理的不是視覺 UI，而是 adoption 與治理能力：

1. 更清楚的定位與 README 首屏敘事
2. 更容易理解的 demo 與 quickstart
3. canonical skill 的治理能力與 trust story
4. 新 target adapter 的擴充模型
5. 之後才考慮企業管理面板或更完整的 UI

## Backlog

以下需求保留到 phase 7 與後續 phase 排程時再細分：

### Product and Adoption

- [ ] 改寫 README 首屏，明確主打 enterprise governance 與 vendor portability
- [ ] 補一個對外一句話定位與使用情境圖
- [ ] 補 canonical source -> Codex / Claude render 的示意圖或 demo
- [ ] 補「為什麼不是 marketplace」與「和官方 skills 能力如何分工」的說明
- [ ] 補一份面向團隊 / 公司導入的 adoption guide

### Governance and Trust

- [ ] 規劃 private registry / approved catalog 模型
- [ ] 規劃 skill provenance、signing 或等價 trust model
- [ ] 規劃 policy enforcement，例如 allowlist / denylist
- [ ] 規劃 audit log 與 skill lifecycle 記錄
- [ ] 規劃 maintainer workflow 與 consumer workflow 的權限分離

### CLI Enhancements

- [ ] 支援非互動模式，例如 `skill-toolkit install commit --yes`
- [ ] 支援依 tag 或 target 篩選 skill
- [ ] 支援以關鍵字搜尋名稱、描述與 tags
- [ ] 加入 preset 機制，一次安裝一組常用 skills
- [ ] 為大量 skill 清單加入分頁或更好的排版
- [x] 支援維護者快速同步 repo 內 maintainer canonical skills 到本地環境

### Metadata and Validation

- [ ] 定義更完整的 canonical metadata schema 驗證
- [ ] 支援 skill 相依性欄位
- [ ] 對 major version 升級顯示更醒目的提示
- [ ] 規劃自動檢查 frontmatter 與 identity / rendered metadata 一致性
- [x] 定義 maintainer/public skill scope 並避免來源混淆
- [ ] 規劃 target capability matrix，明確標示不同 AI target 支援哪些欄位與能力

### Quality

- [ ] 補更完整的 integration tests
- [ ] 補公開版貢獻指南
- [ ] 補 phase 4 / phase 5 的 CI 驗證流程

### UI and Management Surface

- [ ] 先評估是否真的需要 web UI，再決定是否立項
- [ ] 若要做 UI，優先做管理面板而不是 marketing site
- [ ] 管理面板候選功能：catalog、approval、status、compatibility、audit
