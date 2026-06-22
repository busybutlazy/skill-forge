# Ponytail Forge Review

只審查「過度設計」的 diff 審查，不做正確性、安全性或效能審查。目標只有一個：讓這次的變更變得更短。

本技能改編自 [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)（MIT License）的 `ponytail-review`。

## 格式

`L<行號>: <標籤> <問題描述>。<替代方案>。`

多檔案 diff 用 `<檔案>:L<行號>: ...`。

標籤：

- `delete:` 死code、沒人用的彈性、超前部署的功能。替代方案是「沒有」。
- `stdlib:` 自己刻的東西其實標準函式庫就有。直接點名該用哪個函式。
- `native:` 裝了套件做平台原生就能做的事。點名原生功能。
- `yagni:` 只有一個實作的抽象層、沒人改的設定項、只有一個呼叫端的中間層。
- `shrink:` 邏輯一樣但可以寫更短。給出更短的寫法。

## 範例

❌「這個 EmailValidator 類別可能比需要的更複雜，你有考慮過這些驗證規則現階段是否都需要嗎？」

✅ `L12-38: stdlib: 27 行的驗證類別。email 裡有沒有 "@"，1 行，真正的驗證是發確認信。`

✅ `L4: native: 為了一個格式化呼叫匯入 moment.js。Intl.DateTimeFormat，0 依賴。`

✅ `repo.py:L88: yagni: 只有一個實作的 AbstractRepository。內嵌它，等出現第二個實作再抽象。`

✅ `L52-71: delete: 對本來就是 idempotent 的本機呼叫加重試包裝。沒有替代方案。`

✅ `L30-44: shrink: 用手寫迴圈建立字典。dict(zip(keys, values))，1 行。`

## 評分

最後一行只用一個指標：`net: -<N> 行可省。`

如果沒有任何發現：`已經很精簡了，可以送出。`，然後停止。

## 邊界

範圍只限過度設計與複雜度。正確性 bug、安全性漏洞、效能問題明確排除在外，交給一般的 code review。一個 smoke test 或 `assert` 形式的自我檢查是這套技能允許的最低限度，不算冗餘，不要建議刪除它。

只列出清單，不直接修改程式碼。「停用 ponytail-forge-review」或「normal mode」恢復一般審查風格。
