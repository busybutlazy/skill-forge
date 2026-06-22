# Ponytail Forge Audit

`ponytail-forge-review` 的全 repo 版本。不是看 diff，而是掃整個 codebase，產出一份依「砍下去能省最多」排序的清單。

本技能改編自 [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)（MIT License）的 `ponytail-audit`。

## 標籤

跟 `ponytail-forge-review` 用同一套：

- `delete:` 死code、沒人用的彈性、超前部署的功能。替代方案是「沒有」。
- `stdlib:` 自己刻的東西其實標準函式庫就有。直接點名該用哪個函式。
- `native:` 裝了套件做平台原生就能做的事。點名原生功能。
- `yagni:` 只有一個實作的抽象層、沒人改的設定項、只有一個呼叫端的中間層。
- `shrink:` 邏輯一樣但可以寫更短。給出更短的寫法。

## 搜尋目標

標準函式庫或平台原生本來就有的依賴、只有一個實作的介面、只有一個產品的 factory、純轉發的 wrapper、只 export 一個東西的檔案、沒人用的設定旗標與功能開關、自己刻的標準函式庫等價物。

排除 `node_modules`、`vendor`、`dist`、`build`、`.git`、產生的程式碼。

## 輸出

依「砍下去能省最多」排序，一行一個發現：`<標籤> <要砍的東西>。<替代方案>。[路徑]`。

最後一行：`net: -<N> 行, -<M> 個依賴可省。` 沒有東西可砍：`已經很精簡了，可以送出。`

## 邊界

範圍只限過度設計與複雜度。正確性 bug、安全性漏洞、效能問題不在範圍內，交給一般的 code review。只列出清單，不修改任何程式碼。一次性報告。

「停用 ponytail-forge-audit」或「normal mode」恢復一般狀態。
