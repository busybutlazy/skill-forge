# DTO Inventory Builder

把專案中的 API request / response 結構整理成可讀文件，方便維護、review 與跨團隊溝通。

**使用時機**：需要產生或更新 API DTO 文件、盤點現有 schema 結構、或比對新舊版本差異時。
**不適用**：修改程式碼邏輯、重構 schema 設計——這些應另開獨立工作。

## Default Output

- 路徑：`docs/DTOs/DTO_{YYYY-MM-DD}.md`
- 若 `docs/DTOs/` 目錄不存在，先建立再寫入

## Operating Principles

- 以現有程式碼與 schema 為準，不憑空補欄位定義
- 欄位語意不清時要標記問題，而不是自行猜測
- 同一份文件內盡量統一欄位命名與型別描述方式
- 共用型別要抽出整理，避免同樣內容重複出現

## Workflow

### 1. Discover endpoints and schemas

如果使用者有指定範圍（特定資料夾、模組或端點），先以該範圍為主；否則搜尋整個專案的：

- router / controller / handler
- request schema
- response schema
- DTO class、type、interface
- 相關 decorator、annotation、serializer 定義

列出找到的端點清單，必要時請使用者補充遺漏來源，再繼續後續步驟。

### 2. Check existing DTO docs

查看 `docs/DTOs/` 是否已有舊文件。

- **首次建立**：標記文件標頭為「初次建立」，跳過 diff。
- **已有舊版**：讀最新一份作為比對基準，在新文件標頭以 changelog 格式整理新增、刪除、變更的端點與欄位摘要。

### 3. Build endpoint sections

每個端點至少整理：

- method
- path
- request fields
- response fields
- 欄位型別
- 是否必要
- 欄位說明

如果遇到巢狀結構，展開到可讀程度，不要只寫一個模糊型別名稱。

### 4. Extract shared types

將跨端點重複出現的結構整理到共用型別區塊，減少文件重複與維護成本。

### 5. Flag documentation risks

主動指出：

- 同名欄位但語意不同
- 缺少說明的欄位
- 結構不一致的 payload
- 明顯難以維護的 schema 設計

如果問題需要改程式碼才能解決，先向使用者說明，再決定是否另開修改工作。

### 6. Write the document and confirm

寫入文件後，向使用者回報：

- 產生的檔案路徑
- 涵蓋的端點數量
- changelog 摘要（如有舊版比對）
- 尚未釐清的欄位或風險（若無則明確說明「無待釐清項目」）

**完成標準**：所有已發現端點均有對應章節、共用型別已抽出、風險已標記、回報訊息已送出。
