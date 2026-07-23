# Source Inventory：domain-modeling

- Capabilities：定義概念、entity、relationship、boundary、invariant；scenario 壓測；code/document contradiction；glossary；sparse ADR。
- Triggers：主動改變 domain model；本地主要由 workflow 呼叫。
- Do not use：單純讀 vocabulary；不得把未確認推測寫成定義；不得把 `CONTEXT.md` 當 spec 或 scratchpad。
- Support files：`CONTEXT-FORMAT.md`、`ADR-FORMAT.md` 必須保留且在相應寫入時查閱；`agents/openai.yaml` 映射 target frontmatter。
- Workflow order：讀現況 → 挑戰術語 → scenario/code 驗證 → 確認 → inline glossary / sparse ADR。
- Output：confirmed glossary/domain context 與必要 ADR。
- External dependencies：無。
- Permission-sensitive：寫入需由 calling workflow 與 repository policy 授權。
