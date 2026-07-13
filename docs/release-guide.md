# Release Guide

每次發布新版本的完整步驟。

---

## 前置確認（只需做一次）

1. GitHub repo → **Settings → Actions → General**
   → Workflow permissions → 選 **"Read and write permissions"** → Save

2. 第一次 publish 完後，到 `https://github.com/busybutlazy?tab=packages`
   → 點 `skill-forge` → **Package settings** → Change visibility → **Public**

---

## 每次發布流程

### 1. 確認在 main 且乾淨

```bash
git checkout main
git pull origin main
git status   # 應該顯示 "nothing to commit"
```

### 2. 建立 feature branch 並開始工作

```bash
git checkout -b dev_jett
# ... 改 code ...
```

### 3. 更新版本號

兩個檔案都要改，版本號必須一致：

**`pyproject.toml`**
```toml
[project]
version = "1.1.3"   # ← 改這裡
```

**`Dockerfile`**
```dockerfile
ARG FORGE_VERSION=1.1.3   # ← 改這裡
```

版本號規則（[Semantic Versioning](https://semver.org/)）：

| 情境 | 範例 |
|------|------|
| 修 bug、小調整 | `1.1.2` → `1.1.3` |
| 新增功能，不破壞舊用法 | `1.1.2` → `1.2.0` |
| 有 breaking change | `1.1.2` → `2.0.0` |

### 4. Commit 並推上去

```bash
git add .
git commit -m "feat/fix/chore: 描述這次做了什麼"
git push origin dev_jett
```

### 5. 開 PR 並 merge 到 main

```bash
gh pr create --base main --head dev_jett \
  --title "你的 PR 標題" \
  --body "簡短說明"
```

在 GitHub 上確認並 merge。

### 6. 拉最新 main

```bash
git checkout main
git pull origin main
```

### 7. Push tag 觸發自動發布

```bash
git tag v1.1.3
git push origin v1.1.3
```

tag push 後約 2-3 分鐘，GitHub Actions 會自動：
- Build Docker image
- Push 到 `ghcr.io/busybutlazy/skill-forge:1.1.3`
- Push 到 `ghcr.io/busybutlazy/skill-forge:1.1`
- Push 到 `ghcr.io/busybutlazy/skill-forge:latest`

### 8. 確認發布成功

前往 `https://github.com/busybutlazy/skill-forge/actions` 確認 workflow 綠燈。

---

## 本地測試（發布前想先驗證）

```bash
# 用本地 code 建 image
make build-local

# 用本地 image 跑（不走 GHCR）
SKILL_FORGE_IMAGE=ghcr.io/busybutlazy/skill-forge:local make up
```

---

## 常用指令速查

```bash
make up               # pull 最新 image 並執行
make validate-runtime # pull 最新 image 並執行 validate
make build-local      # 本地 build（測試用）
make dev              # 進入開發模式（volume mount 整個 workspace）
```
