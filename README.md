# skill-forge

Version: 1.2.0

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

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Docker | 20.10+ (Compose v2) | Required — `skill-manager` runs entirely inside a container |
| Python | 3.11+ | Only needed if running `skill-forge` CLI directly outside Docker (dev / CI use) |
| git | any recent | Needed for the auto-update check in `skill-manager` |

The recommended end-user path (`skill-manager`) requires **only Docker**. You do not need a local Python installation for day-to-day use.

Python 3.11+ is required inside the dev container (`Dockerfile.dev`) and when running `PYTHONPATH=src python -m skill_forge` commands directly — this is an advanced fallback, not the primary path.

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
* accept or skip the recommended baseline (security settings + `install-my-skill`) with a single `[Y/n]` prompt
* check installed skill status
* install or update skills from a grouped list (`★ Recommended` first, then catalog groups)
* install or update the project guideline (managed instruction files, governance document, and safety hooks) from its own top-level menu entry
* repair broken managed installs
* remove managed skills
* switch targets
* open the expert terminal only when needed

Grouping, recommendations, and description keyword highlighting are configured centrally in `canonical-skills/catalog.json`. See [docs/reference/catalog-and-agent-memory.md](docs/reference/catalog-and-agent-memory.md).

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
* [docs/reference/catalog-and-agent-memory.md](docs/reference/catalog-and-agent-memory.md)

### Project guideline

Besides skills, the repo also manages a set of project guideline config items, each with its own canonical source:

```text
canonical-configs/
├── agent-memory/       # memory.md → CLAUDE.md (claude) / AGENTS.md (codex)
│   ├── config.json
│   └── memory.md
├── agent-guideline/    # guideline.md → docs/agent-guideline.md (both targets)
│   ├── config.json
│   └── guideline.md
└── agent-hooks/        # safety_check.py + additive native hook configuration
    ├── config.json
    └── hooks/safety_check.py
```

The two document items use trailing HTML markers for version and drift detection. `agent-hooks` installs a marker-managed Python runner and structurally merges only skill-forge-owned entries into `.claude/settings.json` or `.codex/hooks.json`; unrelated user settings and hooks are preserved. Existing conflicting files without ownership markers are treated as `unmanaged` and never overwritten.

Managed hooks require a `python3` command running Python 3.11 or newer. Claude uses native `PreToolUse` hooks for `Bash`, `Edit`, and `Write`; Codex uses project `.codex/hooks.json` for `Bash` and `apply_patch`. Codex may require review/trust for each exact hook definition, and `[features] hooks = false` is reported as `inactive`. These hooks are defense in depth—not a replacement for sandboxing, permissions, CI, or human approval.

Recursive forced deletion with an unresolved glob (for example `rm -rf *` or `rm -rf build/*.tmp`) is denied because the hook cannot safely know the expanded target set. Use an explicit scoped path or obtain human approval outside the hook.

Install the items from the `Install / Update project guideline` entry of the interactive menu, or via the CLI:

```bash
skill-forge guideline status  [--item NAME] --target <codex|claude> --project <path> [--json]
skill-forge guideline install [--item NAME] --target <codex|claude> --project <path> [--force] [--yes]
```

Both commands default to all available items; a failed item is reported without aborting the rest. `skill-forge memory status|install` remains a compatibility command for the same `agent-memory` file and marker, while preserving its legacy output shape (`memory status --json` returns an object; the equivalent filtered `guideline` command returns a one-element array).

Use `--item agent-hooks` to manage only the safety bundle. Drift requires `--force` plus confirmation; `unmanaged` files are never overwritten. There is currently no automatic uninstall command: manually remove only the skill-forge-owned matcher handlers and the marker-managed `hooks/skill-forge/safety_check.py` file. Windows launcher support and the Git pre-commit fallback remain deferred.

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
  * `import-plugin-skill`
  * `install-manager-skill`
  * `skill-review-packet`

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
   * `import-plugin-skill`
   * `install-manager-skill`
   * `skill-review-packet`
4. Fall back to terminal commands only when needed.
5. Do not hand-edit rendered artifacts such as:

   * `.agents/skills/`
   * `.claude/skills/`

Recommended responsibility split:

* add a new skill → `create-skill`
* revise an existing skill → `update-skill`
* import a downloaded external skill → `import-plugin-skill`
* finalize and validate changes → `finalize-skill`
* sync manager targets → `install-manager-skill` or `sync-manager-catalog`

### External Skill Import Policy

Downloaded external skills should not be copied straight into `canonical-skills/`.

Maintainers should use `import-plugin-skill` to:

- inspect one local external skill source
- run `skillkeeper` before rewrite to decide whether the skill is worth canonicalizing
- stage a draft outside canonical source through `imitator`, `reviewer`, and final `skillkeeper` admission
- generate a `skill-review-packet` before asking for final human approval
- choose explicitly whether approved content belongs in `regular-skills/` or `manager-skills/`
- finish intake with finalize plus a Codex smoke test
- clean the matching `tmp/import-candidates/` draft only after the full intake flow succeeds

Recommended local workspace layout:

```text
tmp/
├── foreign_skills/
└── import-candidates/
```

- `tmp/foreign_skills/`: downloaded external skill sources
- `tmp/import-candidates/`: staged canonical drafts after review

Promotion is not the end of the workflow. Successful imports should be promoted, finalized, smoke-tested, and then cleaned up.

Detailed workflow:

* [docs/guides/external-skill-import-guide.md](docs/guides/external-skill-import-guide.md)

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
docker run --rm -e PYTHONPATH=src -v "$PWD:/workspace" -w /workspace \
  skill-forge-dev python -m unittest discover -s tests
```

#### Runtime smoke test

```bash
make up
```

---

## Installing skills from within Claude or Codex

The `install-my-skill` skill lets you install and update skills without leaving your AI session.

### Prerequisites

- `install-my-skill` must be installed first. On first setup, install it via `skill-manager`:

  ```bash
  ~/skill-forge/skill-manager
  # Choose Install / Update skills → select install-my-skill
  ```

  Or, if `install-my-skill` is already in your shared catalog, it is included automatically when you run `sync-manager-catalog`.

### Usage

Inside a Claude or Codex session, say:

> "Help me install a skill" or "Update my skills"

The agent will:

1. Fetch the available skill catalog and your current install status
2. Present a selection list with version and status badges
3. Install or update the skills you choose
4. Report results and remind you to reload the session

For Roadmap-driven delivery, install `deliver-roadmap-phase`. Its required Change Workflow skills are disclosed and installed automatically. After reloading the agent session, invoke it with one exact phase:

```text
Use deliver-roadmap-phase.
Roadmap: docs/Roadmap.md
Phase: Phase 1 — Walking Skeleton
Mode: supervised-auto
```

The skill plans only that phase, asks for one execution approval, coordinates the approved child Changes, and stops for independent review and final human acceptance. It never infers the next phase or implicitly commits, pushes, merges, releases, or deploys.

Example output:

```
請選擇要安裝/更新的 skill（可複選）：

 1. commit        v1.3.0  ✓ 已安裝（最新）
 2. create-pr     v1.2.0  ⬆ 有更新（1.1.0→1.2.0）
 3. dto-organizer v0.3.0  ○ 未安裝
```

### Known limits

- **Reload required:** skills load at session startup. After installing, restart your Claude or Codex session for new skills to take effect.
- **Requires Docker:** the agent shells out to `skill-manager`, which runs inside Docker.
- **Unmanaged skills are never overwritten:** if a skill exists but was not installed by skill-forge, the agent will refuse and explain.

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
* `guideline status` / `guideline install`
* `memory status` / `memory install` (compatibility commands for the `agent-memory` item)

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
│   ├── catalog.json
│   ├── regular-skills/
│   └── manager-skills/
├── canonical-configs/
│   ├── agent-memory/
│   ├── agent-guideline/
│   └── agent-hooks/
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
6. [docs/guides/external-skill-import-guide.md](docs/guides/external-skill-import-guide.md)

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

## 環境需求

| 需求 | 版本 | 說明 |
|------|------|------|
| Docker | 20.10+（Compose v2）| 必須 — `skill-manager` 完整執行在容器內 |
| Python | 3.11+ | 僅在直接使用 `skill-forge` CLI（不透過 Docker）時需要，如 dev / CI |
| git | 任意近期版本 | `skill-manager` 自動更新檢查所需 |

推薦的一般使用者路徑（`skill-manager`）**只需要 Docker**，不需要在本機安裝 Python。

Python 3.11+ 是 dev 容器（`Dockerfile.dev`）與直接執行 `PYTHONPATH=src python -m skill_forge` 命令時的需求——這是進階 fallback，不是主要路徑。

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
* 用單一 `[Y/n]` 提問決定是否寫入建議基本配置（security settings + `install-my-skill`）
* 檢查已安裝 skill 狀態
* 從分群清單安裝或更新 skills（`★ Recommended` 在最上，其後依 catalog 群組排列）
* 用獨立的 `Install / Update project guideline` 選項安裝或更新 project guideline（納管的 instruction files、治理文件與安全 hooks）
* 修復 broken 的 managed install
* 移除 managed skills
* 切換 target
* 只有在需要時才進入 expert terminal

分群、推薦清單與描述關鍵字上色都集中設定在 `canonical-skills/catalog.json`，詳見 [docs/reference/catalog-and-agent-memory.md](docs/reference/catalog-and-agent-memory.md)。

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
* [docs/reference/catalog-and-agent-memory.md](docs/reference/catalog-and-agent-memory.md)

### Project guideline

除了 skills 之外，這個 repo 也納管一組 project guideline 設定項，每一項都有自己的 canonical source：

```text
canonical-configs/
├── agent-memory/       # memory.md → CLAUDE.md（claude）/ AGENTS.md（codex）
│   ├── config.json
│   └── memory.md
├── agent-guideline/    # guideline.md → docs/agent-guideline.md（兩個 target 相同）
│   ├── config.json
│   └── guideline.md
└── agent-hooks/        # safety_check.py + additive native hook 設定
    ├── config.json
    └── hooks/safety_check.py
```

兩個文件項目使用檔尾 HTML marker 做版本與 drift 偵測。`agent-hooks` 會安裝帶 marker 的 Python runner，並只把 skill-forge 擁有的 entries 結構化合併至 `.claude/settings.json` 或 `.codex/hooks.json`；其他使用者設定與 hooks 都會保留。既有衝突檔案若沒有 ownership marker，會被視為 `unmanaged`，永遠不會覆蓋。

Managed hooks 需要 `python3` 指向 Python 3.11 或更新版本。Claude 使用原生 `PreToolUse` hooks 保護 `Bash`、`Edit`、`Write`；Codex 使用 project `.codex/hooks.json` 保護 `Bash` 與 `apply_patch`。Codex 可能需要針對每個精確 hook definition 執行 review/trust；`[features] hooks = false` 會回報為 `inactive`。Hooks 只是縱深防禦，不能取代 sandbox、權限、CI 或人工批准。

Recursive forced deletion 若含有無法解析的 glob（例如 `rm -rf *` 或 `rm -rf build/*.tmp`）會被拒絕，因為 hook 無法安全判定展開後的目標集合。請改用明確且局部的路徑，或在 hook 之外取得人工批准。

可從互動選單的 `Install / Update project guideline` 選項安裝，或用 CLI：

```bash
skill-forge guideline status  [--item NAME] --target <codex|claude> --project <path> [--json]
skill-forge guideline install [--item NAME] --target <codex|claude> --project <path> [--force] [--yes]
```

兩個指令預設涵蓋所有可用項目；某一項安裝失敗會回報錯誤但不會中斷其餘項目。`skill-forge memory status|install` 保留為操作同一份 `agent-memory` 檔案與 marker 的相容指令，但維持舊版輸出形狀（`memory status --json` 回傳單一物件；對應的 `guideline` 篩選指令回傳單元素陣列）。

使用 `--item agent-hooks` 可只管理安全 bundle。Drift 需要 `--force` 加確認；`unmanaged` 永遠不覆蓋。目前沒有自動 uninstall 指令：手動 recovery 時只移除 skill-forge 擁有的 matcher handlers，以及帶 marker 的 `hooks/skill-forge/safety_check.py`。Windows launcher 支援與 Git pre-commit fallback 仍延後處理。

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
  * `import-plugin-skill`
  * `install-manager-skill`
  * `skill-review-packet`

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
   * `import-plugin-skill`
   * `install-manager-skill`
   * `skill-review-packet`
4. 只有在必要時才退回 terminal 命令。
5. 不要手動修改 rendered artifacts，例如：

   * `.agents/skills/`
   * `.claude/skills/`

建議分工：

* 新增 skill → `create-skill`
* 修改 skill → `update-skill`
* 匯入下載回來的外部 skill → `import-plugin-skill`
* 收尾與驗證 → `finalize-skill`
* 同步 manager targets → `install-manager-skill` 或 `sync-manager-catalog`

### 外部 skill 匯入策略

下載回來的外部 skill 不應直接複製進 `canonical-skills/`。

維護者應透過 `import-plugin-skill`：

- 檢查單一本機外部 skill 來源
- 先由 `skillkeeper` 判斷這個 skill 是否值得 canonicalize
- 透過 `imitator`、`reviewer` 與 final `skillkeeper` admission 產出 staged draft
- 在詢問最終人工同意前，先產出 `skill-review-packet`
- 明確決定正式納管到 `regular-skills/` 或 `manager-skills/`
- promote 後直接完成 finalize 與 Codex smoke test
- 只有在整個 intake flow 成功後才清掉對應的 staging draft

建議本機工作區結構：

```text
tmp/
├── foreign_skills/
└── import-candidates/
```

- `tmp/foreign_skills/`：下載回來的外部 skill 來源
- `tmp/import-candidates/`：review 後產生的 canonical draft

promotion 不是流程終點。成功匯入後應完成 finalize、smoke test，再清理 staging draft。

詳細流程請參考：

* [docs/guides/external-skill-import-guide.md](docs/guides/external-skill-import-guide.md)

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
docker run --rm -e PYTHONPATH=src -v "$PWD:/workspace" -w /workspace \
  skill-forge-dev python -m unittest discover -s tests
```

#### Runtime smoke test

```bash
make up
```

---

## 在 Claude 或 Codex 內安裝 skills

`install-my-skill` 讓你不需要離開 AI session，直接在對話中安裝和更新 skills。

### 前置條件

- `install-my-skill` 本身需先安裝一次。首次使用時，透過 `skill-manager` 安裝：

  ```bash
  ~/skill-forge/skill-manager
  # 選 Install / Update skills → 選取 install-my-skill
  ```

  若 `install-my-skill` 已在 shared catalog 中，執行 `sync-manager-catalog` 時會自動納入。

### 使用方式

在 Claude 或 Codex session 中，說：

> 「幫我安裝 skill」或「更新我的 skills」

Agent 將會：

1. 取得可安裝清單與目前的安裝狀態
2. 呈現含版本與狀態標記的選單
3. 安裝或更新你選取的 skills
4. 回報結果並提醒你 reload session

若要依 Roadmap 開發，安裝 `deliver-roadmap-phase` 即可；安裝器會揭露並自動帶入所需的 Change Workflow skills。重新開啟 agent session 後，以唯一 Phase 呼叫：

```text
請使用 deliver-roadmap-phase。
Roadmap: docs/Roadmap.md
Phase: Phase 1 — Walking Skeleton
Mode: supervised-auto
```

它只會規劃指定 Phase、要求一次執行批准、協調已批准的子 Changes，最後停在獨立審查與人類驗收；不會自行推定下一 Phase，也不會隱含 commit、push、merge、release 或 deploy。

範例畫面：

```
請選擇要安裝/更新的 skill（可複選）：

 1. commit        v1.3.0  ✓ 已安裝（最新）
 2. create-pr     v1.2.0  ⬆ 有更新（1.1.0→1.2.0）
 3. dto-organizer v0.3.0  ○ 未安裝
```

### 已知限制

- **需要 reload：** skills 在 session 啟動時載入。安裝完成後，需重新開啟 Claude 或 Codex session，新 skill 才會生效。
- **需要 Docker：** agent 透過 shell 呼叫 `skill-manager`，後者在 Docker 容器內執行。
- **不覆蓋 unmanaged skills：** 若 skill 已存在但非由 skill-forge 管理，agent 會拒絕安裝並說明原因。

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
* `guideline status` / `guideline install`
* `memory status` / `memory install`（操作 `agent-memory` 項目的相容指令）

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
│   ├── catalog.json
│   ├── regular-skills/
│   └── manager-skills/
├── canonical-configs/
│   ├── agent-memory/
│   ├── agent-guideline/
│   └── agent-hooks/
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
