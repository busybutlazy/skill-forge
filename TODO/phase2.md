# Phase 2 - Introduce a Neutral Skill Source and Target Adapters

## Goal

把 skill 的核心內容從單一工具格式中抽離，建立一份中立 source，然後透過 adapter/render 層輸出成 Codex 或 Claude 需要的格式，避免長期維護兩份容易漂移的 skill。

## Decisions Locked In

- 使用者介面仍維持 CLI，不做 GUI。
- 不直接維護兩套平行的 skill 內容。
- source model 是唯一 truth；Codex 與 Claude 的安裝內容都視為 derived artifact。
- target adapter 只負責格式轉換與少量 target-specific wrapper，不負責獨立業務邏輯。

## Scope

- 定義 canonical skill package 的資料模型。
- 定義 Codex 與 Claude 的 target output 契約。
- 選定一個最小 skill 做雙 target migration proof。

## Canonical Package Requirements

每個 skill package 至少要能表達：

- shared identity
  - `name`
  - `version`
  - `description`
  - `updated_at`
  - `tags`
- shared instructional content
- optional assets
  - `scripts/`
  - `references/`
  - `examples/`
  - `assets/`
- target-specific overrides
  - trigger wording
  - wrapper/frontmatter fields
  - install target path expectations
- integrity metadata
  - package-level hash 或 manifest 入口

## Adapter Responsibilities

1. Codex adapter
   - 產出可安裝到 `<project>/.agents/skills/<skill>/` 的 package。
   - 產出的 instruction format 要符合 Codex 的 skill 使用方式。

2. Claude adapter
   - 產出可安裝到 `<project>/.claude/agents/<skill>.md` 的 project subagent。
   - 只保留 Claude 真正需要的包裝層，不複製 Codex 專屬假設。

3. Shared renderer rules
   - 相同 skill 的核心內容只維護一份。
   - target-specific 差異必須集中在可追蹤的 override 區塊。
   - render output 必須可重現，不能依賴不穩定排序。

## Deliverables

1. 一份 canonical package spec
   - 明確定義 shared fields、target overrides、integrity fields。

2. 一份 adapter contract
   - 明確定義 Codex 與 Claude 兩種輸出的必要檔案與目標路徑。

3. 一個 migration proof
   - 選一個現有 skill，完成 source -> codex / claude 的雙輸出驗證。

4. 一份 drift policy
   - 明確規定不可直接手改 rendered artifact，source 才是唯一修改入口。

## Phase 2 Output

本 repo 的 phase 2 交付物落在：

- `docs/phase2/canonical-package-spec.md`
- `docs/phase2/adapter-contract.md`
- `docs/phase2/drift-policy.md`
- `canonical-skills/commit/`
- `proof/phase2/rendered/`

補充決議：

- Claude target contract 以 project subagent 為準，目標路徑固定為 `.claude/agents/<name>.md`
- phase 2 proof artifact 只作為 contract 驗證，不作為正式 install source

## Acceptance Criteria

- 至少一個 skill 可以從同一份 source 產出 Codex 與 Claude 兩種 package。
- 同一 skill 的共享內容不需要複製兩份維護。
- target-specific 差異可以被清楚定位，不混在共享指令主體中。
- phase 3 可以直接依照這份 spec 實作 validator 與 renderer。

## Out of Scope

- 大規模遷移所有現有 skill
- 使用者操作體驗優化
- 完整 manager 語言重寫
