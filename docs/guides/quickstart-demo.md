# Quickstart and Demo

## English

### What You Will See

This walkthrough shows the core mental model:

1. define a skill once in `canonical-skills/regular-skills/`
2. render it for Codex or Claude
3. install it into a target project through `skill-manager`

### High-Level Flow

```text
canonical-skills/regular-skills/commit/
        |
        v
 validate + render
        |
        +------------------+
        |                  |
        v                  v
 .agents/skills/      .claude/agents/
   commit/              commit.md
        \                  /
         \                /
          +---- install --+
                 |
                 v
          target project
```

### Quickstart

1. Clone the toolkit repo.

```bash
git clone git@github.com:busybutlazy/skill-forge.git ~/skill-forge
```

2. Open your target project.

```bash
cd /path/to/target-project
```

3. Launch the menu.

```bash
~/skill-forge/skill-manager
```

4. Choose a target.

Pick `codex` or `claude` in the menu.

5. Install an approved skill.

Select `Install` and choose a managed skill such as `commit` or `create-pr`.

6. Check status.

Use `Check installed skill status` to verify whether the installed package is:

- `up_to_date`
- `update_available`
- `drift`
- `broken`
- `unmanaged`

### What Rendered Targets Look Like

#### Codex target

Rendered output installs into:

```text
<project>/.agents/skills/<name>/
```

#### Claude target

Rendered output installs into:

```text
<project>/.claude/agents/<name>.md
```

Claude skills may also include an adjacent assets directory when the canonical package includes managed assets.

### Demo Scenario

Use `commit` as the simplest example:

- the canonical package lives in `canonical-skills/regular-skills/commit/`
- it is validated as a canonical package
- it can be rendered into Codex and Claude target formats
- it can then be installed into a target project through a managed flow

### Maintainer Demo Commands

From the toolkit repo:

```bash
PYTHONPATH=src python -m skill_toolkit --repo-root . validate commit
PYTHONPATH=src python -m skill_toolkit --repo-root . render commit --target codex --output /tmp/commit-codex
PYTHONPATH=src python -m skill_toolkit --repo-root . render commit --target claude --output /tmp/commit-claude
```

### Consumer Demo Path

For an end user, the preferred path is shorter:

```bash
cd /path/to/target-project
~/skill-forge/skill-manager
```

Then:

- select target
- install skill
- check status
- update or remove later through the same menu

### What The Demo Should Prove

The phase 7 demo is successful if a reader can quickly understand:

- there is one canonical source
- Codex and Claude outputs are rendered targets, not separate source trees
- the target-project workflow is managed rather than manual
- the repo is solving governance and portability, not marketplace discovery

## 繁體中文

### 你會看到什麼

這份 walkthrough 要展示的核心心智模型是：

1. 在 `canonical-skills/regular-skills/` 中定義 skill 一次
2. 為 Codex 或 Claude render
3. 透過 `skill-manager` 安裝到 target project

### 高層流程

```text
canonical-skills/regular-skills/commit/
        |
        v
 validate + render
        |
        +------------------+
        |                  |
        v                  v
 .agents/skills/      .claude/agents/
   commit/              commit.md
        \                  /
         \                /
          +---- install --+
                 |
                 v
          target project
```

### 快速開始

1. 複製 toolkit repo。

```bash
git clone git@github.com:busybutlazy/skill-forge.git ~/skill-forge
```

2. 打開你的 target project。

```bash
cd /path/to/target-project
```

3. 啟動 menu。

```bash
~/skill-forge/skill-manager
```

4. 選擇 target。

在 menu 中選 `codex` 或 `claude`。

5. 安裝 approved skill。

選 `Install`，再安裝像 `commit` 或 `create-pr` 這樣的 managed skill。

6. 檢查狀態。

用 `Check installed skill status` 檢查安裝內容目前屬於哪個狀態：

- `up_to_date`
- `update_available`
- `drift`
- `broken`
- `unmanaged`

### Render 後的 targets 長什麼樣

#### Codex target

render 後的 output 會安裝到：

```text
<project>/.agents/skills/<name>/
```

#### Claude target

render 後的 output 會安裝到：

```text
<project>/.claude/agents/<name>.md
```

如果 canonical package 包含 managed assets，Claude skill 旁邊也可能帶一個 assets 目錄。

### Demo 情境

最簡單的示範可以用 `commit`：

- canonical package 位於 `canonical-skills/regular-skills/commit/`
- 它先作為 canonical package 被驗證
- 然後可被 render 成 Codex 與 Claude target format
- 最後再透過 managed flow 安裝到 target project

### Maintainer demo 指令

在 toolkit repo 中可以這樣示範：

```bash
PYTHONPATH=src python -m skill_toolkit --repo-root . validate commit
PYTHONPATH=src python -m skill_toolkit --repo-root . render commit --target codex --output /tmp/commit-codex
PYTHONPATH=src python -m skill_toolkit --repo-root . render commit --target claude --output /tmp/commit-claude
```

### Consumer demo 路徑

對一般使用者來說，推薦路徑更短：

```bash
cd /path/to/target-project
~/skill-forge/skill-manager
```

接著：

- 選 target
- 安裝 skill
- 檢查狀態
- 後續再透過同一個 menu 更新或移除

### Demo 應該證明什麼

如果讀者能快速理解以下幾點，phase 7 demo 就算成功：

- 只有一份 canonical source
- Codex 與 Claude output 是 rendered targets，不是兩套 source tree
- target-project workflow 是 managed 的，不是手動複製
- 這個 repo 解的是治理與可移植性，不是 marketplace discovery
