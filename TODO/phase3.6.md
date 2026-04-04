# Phase 3.6 - Tighten Install Safety and Record Phase Completion

## Goal

把這次 phase review 發現的 phase 3.5 殘留缺口正式收斂，避免 repo 在進入 phase 4 / phase 5 前，仍把 install safety 規則留在「文件有說，但行為尚未完全對齊」的狀態。

## Why This Phase Exists

這次檢查後，phase 2、phase 3、phase 4 都已具體落地，phase 3.5 也大致完成，但還有一個不應直接帶進後續 phase 的缺口：

- `install` 目前對既有目標幾乎是直接刪除後覆蓋，尚未先明確區分 `managed`、`drift`、`broken`、`unmanaged`
- README 已寫出 install / update / remove 規則，但 `install` 的實際安全模型還沒有完整反映這些規則
- phase 文件本身缺少一份回顧後的 completion record，導致之後很難快速判斷哪些 phase 已完成、哪些只是大致完成

## Decisions Locked In

- phase 3.6 不重做 canonical source model。
- phase 3.6 不擴張到 phase 4 容器功能或 phase 5 runtime image。
- phase 3.6 是 phase 3.5 的補完，不是新架構 phase。
- `install`、`update`、`remove` 的規則要以可測試的 CLI 行為為準，不能只有 README 描述。

## Scope

- 補齊 `install` 對既有目標狀態的安全判定。
- 讓 README 與 CLI 行為重新對齊。
- 補一輪對應測試。
- 記錄 phase review 的結論，避免後續再次重複盤點同一批問題。

## Work Items

1. Tighten install safety rules
   - `install` 遇到既有 target 時，先判定 `up_to_date`、`update_available`、`drift`、`broken`、`unmanaged`
   - 明確定義哪些狀態允許直接覆蓋，哪些要拒絕，哪些要先確認
   - 至少要避免對 `unmanaged` 內容靜默刪除後覆蓋

2. Align CLI behavior with README
   - README 中的 install / update / remove 規則要與實際 CLI 完全一致
   - 若規則有變更，要同步更新 README，不保留過時敘述

3. Add regression tests for install safety
   - 補 `install` 遇到 `unmanaged`、`drift`、`broken`、`update_available` 的測試
   - 確認 Codex 與 Claude target 的行為都可預測

4. Record phase completion status
   - 在 roadmap 或相關文件補一份簡短 completion note
   - 明確標示：
     - phase 2 已完成
     - phase 3 已完成
     - phase 3.5 大致完成，但因 install safety 缺口需補 phase 3.6
     - phase 4 已完成

## Acceptance Criteria

- `install` 不會對 `unmanaged` target 做靜默覆蓋。
- `install` 對各種既有狀態的處理規則有測試覆蓋。
- README 與 CLI 行為沒有已知矛盾。
- phase 完成狀態有明確文件可查，不必再重新人工比對整個 repo。

## Out of Scope

- 新增第三種 target
- phase 5 container runtime image
- 大幅擴張 CLI UX，例如 search、preset、pager、全量 update
