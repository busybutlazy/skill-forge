# Source Inventory：grilling

- Capabilities：決策樹追蹤、逐題訪談、依賴排序、推薦答案、環境查證、等待決策者確認。
- Triggers：計畫、設計或想法需要 pressure-test；本地定位改為由 workflow 呼叫。
- Do not use：不得用批次問卷；不得替使用者決策；不得先行實作。
- Support files：`agents/openai.yaml` 只提供 display metadata，已映射至 target frontmatter。
- Workflow order：建立分支 → 查證事實 → 單題提問與推薦 → 等待 → 收斂。
- Output contract：共同理解與已分類的決策狀態。
- External dependencies：無。
- Permission-sensitive behavior：原文「Do not act」必須保留；本地需明示 authority 繼承 caller。
