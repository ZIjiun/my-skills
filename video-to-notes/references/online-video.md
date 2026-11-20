# 線上影片（YouTube、Bilibili）

輸入是 YouTube 或 Bilibili 網址時，第 2 步照這份取得素材。其他步驟見 SKILL.md。

## 下載素材

1. 先看 metadata：`yt-dlp -J "<URL>" > meta.json`。記下標題、頻道、上傳日期、長度、章節、縮圖、可用字幕。
2. **封面**：從 metadata 取最高解析度的縮圖存到本地（`yt-dlp --write-thumbnail --skip-download --convert-thumbnails jpg`），封面頁引用這個檔。有官方封面時不要用隨便一張畫面代替。
3. **字幕**（保留時間戳，先別壓成純文字）：
   - 人工字幕優先於自動字幕。
   - 語言優先順序：影片原本的語言 → `zh-Hant`／`zh-TW` → `zh-Hans`／`zh` → 英文。
   - `yt-dlp --write-subs --write-auto-subs --sub-langs "<語言>" --convert-subs srt --skip-download -o "subs" "<URL>"`
   - 都沒有字幕：抽音訊後語音轉文字（見 `references/transcribe.md`）。
4. **影片**：探測格式，下載實際能下載的最高解析度，用來截圖：`yt-dlp -F "<URL>"` 後 `yt-dlp -f "bv*+ba/b" -o "video.%(ext)s" "<URL>"`。

## 下載不到時（依序試）

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

## Bilibili 注意事項

- 畫質：不登入通常也拿得到一般 1080P，要登入的是「1080P 高碼率」（大會員）和字幕。先看 `-F` 的結果再決定。只拿到 480P／720P、或需要字幕時，請使用者自己決定要不要加 `--cookies-from-browser chrome`（會讀瀏覽器登入資料，**一定先問**；要先完全關掉 Chrome，讀不到時改用 Firefox）。
- **分P 影片**：先列出所有分P，問使用者要做哪幾P；網址加 `?p=N` 指定。
- 字幕：先試 CC 字幕（`zh-Hans,zh-CN,zh,ai-zh`，沒登入通常拿不到），沒有就語音轉文字，再不行就只靠畫面。
- 彈幕不當作教學內容來源。
- 「一鍵三連」「投幣關注」這類頻道宣傳不寫進筆記。
