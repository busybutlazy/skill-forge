# Drift Policy

phase 2 起，`canonical-skills/` 是唯一可直接修改的 skill source。任何 rendered artifact 都視為衍生物，不是編輯入口。

## Policy

1. 不直接手改 rendered artifact。
2. 任何內容調整都先改 canonical package，再重新 render。
3. `version` 是否升版由 canonical package 決定，不由 target artifact 決定。
4. `package_sha256` 與 manifest 必須跟 canonical package 一起更新。
5. 若 target 內容與 source hash 不一致，視為 drift，不視為正常差異。

## Operational Meaning

- `canonical-skills/` 內的檔案可以被 code review、版本控制、驗證器直接檢查。
- `proof/phase2/rendered/` 只用來展示 contract 與 migration proof，不是 phase 3 安裝來源。
- `skill-base/` 在 phase 2 仍保留既有 Codex 發布形式；正式切到 canonical render pipeline 是 phase 3 的責任。

## Forbidden Changes

下列做法都應視為違規：

- 只修改 `skill-base/<skill>/SKILL.md`，卻不回寫 canonical source
- 只修改 Claude target markdown，卻不回寫 canonical source
- 在 target artifact 內加入只有該 artifact 才知道的業務邏輯
- 讓同一 skill 的 shared instruction 同時存在兩份可編輯主本

## Review Rule

只要 PR 觸及 rendered artifact，就必須同時檢查：

- 是否有對應 canonical source 變更
- manifest 與 `package_sha256` 是否一致
- target-specific 差異是否只出現在 override 區塊
