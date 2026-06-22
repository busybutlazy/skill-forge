# Ponytail Forge Debt

把整個 codebase 裡的 `ponytail-forge:` 標記註解收集成一份技術債帳本，讓核心技能刻意留下的捷徑與延後事項不會在「之後再做」裡悄悄爛掉。

本技能改編自 [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)（MIT License）的 `ponytail-debt`。

## 慣例

`ponytail-forge` 每次刻意走捷徑時，會留一個固定格式的註解，寫出天花板與升級時機：

```
# ponytail-forge: <天花板>，<升級時機>
```

例如：`# ponytail-forge: 全域鎖，吞吐量出問題時改成 per-account 鎖`

## 掃描

對整個 repo 執行 grep，排除 `node_modules`、`.git`、build 產物：

```
grep -rnE '(#|//) ?ponytail-forge:' .
```

如果專案用到其他語言的註解符號（例如 `--` 或 `;`），補上對應的 pattern。前綴限定只抓真正的標記，不會抓到只是提到這個慣例的閒聊文字。

## 輸出

每筆標記一行，依檔案分組：

`<檔案>:<行號>，簡化了什麼。天花板：<天花板>。升級時機：<升級時機>。`

天花板與升級時機直接從註解內容拆出來。想知道是誰留下這筆債，可以加一行 `git blame -L<行號>,<行號>`。

如果某筆 `ponytail-forge:` 註解沒寫出升級時機或觸發條件，標記 `no-trigger`，這種債最容易被遺忘、爛掉。

最後一行：`<N> 筆標記，<M> 筆沒有升級時機。` 沒有找到任何標記：`沒有 ponytail-forge: 技術債，帳本是乾淨的。`

## 邊界

只讀取與報告，不修改任何程式碼。使用者要求才會把帳本寫成檔案（例如 `PONYTAIL-FORGE-DEBT.md`）。一次性報告。

「停用 ponytail-forge-debt」或「normal mode」恢復一般狀態。
