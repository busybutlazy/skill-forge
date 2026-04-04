# Skill Toolkit

用來維護、驗證、render、安裝 canonical skills 的 toolkit repo。

phase 3 起，這個 repo 採用單一 canonical source 模型：

- `canonical-skills/` 是唯一 source of truth
- Codex 與 Claude 安裝內容都由 renderer 產出
- `skill-base/` 已淘汰，不再是公開 skill 的維護入口

這個專案的主要使用者不需要是 Python 工程師。phase 6 起，對一般使用者來說，主要入口是 project-local 的 `skill-manager` wrapper 與互動式文字選單。

## 一般使用者流程

### 1. 先準備 toolkit repo

```bash
git clone git@github.com:busybutlazy/skill-forge.git ~/skill-forge
```

把 repo 放在固定位置後，將 [skill-manager](/Users/busybutlazy/Documents/github_projects/skill-forge/skill-manager) 加到你的 `PATH`，或在目標專案中用絕對路徑執行它。

### 2. 到你的 target project 根目錄

```bash
cd /path/to/target-project
```

### 3. 啟動 skill manager

```bash
skill-manager
```

這個 wrapper 會：

- 自動把目前目錄當成 target project
- 自動帶入目前使用者的檔案權限對映
- 啟動 phase 6 的互動式 menu

### 4. 在 menu 裡操作

啟動後先選 `codex` 或 `claude`，再用數字選單操作：

- 檢查目前 project 已安裝 skill 狀態
- 批次安裝或更新多個 skill
- 批次更新或修復多個 skill
- 批次移除 skill
- 切換 target
- 進入 expert terminal

menu 會直接顯示：

- 方框式主畫面與 target / status summary
- 每次切頁會清空舊畫面後重繪，不會一直累積舊 log
- 以顏色區分 `up_to_date`、`update_available`、`drift`、`broken`、`unmanaged`
- 每個 skill 的版本、描述與部分 tags
- 安裝 / 更新 / 移除時的多選模式，可用逗號選多個，安裝與更新也可用 `a` 一次全選

如果你只是要確認現在專案裡哪些 skill 需要更新，直接進入 menu 後選 target，再選 `Check installed skill status` 即可。

## 使用前提

- 一般使用者路線以 Docker 為主
- 主要入口是 target project 內的 `skill-manager`
- 需要先安裝並啟動 Docker Desktop 或等價 Docker daemon
- 不再建議在 host 上直接安裝 toolkit CLI

## 安裝教學

### 1. Clone 這個 repo

```bash
git clone git@github.com:busybutlazy/skill-forge.git ~/skill-forge
cd ~/skill-forge
```

如果你的正式 repo 名稱不同，把上面的 repo URL 換成實際網址即可。

### 2. 確認 Docker 已啟動

```bash
docker version
```

如果 daemon 沒有啟動，`skill-manager` 與容器化 CLI 都無法使用。

### 3. 啟動 skill manager

在 target project 根目錄執行：

```bash
skill-manager
```

第一次執行時，wrapper 會自動 build / 更新 runtime image，之後直接進入互動式 menu。

## 一般使用者常用操作

- 安裝 / 更新 / 移除 skill：直接在 `skill-manager` menu 裡完成
- 切換 target：在 menu 裡選 `Switch target`
- 檢查已安裝狀態：在 menu 裡選 `Check installed skill status`
- 進 expert terminal：執行 `skill-manager shell`

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

### 4. 在容器內驗證 canonical skills

```bash
PYTHONPATH=src python -m skill_toolkit --repo-root . validate
```

### 5. 在容器內跑 phase 3.5 測試

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

### 6. 在容器內做 target smoke test

```bash
mkdir -p /tmp/skill-toolkit-demo
PYTHONPATH=src python -m skill_toolkit --repo-root . install commit --target codex --project /tmp/skill-toolkit-demo
PYTHONPATH=src python -m skill_toolkit --repo-root . list --target codex --project /tmp/skill-toolkit-demo --json
PYTHONPATH=src python -m skill_toolkit --repo-root . remove commit --target codex --project /tmp/skill-toolkit-demo
```

### 7. 使用 `compose.yaml`

如果你的環境支援 Docker Compose，可以改用：

```bash
docker compose run --rm toolkit-dev
```

若你要連續執行多個驗證命令，建議依序執行，不要平行開多個 `docker compose run`。同一個 compose project 在同時建立 network / container 資源時，可能出現暫時性的資源競爭。

這份 `compose.yaml` 只提供維護者快速進入掛載了 repo 的開發 shell，不是 phase 5 的最終 runtime 介面。

## 容器化 CLI

phase 5 / phase 6 的容器模式分成兩層：

- 一般使用者：從 target project 根目錄直接跑 `skill-manager`
- 維護者或進階使用者：在 toolkit repo 內跑 `make up`、`docker compose run` 或 direct CLI

### 一般使用者主入口

在目標專案根目錄執行：

```bash
skill-manager
```

若你要直接進 expert terminal，可執行：

```bash
skill-manager shell
```

如果你只是忘了 wrapper 的用法，可直接在 host 上查：

```bash
skill-manager --help
```

### 維護者入口

在 toolkit repo 根目錄執行：

```bash
make up
```

這會進入同一個 runtime image，只是 mount 預設會以目前目錄作為 target project。

### 直接執行單次命令

如果你是維護者或進階使用者，也可以直接透過 runtime container 執行單次命令：

```bash
docker compose run --build --rm toolkit validate
```

## Project Layout

```text
skill-toolkit/
├── AGENTS.md
├── .dockerignore
├── .agents/
│   └── skills/
├── Makefile
├── compose.yaml
├── docker/
│   ├── runtime-entrypoint.sh
│   └── runtime-shellrc
├── Dockerfile
├── Dockerfile.dev
├── skill-manager
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
docker build -f Dockerfile.dev -t skill-toolkit-dev .
docker run --rm -it -v "$PWD:/workspace" -w /workspace skill-toolkit-dev \
  bash -lc 'PYTHONPATH=src python -m unittest discover -s tests'
```

容器化開發驗證：

```bash
docker build -f Dockerfile.dev -t skill-toolkit-dev .
docker run --rm -it -v "$PWD:/workspace" -w /workspace skill-toolkit-dev
```

phase 5 runtime smoke test：

```bash
make up
```

## Compatibility Note

`skill-manager.sh` 已退役為相容提示入口，不再承擔主要邏輯。核心邏輯仍由 Python CLI 提供；phase 6 另外新增了 project-local 的 `skill-manager` wrapper，作為一般使用者的主要啟動入口。
