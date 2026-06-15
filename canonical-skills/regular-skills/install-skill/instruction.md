---
name: install-skill
description: Skill catalog and install manager. Use when the user wants to install, update, or review available skills without leaving the Claude session.
---

# install-skill

## Trigger

Invoke when the user expresses intent to install, update, list, or manage skills — for example: "install a skill", "update my skills", "what skills can I install?", "manage skills".

## Environment detection (do not ask the user)

**Target**: determined by which agent system is executing this instruction.
- Running in Claude → `--target claude`
- Running in Codex → `--target codex`

**Skill-forge wrapper**: detect the OS, then use the default install location.

```sh
uname -s 2>/dev/null
```

- Linux / macOS → `~/skill-forge/skill-manager`
- Windows (uname unavailable, or returns MINGW / CYGWIN / MSYS) → invoke as `& "$HOME\skill-forge\skill-manager.ps1"` in PowerShell

If the wrapper is not found at the default path, stop and tell the user.

**Project directory**: the current working directory (`pwd`). Run `skill-manager` from that directory — it mounts `$PWD` into Docker automatically. Always pass `--project /workspace/project` to the CLI (that path is fixed inside the container regardless of host OS).

## Flow

### Step 1 — Fetch catalog and status in parallel

```sh
~/skill-forge/skill-manager --no-interactive catalog --target <target> --json
~/skill-forge/skill-manager --no-interactive list --target <target> --project /workspace/project --json
```

Both commands are independent; run them concurrently.

### Step 2 — Present selection list

Cross-reference the two outputs. For each skill in the catalog, assign a status badge:

| Installed status     | Badge |
|----------------------|-------|
| `up_to_date`         | ✓ 已安裝（最新） |
| `update_available`   | ⬆ 有更新（`<installed>` → `<catalog>`） |
| `drift`              | ⚠ 已安裝（有本地修改） |
| `broken`             | ✗ 損壞 |
| not in installed list | ○ 未安裝 |

Present as a numbered list. Include name, catalog version, and badge. Example:

```
請選擇要安裝/更新的 skill（輸入編號，可複選以逗號分隔）：

 1. commit        v1.3.0  ✓ 已安裝（最新）
 2. create-pr     v1.2.0  ⬆ 有更新（1.1.0 → 1.2.0）
 3. dto-organizer v0.3.0  ○ 未安裝
 4. install-skill v1.0.0  ✓ 已安裝（最新）
```

Wait for the user's selection. If nothing is chosen, exit.

### Step 3 — Install selected skills

Handle each selection based on its status:

**Not installed / `update_available`** — install directly:
```sh
~/skill-forge/skill-manager --no-interactive install <name> --target <target> --project /workspace/project
```

**`drift`** — explain that the local copy has been modified and installing will overwrite those changes. Ask the user for explicit confirmation before proceeding. If confirmed:
```sh
~/skill-forge/skill-manager --no-interactive install <name> --target <target> --project /workspace/project --force --yes
```

**`unmanaged`** — do not install. Tell the user the skill was not installed by skill-forge and will not be overwritten automatically. Ask them to remove it manually first if they want to replace it.

**`broken`** — attempt repair:
```sh
~/skill-forge/skill-manager --no-interactive install <name> --target <target> --project /workspace/project --yes
```

Install skills one at a time. Report each result before moving to the next.

### Step 4 — Summary and reload reminder

```
安裝完成：
  ✓ create-pr     → .claude/skills/create-pr/
  ✓ dto-organizer → .claude/skills/dto-organizer/
  ✗ some-skill    → 失敗：<error message>

⚠ 注意：請重新開啟 session 後，新安裝的 skill 才會生效。
```

## Constraints

- Derive target, project path, and skill-forge location automatically. Do not ask the user for any of them.
- `--no-interactive` must always be the first argument to `skill-manager`.
- Do not attempt hot-reload; it is not supported.
- Never overwrite `unmanaged` skills without explicit user instruction.
