# Skill Toolkit

用來維護、驗證、render、安裝 canonical skills 的 toolkit repo。

phase 3 起，這個 repo 採用單一 canonical source 模型：

- `canonical-skills/` 是唯一 source of truth
- Codex 與 Claude 安裝內容都由 renderer 產出
- `skill-base/` 已淘汰，不再是公開 skill 的維護入口

這個專案的主要使用者不需要是 Python 工程師。你只需要照著下面步驟做，就可以把 toolkit 裝起來並安裝 skill 到目標專案。

## 使用前提

- `skill-toolkit ...`
  - 需要先執行 `python3 -m pip install -e .`
- `python3 -m skill_toolkit ...`
  - 也需要先安裝到目前 Python 環境
  - 如果你只是要在 repo 內直接跑開發版本測試，可改用 `PYTHONPATH=src python3 -m skill_toolkit ...`

## 安裝教學

### 1. Clone 這個 repo

```bash
git clone git@github.com:busybutlazy/Skill_Merchant-.git ~/Skill_Merchant
cd ~/Skill_Merchant
```

如果你的正式 repo 名稱不同，把上面的 repo URL 換成實際網址即可。

### 2. 確認電腦有 Python 3.11 以上

先檢查：

```bash
python3 --version
```

你應該看到類似：

```text
Python 3.11.x
```

如果版本太舊，先安裝新版 Python，再回來繼續。

### 3. 建議先建立虛擬環境

這一步不是強制，但很建議。它可以避免把 toolkit 依賴裝到系統全域環境。

建立虛擬環境：

```bash
python3 -m venv .venv
```

啟用虛擬環境：

macOS / Linux:

```bash
source .venv/bin/activate
```

啟用後你通常會看到 shell 提示前面多出 `(.venv)`。

### 4. 安裝 toolkit CLI

在 repo 根目錄執行：

```bash
python3 -m pip install -e .
```

安裝完成後，你可以用任一種方式執行：

```bash
skill-toolkit --help
python3 -m skill_toolkit --help
```

如果 `skill-toolkit --help` 找不到指令，通常代表：

- 你沒有啟用虛擬環境
- 或 PATH 還沒包含目前安裝位置

這種情況直接用：

```bash
python3 -m skill_toolkit --help
```

也可以正常工作。

### 5. 先驗證 toolkit repo 內的 canonical skills

在 toolkit repo 根目錄執行：

```bash
python3 -m skill_toolkit --repo-root . validate
```

如果一切正常，會看到類似：

```text
VALID commit ...
VALID create-pr ...
VALID dto-organizer ...
```

## 安裝 skill 到目標專案

以下範例假設：

- toolkit repo 在 `~/Skill_Merchant`
- 目標專案在 `/path/to/target-project`

### 1. 安裝 Codex skill 到目標專案

```bash
cd ~/Skill_Merchant
python3 -m skill_toolkit --repo-root . install commit --target codex --project /path/to/target-project
```

安裝後，目標專案會出現：

```text
/path/to/target-project/.agents/skills/commit/
```

### 2. 安裝 Claude skill 到目標專案

```bash
cd ~/Skill_Merchant
python3 -m skill_toolkit --repo-root . install commit --target claude --project /path/to/target-project
```

安裝後，目標專案會出現：

```text
/path/to/target-project/.claude/agents/commit.md
```

### 3. 檢查目標專案目前已安裝的 skill

Codex:

```bash
python3 -m skill_toolkit --repo-root . list --target codex --project /path/to/target-project
```

Claude:

```bash
python3 -m skill_toolkit --repo-root . list --target claude --project /path/to/target-project
```

如果你要給自動化流程或腳本使用，可改成：

```bash
python3 -m skill_toolkit --repo-root . list --target codex --project /path/to/target-project --json
```

或：

```bash
python3 -m skill_toolkit --repo-root . list --target claude --project /path/to/target-project --json
```

### 4. 更新已安裝的 skill

一般更新：

```bash
python3 -m skill_toolkit --repo-root . update commit --target codex --project /path/to/target-project
```

若目標安裝已經 `drift`，要明確允許覆蓋本地變動：

```bash
python3 -m skill_toolkit --repo-root . update commit --target codex --project /path/to/target-project --force
```

`--force` 仍會顯示確認提示，避免把本地修改靜默覆蓋。

如果你是重新安裝既有 skill，而該安裝已經 `drift`，`install` 也需要同樣加上 `--force`：

```bash
python3 -m skill_toolkit --repo-root . install commit --target codex --project /path/to/target-project --force
```

### 5. 移除已安裝的 skill

Codex:

```bash
python3 -m skill_toolkit --repo-root . remove commit --target codex --project /path/to/target-project
```

Claude:

```bash
python3 -m skill_toolkit --repo-root . remove commit --target claude --project /path/to/target-project
```

## 常用指令

### 驗證 canonical skills

```bash
python3 -m skill_toolkit --repo-root . validate
```

### 單獨 render 某個 skill 到輸出資料夾

Codex:

```bash
python3 -m skill_toolkit --repo-root . render commit --target codex --output /tmp/rendered
```

Claude:

```bash
python3 -m skill_toolkit --repo-root . render commit --target claude --output /tmp/rendered
```

### 更新單一已安裝 skill

```bash
python3 -m skill_toolkit --repo-root . update commit --target codex --project /path/to/target-project
```

### 直接從 repo 內跑開發版 CLI

```bash
PYTHONPATH=src python3 -m skill_toolkit --repo-root . validate
```

### 跑 phase 3 測試

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

## 容器化開發環境

phase 4 的目的是提供維護者可重現的開發與測試環境，避免依賴 host 上的 Python 狀態。這一段是 maintainer workflow，不是 phase 5 的最終對外發佈方式。

### 1. 先啟動 Docker daemon

先確認 Docker Desktop 或等價 daemon 已啟動：

```bash
docker version
```

如果 daemon 沒有啟動，`docker build` 與 `docker run` 都會失敗。

### 2. 建立開發用 image

在 repo 根目錄執行：

```bash
docker build -f Dockerfile.dev -t skill-toolkit-dev .
```

### 3. 直接用 `docker run` 進入 repo 開發環境

```bash
docker run --rm -it \
  -v "$PWD:/workspace" \
  -w /workspace \
  skill-toolkit-dev
```

進入容器後，先安裝目前 repo 的開發版套件：

```bash
python -m pip install -e .
```

### 4. 在容器內驗證 canonical skills

```bash
python -m skill_toolkit --repo-root . validate
```

### 5. 在容器內跑 phase 3.5 測試

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

### 6. 在容器內做 target smoke test

```bash
mkdir -p /tmp/skill-toolkit-demo
python -m skill_toolkit --repo-root . install commit --target codex --project /tmp/skill-toolkit-demo
python -m skill_toolkit --repo-root . list --target codex --project /tmp/skill-toolkit-demo --json
python -m skill_toolkit --repo-root . remove commit --target codex --project /tmp/skill-toolkit-demo
```

### 7. 使用 `compose.yaml`

如果你的環境支援 Docker Compose，可以改用：

```bash
docker compose run --rm toolkit-dev
```

若你要連續執行多個驗證命令，建議依序執行，不要平行開多個 `docker compose run`。同一個 compose project 在同時建立 network / container 資源時，可能出現暫時性的資源競爭。

進入容器後同樣執行：

```bash
python -m pip install -e .
```

這份 `compose.yaml` 只提供維護者快速進入掛載了 repo 的開發 shell，不是 phase 5 的最終 runtime 介面。

## Project Layout

```text
skill-toolkit/
├── AGENTS.md
├── .dockerignore
├── .agents/
│   └── skills/
├── compose.yaml
├── Dockerfile.dev
├── canonical-skills/
│   └── <skill>/
│       ├── package.json
│       ├── instruction.md
│       ├── manifest.json
│       ├── targets/
│       ├── examples/
│       ├── references/
│       ├── scripts/
│       └── assets/
├── docs/
│   └── phase2/
├── proof/
│   └── phase2/
├── src/
│   └── skill_toolkit/
├── tests/
├── pyproject.toml
├── ROADMAP.md
└── TODO/
```

## Canonical Model

每個公開 skill 都放在 `canonical-skills/<name>/`，至少包含：

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

- `docs/phase2/canonical-package-spec.md`
- `docs/phase2/adapter-contract.md`
- `docs/phase2/drift-policy.md`

## CLI Commands

- `validate`
  - 驗證 canonical package 結構、frontmatter override、manifest、package hash
- `render`
  - 從 canonical source 產出 Codex 或 Claude target artifact
- `install`
  - 安裝 rendered package 到目標專案
  - `up_to_date` 與 `update_available` 的 managed package 會直接覆蓋
  - `broken` 的 managed package 會要求確認後修復
  - `drift` 的 managed package 需加 `--force`，且仍會要求確認
  - `unmanaged` package 會拒絕覆蓋
- `list`
  - 列出已安裝 package 與狀態
  - 可加 `--json` 輸出機器可解析格式
- `remove`
  - 移除 managed package
  - 也允許移除帶 toolkit marker 的 broken install
- `update`
  - 用 canonical source 重新覆蓋已安裝 managed package
  - phase 3.5 先只支援單一 skill 更新
  - `drift` 狀態需加 `--force`，且仍會要求確認

`list` 目前會區分：

- `up_to_date`
- `update_available`
- `drift`
- `broken`
- `unmanaged`

狀態定義：

- `up_to_date`
  - 安裝內容與 canonical render output 一致
- `update_available`
  - 已安裝版本與 canonical source 版本不同
- `drift`
  - 仍可辨識為 toolkit 管理物，但本地內容或 hash 已與 canonical source 不一致
- `broken`
  - 必要檔案缺失、格式錯誤，或無法完成基本解析
- `unmanaged`
  - 目標位置有內容，但不是目前 toolkit 可安全管理的安裝

## 安裝與更新規則

- `install` 對 `up_to_date` 與 `update_available` 的 managed package 直接覆蓋。
- `install` 遇到 `broken` 時會要求確認，再覆蓋修復。
- `install` 遇到 `drift` 時必須加 `--force`，並在覆蓋前要求確認。
- `install` 會拒絕覆蓋 `unmanaged` package。
- `update` 只處理已安裝且可辨識為 managed 的 package。
- `update` 遇到 `drift` 時必須加 `--force`，並在覆蓋前要求確認。
- `update` 遇到 `broken` 時會要求確認，再覆蓋修復。
- `remove` 會拒絕刪除 `unmanaged` package。

## Public Skills vs Maintainer Skills

- `canonical-skills/`
  - 公開可分發 skills 的唯一來源
  - 由 Python CLI 驗證與 render
- `.agents/skills/`
  - 這個 repo 內部使用的 maintainer skills
  - 不會被公開安裝流程直接當作 source

## Validation and Tests

執行 phase 3 測試：

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

容器化驗證：

```bash
docker build -f Dockerfile.dev -t skill-toolkit-dev .
docker run --rm -it -v "$PWD:/workspace" -w /workspace skill-toolkit-dev
```

## Compatibility Note

`skill-manager.sh` 已退役為相容提示入口，不再承擔主要邏輯。新的正式使用方式是 Python CLI。
