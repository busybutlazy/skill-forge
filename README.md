# Skill Toolkit

Version: 1.1.0

## English

Write skills once, govern centrally, deploy to multiple coding AI targets.

Skill Toolkit is an open-source governance layer for AI development skills. It helps teams keep skill definitions in one canonical source, validate package integrity, and render and install the right target artifacts for tools such as Codex and Claude.

This repo is not a public skill marketplace. It is designed for teams that want controlled distribution, portable skill definitions, and a clearer trust boundary around which skills engineers are allowed to use.

### Current Stage

Version `1.1.0` extends the `1.0.0` end-user baseline with a formal maintainer workflow and canonical manager skill model.

The current phase moves beyond the first user-facing baseline and focuses on maintainer operations:

- separating canonical source into `regular-skills/` and `manager-skills/`
- formalizing the manager workflow around `create-skill`, `update-skill`, `finalize-skill`, and `install-manager-skill`
- keeping repo-local Codex and Claude manager artifacts in sync from canonical source

### What Changed In This Stage

- `canonical-skills/` is now split into `canonical-skills/regular-skills/` and `canonical-skills/manager-skills/`
- `finalize-skill` was added so maintainers can finish a canonical edit with `refresh-metadata` and `validate` in one workflow
- `install-manager-skill` was added so manager-only skills and `shared` regular skills can be synced back into this repo's local agent targets
- maintainer guidance in README and the terminal guide now reflects the full create/update/finalize/install loop

### Why This Exists

```text
canonical-skills/
  regular-skills/
  manager-skills/
        |
        v
 validate + render + package integrity
        |
        +--------------------+
        |                    |
        v                    v
   Codex artifact      Claude artifact
        |                    |
        +-------- install / update -------+
                             |
                             v
                    target project workflow
```

Teams adopting coding agents usually run into the same problems:

- engineers install skills from inconsistent or unknown sources
- the same workflow gets rewritten separately for each AI tool
- there is no shared review point for versioning, integrity, or rollout
- switching vendors becomes expensive because skill logic is tied to one tool

Skill Toolkit addresses that by treating `canonical-skills/` as the only canonical source tree, with `regular-skills/` for normal end-user skills and `manager-skills/` for manager-only workflows, then rendering target-specific outputs for each supported tool.

### Who It Is For

- engineering managers who want an approved source for team skills
- platform teams who need a controlled way to distribute internal AI workflows
- developers who want a project-local skill manager without hand-maintaining per-tool copies

This repo is a good fit when you care about governance, portability, and repeatable distribution more than marketplace-style discovery.

### How To Read This Repo

- Start here for the product story and top-level workflow.
- Read [docs/concepts/governance.md](docs/concepts/governance.md) for the governance model and trust story.
- Read [docs/guides/adoption-guide.md](docs/guides/adoption-guide.md) for team rollout guidance.
- Read [docs/guides/quickstart-demo.md](docs/guides/quickstart-demo.md) for a quickstart and demo walkthrough.
- Read [docs/guides/maintainer-terminal-guide.md](docs/guides/maintainer-terminal-guide.md) for the full terminal and maintainer operations manual.

### Quickstart

1. Clone the toolkit repo.

```bash
git clone git@github.com:busybutlazy/skill-forge.git ~/skill-forge
```

2. Go to your target project.

```bash
cd /path/to/target-project
```

3. Launch the project-local skill manager.

```bash
~/skill-forge/skill-manager
```

Or add `~/skill-forge` to your `PATH` and run:

```bash
skill-manager
```

4. Use the interactive menu to:

- choose `codex` or `claude`
- check installed skill status
- install or update skills
- repair broken managed installs
- remove managed skills
- switch targets or open the expert terminal

### Positioning

#### Canonical source, not parallel copies

Public skills live under `canonical-skills/regular-skills/`. Manager-only workflows live under `canonical-skills/manager-skills/`. Both are validated once, versioned once, and rendered into target artifacts instead of being maintained as separate per-tool source trees.

#### Governance layer, not a marketplace

The goal is not to maximize public skill discovery. The goal is to give a team a controlled source, a repeatable packaging model, and a safer install and update path for approved skills.

#### Portability layer, not vendor lock-in

Skill logic should be written once in a tool-neutral canonical package, then adapted to supported targets. That keeps future adapter expansion possible without falling back to copy-paste maintenance.

#### Native capabilities and governance responsibilities

Native AI tool features are still responsible for the in-product execution experience of each tool. Skill Toolkit is trying to solve a different problem: giving teams a canonical source, a governed distribution model, and a more portable way to manage skill definitions across tools.

It is not a replacement for the native capabilities of Codex, Claude, or other coding AI products. It is a team-level governance layer that can sit alongside those tools when a team wants more control over source, rollout, and portability.

### Current User Experience

For day-to-day usage, the main entrypoint is the project-local `skill-manager` wrapper.

- Docker-based runtime for end users
- interactive menu for install, update, remove, and status flows
- direct CLI path for maintainers and advanced users
- Codex and Claude supported as rendered targets

### Canonical Model

Each public skill lives in `canonical-skills/regular-skills/<name>/` and includes:

- `package.json`
- `instruction.md`
- `manifest.json`
- `targets/codex.frontmatter.json`
- `targets/claude.frontmatter.json`

Optional content:

- `examples/`
- `references/`
- `scripts/`
- `assets/`

Detailed contracts:

- `docs/reference/canonical-package-spec.md`
- `docs/reference/adapter-contract.md`
- `docs/reference/drift-policy.md`

### CLI and Safety Model

Core commands:

- `validate`
- `render`
- `install`
- `list`
- `remove`
- `update`
- `refresh-metadata`
- `sync-maintainer`
- `sync-manager-catalog`

Managed install states:

- `up_to_date`
- `update_available`
- `drift`
- `broken`
- `unmanaged`

Key safety rules:

- `install` overwrites managed `up_to_date` and `update_available` installs
- `install` asks for confirmation before repairing `broken`
- `install` requires `--force` before overwriting `drift`
- `install` refuses to overwrite `unmanaged`
- `update` only works on managed installs and also requires `--force` for `drift`
- `remove` refuses to delete `unmanaged`

### Public Skills vs Maintainer Skills

- `canonical-skills/regular-skills/`
  - canonical source for normal end-user skills
  - the only source consumer installs should come from
- `canonical-skills/manager-skills/`
  - canonical source for manager-only workflows such as `create-skill`, `update-skill`, `finalize-skill`, and `install-manager-skill`
  - not intended for normal user installation
- `canonical-skills/regular-skills/` skills may optionally carry the `shared` tag
  - `shared` means the skill stays a regular-skill source, but manager install flow may also sync it into this repo
- `.agents/skills/`
  - rendered Codex artifacts used to work on this repo itself
  - not a source directory
  - can be refreshed from canonical maintainer packages through `sync-maintainer`

### Maintainer Workflow

Containerized development environment:

```bash
docker build -f Dockerfile.dev -t skill-toolkit-dev .
docker run --rm -it -v "$PWD:/workspace" -w /workspace skill-toolkit-dev
```

Validate canonical skills:

```bash
PYTHONPATH=src python -m skill_toolkit --repo-root . validate
```

If you want the low-level terminal fallback after changing a canonical skill, refresh manifest and package integrity metadata with:

```bash
PYTHONPATH=src python -m skill_toolkit --repo-root . refresh-metadata create-skill --today
```

Sync maintainer-only skills into this repo's local Codex skill directory:

```bash
PYTHONPATH=src python -m skill_toolkit --repo-root . sync-maintainer --project . --target codex --force
```

Sync the full manager catalog, including manager-skills plus `shared` regular-skills, into both local targets:

```bash
PYTHONPATH=src python -m skill_toolkit --repo-root . sync-manager-catalog --project . --target all --force
```

Inspect repo-local installs including maintainer-only packages:

```bash
PYTHONPATH=src python -m skill_toolkit --repo-root . list --target codex --project . --scope all --json
```

Run tests:

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

Runtime smoke test:

```bash
make up
```

Recommended maintainer workflow with Codex:

1. Open this repo in Codex and keep the repo-local manager skills available under `.agents/skills/`.
2. Use `create-skill` when you need to add a new canonical skill under `canonical-skills/regular-skills/`.
3. Use `update-skill` when you need to revise an existing canonical skill, including tags such as `shared`.
4. After changing canonical content, run `refresh-metadata` and `validate`.
5. Use `install-manager-skill` or `sync-manager-catalog` when you want to sync manager-skills plus `shared` regular-skills back into this repo's local agent targets.

Recommended maintainer workflow with Claude:

1. Open this repo in Claude and use the manager workflows rendered from `canonical-skills/manager-skills/`.
2. Keep source edits limited to `canonical-skills/regular-skills/` and `canonical-skills/manager-skills/`; do not edit rendered `.agents/skills/` or `.claude/agents/` artifacts by hand.
3. Use `create-skill` only for new canonical packages and `update-skill` only for existing ones.
4. After source changes, run `refresh-metadata`, `validate`, and then `sync-manager-catalog --target all` when you want Codex and Claude maintainer targets refreshed together.

### Project Layout

```text
skill-toolkit/
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
└── skill-manager
```

### Roadmap Direction

The current roadmap focuses on external clarity, adoption, and governance framing rather than new UI work. CLI and TUI remain the primary operating surface for now.

See `ROADMAP.md` for current priorities and direction.

### Compatibility Note

`skill-manager.sh` remains a compatibility shim only. The real workflow is the Python CLI plus the project-local `skill-manager` wrapper.

## 繁體中文

以單一 canonical source 管理 AI coding skills，集中治理，再部署到多個 coding AI target。

Skill Toolkit 是一個面向 AI 開發技能的開源治理層。它讓團隊可以把 skill 定義收斂到單一 canonical source，驗證 package 完整性，並為 Codex、Claude 等工具 render 與安裝正確的 target artifact。

這個 repo 不是公開 skill marketplace。它的定位是提供團隊可控的 skill 分發、可移植的 skill 定義，以及更清楚的信任邊界，讓工程師使用的 skills 有可管理來源。

### 目前階段

`1.1.0` 是在 `1.0.0` 一般使用者基礎體驗之上，正式補齊 maintainer workflow 與 canonical manager skill model 的版本。

目前這個階段則是從第一階段的 user-facing baseline，進一步往 maintainer workflow 收斂：

- 把 canonical source 正式分成 `regular-skills/` 與 `manager-skills/`
- 把管理者流程固定成 `create-skill`、`update-skill`、`finalize-skill`、`install-manager-skill`
- 讓本 repo 的 Codex / Claude manager artifacts 可以從 canonical source 一致同步

### 這個階段改了什麼

- `canonical-skills/` 現在正式拆成 `canonical-skills/regular-skills/` 與 `canonical-skills/manager-skills/`
- 新增 `finalize-skill`，讓維護者可以在同一個 workflow 內完成 `refresh-metadata` 與 `validate`
- 新增 `install-manager-skill`，讓 manager-only skills 與帶 `shared` tag 的 regular skills 可以同步回本 repo 的本地 agent targets
- README 與 maintainer terminal guide 都已更新成完整的 create / update / finalize / install 維護流程

### 為什麼會有這個專案

```text
canonical-skills/
  regular-skills/
  manager-skills/
        |
        v
 validate + render + package integrity
        |
        +--------------------+
        |                    |
        v                    v
   Codex artifact      Claude artifact
        |                    |
        +-------- install / update -------+
                             |
                             v
                    target project workflow
```

導入 coding agent 的團隊通常會遇到相同問題：

- 工程師各自安裝來源不一致、甚至不明的 skills
- 同一套 workflow 被迫為不同 AI 工具重寫多次
- 缺少共用的版本、完整性與發佈審查點
- 一旦 skill 邏輯綁死在單一工具上，改用其他 vendor 的成本就會變高

Skill Toolkit 的解法是把 `canonical-skills/` 視為唯一 canonical source tree，其中 `regular-skills/` 給一般使用者技能、`manager-skills/` 給管理者流程，再為各個支援的工具 render 對應的 target-specific output。

### 適合誰使用

- 想要替團隊建立 approved skill source 的 engineering managers
- 需要可控分發內部 AI workflow 的 platform teams
- 希望用 project-local skill manager，而不是手動維護多套工具版本的 developers

當你更在意治理、可移植性與可重現分發，而不是 marketplace 式的探索體驗時，這個 repo 就是合適選擇。

### 如何閱讀這個 repo

- 先從這份 README 了解產品定位與高層流程。
- 用 [docs/concepts/governance.md](docs/concepts/governance.md) 看治理模型與 trust story。
- 用 [docs/guides/adoption-guide.md](docs/guides/adoption-guide.md) 看團隊導入建議。
- 用 [docs/guides/quickstart-demo.md](docs/guides/quickstart-demo.md) 看 quickstart 與 demo walkthrough。

### 快速開始

1. 複製 toolkit repo。

```bash
git clone git@github.com:busybutlazy/skill-forge.git ~/skill-forge
```

2. 進入 target project。

```bash
cd /path/to/target-project
```

3. 啟動 project-local skill manager。

```bash
~/skill-forge/skill-manager
```

如果你已經把 `~/skill-forge` 加進 `PATH`，也可以直接執行：

```bash
skill-manager
```

4. 在互動式 menu 裡：

- 選 `codex` 或 `claude`
- 檢查已安裝 skill 狀態
- 安裝或更新 skills
- 修復 broken 的 managed install
- 移除 managed skills
- 切換 target 或進入 expert terminal

### 定位

#### canonical source，不是平行副本

公開 skill 都放在 `canonical-skills/regular-skills/`，管理者專用 skill 則放在 `canonical-skills/manager-skills/`。它們都只被驗證一次、只被版本管理一次，再被 render 成不同 target artifact，而不是維護多份平行的 per-tool source tree。

#### 治理層，不是 marketplace

這個 repo 的目標不是最大化公開 skill 的探索與上架，而是提供團隊可控來源、可重現 packaging model，以及對 approved skills 更安全的 install 與 update 路徑。

#### 可移植層，不是 vendor lock-in

skill 邏輯應該先寫成 tool-neutral 的 canonical package，再適配到支援的 targets。這讓未來新增 adapter 成為可能，而不必回到 copy-paste 維護多套版本。

#### 原生能力與治理責任的分工

各個 AI 工具的原生功能仍然負責它們各自產品內的執行體驗。Skill Toolkit 想解的是另一個層次的問題：為團隊提供 canonical source、可治理的分發模型，以及跨工具管理 skill 定義的可移植方式。

它不是要取代 Codex、Claude 或其他 coding AI 產品的原生能力。它比較像是一層團隊級的治理層，讓需要更高來源控制、rollout 管理與可移植性的團隊，可以和這些工具並行使用。

### 目前的使用體驗

日常使用時，主要入口是 project-local `skill-manager` wrapper。

- 一般使用者走 Docker-based runtime
- 透過互動式 menu 完成 install、update、remove 與 status 流程
- 維護者與進階使用者仍可直接走 CLI
- 目前支援 Codex 與 Claude 兩個 rendered targets

### Canonical Model

每個公開 skill 都放在 `canonical-skills/regular-skills/<name>/`，至少包含：

- `package.json`
- `instruction.md`
- `manifest.json`
- `targets/codex.frontmatter.json`
- `targets/claude.frontmatter.json`

可選內容：

- `examples/`
- `references/`
- `scripts/`
- `assets/`

詳細契約請看：

- `docs/reference/canonical-package-spec.md`
- `docs/reference/adapter-contract.md`
- `docs/reference/drift-policy.md`

### CLI 與安全模型

核心指令：

- `validate`
- `render`
- `install`
- `list`
- `remove`
- `update`
- `refresh-metadata`
- `sync-maintainer`
- `sync-manager-catalog`

managed install 狀態：

- `up_to_date`
- `update_available`
- `drift`
- `broken`
- `unmanaged`

主要安全規則：

- `install` 會直接覆蓋 managed 的 `up_to_date` 與 `update_available`
- `install` 修復 `broken` 前會要求確認
- `install` 覆蓋 `drift` 前必須加 `--force`
- `install` 會拒絕覆蓋 `unmanaged`
- `update` 只處理 managed install，遇到 `drift` 也必須加 `--force`
- `remove` 會拒絕刪除 `unmanaged`

### 公開 skills 與 maintainer skills

- `canonical-skills/regular-skills/`
  - 一般使用者 skill 的 canonical source
- `canonical-skills/manager-skills/`
  - 管理者工作流 skill 的 canonical source
  - `create-skill`、`update-skill`、`install-manager-skill` 應只出現在這裡
- `canonical-skills/regular-skills/` 中的 skill 可選擇加上 `shared` tag
  - `shared` 代表 canonical source 仍是 regular-skill，但 manager install flow 也可以額外同步它
- `.agents/skills/`
  - 這個 repo 自己使用的 rendered artifact
  - 不是對外分發 skill 的 source

### 維護者工作流程

容器化開發環境：

```bash
docker build -f Dockerfile.dev -t skill-toolkit-dev .
docker run --rm -it -v "$PWD:/workspace" -w /workspace skill-toolkit-dev
```

驗證 canonical skills：

```bash
PYTHONPATH=src python -m skill_toolkit --repo-root . validate
```

當修改 canonical skill 後，刷新 manifest 與 package hash：

```bash
PYTHONPATH=src python -m skill_toolkit --repo-root . refresh-metadata create-skill --today
```

只同步 manager-only skills 到本 repo 本地 Codex 目錄：

```bash
PYTHONPATH=src python -m skill_toolkit --repo-root . sync-maintainer --project . --target codex --force
```

把 manager-skills 加上帶 `shared` tag 的 regular-skills 一起同步到本 repo 本地 targets：

```bash
PYTHONPATH=src python -m skill_toolkit --repo-root . sync-manager-catalog --project . --target all --force
```

執行測試：

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

Runtime smoke test：

```bash
make up
```

推薦的 Codex 維護流程：

1. 用 Codex 打開這個 repo，並讓 repo-local manager skills 維持在 `.agents/skills/` 可用。
2. 若要新增 skill source，就用 `create-skill` 在 `canonical-skills/regular-skills/` 下建立新的 canonical package。
3. 若要修改既有 skill，就用 `update-skill`，包含像 `shared` 這類 tag 調整。
4. canonical 內容改完後，優先用 `finalize-skill` 收尾；若不走 skill workflow，再用 terminal 跑 `refresh-metadata` 與 `validate`。
5. 若要把 manager-skills 與帶 `shared` tag 的 regular-skills 同步回本 repo agent targets，就用 `install-manager-skill` 或 `sync-manager-catalog`。

推薦的 Claude 維護流程：

1. 用 Claude 打開這個 repo，使用由 `canonical-skills/manager-skills/` render 出來的管理技能。
2. source 編輯只限於 `canonical-skills/regular-skills/` 與 `canonical-skills/manager-skills/`，不要手動修改 `.agents/skills/` 或 `.claude/agents/` rendered artifacts。
3. `create-skill` 只用來建立新的 canonical package，`update-skill` 只用來修改既有 package。
4. source 改完後，優先用 `finalize-skill` 收尾；若要走 terminal fallback，再跑 `refresh-metadata`、`validate`。若要一起刷新 Codex 與 Claude 的管理者 targets，再跑 `sync-manager-catalog --target all`。

### 專案結構

```text
skill-toolkit/
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
└── skill-manager
```

### Roadmap 方向

目前 roadmap 的重點是把對外敘事、導入路徑與治理框架講清楚，而不是新增 UI。現階段主要操作面仍然是 CLI 與 TUI。

請參考 `ROADMAP.md` 了解目前的優先順序與方向。

### 相容性說明

`skill-manager.sh` 目前只保留相容提示用途。真正的工作流程已經是 Python CLI 加上 project-local `skill-manager` wrapper。
