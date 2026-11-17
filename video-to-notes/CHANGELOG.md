# 更新紀錄

## 2026-11-15

- 第一版。把 YouTube、Bilibili、本地影片整理成繁體中文（台灣用語）講義：附截圖、公式、程式碼、總結，編譯成 PDF，並寫進 Notion「影片筆記」資料庫（原生頁面＋附 PDF）。
- 小節、重點、截圖、對話都標時間戳；線上影片可點擊跳到該時間點（`\ts`、`\tsrange`）。
- 初稿完成後由獨立審查 agent 對照原始字幕找漏，只回報不修改，最多 5 輪。
- 改寫自 wdkns/wdkns-skills 的 youtube-render-pdf 與 bilibili-render-pdf（GPL-3.0），本 skill 同樣以 GPL-3.0 授權；修改內容見 `NOTICE.md`。
- 範本改用繁中字型自動挑選（Noto CJK TC／微軟正黑體／新細明體／宋體-繁／蘋方-繁），原本的 fandol 缺許多繁體字。

## 2026-11-15（同日修正）

- Notion 資料庫改成用名稱「影片筆記」搜尋，不再寫死資料庫 ID，因為這個 repo 是公開的。

## 2026-11-15（第二版）

實際用它整理一部 Bilibili 影片（BV1KUTK6JEod，4 分半，無字幕）時碰到的問題：

- **雲端環境下載不到影片**：Claude 桌面版／App 的指令在雲端執行，連 Bilibili 被擋。第 2 步新增「下載不到時」三層做法：先在這裡下載 → 有能在使用者電腦執行指令的工具就自己在那裡下載 → 給使用者可直接貼上的指令，影像和聲音分開抓，使用者電腦不需要 ffmpeg。
- **使用者電腦沒有 winget**：setup.md 新增不安裝、直接下載 yt-dlp.exe 單一執行檔的方式（指令要加 `.\`）。
- **Bilibili 畫質說明錯誤**：原本寫 1080P 要登入，實際上不登入也拿得到一般 1080P，要登入的是「高碼率」和字幕。
- **沒有 whisper、也連不到 Hugging Face**：新增 `scripts/transcribe_sensevoice.py`。語音轉文字改成依語言選：中日韓粵先用 SenseVoice（模型在 GitHub、一般電腦也快），其他語言用 whisper。並提醒語音辨識常聽錯人名和英文縮寫（這次講者「迪迪」被聽成「李迪」）。
- **短暫畫面會漏、截圖被遮住**：第 4 步改成兩段式。新增 `scripts/scan_frames.py`：逐幀場景偵測（門檻 0.02，常用的 0.3 在捲動式畫面幾乎沒反應）＋每秒一格保底＋嚴格去重複，產生總覽圖；選定後回原影片用原解析度出圖。新增被字幕、游標遮住時，用同一畫面不同時間點拼合的做法。這次新腳本抓到了舊方法漏掉、只出現 2 格的開頭標題卡。
- **審查漏看畫面**：審查 agent 也拿到總覽圖和畫面段落清單，並列出四類要檢查的問題（漏寫、只在畫面上的內容、時間戳偏差、沒標明的補充）。這次審查就是靠畫面發現講者名字寫錯。
- **xelatex 在、但缺中文套件**：check_env.py 原本只檢查 xelatex，編譯時才發現缺 ctex。現在會檢查 ctex、xeCJK、zhnumber，也檢查 sherpa-onnx；setup.md 新增補裝方法（含在 Ubuntu TeX Live 2023 上實測過的原始碼建置步驟；ctex-kit 最新版需要 2026 年以後的 LaTeX，所以固定在 2022 年的版本）。
- **Notion 的 PDF 欄位填不進去**：同一次上傳不能同時用在頁面內容和 PDF 欄位，會報 `File not found`。notion-output.md 改成上傳兩次。
- upstream-sources.json 新增 claude-video（只借想法，MIT）。

## 2026-11-15（第三版）

- **雲端缺工具時直接裝**：第 0 步原本只寫「不要替使用者安裝」，在雲端環境可能被誤解成連自己的工作環境也不能裝，而停下來問使用者。改成：雲端（每個對話都是新環境）缺的套件、模型、中文 LaTeX 套件直接補齊；「不要替使用者安裝」只適用使用者自己的電腦。
- **下載指令第一行固定 `yt-dlp -U`**：舊版 yt-dlp 常因網站改版下載失敗，使用者不用記得更新。
- **語音轉文字改成 sherpa-onnx 一套跑兩種引擎**：`scripts/transcribe_sensevoice.py` 改名 `scripts/transcribe.py`，加 `--engine whisper`。原本的 openai-whisper 要從 OpenAI 下載模型，雲端連不到，英文影片沒字幕時會卡住；改用 GitHub 上 sherpa-onnx 轉好的 whisper large-v3-turbo。
- **語言對照表修正**：原本寫 SenseVoice 不支援英文，錯了，它支援中英日韓粵。實測一段 33 秒的英文，兩者都轉對，SenseVoice 5 秒、whisper 63 秒，所以英文也改成 SenseVoice 優先，whisper 當備案；其他語言用 whisper。日文、韓文也實測過 whisper 自動判斷語言正常。

## 2026-11-17

實際用它整理 Bilibili 影片 BV13PVf6QEFN（5 分半，無字幕）後，使用者表示平常不需要 PDF：

- **PDF 改成選配，開始前先問**：新增「開始前：問要不要 PDF」。要：照原流程產出 `.tex` 和 PDF、附進 Notion、填 PDF 欄位。不要：只做 Notion 頁面。使用者已經說明就不再問；沒人能回答時（排程執行）當作不要，並在交付時註明。
- **不做 PDF 時初稿改寫成 `筆記.md`**：原本要寫 `.tex` 一次、再轉成 Notion 格式寫一次，等於整份內容寫兩遍。現在直接用 Notion 格式寫 `筆記.md`，審查 agent 對照它找漏，審完直接寫進 Notion。寫作規則不變，LaTeX 名稱對應到 notion-output.md 的格式。
- **`check_env.py` 加 `--pdf`**：預設不再檢查 xelatex、中文 LaTeX 套件和繁中字型，也不會因為沒裝 xelatex 回報「缺少必要工具」；要 PDF 時加 `--pdf` 才檢查。
- setup.md、notion-output.md、local-video.md 裡只跟 PDF 有關的步驟都標明「只在要 PDF 時」。
