# skill-forge

Version: 1.1.2

Write skills once, govern centrally, deploy to multiple coding AI targets.

`skill-forge` is an open-source governance layer for AI development skills. It helps teams keep skill definitions in one canonical source, validate package integrity, and render installable target artifacts for tools such as Codex and Claude.

這是一個面向 AI 開發技能的開源治理層，讓團隊可以把 skill 定義集中在單一 canonical source，驗證 package 完整性，並為 Codex、Claude 等工具產生可安裝的 target artifacts。

> This repo is **not** a public skill marketplace.  
> It is designed for teams that want controlled distribution, portable skill definitions, and a clearer trust boundary around which skills engineers are allowed to use.

---

## Language

- [English](#english)
- [繁體中文](#繁體中文)

---

# English

## Overview

`skill-forge` lets teams define skills once in a canonical source tree, then render and distribute the correct artifacts to supported coding AI tools.

It is built for teams that care about:

- centralized governance
- portable skill definitions
- controlled rollout
- repeatable installation
- lower vendor lock-in

### What problems it solves

Teams adopting coding agents usually run into the same problems:

- engineers install skills from inconsistent or unknown sources
- the same workflow gets rewritten separately for each AI tool
- there is no shared review point for versioning, integrity, or rollout
- switching vendors becomes expensive because skill logic is tied to one tool

`skill-forge` addresses this by treating `canonical-skills/` as the only source of truth, then rendering target-specific artifacts for supported tools.

---

## Who this is for

- engineering managers who want an approved source for team skills
- platform teams who need controlled distribution for internal AI workflows
- developers who want a project-local skill manager without hand-maintaining per-tool copies

This repo is a good fit when you care more about governance, portability, and repeatable distribution than marketplace-style discovery.

---

## Recommended usage by role

### End users

**Recommended path: `CLI/TUI`**

For normal users, the default path should be the interactive `skill-manager` flow.

Use it to:

- install skills
- update skills
- check skill status
- repair managed installs
- remove managed skills
- switch between `codex` and `claude`

### Maintainers

**Recommended path: AI collaboration**

For maintainers, the default path should be working in Codex or Claude with manager skills.

Use it to:

- create new canonical skills
- update existing canonical skills
- finalize metadata and validation
- sync manager-skills and shared regular-skills
- refresh repo-local agent targets

### Advanced fallback

**Direct terminal commands are supported, but not recommended as the primary path.**

Use them when you need:

- debugging
- low-level inspection
- automation scripts
- terminal fallback during maintainer work

---

## Quickstart

Recommended user path: `CLI/TUI`.

### 1. Clone the repo

```bash
git clone https://github.com/busybutlazy/skill-forge.git ~/skill-forge
```

PowerShell:

```powershell
git clone https://github.com/busybutlazy/skill-forge.git "$HOME\skill-forge"
```

### 2. Go to your target project

```bash
cd /path/to/target-project
```

### 3. Launch the project-local skill manager

```bash
~/skill-forge/skill-manager
```

PowerShell:

```powershell
& "$HOME\skill-forge\skill-manager.ps1"
```

Or add `~/skill-forge` to your `PATH` and run:

```bash
skill-manager
```

On Windows PowerShell, prefer `$HOME\skill-forge\skill-manager.ps1` over `~`, and keep container-internal paths such as `/workspace/project` unchanged when passing CLI arguments through Docker.

If PowerShell blocks the launcher with an execution-policy error, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& "$HOME\skill-forge\skill-manager.ps1"
```

### 4. Use the interactive menu

Use the menu to:

* choose `codex` or `claude`
* check installed skill status
* install or update skills
* repair broken managed installs
* remove managed skills
* switch targets
* open the expert terminal only when needed

> For normal users, `skill-manager` should remain the default entry point.

If you need the low-level path, use the expert terminal and Python CLI directly, then refer to [the terminal operations guide](docs/guides/terminal-operations-guide.md) for the detailed command reference.

---

## Canonical model

Public skills live under:

```text
canonical-skills/regular-skills/<name>/
```

Required files:

* `package.json`
* `instruction.md`
* `manifest.json`
* `targets/codex.frontmatter.json`
* `targets/claude.frontmatter.json`

Optional content:

* `examples/`
* `references/`
* `scripts/`
* `assets/`

Detailed references:

* [docs/reference/canonical-package-spec.md](docs/reference/canonical-package-spec.md)
* [docs/reference/adapter-contract.md](docs/reference/adapter-contract.md)
* [docs/reference/drift-policy.md](docs/reference/drift-policy.md)

---

## Public skills vs maintainer skills

### `canonical-skills/regular-skills/`

* canonical source for normal end-user skills
* the only source normal installs should come from

### `canonical-skills/manager-skills/`

* canonical source for maintainer-only workflows
* includes workflows such as:

  * `create-skill`
  * `update-skill`
  * `finalize-skill`
  * `install-manager-skill`

### `shared` tag

Skills under `regular-skills/` may optionally carry the `shared` tag.

This means the skill remains a regular skill, but may also be synced through manager install flows.

### `.agents/skills/`

* rendered artifacts used by this repo itself
* not canonical source
* should not be edited by hand as source

---

## Maintainer workflow

There are two maintainer paths, but only one should be the default.

### Preferred: AI collaboration

Use this path when working inside Codex or Claude.

Recommended flow:

1. Open this repo in Codex or Claude.
2. Only edit canonical source:

   * `canonical-skills/regular-skills/`
   * `canonical-skills/manager-skills/`
3. Use manager skills:

   * `create-skill`
   * `update-skill`
   * `finalize-skill`
   * `install-manager-skill`
4. Fall back to terminal commands only when needed.
5. Do not hand-edit rendered artifacts such as:

   * `.agents/skills/`
   * `.claude/skills/`

Recommended responsibility split:

* add a new skill → `create-skill`
* revise an existing skill → `update-skill`
* finalize and validate changes → `finalize-skill`
* sync manager targets → `install-manager-skill` or `sync-manager-catalog`

### Fallback: terminal workflow

Use terminal only when AI collaboration is not suitable, or when low-level inspection is needed.

For the full command reference, see [docs/guides/terminal-operations-guide.md](docs/guides/terminal-operations-guide.md).

#### Containerized development environment

```bash
docker build -f Dockerfile.dev -t skill-forge-dev .
docker run --rm -it -v "$PWD:/workspace" -w /workspace skill-forge-dev
```

#### Validate canonical skills

```bash
PYTHONPATH=src python -m skill_forge --repo-root . validate
```

#### Refresh metadata

```bash
PYTHONPATH=src python -m skill_forge --repo-root . refresh-metadata create-skill --today
```

#### Sync maintainer-only skills into the local Codex directory

```bash
PYTHONPATH=src python -m skill_forge --repo-root . sync-maintainer --project . --target codex --force
```

#### Sync manager-skills and `shared` regular-skills into local targets

```bash
PYTHONPATH=src python -m skill_forge --repo-root . sync-manager-catalog --project . --target all --force
```

#### Inspect install status

```bash
PYTHONPATH=src python -m skill_forge --repo-root . list --target codex --project . --scope all --json
```

#### Run tests

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

#### Runtime smoke test

```bash
make up
```

---

## CLI and safety model

Core commands:

* `validate`
* `render`
* `install`
* `list`
* `remove`
* `update`
* `refresh-metadata`
* `sync-maintainer`
* `sync-manager-catalog`

Managed install states:

* `up_to_date`
* `update_available`
* `drift`
* `broken`
* `unmanaged`

Key safety rules:

* `install` overwrites managed `up_to_date` and `update_available`
* `install` asks for confirmation before repairing `broken`
* `install` requires `--force` before overwriting `drift`
* `install` refuses to overwrite `unmanaged`
* `update` only works on managed installs and also requires `--force` for `drift`
* `remove` refuses to delete `unmanaged`

---

## Project layout

```text
skill-forge/
├── AGENTS.md
├── .agents/
├── canonical-skills/
│   ├── regular-skills/
│   └── manager-skills/
├── docs/
│   ├── concepts/
│   ├── guides/
│   └── reference/
├── src/
├── tests/
├── Dockerfile
├── Dockerfile.dev
├── compose.yaml
├── Makefile
├── skill-manager
└── skill-manager.ps1
```

---

## How to read this repo

Recommended reading order:

1. `README.md`
2. [docs/concepts/governance.md](docs/concepts/governance.md)
3. [docs/guides/adoption-guide.md](docs/guides/adoption-guide.md)
4. [docs/guides/quickstart-demo.md](docs/guides/quickstart-demo.md)
5. [docs/guides/terminal-operations-guide.md](docs/guides/terminal-operations-guide.md)

For normal users, start with quickstart and the `skill-manager` flow.
For maintainers, then go deeper into governance and terminal operations.

---

## Positioning

### Not a marketplace

`skill-forge` is not trying to maximize public discovery.
It is trying to provide a controlled source, a repeatable packaging model, and a safer install/update path for approved skills.

### Not vendor lock-in

Skill logic should be written once as a tool-neutral canonical package, then adapted to supported targets instead of maintained as parallel per-tool copies.

### Not a replacement for native AI tool features

Codex, Claude, and similar tools still own their in-product execution experience.

`skill-forge` solves a different problem: canonical source, governance, distribution, and cross-tool portability.

---

## Current version focus

Version `1.1.2` extends the `1.0.0` end-user baseline with a formal maintainer workflow and canonical manager skill model.

This stage focuses on:

* formally splitting `canonical-skills/` into:

  * `canonical-skills/regular-skills/`
  * `canonical-skills/manager-skills/`
* adding `finalize-skill`
* adding `install-manager-skill`
* aligning maintainer guidance around the create / update / finalize / install loop

---

## Roadmap

The current roadmap focuses on:

* clearer external positioning
* better adoption guidance
* stronger governance framing

CLI/TUI and AI collaboration remain the primary operating surfaces for now.

See `ROADMAP.md` for current priorities and direction.

---

## Compatibility note

`skill-manager.sh` remains a compatibility shim only.
`skill-manager.ps1` is the Windows PowerShell launcher.

The real workflow is now:

* end users: `skill-manager`
* maintainers: AI collaboration first, Python CLI as fallback

---

# 繁體中文

## 專案簡介

`skill-forge` 讓團隊可以把 skills 集中定義在同一套 canonical source 中，再依不同 coding AI 工具 render 並分發對應的 artifacts。

它適合那些在意以下幾件事的團隊：

* 集中治理
* skill 定義可移植
* 發佈與安裝流程可控
* 安裝結果可重現
* 降低 vendor lock-in

### 這個專案解決什麼問題

導入 coding agents 的團隊，常會遇到這些問題：

* 工程師各自安裝不同來源的 skills，缺乏一致管理
* 同一套 workflow 被迫為不同 AI 工具重寫
* 沒有明確的版本、完整性與發佈審查點
* skill 邏輯綁死在單一工具上，未來切換成本高

`skill-forge` 的做法，是把 `canonical-skills/` 當作唯一 source of truth，再為支援的工具 render 出 target-specific artifacts。

---

## 適合誰使用

* 想建立團隊 approved skill source 的 engineering managers
* 需要可控分發內部 AI workflows 的 platform teams
* 想用 project-local skill manager，而不是手動維護多套工具版本的 developers

如果你在意的是治理、可移植性與可重現分發，而不是公開 marketplace 式的探索體驗，這個 repo 會比較適合你。

---

## 依角色區分的建議用法

### 一般使用者

**建議路徑：`CLI/TUI`**

對一般使用者來說，預設應該走 `skill-manager` 的互動式流程，而不是直接記憶底層命令。

適合用來：

* 安裝 skills
* 更新 skills
* 檢查 skill 狀態
* 修復 managed installs
* 移除 managed skills
* 在 `codex` 與 `claude` 間切換

### 維護者

**建議路徑：AI 協作**

對維護者來說，預設應該是在 Codex 或 Claude 中，搭配 manager skills 進行維護，而不是一開始就手打 terminal 命令。

適合用來：

* 建立新的 canonical skills
* 修改既有 canonical skills
* 收尾 metadata 與 validation
* 同步 manager-skills 與 shared regular-skills
* 更新 repo-local agent targets

### 進階 fallback

**直接輸入 terminal 命令仍然支援，但不建議作為主路徑。**

適合用在：

* 除錯
* 低階檢查
* 自動化腳本整合
* 維護者在協作流程中需要 fallback 時

---

## 快速開始

推薦的一般使用者路徑是 `CLI/TUI`。

### 1. Clone repo

```bash
git clone https://github.com/busybutlazy/skill-forge.git ~/skill-forge
```

PowerShell:

```powershell
git clone https://github.com/busybutlazy/skill-forge.git "$HOME\skill-forge"
```

### 2. 進入你的 target project

```bash
cd /path/to/target-project
```

### 3. 啟動 project-local skill manager

```bash
~/skill-forge/skill-manager
```

PowerShell:

```powershell
& "$HOME\skill-forge\skill-manager.ps1"
```

如果你已經把 `~/skill-forge` 加進 `PATH`，也可以直接執行：

```bash
skill-manager
```

在 Windows PowerShell 請優先使用 `$HOME\skill-forge\skill-manager.ps1`，不要把 `~` 當成預設寫法；但像 `/workspace/project` 這種容器內路徑在 CLI 參數中仍應保留斜線形式，不要全部改成反斜線。

如果 PowerShell 因為 execution policy 擋住啟動器，可以先執行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& "$HOME\skill-forge\skill-manager.ps1"
```

### 4. 在互動式選單中完成操作

你可以透過選單進行：

* 選擇 `codex` 或 `claude`
* 檢查已安裝 skill 狀態
* 安裝或更新 skills
* 修復 broken 的 managed install
* 移除 managed skills
* 切換 target
* 只有在需要時才進入 expert terminal

> 對一般使用者來說，`skill-manager` 應該是預設入口。

如果你需要走低階路徑，可以進 expert terminal 直接使用 Python CLI，詳細指令請參考 [terminal 操作手冊](docs/guides/terminal-operations-guide.md)。

---

## Canonical Model

公開 skills 放在：

```text
canonical-skills/regular-skills/<name>/
```

至少包含：

* `package.json`
* `instruction.md`
* `manifest.json`
* `targets/codex.frontmatter.json`
* `targets/claude.frontmatter.json`

可選內容：

* `examples/`
* `references/`
* `scripts/`
* `assets/`

詳細規格請參考：

* [docs/reference/canonical-package-spec.md](docs/reference/canonical-package-spec.md)
* [docs/reference/adapter-contract.md](docs/reference/adapter-contract.md)
* [docs/reference/drift-policy.md](docs/reference/drift-policy.md)

---

## 公開 skills 與 maintainer skills

### `canonical-skills/regular-skills/`

* 一般使用者 skills 的 canonical source
* 一般安裝流程應以這裡為來源

### `canonical-skills/manager-skills/`

* 維護者工作流的 canonical source
* 例如：

  * `create-skill`
  * `update-skill`
  * `finalize-skill`
  * `install-manager-skill`

### `shared` tag

`regular-skills/` 下的 skill 可以帶 `shared` tag。

這代表它仍然是 regular skill，但也可以透過 manager install flow 一起同步。

### `.agents/skills/`

* 這是本 repo 自己使用的 rendered artifacts
* 不是 canonical source
* 不應手動當作 source 編輯

---

## 維護者工作流程

維護者其實有兩條路，但只有一條應該是主路徑。

### 首選：AI 協作

這條路徑適合在 Codex 或 Claude 中維護。

建議流程：

1. 用 Codex 或 Claude 打開這個 repo。
2. 只編輯 canonical source：

   * `canonical-skills/regular-skills/`
   * `canonical-skills/manager-skills/`
3. 用 manager skills 進行操作：

   * `create-skill`
   * `update-skill`
   * `finalize-skill`
   * `install-manager-skill`
4. 只有在必要時才退回 terminal 命令。
5. 不要手動修改 rendered artifacts，例如：

   * `.agents/skills/`
   * `.claude/skills/`

建議分工：

* 新增 skill → `create-skill`
* 修改 skill → `update-skill`
* 收尾與驗證 → `finalize-skill`
* 同步 manager targets → `install-manager-skill` 或 `sync-manager-catalog`

### fallback：terminal workflow

只有在 AI 協作不適合，或需要做更低階檢查時，再使用 terminal。

完整命令說明請看 [docs/guides/terminal-operations-guide.md](docs/guides/terminal-operations-guide.md)。

#### 容器化開發環境

```bash
docker build -f Dockerfile.dev -t skill-forge-dev .
docker run --rm -it -v "$PWD:/workspace" -w /workspace skill-forge-dev
```

#### 驗證 canonical skills

```bash
PYTHONPATH=src python -m skill_forge --repo-root . validate
```

#### 更新 metadata

```bash
PYTHONPATH=src python -m skill_forge --repo-root . refresh-metadata create-skill --today
```

#### 只同步 manager-only skills 到本地 Codex 目錄

```bash
PYTHONPATH=src python -m skill_forge --repo-root . sync-maintainer --project . --target codex --force
```

#### 同步 manager-skills 與 `shared` regular-skills 到本地 targets

```bash
PYTHONPATH=src python -m skill_forge --repo-root . sync-manager-catalog --project . --target all --force
```

#### 查看 install 狀態

```bash
PYTHONPATH=src python -m skill_forge --repo-root . list --target codex --project . --scope all --json
```

#### 執行測試

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

#### Runtime smoke test

```bash
make up
```

---

## CLI 與安全模型

核心指令：

* `validate`
* `render`
* `install`
* `list`
* `remove`
* `update`
* `refresh-metadata`
* `sync-maintainer`
* `sync-manager-catalog`

managed install 狀態：

* `up_to_date`
* `update_available`
* `drift`
* `broken`
* `unmanaged`

主要安全規則：

* `install` 會直接覆蓋 managed 的 `up_to_date` 與 `update_available`
* `install` 修復 `broken` 前會要求確認
* `install` 覆蓋 `drift` 前必須加 `--force`
* `install` 會拒絕覆蓋 `unmanaged`
* `update` 只處理 managed install，遇到 `drift` 也必須加 `--force`
* `remove` 會拒絕刪除 `unmanaged`

---

## 專案結構

```text
skill-forge/
├── AGENTS.md
├── .agents/
├── canonical-skills/
│   ├── regular-skills/
│   └── manager-skills/
├── docs/
│   ├── concepts/
│   ├── guides/
│   └── reference/
├── src/
├── tests/
├── Dockerfile
├── Dockerfile.dev
├── compose.yaml
├── Makefile
├── skill-manager
└── skill-manager.ps1
```

---

## 如何閱讀這個 repo

建議閱讀順序：

1. `README.md`
2. [docs/concepts/governance.md](docs/concepts/governance.md)
3. [docs/guides/adoption-guide.md](docs/guides/adoption-guide.md)
4. [docs/guides/quickstart-demo.md](docs/guides/quickstart-demo.md)
5. [docs/guides/terminal-operations-guide.md](docs/guides/terminal-operations-guide.md)

一般使用者優先看 quickstart 與 `skill-manager` 流程。
維護者再深入看 governance 與 terminal 操作文件。

---

## 定位說明

### 這不是 marketplace

`skill-forge` 的目標不是最大化公開探索與上架，而是提供團隊可控來源、可重現 packaging model，以及更安全的 install / update 路徑。

### 這不是 vendor lock-in

skill 邏輯應該先寫成 tool-neutral 的 canonical package，再適配到支援的 targets，而不是為每個工具手動維護平行版本。

### 這不是用來取代原生 AI 工具能力

Codex、Claude 等工具仍然負責各自產品內的執行體驗。

`skill-forge` 處理的是另一個層次的問題：canonical source、治理、分發與跨工具可移植性。

---

## 目前版本重點

`1.1.2` 是在 `1.0.0` 一般使用者基礎體驗之上，正式補齊 maintainer workflow 與 canonical manager skill model 的版本。

這個版本的重點包括：

* `canonical-skills/` 正式拆分為：

  * `canonical-skills/regular-skills/`
  * `canonical-skills/manager-skills/`
* 新增 `finalize-skill`
* 新增 `install-manager-skill`
* 讓維護者工作流更明確地收斂到 create / update / finalize / install 這條主線

---

## Roadmap

目前 roadmap 的重點是：

* 對外定位更清楚
* 導入說明更完整
* 治理模型更明確

現階段主要操作面仍然以 CLI/TUI 與 AI 協作流程為主。

請參考 `ROADMAP.md` 了解目前方向。

---

## 相容性說明

`skill-manager.sh` 目前只保留相容提示用途。
`skill-manager.ps1` 是給 Windows PowerShell 的啟動器。

真正的工作流程已經是：

* 一般使用者：`skill-manager`
* 維護者：AI 協作優先，Python CLI 為 fallback
