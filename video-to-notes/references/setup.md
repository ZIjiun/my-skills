# 工具安裝（每台電腦各裝一次）

需要的工具：

| 工具 | 用途 | 一定要嗎 |
|---|---|---|
| yt-dlp | 下載 YouTube／Bilibili 的影片、封面、字幕 | 線上影片要 |
| ffmpeg（含 ffprobe） | 抽截圖、抽音訊、讀本地影片資訊和字幕 | 要 |
| xelatex（TeX Live 或 MiKTeX） | 編譯 PDF 講義 | 只有要 PDF 才要 |
| ImageMagick（magick） | 拼縮圖總覽、裁切、壓縮圖片 | 建議 |
| sherpa-onnx＋語音模型（SenseVoice、whisper） | 沒字幕時語音轉文字 | 沒字幕的影片才要 |
| Python 3 | 跑語音轉文字和檢查腳本 | 要 |

裝完後**重開終端機**（或重開 Claude 桌面版），再執行 `python scripts/check_env.py` 確認（會做 PDF 講義的話加 `--pdf`，一併檢查 xelatex、中文套件和字型）。

## Windows（用 winget，在 PowerShell 執行）

```powershell
winget install --id Python.Python.3.12 -e
winget install --id yt-dlp.yt-dlp -e
winget install --id Gyan.FFmpeg -e
winget install --id ImageMagick.ImageMagick -e
winget install --id MiKTeX.MiKTeX -e   # 只有要 PDF 講義才需要
```

- **TeX**（只有要 PDF 講義才需要）：MiKTeX 比較小，缺的套件會在第一次編譯時自動下載（第一次會比較久）。打開「MiKTeX Console」→ Settings，把「Install missing packages on-the-fly」設成 **Always**，不然編譯時會跳視窗卡住。想一次裝齊可改裝 TeX Live（`winget install --id TeXLive.TeXLive -e`，約 8 GB）。
- **字型**：Windows 內建「微軟正黑體」和「新細明體」，範本會自動使用，不用另外裝。想要更好看的明體可以裝 Noto Serif CJK TC（Google Fonts 下載，右鍵「為所有使用者安裝」）。
- **語音轉文字**（只有沒字幕的影片才需要）：
  ```powershell
  pip install sherpa-onnx soundfile numpy
  ```
  模型下載網址寫在 `scripts/transcribe.py` 開頭：`silero_vad.onnx` 一定要；SenseVoice（約 1GB，中日韓粵英）和 whisper turbo（約 560MB，其他語言）依需要下載。全部解壓到同一個資料夾，例如 `%USERPROFILE%\models`，只要下載一次。
- PowerShell 裡的 `curl` 是別名，上傳檔案到 Notion 時要用 `curl.exe`（Windows 10 以上內建）。

### 沒有 winget 時

有些 Windows（較舊的 Windows 10、公司管理的電腦）沒有 winget，PowerShell 會說「無法辨識 'winget'」。這時：

- **yt-dlp**：不用安裝，下載單一執行檔到要放影片的資料夾，執行時指令開頭加 `.\`：
  ```powershell
  curl.exe -L -o yt-dlp.exe https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe
  .\yt-dlp.exe --version
  ```
- **ffmpeg**：只是要下載影片的話可以不裝，影像和聲音分開抓（見 `references/online-video.md`「下載不到時」）。要在這台電腦上抽截圖才需要，到 https://www.gyan.dev/ffmpeg/builds/ 下載 release essentials 的 zip，解壓後把 `bin` 資料夾加進 PATH。
- 其他工具到各自官網下載安裝程式（Python：python.org；MiKTeX：miktex.org；ImageMagick：imagemagick.org）。

## macOS（用 Homebrew，在「終端機」執行）

沒有 Homebrew 先照 https://brew.sh 裝。

```bash
brew install python yt-dlp ffmpeg imagemagick
brew install --cask mactex-no-gui   # 只有要 PDF 講義才需要
pip3 install sherpa-onnx soundfile numpy   # 語音轉文字；模型網址見 scripts/transcribe.py
```

- MacTeX 約 5 GB，裝完要重開終端機，`xelatex` 才找得到。
- 字型：macOS 內建「宋體-繁」（Songti TC）和「蘋方-繁」（PingFang TC），範本會自動使用。

## 中文 LaTeX 套件（ctex、xeCJK）

只有要 PDF 講義時才需要。範本需要 ctex 和 xeCJK，`check_env.py --pdf` 回報缺少時：

- **MiKTeX**：第一次編譯會自動下載，不用另外處理（記得把「Install missing packages on-the-fly」設成 Always）。
- **TeX Live**：`tlmgr install ctex xecjk zhnumber`。
- **Linux 系統套件裝的 TeX Live**（例如 Ubuntu 的 `texlive-xetex`，常見於雲端環境）：`sudo apt install texlive-lang-chinese`。套件來源沒有它時，從 GitHub 的 CTeX-org/ctex-kit 原始碼建置，放進個人 TeX 目錄（在 Ubuntu 的 TeX Live 2023 上驗證過；`xetex --version` 顯示 2025 年以後的 TeX Live 可以拿掉 `git fetch` 那行的版本、改抓最新版）：
  ```bash
  # 新版 ctex-kit 需要 2026 年以後的 LaTeX；TeX Live 2023 用下面這個驗證過的 2022 版本
  mkdir ctex-kit && cd ctex-kit
  git init -q && git remote add origin https://github.com/CTeX-org/ctex-kit.git
  git fetch -q --depth 1 origin c3d9e851ca84eeb575335b65dd46d00b42a16e83
  git checkout -q FETCH_HEAD
  export TEXINPUTS=$PWD/support//:   # 建置需要 support/ctxdocstrip.tex
  # 每一行都會順便排版說明文件，可能印出錯誤；不用理會，最後 kpsewhich 找得到就成功
  (cd xeCJK && xetex -interaction=nonstopmode xeCJK.dtx || true)
  (cd ctex && xetex -interaction=nonstopmode ctex.dtx || true)
  (cd zhnumber && xetex -interaction=nonstopmode zhnumber.dtx || true)
  unset TEXINPUTS
  mkdir -p ~/texmf/tex/latex/ctexkit
  cp xeCJK/*.sty xeCJK/*.cfg xeCJK/*.def ~/texmf/tex/latex/ctexkit/
  cp ctex/*.sty ctex/*.cls ctex/*.def ctex/*.cfg ctex/*.fd ctex/*.clo ctex/*.tex ctex/*.spa ctex/*.dict ~/texmf/tex/latex/ctexkit/
  cp zhnumber/*.sty zhnumber/*.cfg ~/texmf/tex/latex/ctexkit/
  kpsewhich ctex.sty xeCJK.sty zhnumber.sty   # 三個都要找得到
  ```

## 常見問題

- **yt-dlp 下載失敗**：先 `yt-dlp -U`（winget 安裝的用 `winget upgrade yt-dlp.yt-dlp`）。YouTube 常改版，舊版很容易壞。
- **Bilibili 畫質**：不登入通常也有一般 1080P，先用 `-F` 看。只拿到 480P／720P、或要字幕時，可加 `--cookies-from-browser chrome`（會讀 Chrome 的登入資料，要先同意；要先完全關掉 Chrome，讀不到時改用 Firefox）。
- **雲端環境下載被擋**（`403`、`Unable to connect to proxy`）：不是暫時性錯誤，改在使用者電腦下載，見 `references/online-video.md`「下載不到時」。
- **編譯出現 Missing character**：字型缺字。確認 check_env.py 有找到繁中字型。
- **whisper 很慢**：處理時間約是音訊長度的 2 倍。中日韓粵英影片改用 SenseVoice；其他語言只能等，或先只轉需要的片段。
- **連不到 Hugging Face 或 OpenAI 的模型網址**（雲端環境常見）：本 skill 的模型都從 GitHub 下載，不受影響。
