# Drift Policy

## English

`canonical-skills/` is the only skill source that may be edited directly. Every rendered artifact is a derived output, not an editing entrypoint.

### Policy

1. Do not edit rendered artifacts directly.
2. Make every content change in the canonical package first, then render again.
3. Let the canonical package decide whether `version` changes; target artifacts do not control versioning.
4. Update `package_sha256` and the manifest together with the canonical package.
5. If target content diverges from source hash expectations, treat it as drift rather than a normal difference.

### Operational Meaning

- files under `canonical-skills/` can be reviewed, versioned, and validated directly
- proof artifacts exist only to demonstrate contracts or migration examples, not as official install sources
- `skill-base/` is not a formal public source; the canonical render pipeline is the official path

### Forbidden Changes

The following should be treated as violations:

- editing `skill-base/<skill>/SKILL.md` without writing back to the canonical source
- editing only Claude target Markdown without writing back to the canonical source
- adding business logic that exists only inside a target artifact
- maintaining two editable primary copies of the same shared instruction

### Review Rule

When a pull request touches rendered artifacts, review must also check:

- whether the matching canonical source was updated
- whether the manifest and `package_sha256` stay consistent
- whether target-specific differences are still isolated to override files

## 繁體中文

`canonical-skills/` 是唯一可以直接編輯的 skill source。所有 rendered artifact 都是衍生輸出，不是編輯入口。

### 政策

1. 不直接手改 rendered artifact。
2. 任何內容調整都先改 canonical package，再重新 render。
3. `version` 是否升版由 canonical package 決定，不由 target artifact 決定。
4. `package_sha256` 與 manifest 必須隨 canonical package 一起更新。
5. 若 target 內容與 source hash 預期不一致，視為 drift，而不是正常差異。

### 實際意義

- `canonical-skills/` 內的檔案可以直接被 code review、版本控制與驗證器檢查
- proof artifact 只用來展示契約或 migration 範例，不是正式安裝來源
- `skill-base/` 已不是正式公開 source；正式流程以 canonical render pipeline 為準

### 禁止的變更

下列做法都應視為違規：

- 只修改 `skill-base/<skill>/SKILL.md`，卻不回寫 canonical source
- 只修改 Claude target Markdown，卻不回寫 canonical source
- 在 target artifact 內加入只有該 artifact 才知道的業務邏輯
- 讓同一 skill 的 shared instruction 同時存在兩份可編輯主本

### Review 規則

只要 PR 觸及 rendered artifact，就必須同時檢查：

- 是否有對應 canonical source 變更
- manifest 與 `package_sha256` 是否保持一致
- target-specific 差異是否仍只存在於 override 檔案中
