# 編譯 PDF（只在要 PDF 時）

第 7 步。

```
xelatex -interaction=nonstopmode "<檔名>.tex"
xelatex -interaction=nonstopmode "<檔名>.tex"
```

- 跑兩次讓目錄和連結正確。有錯就看 `.log` 修正後重跑，直到沒有錯誤。
- 檢查 log 有沒有 `Missing character`（缺字）：有就表示字型找不到某些繁體字，換字型或改字。
- 檔名用有意義的繁中名稱：`<影片中文標題>_筆記.tex`、`<影片中文標題>_筆記.pdf`（去掉 `\/:*?"<>|`）。
- 編譯後實際看幾頁 PDF（轉成圖片檢查），確認封面、截圖、公式、時間戳連結正常。
