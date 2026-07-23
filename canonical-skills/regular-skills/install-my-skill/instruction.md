# install-my-skill

## Trigger

Invoke when the user expresses intent to install, update, list, or manage skills — for example: "install a skill", "update my skills", "what skills can I install?", "manage skills".

## Hard rules — read before running anything

Everything needed to complete this task is in this file. Run the commands below **verbatim**; the only substitution you ever make is `<target>` and `<name>`.

1. **Do not explore.** Never `ls`, `cat`, `find`, or read files under `~/skill-forge/`, the wrapper script itself, or the installed skill directories (`.claude/skills/`, `.agents/skills/`) to "figure out how this works". The commands below are the complete interface. The one exception is that `plan` already returns everything you need — you never need to read a catalog or list file yourself.
2. **Never run `skill-manager` without `--no-interactive`.** The bare command opens an interactive TTY menu that waits for keyboard input and will hang forever in an agent session. `--no-interactive` must always be the first argument.
3. **Do not call `docker` or `docker compose` directly.** The wrapper handles all container setup.
4. **Only ever install `public` skills.** This flow uses `plan`, which returns public skills only — manager/maintainer skills are structurally excluded and must never be installed here. Never pass `--scope all` or `--scope maintainer` in this flow.
5. **stderr noise is normal.** The wrapper prints image pull/build logs and `Container ... Creating` messages to stderr. That is not an error. Parse stdout only; a command failed only if its exit code is non-zero.
6. **First run can be slow** (Docker image pull, 1–3 minutes). Do not abort, retry, or switch strategies while it runs.

## Environment (derive silently — never ask the user)

- **Target**: Claude session → `--target claude`; Codex session → `--target codex`.
- **Wrapper**: `~/skill-forge/skill-manager` on Linux/macOS; on Windows PowerShell use `& "$HOME\skill-forge\skill-manager.ps1"` with the same arguments.
- **Working directory**: run the wrapper from the project root (current `pwd`); it mounts the current directory into Docker automatically. Always pass `--project /workspace/project` — that container-internal path is fixed on every host OS.

## Flow — follow every step in order; do not skip Step 0 or Step 2

### Step 0 — Necessary project settings (auto-apply, but tell the user first)

The project needs baseline security settings in `.claude/settings.local.json`. Check first:

```sh
test -x ~/skill-forge/skill-manager || echo WRAPPER_MISSING
~/skill-forge/skill-manager --no-interactive check-security --project /workspace/project
```

If `WRAPPER_MISSING` is printed, stop and tell the user to clone the repo first: `git clone https://github.com/busybutlazy/skill-forge.git ~/skill-forge`.

**Exit-code semantics for `check-security` only** (this overrides Hard Rule #5 for this one command):
- **Exit 0** — settings already complete. Say nothing, move on.
- **Exit 1 with `Missing:` on stderr** — this is *not* a failure. It means the settings are absent. Tell the user in one line ("我會補上必要的安全設定到 `.claude/settings.local.json`"), then apply them — this is the only thing you apply without a yes/no confirmation:

```sh
~/skill-forge/skill-manager --no-interactive check-security --project /workspace/project --init
```

(Note: running Step 1's `plan --target claude` will also auto-repair missing settings as a safety net, but you should still surface the notice here so the user knows.)

### Step 1 — Fetch the merged plan (one command)

```sh
~/skill-forge/skill-manager --no-interactive plan --target <target> --project /workspace/project --json
```

This one call returns everything: each public skill with its `catalog_version`, `installed_version`, `status`, a ready-to-print `badge`, a `recommended` flag, `tags`, `description`, and `dependencies` — plus a top-level `intent_hints` map. **Do not** call `catalog` or `list` separately, and **do not** cross-reference anything yourself.

`status` is one of: `not_installed`, `up_to_date`, `update_available`, `drift`, `broken`, `unmanaged`.

### Step 2 — Ask the user's project intent (mandatory — never skip)

Before showing any list, ask the user 1–2 short questions about what this project is and what they want to accomplish. You must do this every time; it is what makes the recommendation useful. Examples:

> 這個專案在做什麼？你接下來主要想完成哪類工作（例如：git 提交/PR、規格與變更治理、程式碼審查、文件整理、翻譯…）？

Keep it to one or two questions. Do not guess intent silently.

### Step 3 — Present a recommended, numbered multi-select list

Map the user's stated intent to the `intent_hints` map returned by `plan` (its keys are plain-language intent labels; its values are skill names). Mark a skill with **★推薦** when either:
- its `recommended` flag is `true` (always-recommended baseline), **or**
- its name appears in an `intent_hints` bucket that matches the user's stated intent, **or**
- its `tags` clearly match the user's stated goal.

Present a numbered list using each skill's `badge` verbatim. Put ★推薦 items first. Example:

```
依你的目標，建議安裝（★ 為推薦，輸入編號可複選，逗號分隔；不想裝的直接略過）：

 1. ★ commit        1.3.0  ⬆ 有更新（1.1.0 → 1.3.0）
 2. ★ create-pr     1.3.0  ○ 未安裝
 3. ★ plan-change   0.2.2  ○ 未安裝
 4.   dto-organizer 1.3.0  ○ 未安裝
 5.   translate-pdf-book 1.3.0  ○ 未安裝
```

Everything is opt-in: only install what the user selects. Wait for the selection. If nothing is chosen, exit.

### Step 4 — Install selected skills

Handle each selection based on its `status`:

**`not_installed` / `update_available`** — install directly:
```sh
~/skill-forge/skill-manager --no-interactive install <name> --target <target> --project /workspace/project
```

**`drift`** — explain that the local copy has been modified and installing will overwrite those changes. Ask for explicit confirmation. If confirmed:
```sh
~/skill-forge/skill-manager --no-interactive install <name> --target <target> --project /workspace/project --force --yes
```

**`unmanaged`** — do not install. Tell the user the skill was not installed by skill-forge and will not be overwritten automatically. Ask them to remove it manually first if they want to replace it.

**`broken`** — attempt repair:
```sh
~/skill-forge/skill-manager --no-interactive install <name> --target <target> --project /workspace/project --yes
```

Install skills one at a time. Report each result before moving to the next.

### Step 5 — Summary and reload reminder

```
安裝完成：
  ✓ create-pr     → .claude/skills/create-pr/
  ✗ some-skill    → 失敗：<exit code 非 0 時的 stderr 最後幾行>

⚠ 注意：請重新開啟 session 後，新安裝的 skill 才會生效。
```

## Constraints

- Derive target, project path, and skill-forge location automatically. Do not ask the user for any of them.
- Never skip Step 0 (settings check) or Step 2 (intent question).
- Only install `public` skills; never `--scope all`/`--scope maintainer`; never install manager skills.
- Do not attempt hot-reload; it is not supported.
- Never overwrite `unmanaged` skills without explicit user instruction.
- If a command fails (non-zero exit), report the tail of its stderr to the user and stop — do not start reading repo files to debug on your own.
