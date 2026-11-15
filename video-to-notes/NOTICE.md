# 來源與修改說明

本 skill 改寫自 [wdkns/wdkns-skills](https://github.com/wdkns/wdkns-skills)（commit `496fb3f`，2026-10-22）的：

- `skills/youtube-render-pdf`（SKILL.md、assets/notes-template.tex）
- `skills/bilibili-render-pdf`（SKILL.md）

原作採 GNU GPL-3.0 授權，本 skill 為衍生作品，同樣以 GPL-3.0 授權（全文見 `LICENSE`）。若公開散佈本 skill 或其修改版，必須沿用 GPL-3.0 並保留本說明。

## 修改內容（2026-11-15）

| 項目 | 原本 | 本 skill |
|---|---|---|
| 結構 | YouTube、Bilibili 各一個 skill | 合併成一個，依輸入判斷來源 |
| 本地影片 | 不支援 | 新增（`references/local-video.md`）：ffprobe 讀資訊、內嵌／外掛字幕、whisper、封面替代 |
| 語言 | 中文（範本為簡體） | 一律繁體中文、台灣用語；範本、章節名稱改為繁體 |
| 字型 | fandol（缺許多繁體字） | 自動挑選 Noto CJK TC／微軟正黑體／新細明體／宋體-繁／蘋方-繁 |
| 時間戳 | 只有截圖頁尾註腳 | 新增 `\ts`、`\tsrange`；小節、重點、截圖、對話都標時間；線上影片可點擊跳轉 |
| 補漏 | README 建議另外追問 | 寫進流程：獨立審查 agent 對照字幕，只回報不修改，最多 5 輪 |
| 輸出 | `.tex`＋PDF | 另外寫進 Notion「影片筆記」資料庫（原生頁面＋附 PDF） |
| 環境檢查 | 無 | 新增 `scripts/check_env.py`、`references/setup.md` |
| 平台 | Codex（`agents/openai.yaml`） | Claude Code／Cowork；未附 openai.yaml |
