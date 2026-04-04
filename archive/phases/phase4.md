# Phase 4 - Containerize the Development and Test Environment

## Goal

提供一致、乾淨、可重現的容器化開發與測試環境，讓 phase 3 的 Python CLI 可以在不依賴 host 差異的前提下被驗證。

## Decisions Locked In

- 本 phase 的重點是維護者環境，不是最終對外發布 image。
- phase 3 的 Python CLI 與 canonical source model 已存在，phase 4 不重做核心功能。
- 容器內應能直接跑 validate/render/install/list/remove 的測試流程。

## Scope

- 建立開發用 Dockerfile。
- 規劃簡單的 compose 或等價啟動方式。
- 視需要加入 `.devcontainer/`。
- 補 README 中的容器化開發說明。

## Acceptance Criteria

- 維護者可在乾淨容器內跑 phase 3 測試。
- 維護者可在容器內對本 repo 執行 Python CLI。
- 容器環境可以重現 canonical validation 與 target render/install smoke tests。

## Out of Scope

- 正式對外發布 skill-forge image
- 以容器作為一般使用者的唯一使用方式
