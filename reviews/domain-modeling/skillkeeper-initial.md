# Skillkeeper Initial：domain-modeling

## 來源摘要

來源為 Matt Pocock `skills/engineering/domain-modeling`，包含 ubiquitous language、scenario testing、code contradiction 與 sparse ADR 方法。

## 納管價值與風險

它補足決策過程中的術語、邊界與 invariant 管理。風險是把推測寫入 glossary、ADR 膨脹或越權修改程式碼。

## Must preserve

- fuzzy/overloaded term 挑戰
- concrete scenario 與 code cross-reference
- confirmed terms inline 寫入 glossary
- `CONTEXT.md` 僅作 glossary/domain context
- ADR 三條件缺一不可
- lazy artifact creation

## Removable only if justified

- 直接 user invocation 定位

## Verdict

`allow`
