# 寫進 Notion

## 目的地

- 資料庫：Notion 工作區裡名為「影片筆記」的資料庫。

用 Notion connector 的 search 找「影片筆記」，再 fetch 它的 data source（`collection://…`）確認欄位名稱。找到多個同名的，問使用者用哪一個。找不到（被刪掉、換了工作區）時，問使用者要照下面的欄位重建資料庫，還是改放別的地方，不要自己亂建。

## 欄位

| 欄位 | 類型 | 填什麼 |
|---|---|---|
| 標題 | title | 影片的繁中標題（原標題是外文時：繁中翻譯，後面括號附原文） |
| 來源 | select | `YouTube`／`Bilibili`／`本地影片` |
| 網址 | url | 線上影片網址；本地影片留空 |
| 本地檔名 | text | 本地影片的檔名；線上影片留空 |
| 講者或頻道 | text | 頻道或講者 |
| 影片長度 | text | `h:mm:ss` 或 `mm:ss` |
| 發布日期 | date | `date:發布日期:start` 填 `YYYY-MM-DD`；不知道就不填 |
| 標籤 | multi_select | 2 到 5 個主題標籤（例如 `LLM`、`作業系統`、`投資`），優先沿用資料庫已有的標籤 |
| PDF | files | 上傳後 PDF 的 `file_upload_id`（JSON 陣列）；欄位填不進去就只放在頁面最後 |

**新標籤要先加進資料庫**：標籤欄只接受已存在的選項，直接填新的會報錯（`Invalid multi_select value`）。先 fetch data source 看現有選項；要用新標籤時，先用 update-data-source 把新選項加進「標籤」欄，再建頁面。
| 建立日期 | created_time | 自動，不用填 |

## 頁面內容（Notion-flavored Markdown）

寫之前讀一次 Notion connector 的 Markdown 規格（fetch `notion://docs/notion-flavored-markdown-spec`），不要自己發明語法。內容就是 `.tex` 筆記的 Notion 版本，**不要只放摘要**：

- 頁首：一個 `<callout icon="🎬" color="gray_bg">`，寫來源、講者、長度、影片連結；接著放封面圖；再放 `<table-of-contents />`。
- `\section` → `## 標題`，`\subsection` → `### 標題`；小節標題下第一行放時間區間。
- 段落照抄筆記內容（繁中），LaTeX 指令要轉掉：`\textbf{x}` → `**x**`、`\emph{x}` → `*x*`、行內公式 `$...$` 保留。
- 顯示公式：`$$` 自己一行、公式一行、`$$` 自己一行（不要寫在同一行）。符號說明照樣用清單。
- 程式碼：用 code fence 並標語言；caption 寫在 code block 前一行粗體。
- 重點框轉 callout：
  - importantbox → `<callout icon="💡" color="yellow_bg">`
  - knowledgebox → `<callout icon="📘" color="blue_bg">`
  - warningbox → `<callout icon="⚠️" color="red_bg">`
  - dialoguebox → `<callout icon="💬" color="gray_bg">`
  框的標題放在 callout 第一行加粗。
- 表格用 pipe table。
- 圖：每張圖自己一個區塊，圖說放在 image 的 caption，caption 結尾附時間戳。
- 最後一節「總結與延伸」之後，加一段 `---`，再放 PDF 區塊。

### 時間戳

- 線上影片：`[▶ 12:31](https://youtu.be/<ID>?t=751)`，Bilibili 用 `https://www.bilibili.com/video/<BV號>?t=751`（分P加 `p=N&t=751`）。時間區間寫 `[▶ 12:31–15:02](…?t=751)`，連到起點。
- 本地影片：`⏱ 12:31`、`⏱ 12:31–15:02`，不做連結。
- 位置和 `.tex` 一樣：小節開頭、關鍵論點後、圖說、對話框標題。

## 上傳圖片和 PDF

Notion 的圖片和 PDF 要先上傳到 Notion，不能用本地路徑：

1. 對每個檔案呼叫 Notion connector 的 **create-file-upload**（`filename` 例如 `fig_attention.png`、`筆記.pdf`），拿到 `upload_url`、`upload_headers`、`markdown_source`。
2. 用 curl 送出（一個網址只送一次，把 `upload_headers` 每一項都帶上）：
   ```
   curl -sS -X POST "<upload_url>" -H "<header 名稱>: <值>" -F "file=@<本地檔案路徑>"
   ```
   Windows 的 PowerShell 請用 `curl.exe`（不是 `curl` 別名）。
3. 在頁面內容裡用回傳的 `markdown_source`：圖片寫 `<image source="<markdown_source>">圖說</image>`，PDF 寫 `<pdf source="<markdown_source>">PDF 講義</pdf>`。
4. 上傳後沒放進頁面的檔案過一段時間會被刪，所以上傳完就盡快建頁面。

限制與對策：

- 單檔上限 20 MiB。PDF 太大時，先把筆記裡的截圖壓小（`magick in.png -resize 1600x\> -quality 85 out.jpg`）重新編譯；仍然太大，就在頁面寫明 PDF 的本地路徑，不附檔，並告訴使用者。
- 截圖很多時，可以只上傳筆記實際用到的圖，不要上傳候選畫面。

## 建立頁面

- 用 create-pages，parent 用上面的 data source，`properties` 填欄位，`content` 放頁面內容。
- 內容太長、一次送不完時：先建頁面放前幾節，再用 update-page 把後面的章節依序附加上去。
- 建好後 fetch 一次，確認沒有 `truncated` 或缺漏的區塊，圖片和 PDF 都有出現。
- 交付時給使用者這頁的連結。
