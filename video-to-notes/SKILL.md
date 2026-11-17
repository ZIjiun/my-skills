---
name: video-to-notes
description: 把 YouTube、Bilibili 或電腦上的影片檔整理成繁體中文（台灣用語）的圖文講義：附關鍵截圖、公式、程式碼、可點擊的時間戳和總結，寫進 Notion「影片筆記」資料庫；開始前會先問要不要另外做 PDF 講義（.tex 編譯）。完成初稿後會開獨立審查 agent 對照原始字幕補漏。使用者貼上 YouTube／Bilibili 網址或影片檔路徑，說「整理成筆記」「做成講義」「影片轉 PDF」「存到 Notion」時使用。
---

# 影片轉筆記（video-to-notes）

把一部影片做成**一頁完整的 Notion 筆記**。使用者要的話，另外做**可編譯的繁中 `.tex` 講義和 PDF**（見「開始前：問要不要 PDF」）。

改寫自 [wdkns/wdkns-skills](https://github.com/wdkns/wdkns-skills) 的 `youtube-render-pdf` 和 `bilibili-render-pdf`（GPL-3.0），差異見 `NOTICE.md`。

## 一定要做到

- 內容來自影片真正的教學內容，不是字幕逐字稿。
- **一律寫繁體中文、台灣用語**，不管影片是簡中、英文或其他語言（見「繁中寫作」）。
- 每個小節、重要截圖、對話片段都附**時間戳**；線上影片的時間戳可以點擊跳到該時間點（見「時間戳」）。
- 封面用影片原始封面；放進所有必要的高價值截圖，不放重複畫面。
- 結尾有總結章節：講者實質的結語＋你的整理。
- 初稿完成後跑**審查迴圈**（見第 6 步），補完漏掉的內容才定稿。
- 交付 Notion 頁面連結；要 PDF 時另外交付 `.tex` 和 `.pdf`。

## 開始前：問要不要 PDF

拿到影片後、開始做之前，先問使用者一句：**這次要不要另外做 PDF 講義？**（有提問工具就用選擇題：要／不要。）

- **不要**：只做 Notion 頁面。初稿寫成 `筆記.md`（Notion 格式的 Markdown），不寫 `.tex`、不跑 xelatex、不檢查 LaTeX 相關工具，Notion 頁面不附 PDF、不填 PDF 欄位。
- **要**：照完整流程，初稿寫成 `.tex`，第 7 步編譯成 PDF，第 8 步把 PDF 附進 Notion 並填 PDF 欄位。
- 使用者在要求裡已經說了要或不要（例如「做成 PDF 講義」「只要 Notion」），就照他說的，不再問。
- 沒人能回答時（排程執行、使用者不在）：當作不要，並在交付時註明「這次沒做 PDF，要的話說一聲」。

下面寫「只在要 PDF 時」的步驟，不要 PDF 就跳過。

## 第 0 步：檢查工具

先執行 `python scripts/check_env.py`（macOS 用 `python3`）。它會列出 yt-dlp、ffmpeg、ffprobe、magick、語音轉文字工具（sherpa-onnx）是否可用。要 PDF 時加 `--pdf`，才會一併檢查 xelatex、中文 LaTeX 套件（ctex、xeCJK）和繁中字型。

- **在雲端環境缺工具：自己裝，不用問。**雲端的工作環境每個對話都是新的，上次裝的都不在，這是正常的。直接補齊：`pip install yt-dlp sherpa-onnx soundfile numpy opencc`（pip 要加 `--break-system-packages`）、需要的語音模型（網址在 `scripts/transcribe.py` 開頭）；要 PDF 時，缺 ctex／xeCJK 就照 `references/setup.md`「中文 LaTeX 套件」的原始碼建置。
- **在使用者自己的電腦缺工具**（Claude Code，或下面第 2 步請使用者下載時）：照 `references/setup.md` 告訴使用者怎麼裝（Windows 用 winget，沒有 winget 時改下載單一執行檔；macOS 用 Homebrew），不要自己替使用者安裝系統軟體。
- 語音轉文字的套件和模型只有沒字幕的影片才需要（見「語音轉文字」），有字幕時不用準備。
- 只在要 PDF 時：缺 xelatex 仍可做 Notion 頁面，但要明講這次沒有 PDF。xelatex 在但缺 ctex／xeCJK：照 `references/setup.md`「中文 LaTeX 套件」補裝，否則第 7 步一定失敗。

**這個 skill 可能跑在哪裡**：Claude 桌面版／App 的對話，指令其實在雲端環境執行，常常連不到 Bilibili、YouTube 和 Hugging Face；使用者的電腦另外透過連結的資料夾存取。Claude Code 則直接在使用者電腦上執行。第 2 步的下載方式依這點決定。

工作資料夾：在目前工作目錄下建 `video-notes/<影片標題的安全檔名>/`，所有中間檔（metadata、封面、字幕、影片、截圖）都放這裡。

## 第 1 步：判斷來源

| 輸入 | 來源 | 細節 |
|---|---|---|
| `youtube.com/watch?v=`、`youtu.be/`、`youtube.com/live/` | YouTube | 本檔「線上影片」 |
| `bilibili.com/video/BV…`、`b23.tv/…` | Bilibili | 本檔「線上影片」＋「Bilibili 注意事項」 |
| 電腦上的路徑（`.mp4 .mkv .mov .webm .avi .m4v` 等） | 本地影片 | `references/local-video.md` |

Windows 路徑含空白或中文時，命令列一律加引號。

## 第 2 步：取得素材

### 線上影片

1. 先看 metadata：`yt-dlp -J "<URL>" > meta.json`。記下標題、頻道、上傳日期、長度、章節、縮圖、可用字幕。
2. **封面**：從 metadata 取最高解析度的縮圖存到本地（`yt-dlp --write-thumbnail --skip-download --convert-thumbnails jpg`），封面頁引用這個檔。有官方封面時不要用隨便一張畫面代替。
3. **字幕**（保留時間戳，先別壓成純文字）：
   - 人工字幕優先於自動字幕。
   - 語言優先順序：影片原本的語言 → `zh-Hant`／`zh-TW` → `zh-Hans`／`zh` → 英文。
   - `yt-dlp --write-subs --write-auto-subs --sub-langs "<語言>" --convert-subs srt --skip-download -o "subs" "<URL>"`
   - 都沒有字幕：抽音訊後語音轉文字（見下方「語音轉文字」）。
4. **影片**：探測格式，下載實際能下載的最高解析度，用來截圖：`yt-dlp -F "<URL>"` 後 `yt-dlp -f "bv*+ba/b" -o "video.%(ext)s" "<URL>"`。

### 下載不到時（依序試）

雲端環境常被擋（錯誤像 `Tunnel connection failed: 403`、`Unable to connect to proxy`）。被擋不是暫時的，換指令重試沒有用，直接往下一層：

1. **在這裡直接下載**（上面的指令）。
2. **在使用者電腦上下載，我自己執行**：有能在使用者電腦執行指令的工具（例如 `device_bash`）時，先請使用者連結一個資料夾，在那裡執行下面第 3 層的指令，再把檔案帶進工作資料夾。
3. **請使用者自己下載**：上面兩層都不行時，給他可以直接貼上的指令，下載完請他在桌面版按「Add folder」連結資料夾，再讀進來。
   - 沒有 yt-dlp 時，Windows 可以不安裝，直接下載單一執行檔到該資料夾：`curl.exe -L -o yt-dlp.exe https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe`，之後指令開頭寫 `.\yt-dlp.exe`（PowerShell 執行目前資料夾的程式一定要加 `.\`）。沒有 winget 的電腦也適用。
   - **給使用者的每一段指令，第一行固定放更新**：`.\yt-dlp.exe -U`（用 winget 或 Homebrew 裝的寫 `yt-dlp -U`）。Bilibili、YouTube 常改版，舊版容易下載失敗；放在第一行，使用者整段貼上就會先更新，不用記。
   - 先跑 `-F` 列格式，再**影像、聲音分開下載**，使用者電腦就不需要 ffmpeg，合併在這裡做：
     ```
     .\yt-dlp.exe -U
     .\yt-dlp.exe -F "<URL>"
     ```
     看完格式後：
     ```
     .\yt-dlp.exe -U
     .\yt-dlp.exe -f "<影像格式ID>,<聲音格式ID>" --write-info-json --write-thumbnail --write-subs --write-auto-subs --sub-langs "<語言>" -o "video.f%(format_id)s.%(ext)s" "<URL>"
     ```
     讀進來後合併：`ffmpeg -i video.f<影像>.mp4 -i video.f<聲音>.m4a -c copy video.mp4`。
   - 下載中斷（`Connection reset`）yt-dlp 會自己續傳；聲音檔出現 `HTTP Error 567` 多半是連結過期，單獨重抓聲音即可。
   - 單一檔案超過約 400MB 帶不進來時，改抓 720P。

### Bilibili 注意事項

- 畫質：不登入通常也拿得到一般 1080P，要登入的是「1080P 高碼率」（大會員）和字幕。先看 `-F` 的結果再決定。只拿到 480P／720P、或需要字幕時，請使用者自己決定要不要加 `--cookies-from-browser chrome`（會讀瀏覽器登入資料，**一定先問**；要先完全關掉 Chrome，讀不到時改用 Firefox）。
- **分P 影片**：先列出所有分P，問使用者要做哪幾P；網址加 `?p=N` 指定。
- 字幕：先試 CC 字幕（`zh-Hans,zh-CN,zh,ai-zh`，沒登入通常拿不到），沒有就語音轉文字，再不行就只靠畫面。
- 彈幕不當作教學內容來源。
- 「一鍵三連」「投幣關注」這類頻道宣傳不寫進筆記。

### 語音轉文字（沒有字幕時）

先抽音訊：`ffmpeg -i "<影片或音訊>" -vn -ac 1 -ar 16000 audio.wav`。用 `scripts/transcribe.py`，依影片語言選引擎：

| 影片語言 | 第一選擇 | 備案 |
|---|---|---|
| 中文、粵語、日文、韓文 | SenseVoice | whisper |
| 英文 | SenseVoice | whisper（腔調重、術語多、SenseVoice 轉出來錯很多時） |
| 其他語言（法文、西班牙文等） | whisper | 沒有（SenseVoice 不支援） |

```
python scripts/transcribe.py audio.wav <模型資料夾> subs.srt --engine sensevoice --lang auto
python scripts/transcribe.py audio.wav <模型資料夾> subs.srt --engine whisper --lang auto
```

- 兩種引擎都透過 sherpa-onnx 執行，模型都放在 GitHub（網址在腳本開頭）。OpenAI 官方和 Hugging Face 的模型網址在雲端環境連不到，所以不用 `pip install openai-whisper` 那一套。
- **SenseVoice**：很快，一般電腦或雲端都是幾分鐘的影片幾秒到幾十秒轉完，會自動加標點。模型約 1GB。
- **whisper**（large-v3-turbo，約 560MB）：自動判斷語言，支援的語言最多，但慢很多。實測雲端 2 核心時，處理時間約是音訊長度的 2 倍（33 秒的英文花 63 秒；SenseVoice 花 5 秒），超過 20 分鐘的影片先告訴使用者大約要多久。
- 時間戳以語音段落為單位（每段最長約 12 秒），找截圖和標時間戳夠用。
- 使用者自己的電腦已經裝好 openai-whisper、又有 NVIDIA 顯示卡時（Claude Code），也可以直接用它：`whisper audio.wav --model medium --output_format srt --output_dir .`。

**兩個都要注意**：

- 輸出多半是簡體，而且會聽錯人名、英文縮寫和術語（例如 SCR 聽成「SC2」、deck 聽成「dck」）。寫筆記時對照畫面上的文字和燒進影片的字幕校正，講者名字以畫面或頻道資訊為準。
- 音質太差、轉出來不能用：改用「只看畫面」模式，從第 4 步的總覽圖整理。

## 第 3 步：長影片分段

影片超過 20 分鐘或字幕超過 300 條時，不要一次處理：

- 優先按章節（或分P）切；沒有章節就按連貫的時間區間切，相鄰段落留一點重疊。
- 有 subagent 時，平行派給多個 subagent，每個負責一段，回傳：這段的教學目標、核心論點、重要公式或程式碼、需要的截圖與**時間區間**、需要整合時決定的疑點。
- 主流程把各段整合成**一份**大綱和一條連貫的敘事，讀起來像一份講義，不是拼起來的摘要。

## 第 4 步：截圖

依教學價值挑圖，不設張數上限，也不要為了版面精簡而省圖。分兩段做：先用小圖找畫面，再用原解析度出圖。

**第一段：找畫面**

```
python scripts/scan_frames.py video.mp4 frames_scan
```

它會產生 `frames_scan/sheet_XX.jpg`（6x6 總覽圖，每格印時間）和 `segments.txt`（畫面段落清單）：

- **逐幀場景偵測**：每一格都比對，停留不到 1 秒的畫面（只閃幾格的提示詞、標題卡）會把那幾格全部抽出來。門檻預設 `0.02`，適合投影片捲動、螢幕錄影；常用的 0.3 在這類影片幾乎抓不到變化。剪接明顯的影片可以用 `--threshold 0.1` 以上減少雜訊。
- **每秒一格保底**：抓慢慢捲動、逐字打出這類變化太小、偵測不到的畫面。
- **去重複**：只拿掉和前一張幾乎一模一樣的保底格，多一行字就會保留；短暫畫面的格一律不去除。
- 4 分半的影片約 2 分鐘。超過 30 分鐘的影片，依第 3 步的分段各跑一次，或先告訴使用者大約要多久。

接著用讀圖工具**逐張看總覽圖**，決定要哪些畫面；也可以用字幕找到講某概念的時間區間，再對照那段的總覽格。**留或不留、檔名叫什麼，一定要實際看過圖片再決定**，不要用 OCR 取代，也不要只靠字幕或時間猜畫面內容。

**第二段：出圖**

- 選定的時間點回原影片抽**原解析度**的畫面：`ffmpeg -ss <秒> -i video.mp4 -frames:v 1 t_00-12-31.png`。總覽圖的小圖只用來找，不要直接放進筆記。
- 原始候選用時間命名（`t_00-12-31.png`），確認內容後才改成描述性的檔名。

**畫面被遮住時**：燒進影片的字幕、手勢游標、講者小視窗常會擋住投影片的一部分。

- 先在同一畫面停留的時間內找沒被擋的那一格（字幕換句之間、游標移開時）。
- 每一格都有東西擋住時，用不同時間點沒被擋的區塊拼成一張（`magick` 裁切後 `-append`）。只能拼**同一個畫面**的不同時間點，不能改動內容；圖說或註腳寫明「由某幾個時間點的畫面拼合，用來避開遮擋」。
- 只需要畫面一部分（例如投影片標題）時，直接裁切，避開遮擋的區域。

**每張圖放進去前檢查**：

- 相關：直接支援旁邊段落講的那個概念。
- 完整：文中提到的元素都已出現；投影片逐步出現、動畫、白板時，取**最後完整**的那一格。
- 最佳：比較附近幾格，選最完整又最清楚的。
- 清楚：字、公式、標籤看得清楚；太鬆就裁切放大。
- 畫面難懂時，可以重畫示意圖，但不加裝飾性圖片。不做 PDF 時用 matplotlib 輸出 PNG（Notion 用）；要 PDF 時可以用 TikZ／PGFPlots 或 matplotlib 輸出 PDF 向量圖，另外存一張 PNG 給 Notion。

## 第 5 步：寫初稿

依「開始前」的回答選格式：

- **不要 PDF**：寫成工作資料夾裡的 `筆記.md`，直接用 `references/notion-output.md` 的 Notion 格式（標題、callout、圖片、時間戳連結）。圖片先寫本地路徑（`<image source="figs/xxx.png">圖說</image>`），第 8 步上傳後再換成 Notion 的來源。
- **要 PDF**：從 `assets/notes-template.tex` 開始，填好封面資訊（`\videosource`、`\videochannel`、`\videourl` 或 `\videofile`、`\videocoverpath`、`\videotimeprefix`），把正文區塊換成筆記。

下面的寫法規則兩種格式都適用。規則裡用 LaTeX 的名稱寫，寫 `筆記.md` 時照 `references/notion-output.md` 的對應：`\section`／`\subsection` → `##`／`###`，`importantbox` 等重點框 → 對應顏色的 callout，`\ts`／`\tsrange` → 時間戳連結，截圖時間寫在圖說結尾。

### 教學寫法

- 每個主要章節依序交代：要解決什麼問題 → 為什麼簡單的看法不夠 → 核心概念 → 怎麼運作 → 例子或證據 → 讀者該帶走什麼。
- 重建教學順序，不要照字幕順序逐段搬。先講直覺，再上形式化。密的段落拆成多個小節逐步建立。
- 不要濫用「不是……而是……」句型。不寫空泛抽象的句子，盡量落在具體機制、例子、變數、步驟、時間點或講者給的證據。
- 用 `\section{}`、`\subsection{}` 組織。每個主要章節最後放 `\subsection{本章小結}`；有一兩個值得看的外部連結時加 `\subsection{延伸閱讀}`。
- 公式：先用白話說明它在表達什麼、為什麼出現 → 用 `$$...$$` 顯示 → 緊接著用清單解釋每個符號。
- 程式碼：先說明用途，放在有 `caption` 的 `lstlisting`，需要時再說明預期行為。
- 重點框（每個框都要有具體內容，不是裝飾；一節可以有好幾個）：
  - `importantbox`：一定要記得的核心概念、定義、關鍵步驟、密集段落後的精簡重述。
  - `knowledgebox`：背景知識、前置概念、歷史脈絡、工程取捨、類比。
  - `warningbox`：常見誤解、隱藏假設、容易犯的錯。
  - `dialoguebox`：只用在訪談、對談類影片，保留短而高資訊量、有趣或特別直覺的原始對話，附講者和時間戳，框後用一段文字說明它為什麼重要。不放寒暄或長段逐字稿。
  - 圖片不要放進任何框裡。
- 略過：打招呼、閒聊、業配、頻道宣傳、結尾客套話。保留講者有實質內容的結語（限制、未來方向、取捨、建議、開放問題）。
- 最後一節 `\section{總結與延伸}`：講者的實質結語、你對核心論點與機制的結構化整理、跨章節的連結、具體的收穫、開放問題或下一步。
- 不要留下 `[cite]` 之類的佔位符。

### 繁中寫作

- 全文繁體中文、台灣用語。影片是簡中時，**不是只轉字形**，用語也要換：影片（视频）、程式（程序）、資料（数据）、網路（网络）、軟體（软件）、硬體（硬件）、演算法（算法）、記憶體（内存）、品質（质量）、預設（默认）、訊息（信息）、伺服器（服务器）、介面（接口／界面）、物件（对象）、變數（变量）、函式（函数）、模型訓練、最佳化（优化）。
- 英文術語第一次出現時寫「中文（English）」，之後用最常見的說法；沒有通行中譯的保留英文。
- `dialoguebox` 引用原話時：中文原話轉成繁體字、保留原本說法；外語原話翻成繁中，必要時附短原文。
- 有 OpenCC（`pip install opencc`）時，可以用 s2twp 掃一遍**正文文字**找漏網的簡體字，但只拿來檢查，別整份檔案自動轉換（會動到程式碼和網址）。

### 時間戳

- 時間格式：一小時內寫 `mm:ss`，超過寫 `h:mm:ss`。
- `\videotimeprefix`（網址前綴，後面直接接秒數）：
  - YouTube：`https://youtu.be/<影片ID>?t=`
  - Bilibili：`https://www.bilibili.com/video/<BV號>?t=`；分P寫 `https://www.bilibili.com/video/<BV號>?p=<N>\&t=`
  - 本地影片：留空，時間戳只顯示文字。
- 用法：
  - 每個 `\subsection` 標題後第一行：`\tsrange{起始秒數}{起始}{結束}`。
  - 關鍵論點、公式、例子後：`\ts{秒數}{mm:ss}`，挑真正有用的地方放，別每句都放。
  - 截圖：時間來自定位該圖用的字幕區間，不是整章的粗估。`.tex` 寫在頁尾註腳 `\footnotetext{影片畫面時間區間：\tsrange{…}{…}{…}。}`，圖和註腳要在同一頁（用 `[H]`）；`筆記.md` 寫在圖說結尾。
  - `dialoguebox` 標題附 `\tsrange`。
- `筆記.md` 的時間戳格式見 `references/notion-output.md`「時間戳」。
- 時間戳必須對得上字幕或畫面，不確定就回字幕查，不要估。

## 第 6 步：審查迴圈（補漏）

AI 整理常見的問題是漏掉內容。初稿（`筆記.md` 或 `.tex`）寫完、**定稿之前**：

1. 開一個**獨立的審查 agent**（Claude Code／Cowork 用 Agent／Task 工具；它看不到你的對話，所以要把檔案路徑寫清楚）。給它的指示：

   > 你是審查者。讀原始字幕 `<字幕檔路徑>`、畫面總覽圖 `<frames_scan/sheet_*.jpg>`（用讀圖工具實際看）、畫面段落清單 `<frames_scan/segments.txt>`，以及筆記 `<初稿路徑>`。字幕是語音辨識產生時，會有聽錯的人名、英文縮寫和術語，以畫面上的文字為準。逐段比對，找出：(1) 筆記漏掉的資訊：重要論點、具體細節（數字、條件、步驟、例子、反例）、有趣或有啟發的說法、講者特別強調的地方；(2) 只出現在畫面上、有教學價值但筆記沒寫的內容，以及有沒有哪個畫面段落被跳過；(3) 時間戳和字幕差超過約 3 秒的地方；(4) 筆記說了但影片沒講、又沒標明是補充的內容。**只回報，不要修改任何檔案。**每一項寫：字幕或畫面的時間區間、漏了或錯了什麼、建議放在筆記哪一節、重要程度（高／中／低）。如果你認為筆記已經完整，只回覆「已完備」並說明理由。

2. 主流程依回報補進初稿（照樣遵守寫作和時間戳規則）。判斷某項不該加（例如閒聊、重複）可以不加，但要記下理由。
3. 把補好的版本再交給審查 agent（同一個 agent 繼續，或開新的並附上前幾輪紀錄），重複直到它回「已完備」。
4. 最多跑 **5 輪**。5 輪後仍有回報，就停下，在交付時列出還沒處理的項目讓使用者決定。
5. 長影片可以每段各派一個審查 agent，最後再整體審一次。
6. 沒有 subagent 工具的環境（例如 claude.ai）：自己另做一輪「只對照字幕找漏」的檢查，照上面的格式列清單再補，並告訴使用者這次不是獨立 agent 審查。

## 第 7 步：編譯 PDF（只在要 PDF 時）

```
xelatex -interaction=nonstopmode "<檔名>.tex"
xelatex -interaction=nonstopmode "<檔名>.tex"
```

- 跑兩次讓目錄和連結正確。有錯就看 `.log` 修正後重跑，直到沒有錯誤。
- 檢查 log 有沒有 `Missing character`（缺字）：有就表示字型找不到某些繁體字，換字型或改字。
- 檔名用有意義的繁中名稱：`<影片中文標題>_筆記.tex`、`<影片中文標題>_筆記.pdf`（去掉 `\/:*?"<>|`）。
- 編譯後實際看幾頁 PDF（轉成圖片檢查），確認封面、截圖、公式、時間戳連結正常。

## 第 8 步：寫進 Notion

照 `references/notion-output.md`：在「影片筆記」資料庫建一頁，內容是筆記的 Notion 原生版本（標題、段落、公式、截圖、重點框、時間戳連結），並填好欄位。

- 不要 PDF：頁面內容就是審查過的 `筆記.md`，把圖片來源換成上傳後的來源。
- 要 PDF：把 `.tex` 的內容轉成 Notion 格式，最後附上 PDF，並填 PDF 欄位。

Notion connector 沒接或寫入失敗時：把 `筆記.md`（要 PDF 時是 PDF）和圖檔照樣交付，告訴使用者 Notion 這步沒完成和原因。

## 最後檢查

- 沒有漏掉重要內容或關鍵細節（審查迴圈已完成，或已列出未處理項目）。
- 每張圖都支援旁邊的說明，是最完整清楚的那一格，需要裁切的已裁切。
- 圖夠多：還有沒有該加的截圖或重畫圖。
- 全文繁中、台灣用語，沒有殘留簡體字。
- 時間戳格式一致、對得上、線上影片的連結能跳到正確時間。
- Notion 頁面內容完整。要 PDF 時：PDF 編譯成功，也已附進 Notion。

## 交付

用一段話告訴使用者：

- Notion 頁面連結。
- 工作資料夾的位置（`筆記.md`、封面和所有圖檔）；要 PDF 時加上 PDF 和 `.tex` 的路徑。沒做 PDF 是因為沒人回答時，提一句「要的話說一聲」。
- 審查迴圈跑了幾輪、補了哪些重點；還有未處理項目就列出來。
- 這次用了哪種語音轉文字（或用字幕）、在哪裡下載的，以及有沒有哪步沒做成（例如 Bilibili 只拿到低畫質）。

## 檔案

- `assets/notes-template.tex`：繁中 LaTeX 範本（字型自動挑選、`\ts`／`\tsrange` 時間戳），只在要 PDF 時用
- `references/local-video.md`：本地影片的 metadata、字幕、封面處理
- `references/notion-output.md`：Notion 頁面格式、上傳圖片和 PDF、欄位對應
- `references/setup.md`：Windows／macOS 工具安裝步驟
- `scripts/check_env.py`：檢查工具；加 `--pdf` 時也檢查 xelatex、中文 LaTeX 套件與字型
- `scripts/scan_frames.py`：截圖第一段，逐幀場景偵測＋每秒保底＋去重複，產生總覽圖
- `scripts/transcribe.py`：用 SenseVoice 或 whisper（sherpa-onnx）把音訊轉成 SRT
