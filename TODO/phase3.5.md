# Phase 3.5 - Close the Pipeline Gaps Before Containerization

## Goal

在不擴張到 phase 4 容器化開發環境與 phase 5 容器化發佈的前提下，先把 phase 3 已經落地但仍未收斂的管理、狀態判定、安裝安全性、測試與文件缺口補齊，讓後續容器化只是在包裝一條穩定的 CLI pipeline，而不是把未完成的核心邏輯一起打包。

## Why This Phase Exists

目前 repo 已經有可用的 Python CLI、canonical validator、renderer 與雙 target install pipeline，但還有幾個會直接影響 phase 4 / phase 5 的缺口：

- phase 3 規劃中的 `update` 尚未實作
- install 行為目前偏向直接覆蓋，缺少更清楚的 safety model
- `list` 雖有狀態分類，但測試與文件主要覆蓋 happy path，對 `broken`、`unmanaged`、`update_available` 的驗證還不完整
- README 目前同時混有 repo 開發用法與 end-user 使用方式，且部分指令前提不夠明確
- phase 4 與 phase 5 都假設 CLI 已經穩定可預測，因此這些缺口應在容器化前先收斂

## Decisions Locked In

- `canonical-skills/` 仍是唯一公開 source of truth。
- phase 3.5 不重做 phase 3 架構，不回退到 shell manager。
- phase 3.5 不直接做 Dockerfile、compose、devcontainer 或 runtime image。
- phase 3.5 優先補齊 CLI 契約與測試，而不是加入大量新 UX 功能。
- phase 3.5 可以調整現有 CLI 子命令與文件，只要不破壞 canonical source model。

## Scope

- 補齊 phase 3 遺漏的 CLI 責任。
- 重新定義 install / update 的安全規則。
- 補齊已安裝狀態判定與對應測試。
- 補齊 phase 3 README 與操作文件，使 phase 4 容器化時可以直接沿用。
- 釐清哪些功能屬於 phase 3.5 必做，哪些延後到 phase 4 / phase 5 或 backlog。

## Work Items

1. Add explicit `update` command
   - 實作 `update` 子命令，讓使用者可以基於 canonical source 更新已安裝 skill。
   - `update` 必須沿用 render pipeline，不可直接手改 target artifact。
   - phase 3.5 先支援單一 skill 更新，不要求同一版就提供全量更新。

2. Tighten install and overwrite rules
   - install 到既有 managed package 時，預設直接覆蓋，不要求先執行 `update`。
   - 對 `broken`、`drift`、`unmanaged` 目標分別定義 install / update / remove 的處理規則。
   - CLI 與 README 必須明確說明直接覆蓋模式的效果與風險。

3. Complete installed status contract
   - 重新檢查 `up_to_date`、`update_available`、`drift`、`broken`、`unmanaged` 的判定條件是否完整且互斥。
   - `drift` 定義為 package 仍可辨識為 toolkit 管理物，但內容或 source hash 已與 canonical source 不一致；`broken` 則是必要檔案缺失、格式錯誤或無法完成基本解析。
   - 補齊 Codex 與 Claude target 對應的 broken / foreign install / local drift 偵測。
   - 規範 `list` 輸出的欄位與可預期含義，避免 phase 5 容器輸出格式漂移。
   - phase 3.5 要新增穩定的 `--json` 輸出選項，讓 phase 4 / phase 5 與後續自動化可以直接依賴機器可解析格式。

4. Strengthen automated tests
   - 補齊 `validate`、`render`、`install`、`list`、`remove`、`update` 的基本自動化測試。
   - 新增針對 `broken`、`unmanaged`、`update_available`、`drift` 的負面與邊界情境測試。
   - 保留 phase 3 現有 smoke tests，同時補至少一組更接近真實使用的 install lifecycle 測試。

5. Refresh documentation for stable CLI usage
   - README 明確分開「維護者開發用法」與「一般使用者安裝 / 使用用法」。
   - 文件要寫清楚 `python3 -m skill_toolkit` 與 `skill-toolkit` 的前提條件。
   - 文件要反映實際存在的子命令、狀態值與 install/update/remove 規則。
   - phase 4 容器化段落只保留銜接說明，不提前混入具體容器指令。

6. Clean up phase 3 leftovers that affect future phases
   - 確認 `skill-base/` 已不再參與任何正式流程，避免 phase 4 / 5 容器內外行為不一致。
   - 確認 proof artifact、canonical source、README 說明之間沒有互相矛盾的地方。
   - 對外使用入口應只剩 Python CLI；相容 wrapper 只保留提示用途。

## Acceptance Criteria

- CLI 正式支援 `validate`、`render`、`install`、`list`、`remove`、`update` 六個核心操作。
- `list` 可以穩定區分 `up_to_date`、`update_available`、`drift`、`broken`、`unmanaged`，且至少有自動化測試覆蓋各狀態。
- install / update / remove 對 managed、broken、drift、unmanaged package 的處理規則有明確文件與測試。
- README 與實際 CLI 行為一致，不再依賴隱含前提才能成功執行。
- phase 4 可以直接把這條 CLI pipeline 放進容器驗證，而不需要先補核心行為。
- phase 5 可以直接沿用 phase 3.5 收斂後的 CLI 契約作為 container entrypoint 基礎。

## Relationship to Phase 4 and Phase 5

- phase 3.5 不負責提供容器環境，但必須讓 phase 4 有一條穩定、可測的 CLI 可以搬進容器。
- phase 3.5 不負責發布 container image，但必須先固定 CLI 命令、狀態輸出與檔案覆蓋規則，避免 phase 5 包出一個行為仍會變動的 image。
- phase 4 驗證的是環境可重現性；phase 3.5 驗證的是 CLI 契約完整性。
- phase 5 驗證的是發佈形式；phase 3.5 驗證的是發佈內容本身已經可靠。

## Confirmed Direction

1. `install` 遇到既有 managed package 時，預設直接覆蓋，不要求先走 `update`。
2. `update` 遇到 `drift` 狀態時，允許強制覆蓋，但必須先顯示清楚警告與確認提示，讓使用者知道本地修改或異常內容將被覆寫。
3. `remove` 允許移除帶有 toolkit marker 的 `broken` 安裝，不限於完全健康的 managed package。
4. `list` 在 phase 3.5 就新增 `--json`，固定機器可解析輸出契約。
5. `update` 在 phase 3.5 先只做單一 skill 更新；全量更新延後。

## Explicitly Out of Scope

- Dockerfile、compose、`.devcontainer/`
- 對外發布 container image
- 非互動模式大擴充，例如 `--yes`、preset、search、filter、pager
- 第三種 target
- 完整 schema evolution 或 dependency system
