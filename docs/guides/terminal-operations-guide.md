# Terminal Operations Guide

## English

### Purpose

This guide explains the current terminal surface end to end so maintainers can tell which entrypoint to use, what each command does, and when to use the maintainer-only workflow instead of the consumer menu.

### Two Mental Models

Use the terminal surface in two different ways:

- consumer path: run `skill-manager` from a target project and use the menu
- maintainer path: run `python -m skill_forge` from the skill-forge repo

The key difference is simple:

- consumers manage installed approved skills
- maintainers manage the canonical source itself

### `skill-manager`

`skill-manager` is the preferred consumer entrypoint.

On Windows PowerShell, use `skill-manager.ps1`.

Behavior:

- with no arguments, it opens the interactive menu for the current project
- `skill-manager shell` opens the runtime container's expert terminal
- `skill-manager help` prints local usage text without starting Docker
- any other arguments are forwarded to the containerized `skill-forge` CLI
- before each run, it checks whether the skill-forge repo is behind upstream and can offer a `git pull --ff-only`
- it rebuilds the runtime image before execution

Use `skill-manager` when you want:

- install or update approved skills
- remove managed installs
- inspect current install state
- avoid thinking about Docker flags or project paths

PowerShell examples:

```powershell
& "$HOME\skill-forge\skill-manager.ps1"
& "$HOME\skill-forge\skill-manager.ps1" shell
& "$HOME\skill-forge\skill-manager.ps1" list --target codex --project /workspace/project --json
```

Windows path notes:

- use `$HOME\skill-forge\skill-manager.ps1` instead of `~/skill-forge/skill-manager`
- keep the host mount path in Windows form for Docker invocation; the launcher normalizes it for Compose
- keep container paths such as `/workspace/project` in CLI arguments because those paths are resolved inside the Linux container

If PowerShell blocks `.ps1` execution, allow the current session and retry:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& "$HOME\skill-forge\skill-manager.ps1"
```

### Interactive Menu

The menu wraps the core CLI behavior for consumers.

Main actions:

- `Check installed skill status`: show installed skills and their state
- `Install / Update skills`: install new public skills or refresh current ones
- `Update / Repair skills`: repair `broken` installs or update `update_available` installs
- `Remove installed skills`: remove managed installs
- `Switch target`: switch between `codex` and `claude`
- `Open expert terminal`: drop into the runtime shell, then return to the menu after exit

### Status Model

- `up_to_date`: installed artifact matches the canonical package
- `update_available`: installed version differs from the current canonical version
- `drift`: managed install exists but installed files no longer match rendered output
- `broken`: required managed files are missing or invalid
- `unmanaged`: files exist in the target location but were not installed by skill-forge

Safety rules:

- `install` and `update` refuse to overwrite `unmanaged`
- `install` and `update` require `--force` before overwriting `drift`
- `install` and `update` ask for confirmation before repairing `broken`
- `remove` refuses to delete `unmanaged`

### Core CLI Commands

Run these from the skill-forge repo:

```bash
PYTHONPATH=src python -m skill_forge --repo-root .
```

Commands:

- `validate`: validate canonical packages under both `canonical-skills/regular-skills/` and `canonical-skills/manager-skills/`
- `render`: render one canonical package to a target output tree
- `install`: install one public canonical skill into a target project
- `list`: inspect installed state for a target project
- `list --scope all`: inspect installed state including maintainer-only canonical packages
- `remove`: remove a managed install from a target project
- `update`: update a managed install from canonical source
- `menu`: open the interactive menu directly
- `refresh-metadata`: rebuild `manifest.json` and integrity hash for one canonical skill
- `sync-maintainer`: render and install maintainer-only skills into a project, usually this repo itself
- `sync-manager-catalog`: render and install manager-skills plus `shared` regular-skills into local agent targets

Recommended manager-skill-first flow:

- `create-skill` or `update-skill` for source edits
- `import-plugin-skill` for reviewed external skill imports
- `finalize-skill` for refresh + validate
- `install-manager-skill` for local target sync

Use direct CLI commands as the fallback path, not the primary path.

### External Skill Imports

Use `import-plugin-skill` when a maintainer needs to bring a downloaded external skill into the canonical workflow without bypassing review.

Policy:

- keep downloaded sources under `tmp/foreign_skills/`
- stage converted drafts under `tmp/import-candidates/`
- do not copy external content directly into `canonical-skills/`
- require an LLM review before promotion
- run `finalize-skill` after promotion

### Maintainer-Only Commands

#### `refresh-metadata`

Use after changing a canonical skill's shared instruction, target overrides, or managed assets.

Examples:

```bash
PYTHONPATH=src python -m skill_forge --repo-root . refresh-metadata create-skill --today
PYTHONPATH=src python -m skill_forge --repo-root . refresh-metadata commit --version 1.0.1 --updated-at 2026-04-04
```

What it does:

- rebuilds the manifest file list from `instruction.md`, `targets/`, and managed asset directories
- recalculates file `sha256` values
- recalculates `manifest.json.package_sha256`
- syncs `package.json.integrity.package_sha256`
- optionally updates `identity.version`
- optionally updates `identity.updated_at`

#### `sync-maintainer`

Use when the repo's local `.agents/skills/` should be refreshed from canonical maintainer packages.

Examples:

```bash
PYTHONPATH=src python -m skill_forge --repo-root . sync-maintainer --project . --target codex
PYTHONPATH=src python -m skill_forge --repo-root . sync-maintainer --project . --target codex --force
```

When to use `--force`:

- migrating old unmanaged maintainer skill folders into canonical managed output
- overwriting local drift in an existing maintainer install

#### `sync-manager-catalog`

Use when the repo's local agent targets should include both:

- all `manager-skills/`
- selected `regular-skills/` tagged with `shared`

Examples:

```bash
PYTHONPATH=src python -m skill_forge --repo-root . sync-manager-catalog --project . --target all
PYTHONPATH=src python -m skill_forge --repo-root . sync-manager-catalog create-skill commit --project . --target codex --force
```

### Public vs Maintainer Skills

`canonical-skills/` is split into two explicit roots:

- `canonical-skills/regular-skills/`: distributable skills exposed through the normal consumer path
- `canonical-skills/manager-skills/`: manager-only workflows that should stay out of the consumer menu
- some regular-skills may also carry the `shared` tag so manager workflows can sync them without creating a second source package

`.agents/skills/` is not source. It is a rendered Codex artifact location.

### Recommended Maintainer Loop

1. Edit a canonical package in `canonical-skills/regular-skills/` or `canonical-skills/manager-skills/`.
2. Run `validate`.
3. Run `refresh-metadata` if render-driving files changed.
4. Run `validate` again.
5. Run `finalize-skill` after source edits; if you skip the skill flow, use `refresh-metadata` plus `validate` directly.
6. If the skill is manager-only, run `sync-maintainer --project . --target codex`; if it is a shared manager catalog flow, run `install-manager-skill` or `sync-manager-catalog`.
6. Run tests and smoke checks.

## 繁體中文

### 目的

這份文件把目前 terminal surface 從頭到尾講清楚，讓 maintainer 能快速判斷該用哪個入口、每個命令實際做什麼，以及什麼時候要走 maintainer workflow，而不是 consumer menu。

### 兩條心智模型

terminal 介面其實分成兩種用法：

- consumer path：在 target project 執行 `skill-manager`
- maintainer path：在 skill-forge repo 執行 `python -m skill_forge`

關鍵差異很簡單：

- consumer 管的是已安裝的 approved skills
- maintainer 管的是 canonical source 本身

### `skill-manager`

`skill-manager` 是一般使用者的主要入口。

在 Windows PowerShell 上請使用 `skill-manager.ps1`。

它的行為是：

- 不帶參數時，為目前專案打開 interactive menu
- `skill-manager shell` 會進入 runtime container 的 expert terminal
- `skill-manager help` 只在本機顯示 usage，不會啟動 Docker
- 其他參數會直接轉發到 containerized `skill-forge` CLI
- 每次執行前會檢查 repo 是否落後 upstream，必要時提示 `git pull --ff-only`
- 每次執行前都會重建 runtime image

適合用在：

- 安裝或更新 approved skills
- 移除 managed install
- 檢查目前狀態
- 不想自己處理 Docker 參數與 project path

PowerShell 範例：

```powershell
& "$HOME\skill-forge\skill-manager.ps1"
& "$HOME\skill-forge\skill-manager.ps1" shell
& "$HOME\skill-forge\skill-manager.ps1" list --target codex --project /workspace/project --json
```

Windows 路徑注意事項：

- 啟動器請用 `$HOME\skill-forge\skill-manager.ps1`，不要預設寫成 `~/skill-forge/skill-manager`
- host 端掛載路徑維持 Windows 路徑語意，由啟動器轉成 Compose 較穩定的格式
- CLI 參數中的 `/workspace/project` 這類容器內路徑仍然保留正斜線，因為它是在 Linux container 內解析

如果 PowerShell 擋住 `.ps1` 執行，可以先放行目前這個 session 再重試：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& "$HOME\skill-forge\skill-manager.ps1"
```

### Interactive Menu

這個 menu 是 consumer flow 的包裝層。

主功能：

- `Check installed skill status`：列出已安裝 skill 與狀態
- `Install / Update skills`：安裝新的 public skill，或刷新目前版本
- `Update / Repair skills`：修復 `broken` 或更新 `update_available`
- `Remove installed skills`：移除 managed install
- `Switch target`：切換 `codex` 與 `claude`
- `Open expert terminal`：進入 runtime shell，離開後回到 menu

### 狀態模型

- `up_to_date`：已安裝內容與 canonical package 一致
- `update_available`：已安裝版本和目前 canonical version 不同
- `drift`：是 managed install，但檔案內容已不等於 render output
- `broken`：managed install 缺少必要檔案或 metadata 異常
- `unmanaged`：目標位置有內容，但不是由 skill-forge 安裝

安全規則：

- `install` 與 `update` 不會覆蓋 `unmanaged`
- `install` 與 `update` 覆蓋 `drift` 前必須 `--force`
- `install` 與 `update` 修復 `broken` 前會要求確認
- `remove` 不會刪除 `unmanaged`

### Core CLI Commands

在 skill-forge repo 裡執行：

```bash
PYTHONPATH=src python -m skill_forge --repo-root .
```

命令用途：

- `validate`：驗證 `canonical-skills/regular-skills/` 與 `canonical-skills/manager-skills/` 底下的 canonical package
- `render`：把單一 canonical skill render 到指定 target output tree
- `install`：把單一 public canonical skill 安裝到 target project
- `list`：查看 target project 的安裝狀態
- `list --scope all`：查看 target project 狀態時一併納入 maintainer-only canonical packages
- `remove`：從 target project 移除 managed install
- `update`：用 canonical source 更新 managed install
- `menu`：直接打開 interactive menu
- `refresh-metadata`：重建單一 canonical skill 的 `manifest.json` 與 integrity hash
- `sync-maintainer`：把 maintainer-only skills render/install 到指定專案，通常就是這個 repo 自己
- `sync-manager-catalog`：把 manager-skills 加上帶 `shared` tag 的 regular-skills 一起同步到本地 agent targets

推薦的 manager-skill-first 流程：

- source 編輯用 `create-skill` 或 `update-skill`
- 外部匯入用 `import-plugin-skill`
- 收尾用 `finalize-skill`
- 本地同步用 `install-manager-skill`

直接 CLI 指令保留作 fallback，不是主要推薦路徑。

### 外部 skill 匯入

當 maintainer 要把下載回來的外部 skill 納入 canonical workflow 時，應使用 `import-plugin-skill`，不要直接把內容搬進 `canonical-skills/`。

策略：

- 下載來源放在 `tmp/foreign_skills/`
- 轉換後的 draft 放在 `tmp/import-candidates/`
- promotion 前先做 LLM review
- promotion 完成後再跑 `finalize-skill`

### 維護者專用命令

#### `refresh-metadata`

當你修改了 canonical skill 的 shared instruction、target override 或 managed assets 之後使用。

範例：

```bash
PYTHONPATH=src python -m skill_forge --repo-root . refresh-metadata create-skill --today
PYTHONPATH=src python -m skill_forge --repo-root . refresh-metadata commit --version 1.0.1 --updated-at 2026-04-04
```

它會做的事：

- 從 `instruction.md`、`targets/` 與受管 asset 目錄重建 manifest 檔案清單
- 重算各檔案 `sha256`
- 重算 `manifest.json.package_sha256`
- 同步更新 `package.json.integrity.package_sha256`
- 視需要更新 `identity.version`
- 視需要更新 `identity.updated_at`

#### `sync-maintainer`

當 repo 本地的 `.agents/skills/` 需要從 canonical maintainer packages 重新同步時使用。

範例：

```bash
PYTHONPATH=src python -m skill_forge --repo-root . sync-maintainer --project . --target codex
PYTHONPATH=src python -m skill_forge --repo-root . sync-maintainer --project . --target codex --force
```

`--force` 適用時機：

- 要把舊的 unmanaged maintainer skill 目錄遷移成 canonical managed output
- 要覆寫既有 maintainer install 的 drift

#### `sync-manager-catalog`

當 repo 本地 agent targets 應該同時包含下列內容時使用：

- `manager-skills/` 內全部技能
- 帶有 `shared` tag 的 `regular-skills/`

範例：

```bash
PYTHONPATH=src python -m skill_forge --repo-root . sync-manager-catalog --project . --target all
PYTHONPATH=src python -m skill_forge --repo-root . sync-manager-catalog create-skill commit --project . --target codex --force
```

### Public 與 Maintainer Skills

`canonical-skills/` 現在明確分成兩個根目錄：

- `canonical-skills/regular-skills/`：一般分發用 skill，會出現在正常 consumer flow
- `canonical-skills/manager-skills/`：repo 管理者維護技能，不應出現在 consumer menu
- 某些 `regular-skills/` 可以加上 `shared` tag，表示 manager install flow 也能同步它，但 canonical source 仍只有一份

`.agents/skills/` 不是來源，只是 rendered Codex artifact 位置。

### 建議的 Maintainer 工作循環

1. 在 `canonical-skills/regular-skills/` 或 `canonical-skills/manager-skills/` 修改 source。
2. 跑 `validate`。
3. 如果動到 render-driving files，就跑 `refresh-metadata`。
4. 再跑一次 `validate`。
5. source 改完後先跑 `finalize-skill`；若跳過 skill flow，才直接用 `refresh-metadata` 與 `validate`。
6. 若是 manager-only skill，就跑 `sync-maintainer --project . --target codex`；若屬於 manager catalog，改跑 `install-manager-skill` 或 `sync-manager-catalog`。
6. 補測試與 smoke check。
