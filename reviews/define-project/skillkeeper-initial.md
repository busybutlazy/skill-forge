# Skillkeeper Initial：define-project

## 來源摘要

`define-project` 依據本專案核准的 Change B 規格原創，用來把已收斂決策整理為可批准的 Project Definition；不是 Matt Pocock `to-spec` 的匯入或改編。

## 納管價值與風險

它補足 decision readiness 與 bootstrap 之間的 synthesis 階段。主要風險是自行補完未決策答案、把 implementation detail 寫成 contract，或未經人類批准進入 bootstrap。

## Canonicalization constraints

- blocking ambiguity 必須路由 `grill-with-docs`
- 只寫 project-definition artifacts
- Walking Skeleton 必須可執行且跨主要邊界
- Roadmap 必須依 observable vertical outcomes 拆分
- 完成後停止等待 human project approval

## Must preserve

- readiness admission gate
- SPEC／必要 CONTRACTS／ROADMAP
- intentionally deferred decisions
- Project Approval Packet
- production implementation authority prohibition

## Removable only if justified

- 無。

## Verdict

`allow`
