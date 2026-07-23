# Skillkeeper Initial：grill-with-docs

## 來源摘要

來源為 Matt Pocock `skills/engineering/grill-with-docs`，是 `grilling` 與 `domain-modeling` 的 user-facing 組合入口。

## 納管價值與風險

此入口直接補足模糊專案到 decision readiness 的流程。上游 instruction 極短，功能契約分散於兩個 dependencies；本地 adaptation 必須完整展開 admission、readiness summary 與寫入邊界，但不能把它縮為另一 workflow 的提問章節。

## Must preserve

- user-facing explicit invocation
- 完整 grilling 行為
- glossary inline capture
- sparse ADR
- codebase fact lookup
- 在 spec/planning 之前完成決策收斂

## Removable only if justified

- 上游 `to-spec → to-tickets` 專屬路由

## Verdict

`allow`
