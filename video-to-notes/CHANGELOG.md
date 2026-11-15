# 更新紀錄

## 2026-11-15

- 第一版。把 YouTube、Bilibili、本地影片整理成繁體中文（台灣用語）講義：附截圖、公式、程式碼、總結，編譯成 PDF，並寫進 Notion「影片筆記」資料庫（原生頁面＋附 PDF）。
- 小節、重點、截圖、對話都標時間戳；線上影片可點擊跳到該時間點（`\ts`、`\tsrange`）。
- 初稿完成後由獨立審查 agent 對照原始字幕找漏，只回報不修改，最多 5 輪。
- 改寫自 wdkns/wdkns-skills 的 youtube-render-pdf 與 bilibili-render-pdf（GPL-3.0），本 skill 同樣以 GPL-3.0 授權；修改內容見 `NOTICE.md`。
- 範本改用繁中字型自動挑選（Noto CJK TC／微軟正黑體／新細明體／宋體-繁／蘋方-繁），原本的 fandol 缺許多繁體字。

## 2026-11-15（同日修正）

- Notion 資料庫改成用名稱「影片筆記」搜尋，不再寫死資料庫 ID，因為這個 repo 是公開的。
