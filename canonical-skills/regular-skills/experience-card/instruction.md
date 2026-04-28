# Experience Card

在 session 結束或使用者要求時，自動從對話中萃取有沉澱價值的知識，生成結構化的經驗卡片並儲存到 `docs/experience-cards/`。

## When to Use

- 使用者明確呼叫 `/experience-card`
- 使用者說「記一下」「儲存這個」「做成卡片」「幫我存下來」
- 使用者確認問題已解決並希望保留解法

## Do Not Use

- 對話中沒有明確的問題、解法、決策或教學內容
- 使用者只在閒聊，沒有實質知識產生
- 使用者明確說不需要記錄

## Card Types and Directories

| Type | Directory | 用途 |
|------|-----------|------|
| `how_to` | `docs/experience-cards/how-to/` | 操作步驟教學，例如 Word、Excel、內部系統 |
| `troubleshooting` | `docs/experience-cards/troubleshooting/` | 錯誤排除流程，例如登入失敗、系統異常 |
| `decision` | `docs/experience-cards/decision/` | 決策紀錄，例如流程改成先審核再發佈 |
| `faq` | `docs/experience-cards/faq/` | 重複出現的常見問題 |
| `warning` | `docs/experience-cards/warning/` | 容易做錯的地方 |
| `policy` | `docs/experience-cards/policy/` | 公司規範、審核規則、注意事項 |
| `training` | `docs/experience-cards/training/` | 可用於新人教育或數位工具訓練的素材 |

## Workflow

### Step 1: Session Analysis (Module 1 + 2)

回顧整個對話，找出具備沉澱價值的片段。

**有價值的訊號：**
- 問題已被解決
- 對話中出現明確操作步驟
- 形成了決策或結論
- 發現了容易出錯的地方
- 使用者說「原來是這樣」「解決了」「記一下」
- 問題有重複發生的可能性

**不需要建立卡片的情況：**
- 純粹閒聊，無實質內容
- 問題尚未解決，解法不確定
- 一次性問題，幾乎不會再發生
- 對話只是延伸討論，沒有明確結論

從 session 中找出 1-3 個候選片段，每個候選列出：
- 核心問題或主題
- 建議卡片類型（從上表選擇）
- 一行摘要

詢問使用者確認哪些要建立成卡片（或全部建立）。若明顯只有一個候選，可直接進入 Step 2 不必詢問。

### Step 2: Duplicate Check (Module 5)

在生成卡片前，先檢查是否已有類似卡片：

```bash
find docs/experience-cards/ -name "*.yaml" 2>/dev/null
```

讀取標題與 tags 相近的既有卡片內容，判斷：

| 情況 | 處理方式 |
|------|---------|
| 無相似卡片 | 直接進入 Step 3 |
| 有相似但內容不足 | 告知使用者，詢問是補充既有卡片還是建立新卡片 |
| 幾乎完全重複 | 提示既有卡片路徑，詢問是否要更新而非新建 |

若 `docs/experience-cards/` 目錄不存在，跳過此步驟直接建立。

### Step 3: Generate Card Draft (Module 3)

依照以下格式生成 YAML。根據卡片類型選用對應的欄位結構：

**`search_hint` 填寫原則**：這個欄位是專為向量搜尋設計的，不是給人讀的文件內容。
填寫時用這個問題引導自己：「一個不知道這張卡片存在的使用者，遇到這個問題時，會在搜尋框裡打什麼？」
列出 3-5 種不同說法，包含口語、同義詞、常見錯誤描述方式。
(註：RAG pipeline 建議 embed `title + search_hint` 的串接文字。)

#### How-to Card

```yaml
type: how_to
title: "動作 + 對象，例如：在 Word 中設定自動目錄"
created_at: "YYYY-MM-DD"
tags:
  - "主題關鍵字"
  - "工具或系統名稱"
search_hint: >
  使用者會用來搜尋這張卡片的 3-5 種說法，包含同義詞與口語描述。
  例如：Word 目錄怎麼做、Word 自動產生目錄、Word 章節目錄設定
audience:
  - "適用對象"
when_to_use: >
  描述什麼情境下應該用這張卡片。
  例如：當你需要在 Word 文件中建立可自動更新的目錄時。
prerequisites:
  - "執行前需要具備的條件（選填，無則省略）"
steps:
  - step: 1
    action: "具體操作描述"
    note: "注意事項（選填）"
  - step: 2
    action: "..."
expected_result: >
  完成後應看到的結果或狀態。
common_mistakes:
  - "容易犯的錯誤（至少一條）"
```

#### Troubleshooting Card

```yaml
type: troubleshooting
title: "現象 + 處理方式，例如：Word 目錄未顯示標題的排除方法"
created_at: "YYYY-MM-DD"
tags:
  - "錯誤類型"
  - "工具或系統名稱"
search_hint: >
  使用者會用來搜尋這個問題的 3-5 種說法，著重在「症狀描述」。
  例如：Word 目錄不見了、目錄標題消失、更新目錄沒有出現章節、Word 目錄只有頁碼
audience:
  - "適用對象"
symptoms:
  - "使用者看到或感受到的症狀"
cause: >
  問題的根本原因。
solution_steps:
  - step: 1
    action: "具體操作描述"
    note: "注意事項（選填）"
  - step: 2
    action: "..."
verification: >
  如何確認問題已解決。
common_mistakes:
  - "排除時容易犯的錯誤"
```

#### Decision Card

```yaml
type: decision
title: "決策主題，例如：採用先審核再發佈的內容流程"
created_at: "YYYY-MM-DD"
tags:
  - "決策領域"
  - "相關系統或流程"
search_hint: >
  使用者想查詢這個決策時會用的說法，著重在「決策主題」與「涉及的流程或系統」。
  例如：發布流程決定、內容審核規定、為什麼要先審核、發文要送審嗎
context: >
  做出這個決策的背景與驅動因素。
decision: >
  決定做什麼，以及範圍。
rationale: >
  為什麼選擇這個方向而非其他選項。
alternatives_considered:
  - "曾考慮過但沒選的方案，以及原因（一句話）"
  - "例如：直接發佈不審核 — 品質風險太高"
impact: >
  預期影響，包含誰受影響、何時生效。
```

#### FAQ Card

```yaml
type: faq
title: "問題本身，例如：為什麼簽核流程送出後沒有通知？"
created_at: "YYYY-MM-DD"
tags:
  - "問題類別"
  - "相關系統"
search_hint: >
  使用者會用來搜尋這個問題的 3-5 種說法，包含不同問法與口語表達。
  例如：簽核沒有通知、送出申請後沒收到信、審核通知沒來、沒有收到簽核提醒
audience:
  - "適用對象"
question: >
  完整且清楚的問題描述，讀者能透過標題找到這張卡片。
short_answer: >
  一句話直接回答問題。
  例如：簽核通知預設只寄給簽核人，送件人需手動勾選「副本通知我」。
details: >
  補充說明、背景原因，或有步驟時在此列出。
  例如：1. 開啟表單 2. 勾選「副本通知我」3. 送出
  若問題的回答本身已足夠清楚，可省略此欄位。
related_cards:
  - "相關卡片的標題或檔案路徑（選填，無則省略）"
```

#### Warning Card

```yaml
type: warning
title: "容易犯的錯誤，例如：不要只用加粗替代 Word 標題樣式"
created_at: "YYYY-MM-DD"
tags:
  - "錯誤類型"
  - "工具或情境"
search_hint: >
  使用者在犯了這個錯之後，或不確定做法時，會搜尋的 3-5 種說法。
  例如：Word 標題加粗目錄不顯示、Word 手動標題目錄看不到、為什麼目錄只有部分顯示
scenario: >
  在什麼情況下容易犯這個錯誤。
wrong_approach: >
  常見的錯誤做法與表面看起來合理的原因。
steps:
  - step: 1
    action: "正確做法的具體步驟"
    note: "注意事項（選填）"
  - step: 2
    action: "..."
why_it_matters: >
  為什麼這個錯誤會造成問題，後果是什麼。
```

#### Policy Card

```yaml
type: policy
title: "規範名稱，例如：內容發佈需經主管審核後才能上線"
created_at: "YYYY-MM-DD"
effective_date: "YYYY-MM-DD（此規範開始生效的日期）"
tags:
  - "規範類別"
  - "適用部門或系統"
search_hint: >
  使用者想確認規範時，會搜尋的 3-5 種說法，包含詢問式與確認式語氣。
  例如：內容可以直接發嗎、發布前要審核嗎、誰有權限上線內容、發文審核流程
scope:
  - "適用的部門、角色或情境"
  - "例如：所有對外發布的內容"
rule: >
  規範的具體內容與要求。
exceptions:
  - "例外情況說明（無例外則省略此欄位）"
rationale: >
  為什麼有這個規範，背景原因。
```

#### Training Card

Training Card 的設計目標是讓新人或不熟悉工具的員工，能夠自己看懂、解決問題、不需要再問第二次。
格式以「遇到這個情境 → 通常會怎麼做（錯在哪）→ 正確做法」為骨幹。

```yaml
type: training
title: "情境 + 處理方式，例如：Excel 公式顯示 #REF! 的處理方式"
created_at: "YYYY-MM-DD"
tags:
  - "工具或系統名稱"
  - "問題類別"
search_hint: >
  遇到這個情境的使用者，會搜尋的 3-5 種說法，用他們自己的語言。
  例如：Excel 公式出現 #REF!、公式被刪格影響、Excel 公式顯示錯誤、刪欄後公式壞掉
audience:
  - "新人"
  - "中高齡員工（選填）"
scenario: >
  描述使用者實際遇到的情境，要讓人一眼認出「這就是我遇到的狀況」。
  例如：刪除某欄後，原本正常的公式突然顯示 #REF!，不知道怎麼辦。
what_users_usually_try: >
  描述使用者通常的直覺反應，以及為什麼這樣做會出問題。
  例如：直接刪掉那格、重新輸入數字，但這樣會讓其他引用該公式的格子也跟著出錯。
cause: >
  問題的根本原因，用非技術語言說明。
steps:
  - step: 1
    action: "具體操作描述"
    note: "注意事項（選填）"
  - step: 2
    action: "..."
takeaway: >
  這張卡片最重要的一句話，讓人帶走的核心觀念。
  例如：公式有引用其他格時，不能直接刪資料，要先改公式或清空內容。
practice: "可以自己試試看的練習，例如：在空白欄位重現這個錯誤，再用上面步驟修復（選填）"
```

### Step 4: Sensitive Data Filter (Module 4)

在寫入前，對所有欄位套用以下遮蔽規則：

| 資料類型 | 遮蔽方式 |
|---------|---------|
| 個人姓名（中英文） | `某位使用者` 或 `某位同仁` |
| 電話號碼 | `[phone redacted]` |
| Email 地址 | `[email redacted]` |
| 身分證字號 | `[id redacted]` |
| 客戶或公司名稱 | `某客戶` 或 `某公司` |
| 帳號或密碼 | `[password redacted]` |
| API Key / Token / Secret | `[secret redacted]` |
| 內部路徑、IP 位址、主機名 | `[internal redacted]` |
| 合約金額或薪資數字 | `[amount redacted]` |
| 未公開業務資訊 | `[confidential redacted]` |

遮蔽後若卡片內容因此失去意義，告知使用者哪個欄位需要補充描述，請使用者提供可公開的替代說明。

### Step 5: Save Card (Module 1 - persistence)

確認使用者同意後執行儲存：

1. 建立目錄（若不存在）：
```bash
mkdir -p docs/experience-cards/<type-dir>/
```

2. 檔案命名規則：`YYYY-MM-DD_<slug>.yaml`
   - 日期為今天的 ISO 日期
   - slug 從 title 取主要關鍵字，轉為小寫英文 kebab-case（3-5 個詞）
   - 若 title 為中文，將核心概念翻譯為英文 slug

   範例：
   - `Word 目錄未顯示標題的排除方法` → `2026-04-29_word-toc-not-showing.yaml`
   - `採用先審核再發佈的內容流程` → `2026-04-29_content-review-before-publish.yaml`

3. 以 Write 工具寫入 YAML 檔案

4. 儲存成功後輸出：
   - 儲存路徑
   - 卡片標題與類型
   - 若發現相似既有卡片，提醒使用者未來可考慮合併

## Quality Bar

- 生成的卡片必須能獨立閱讀，不依賴對話上下文
- `title` 必須清楚描述問題或主題，讀者不看內容就能判斷是否相關
- `tags` 至少 2 個，包含主題關鍵字和工具/系統名稱
- 敏感資訊必須在寫入前完成遮蔽
- 不強制詢問使用者拒絕建立卡片的原因
- 同一次呼叫最多建立 3 張卡片，避免資訊爆炸
