# Governance Model

## English

### Overview

Skill Toolkit treats AI coding skills as governed packages, not loose prompt snippets.

The central idea is simple: keep one canonical source, validate it, track its package integrity, and only then render and install target-specific artifacts.

### What "Approved Source" Means

An approved source is the set of canonical skill packages your team is willing to distribute.

In this repo, that source lives under `canonical-skills/`. Public skills are reviewed there, versioned there, and rendered from there.

That gives teams a stable review point:

- where skill behavior is defined
- where target differences are declared
- where integrity metadata is checked
- where rollout decisions can be made

### Why Canonical Packages Matter

A canonical package is more than an instruction file. It includes:

- identity and version metadata
- target-specific frontmatter overrides
- manifest-driven file tracking
- package integrity hash

This matters because teams need to know not only what a skill says, but also whether the installed artifact still corresponds to an approved package.

### Trust Story

The trust model in the current repo is intentionally practical:

- the canonical source is explicit
- package structure is validated
- render-driving files are tracked in `manifest.json`
- package integrity is represented by `package_sha256`
- installed artifacts are checked against canonical expectations

This does not make the repo a full policy engine, signing system, or audit backend yet. It does provide a concrete base for controlled distribution.

### Maintainer Workflow vs Consumer Workflow

#### Maintainers

Maintainers work in the toolkit repo:

- edit canonical skill packages
- validate structure and integrity
- render and install through the CLI for testing
- decide what is ready for team distribution

#### Consumers

Consumers work in target projects:

- use `skill-manager`
- install approved skills
- update managed installs
- avoid hand-maintaining target-specific copies

### Why This Lowers Risk

This repo lowers common team risk in a few practical ways:

- engineers do not need to independently hunt for skills from random sources
- teams can review skill packages before distribution
- install and update flows distinguish managed content from unmanaged content
- drift and broken states are explicit instead of silently overwritten

### What This Repo Is Not

- not a public skill marketplace
- not a replacement for native AI tool features
- not yet a private registry, signing service, or audit platform

### Native Tool Features vs Governance Layer

Native tool features focus on each product's own execution model and in-product experience. This repo focuses on a different layer: canonical source management, reviewable packaging, controlled distribution, and portability across supported targets.

That means the repo is not competing with native platform capabilities. It is a complementary governance layer for teams that want a clearer source of truth and a more consistent rollout model for AI development skills.

### Future Governance Directions

Phase 7 does not implement these yet, but the roadmap now points toward:

- private catalog or approved registry
- provenance or signing model
- policy enforcement such as allowlists and denylists
- audit trail and skill lifecycle records
- target capability matrix

## 繁體中文

### 概觀

Skill Toolkit 把 AI coding skills 視為可治理的 package，而不是零散 prompt 片段。

核心概念很簡單：維持單一 canonical source，先驗證、先追蹤 package 完整性，再 render 與安裝 target-specific artifact。

### 什麼是「approved source」

approved source 指的是你的團隊願意分發的 canonical skill package 集合。

在這個 repo 中，這個來源就是 `canonical-skills/`。公開 skills 在這裡被審查、在這裡被版本化，也從這裡被 render。

這讓團隊擁有穩定的審查點：

- skill 行為在哪裡被定義
- target 差異在哪裡被宣告
- 完整性 metadata 在哪裡被檢查
- rollout 決策在哪裡被做出

### 為什麼 canonical package 很重要

canonical package 不只是 instruction file。它還包含：

- identity 與 version metadata
- target-specific frontmatter override
- manifest 驅動的檔案追蹤
- package integrity hash

這很重要，因為團隊不只需要知道 skill 內容是什麼，也需要知道已安裝 artifact 是否仍然對應到某個 approved package。

### Trust Story

目前 repo 的 trust model 是刻意走實用路線：

- canonical source 是明確的
- package 結構會被驗證
- `manifest.json` 會追蹤 render-driving files
- `package_sha256` 代表 package 完整性
- 已安裝 artifact 會被拿來對照 canonical 預期

這不代表 repo 已經是完整的 policy engine、signing system 或 audit backend。但它已經提供了一個可用於可控分發的基礎。

### 維護者工作流程與使用者工作流程

#### 維護者

維護者在 toolkit repo 中工作：

- 編輯 canonical skill packages
- 驗證結構與完整性
- 透過 CLI render 與 install 做測試
- 決定哪些內容可以分發給團隊

#### 使用者

使用者在 target project 中工作：

- 使用 `skill-manager`
- 安裝 approved skills
- 更新 managed install
- 避免手動維護 target-specific copies

### 為什麼這能降低風險

這個 repo 透過幾個實際做法降低常見團隊風險：

- 工程師不需要各自去找來源不明的 skills
- 團隊可以在分發前先審查 skill packages
- install 與 update 流程會區分 managed 與 unmanaged 內容
- drift 與 broken 狀態會被明確標示，而不是被靜默覆蓋

### 這個 repo 不是什麼

- 不是公開 skill marketplace
- 不是原生 AI 工具能力的替代品
- 目前也還不是 private registry、signing service 或 audit platform

### 原生工具能力與治理層的分工

原生工具能力主要處理各產品自身的執行模型與產品內體驗。這個 repo 處理的是另一層：canonical source 管理、可審查的 packaging、可控分發，以及跨支援 target 的可移植性。

也就是說，這個 repo 不是在和原生平台能力競爭，而是在補上一層治理能力，讓團隊可以用更清楚的 source of truth 與更一致的 rollout 模型來管理 AI development skills。

### 未來治理方向

phase 7 這次不會實作下列能力，但 roadmap 已經把方向定下來：

- private catalog 或 approved registry
- provenance 或 signing model
- allowlist / denylist 類 policy enforcement
- audit trail 與 skill lifecycle records
- target capability matrix
