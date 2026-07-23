# Lifecycle Decision Contracts Final Review Packet

## 審查範圍

本 packet 整理 `grilling`、`grill-with-docs`、`define-project` 與 `deliver-roadmap-phase` 最終決策契約，供獨立 reviewer 與人類審核。它不改寫先前匯入階段的 `reviews/*/reviewer-report.md`，也不宣稱取代獨立 review。

| Skill | Version | Package SHA-256 |
|---|---|---|
| `grilling` | `0.3.0` | `7f7ed9c1c27cb036e13368b21b16f9c0ce88d874c1ece97faa00f35cd839a530` |
| `grill-with-docs` | `0.3.0` | `c9bb7f6c5b2b969406142f58c037b9b3a7304c6df1a53466b10e618c6515a498` |
| `define-project` | `0.3.0` | `f8bf0ed4dd78ae8d4da166dde2f8f7dc1b082ebc14042754ed79f4eab621584d` |
| `deliver-roadmap-phase` | `0.3.0` | `d842d5627deb3ef96f57735a79585bca694d14eba78ec53e17711f1068629cce` |

## Revision Inputs

- 人工 review：完整 decision inventory、Safe Deferral、Roadmap Decision Gates。
- 再審建議：Implementation-Owned Gate、前瞻式 deferral、non-start gate enforcement、readiness status、equivalent evidence、enabling Phase、approval owner。
- 人工補充：第三種 `Incomplete` 狀態、freshness／scope／conflict、progressive disclosure。

## Evidence Mapping

| Required behavior | Canonical location | Challenge performed | Expected result |
|---|---|---|---|
| 技術選擇不得自動視為 implementation-owned | `grilling/references/DECISION_OWNERSHIP.md` | retry、soft delete、transaction、authentication storage 是否可能改變 observable behavior 或 authority | 任一 gate 失敗或分類不確定時，改列 user-owned 或 blocking |
| 尚未建立下游文件不得成為 safe-deferral 理由 | `grill-with-docs/instruction.md` Safe Deferral Gate | 在 SPEC／Roadmap 尚不存在時嘗試延後 contract 或 ownership 決策 | 必須證明下一 artifact 與 trigger 前授權工作不需假設答案 |
| 中途停止不得誤報 ready 或正式 blocker assessment | `grill-with-docs/references/READINESS_SUMMARY_FORMAT.md` | 使用者在 inventory 未完成時結束 session | 使用 `Incomplete — Session Stopped Before Readiness Assessment` |
| Decision Inventory 必須承接 method output | `grill-with-docs/references/DECISION_INVENTORY_FORMAT.md` | implementation defaults、dependencies 或 inventory gaps 是否可能從 summary 消失 | 完整 inventory 為必要 artifact；summary 引用它 |
| Equivalent evidence 不得繞過 readiness | `define-project/references/DECISION_READINESS_EVIDENCE.md` | 使用過期 README、部分 ADR 或互相矛盾的 code 作為 readiness | completeness、scope、freshness、conflict 任一無法成立即拒絕 admission |
| Enabling Phase 不得偽裝成 outcome slice | `define-project/instruction.md` Roadmap phase rules | foundation-only Phase 是否可無條件通過 | 只有可獨立驗證、為後續必要且不能安全併入第一個 dependent slice 時允許 |
| 非 start Decision Gate 不得被忽略 | `deliver-roadmap-phase/instruction.md` Phase Workflow | gate 位於 child start 或 Phase completion | 轉為 human checkpoint，阻擋 named child、dependent work 或 completion |
| Deferred owner 不得在批准時消失 | `define-project/references/PROJECT_APPROVAL_PACKET_TEMPLATE.md` | approval packet 是否只保留 rationale／trigger | 必須保留 affected scope、owner 與 Roadmap gate／trigger |

## Adversarial Cases

獨立 reviewer 應至少挑戰：

1. blocking decision 是否可被重新標成 deferred，而不證明 trigger 前工作安全。
2. implementation-owned default 是否能改變 observable behavior、security、data semantics 或 acceptance。
3. partial／stale／conflicting evidence 是否能被稱為 equivalent evidence。
4. 使用者中途停止時，workflow 是否錯誤宣告 blocker assessment 已完成。
5. child-specific 或 Phase-completion Decision Gate 是否能在 execution 中被略過。
6. enabling Phase 是否只是未受約束的 horizontal technical layer。

## Reviewer Status

`Pending independent review`

此 packet 只整理修正契約與 challenge cases。最終 `pass`／`revise` verdict 必須由未執行本次修改的 reviewer 或人類給出。

## Open Questions for Human Review

- Decision Inventory 的 repository-specific canonical path 是否需要由個別專案規則固定。
- 大型 Roadmap 是否需要獨立機械檢查 Decision Gate 與 child Change mapping。
- 是否要在未來版本將 readiness evidence schema 提供為 machine-readable format。
