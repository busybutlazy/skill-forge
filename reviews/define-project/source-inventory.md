# Source Inventory：define-project

- Source：skill-forge Change B project-definition requirements；本地原創，無外部 source files。
- Capabilities：readiness admission、project synthesis、contract identification、Walking Skeleton、Roadmap phases、approval packet。
- Triggers：決策已完整但尚未形成正式 project definition。
- Do not use：blocking decisions 尚存、需要選方案、production implementation、bootstrap。
- Support files：`references/PROJECT_APPROVAL_PACKET_TEMPLATE.md`；組裝 approval packet 時必須使用。
- Workflow order：讀 readiness/context/ADR → admission → synthesize → outputs → approval packet → stop。
- Output contract：`docs/SPEC.md`、條件式 `docs/CONTRACTS.md`、`docs/ROADMAP.md`、Project Approval Packet。
- External dependencies：無。
- Permission-sensitive behavior：只可寫 project-definition artifacts；兩個 target 均須禁止 implicit invocation。
