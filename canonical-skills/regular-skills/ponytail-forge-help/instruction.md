# Ponytail Forge Help

顯示 ponytail-forge 全家族的快速參考卡。一次性顯示，不是持續生效的模式，不修改任何狀態。

本技能改編自 [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)（MIT License）的 `ponytail-help`。

## 顯示內容

被呼叫時直接顯示這張卡片，不要新增額外的說明：

```
ponytail-forge 快速參考

等級（核心技能 ponytail-forge）
  lite   照需求做，順帶點出更懶的替代方案
  full   階梯強制套用（預設）：YAGNI → stdlib → 平台原生 → 一行 → 最少程式碼
  ultra  YAGNI 極端主義：先交出一行解法，同時質疑需求本身

家族技能
  ponytail-forge          懶惰模式本身，套用階梯寫出最精簡的程式碼
  ponytail-forge-review   審查目前 diff 的過度設計，列出可刪清單，不動手改
  ponytail-forge-audit    全 repo 範圍版本，掃整個 codebase 找過度設計
  ponytail-forge-debt     收集 `ponytail-forge:` 標記，整理成技術債帳本
  ponytail-forge-help     這張卡片

關閉
  說「停用 ponytail-forge」或「normal mode」即可恢復一般行為。
  等級會持續生效，直到被改變或對話結束。
```

## 邊界

一次性顯示，不修改任何程式碼、不寫入任何檔案、不改變目前的等級設定。
