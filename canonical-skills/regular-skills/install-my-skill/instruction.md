# install-my-skill

## Trigger

Invoke when the user expresses intent to install, update, list, or manage skills — for example: "install a skill", "update my skills", "what skills can I install?", "manage skills".

## Hard rules — read before running anything

Everything needed to complete this task is in this file. Run the commands below **verbatim**; the only substitution you ever make is `<target>` and `<name>`.

1. **Do not explore.** Never `ls`, `cat`, `find`, or read files under `~/skill-forge/`, the wrapper script itself, or the installed skill directories (`.claude/skills/`, `.agents/skills/`) to "figure out how this works". The commands below are the complete interface.
2. **Never run `skill-manager` without `--no-interactive`.** The bare command opens an interactive TTY menu that waits for keyboard input and will hang forever in an agent session. `--no-interactive` must always be the first argument.
3. **Do not call `docker` or `docker compose` directly.** The wrapper handles all container setup.
4. **stderr noise is normal.** The wrapper prints image pull/build logs and `Container ... Creating` messages to stderr. That is not an error. Parse stdout only; a command failed only if its exit code is non-zero.
5. **First run can be slow** (Docker image pull, 1–3 minutes). Do not abort, retry, or switch strategies while it runs.

## Environment (derive silently — never ask the user)

- **Target**: Claude session → `--target claude`; Codex session → `--target codex`.
- **Wrapper**: `~/skill-forge/skill-manager` on Linux/macOS; on Windows PowerShell use `& "$HOME\skill-forge\skill-manager.ps1"` with the same arguments.
- **Working directory**: run the wrapper from the project root (current `pwd`); it mounts the current directory into Docker automatically. Always pass `--project /workspace/project` — that container-internal path is fixed on every host OS.

## Flow

### Step 1 — Fetch catalog and install status

Run exactly (both JSON commands are independent — run them in parallel when possible):

```sh
test -x ~/skill-forge/skill-manager || echo WRAPPER_MISSING
~/skill-forge/skill-manager --no-interactive catalog --target <target> --json
~/skill-forge/skill-manager --no-interactive list --target <target> --project /workspace/project --json
```

If `WRAPPER_MISSING` is printed, stop and tell the user to clone the repo first: `git clone https://github.com/busybutlazy/skill-forge.git ~/skill-forge`.

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
 4. install-my-skill v1.0.0  ✓ 已安裝（最新）
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
  ✗ some-skill    → 失敗：<exit code 非 0 時的 stderr 最後幾行>

⚠ 注意：請重新開啟 session 後，新安裝的 skill 才會生效。
```

## Constraints

- Derive target, project path, and skill-forge location automatically. Do not ask the user for any of them.
- Do not attempt hot-reload; it is not supported.
- Never overwrite `unmanaged` skills without explicit user instruction.
- If a command fails (non-zero exit), report the tail of its stderr to the user and stop — do not start reading repo files to debug on your own.
