# Skillkeeper Initial：grilling

## 來源摘要

來源為 Matt Pocock `skills/productivity/grilling`，提供依決策依賴逐題訪談的方法。

## 納管價值與風險

它補足專案決策收斂的核心 primitive，且維護面積小。主要風險是把推薦誤認成決策、或讓 method 越權進入實作；canonicalization 必須加入 authority adapter，並定位為 internal method。

## Must preserve

- decision tree 與依賴順序
- 一次一個主要問題
- 每題具體推薦
- 可查證事實先自行查證
- 決策仍由使用者確認
- 未達共同理解前不執行

## Removable only if justified

- 上游針對直接 `/grilling` 呼叫的入口文案

## Verdict

`allow`
