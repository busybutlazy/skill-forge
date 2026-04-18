# Reviews Summary

這份摘要用來保留 `reviews/` 內審查紀錄的最小必要資訊，方便後續刪除細節檔時仍能看懂決策脈絡。

## verified-operator

來源：

- source root: `tmp/foreign_skills/soxakore-codex-engineering-skills-verified-operator-1`
- source type: single skill folder
- requested canonical name: `verified-operator`

結論：

- 初次準入：`allow`
- reviewer fidelity：`pass`
- 最終準入：`admit`

保留理由：

- skill 明確面向「實際操作並驗證結果」的工作，不是單純敘述型 prompt
- 核心能力包含 world model、risk grading、receipts、rollback、drift recovery、checkpoint、completion bar
- 複雜任務能力完整保留：dependency graph、confidence scoring、invariants、failure taxonomy、multi-phase orchestration、temporal reasoning
- `examples/` 與 `templates/templates.md` 都仍被保留且仍有明確使用時機

審查後接受的 canonicalization：

- source frontmatter 改映射到 canonical `package.json`
- `agents/openai.yaml` 改映射到 target frontmatter
- canonical 名稱使用 `verified-operator`，不沿用外部來源資料夾 slug
- 指令內容可做最小重寫與精簡，但不得移除 safety rules、support-file hooks、advanced sections 與 trigger boundaries

主要風險：

- instruction 偏長，後續維護容易 drift
- 目前 repo tooling 不會把 `templates/` 納入 manifest integrity；`templates/templates.md` 仍需靠人工 review 與 diff 追蹤
- promote 前仍需明確決定此 skill 應進 `regular-skills` 或 `manager-skills`

建議保留的最小紀錄：

- intake verdict: `allow`
- reviewer verdict: `pass`
- final verdict: `admit`
- must-preserve areas: risk model、approval gates、receipts/rollback/checkpoint、examples/templates、advanced sections
- unresolved risks: `templates/` integrity 尚未被 tooling 覆蓋

對應細節檔：

- `reviews/verified-operator/skillkeeper-initial.md`
- `reviews/verified-operator/source-inventory.md`
- `reviews/verified-operator/reviewer-report.md`
- `reviews/verified-operator/skill-review-packet.md`
- `reviews/verified-operator/skillkeeper-final.md`
