# Source Inventory：grill-with-docs

- Capabilities：以 `grilling` 逐題收斂決策，並用 `domain-modeling` 留下 glossary/ADR paper trail。
- Triggers：模糊新專案、重大變更、domain/contract/architecture 不確定；明確 user-facing entrypoint。
- Do not use：明確小改、已批准執行、單純 verification/review、已知 root cause 修復。
- Support files：上游無直接 support files；依賴 skill 的 references 隨 dependency 安裝。
- Workflow order：讀 repository/doc/code → decision tree → dependency-order grill → domain artifacts → readiness output。
- Output：Decision Readiness Summary，含 resolved/deferred/blocking/conflicts/artifacts/next route。
- Dependencies：`grilling`、`domain-modeling`。
- Permission-sensitive：只可寫 definition/decision artifacts；不得 implementation 或自行批准。
