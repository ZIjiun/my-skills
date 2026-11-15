# 工具安裝（每台電腦各裝一次）

需要的工具：

| 工具 | 用途 | 一定要嗎 |
|---|---|---|
| yt-dlp | 下載 YouTube／Bilibili 的影片、封面、字幕 | 線上影片要 |
| ffmpeg（含 ffprobe） | 抽截圖、抽音訊、讀本地影片資訊和字幕 | 要 |
| xelatex（TeX Live 或 MiKTeX） | 編譯 PDF | 要 PDF 就要 |
| ImageMagick（magick） | 拼縮圖總覽、裁切、壓縮圖片 | 建議 |
| whisper（openai-whisper） | 沒字幕時語音轉文字 | 沒字幕的影片才要 |
| Python 3 | 跑 whisper 和檢查腳本 | 要 |

裝完後**重開終端機**（或重開 Claude 桌面版），再執行 `python scripts/check_env.py` 確認。

## Windows（用 winget，在 PowerShell 執行）

```powershell
winget install --id Python.Python.3.12 -e
winget install --id yt-dlp.yt-dlp -e
winget install --id Gyan.FFmpeg -e
winget install --id ImageMagick.ImageMagick -e
winget install --id MiKTeX.MiKTeX -e
```

- **TeX**：MiKTeX 比較小，缺的套件會在第一次編譯時自動下載（第一次會比較久）。打開「MiKTeX Console」→ Settings，把「Install missing packages on-the-fly」設成 **Always**，不然編譯時會跳視窗卡住。想一次裝齊可改裝 TeX Live（`winget install --id TeXLive.TeXLive -e`，約 8 GB）。
- **字型**：Windows 內建「微軟正黑體」和「新細明體」，範本會自動使用，不用另外裝。想要更好看的明體可以裝 Noto Serif CJK TC（Google Fonts 下載，右鍵「為所有使用者安裝」）。
- **whisper**：
  ```powershell
  pip install -U openai-whisper
  ```
  有 NVIDIA 顯示卡的話，先照 https://pytorch.org 的指示裝 CUDA 版 PyTorch，速度會快很多。
- PowerShell 裡的 `curl` 是別名，上傳檔案到 Notion 時要用 `curl.exe`（Windows 10 以上內建）。

## macOS（用 Homebrew，在「終端機」執行）

沒有 Homebrew 先照 https://brew.sh 裝。

```bash
brew install python yt-dlp ffmpeg imagemagick
brew install --cask mactex-no-gui
pip3 install -U openai-whisper
```

- MacTeX 約 5 GB，裝完要重開終端機，`xelatex` 才找得到。
- 字型：macOS 內建「宋體-繁」（Songti TC）和「蘋方-繁」（PingFang TC），範本會自動使用。
- Apple Silicon（M 系列）跑 whisper 不需要額外設定；想更快可以改用 `pip3 install mlx-whisper`，但這個 skill 的指令是以 openai-whisper 為準。

## 常見問題

- **yt-dlp 下載失敗**：先 `yt-dlp -U`（winget 安裝的用 `winget upgrade yt-dlp.yt-dlp`）。YouTube 常改版，舊版很容易壞。
- **Bilibili 只拿到 480P／720P**：要登入才有 1080P。可加 `--cookies-from-browser chrome`（會讀 Chrome 的登入資料，要先同意）。
- **編譯出現 Missing character**：字型缺字。確認 check_env.py 有找到繁中字型。
- **whisper 很慢**：沒有顯示卡時，改 `--model small`，或先只轉需要的片段。
