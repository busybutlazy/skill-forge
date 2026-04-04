# Adoption Guide

## English

### Who Should Adopt This

Skill Toolkit is a strong fit for teams that want to standardize how AI coding skills are distributed and updated.

Typical adopters:

- engineering managers building a controlled AI tooling baseline
- platform teams supporting multiple coding agent tools
- teams that want internal workflows without vendor-specific source duplication

### When It Is a Good Fit

Use this repo when:

- your team wants an approved source of skills
- you care about portability across AI coding tools
- you want install and update behavior to reflect governance decisions
- you need a shared maintainer workflow instead of personal local conventions

### When It Is Not the Best Fit

This repo is less useful when:

- you only need one-off personal prompts
- you do not care about centralized review or package integrity
- your workflow is intentionally tied to a single AI tool forever

### Recommended Rollout Path

1. Start with one approved skill set.

Pick a small initial set of skills your team already trusts.

2. Define maintainer ownership.

Make it explicit who can update canonical packages and who reviews those changes.

3. Introduce consumer usage through `skill-manager`.

Have developers consume skills from the target project rather than copying files by hand.

4. Add governance rules gradually.

First standardize the source of truth. Then add stronger policy, provenance, or approval layers later.

### What Success Looks Like

Adoption is working when:

- the team knows where approved skills come from
- per-tool copies are no longer hand-maintained
- updates happen through a repeatable managed flow
- skill changes are reviewed at the canonical package layer

### Suggested Internal Narrative

If you are socializing this internally, a useful message is:

`We are not trying to create another marketplace. We are creating a governed source for the AI coding skills our team is willing to use.`

### Practical Adoption Checklist

- choose 1 to 3 initial skills
- assign maintainers
- standardize one target-project entry path
- teach the team to use `skill-manager`
- document what counts as approved vs unmanaged

## 繁體中文

### 適合誰採用

Skill Toolkit 很適合想要標準化 AI coding skill 分發與更新方式的團隊。

典型採用者包括：

- 想建立可控 AI 工具基線的 engineering managers
- 支援多種 coding agent 工具的 platform teams
- 想避免 vendor-specific source duplication 的團隊

### 什麼情況適合

適合採用這個 repo 的情境：

- 團隊需要 approved source of skills
- 在意跨 AI coding tool 的可移植性
- 希望 install 與 update 行為能反映治理決策
- 需要共享的 maintainer workflow，而不是每人一套本地慣例

### 什麼情況不適合

以下情況就不一定適合：

- 你只需要一次性的個人 prompt
- 你不在意集中審查或 package 完整性
- 你的 workflow 刻意永久綁定單一 AI 工具

### 建議的導入路徑

1. 先從一組 approved skills 開始。

挑選一小組團隊已經信任的 skills。

2. 定義 maintainer ownership。

明確定義誰可以更新 canonical package，以及誰負責 review。

3. 透過 `skill-manager` 引入 consumer usage。

讓開發者在 target project 中透過 `skill-manager` 使用 skills，而不是手動複製檔案。

4. 逐步加上治理規則。

先把 source of truth 標準化，再逐步補更強的 policy、provenance 或 approval layer。

### 什麼叫做導入成功

導入成功的樣子會是：

- 團隊知道 approved skills 從哪裡來
- 不再手動維護 per-tool copies
- 更新透過可重現的 managed flow 進行
- skill 變更在 canonical package 層被 review

### 建議的內部敘事

如果你要在內部推動這套做法，可以用這句話：

`我們不是在做另一個 marketplace，而是在建立團隊願意使用的 AI coding skills 的治理來源。`

### 實際導入清單

- 選定 1 到 3 個初始 skills
- 指派 maintainers
- 標準化 target-project 入口
- 教團隊使用 `skill-manager`
- 文件化 approved 與 unmanaged 的差異
