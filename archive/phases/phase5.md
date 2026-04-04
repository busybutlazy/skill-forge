# Phase 5 - Ship skill-forge as a Containerized CLI

## Goal

把 phase 3 的 Python CLI 打包為可直接執行的 container image，讓使用者可以透過掛載專案目錄來執行 validate/render/install/list/remove。

## Decisions Locked In

- phase 5 建立在 phase 3 與 phase 4 完成後的穩定 CLI 上。
- container image 是額外發佈形式，不改變 canonical source model。
- host project 需以 volume mount 形式提供給 container。

## Scope

- 建立正式 runtime Dockerfile。
- 設計 image entrypoint。
- 補容器執行文件與版本標記方式。
- 定義 project mount、output path、檔案權限規則。

## Acceptance Criteria

- 使用者可透過 `docker run` 或等價方式執行 skill-forge CLI。
- 容器內執行結果與本地 Python CLI 一致。
- target artifact 可正確寫回掛載的 host project。

## Out of Scope

- GUI
- 第三種 target
- phase 5 內一次完成所有進階 CLI UX 功能
