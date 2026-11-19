# 本地影片

使用者給的是電腦上的影片檔路徑時，用這份流程取代 `references/online-video.md`。其他步驟（分段、截圖、寫作、審查、編譯、Notion）都一樣。

## 1. 確認檔案

- 路徑有空白或中文時加引號。Windows 路徑可以直接用 `C:\Users\...`，也可以用 `/`。
- 找不到檔案就請使用者確認路徑，不要猜。
- 一次給多個檔案或一整個資料夾時，先列出清單問：要各做一份筆記，還是當成同一門課的多集合併成一份。

## 2. Metadata

```
ffprobe -v quiet -print_format json -show_format -show_streams "<影片>" > meta.json
```

- 標題：`format.tags.title`；沒有就用檔名（去掉副檔名）。
- 長度：`format.duration`（秒），換成 `h:mm:ss`。
- 日期：`format.tags.creation_time`；沒有就留空，不要用檔案修改時間假裝是發布日期。
- 講者：`format.tags.artist`／`author`；沒有就看影片開頭畫面或字幕自我介紹，再沒有就寫「未知」。
- 章節：`ffprobe -show_chapters`，有就拿來分段。

## 3. 字幕（依序嘗試）

1. **內嵌字幕軌**：`meta.json` 裡 `codec_type` 為 `subtitle` 的串流。文字型（subrip、ass、mov_text、webvtt）可直接抽：
   ```
   ffmpeg -i "<影片>" -map 0:s:<第幾條字幕，從0算> subs.srt
   ```
   圖片型字幕（hdmv_pgs_subtitle、dvd_subtitle）沒辦法直接轉文字，跳到下一項。
2. **同資料夾的外掛字幕**：同檔名的 `.srt`、`.vtt`、`.ass`（例如 `lecture.zh-TW.srt`）。`.ass`／`.vtt` 用 `ffmpeg -i x.ass subs.srt` 轉成 srt。
3. **語音轉文字**：見 `references/transcribe.md`（中日韓粵英用 SenseVoice，其他語言用 whisper）。
4. **只看畫面**：音質太差時，密集抽格，從畫面整理。

有多條字幕時，選影片原本語言的那條；拿不準就問使用者。

## 4. 封面

本地影片通常沒有官方封面：

1. 有內嵌封面圖（`disposition.attached_pic = 1` 的串流）就用它：
   ```
   ffmpeg -i "<影片>" -map 0:v:<那條串流的序號> -frames:v 1 cover.jpg
   ```
2. 沒有就從片頭找一張最能代表主題的畫面（標題投影片、課程名稱畫面），**看過圖片再決定**。封面頁上這張圖的說明寫「影片畫面（mm:ss）」，不要說它是官方封面。

## 5. 時間戳

- 要 PDF 時：`\videotimeprefix` 留空，`\videourl` 留空，`\videofile` 填檔名（不含使用者的完整路徑，避免把個人資料夾結構印在 PDF 上）。
- 時間戳顯示成 `[12:31]`，不做連結。
- Notion 裡寫成 `⏱ 12:31`（見 notion-output.md）。

## 6. 截圖

本地檔通常就是最高畫質，直接用 ffmpeg 抽格。影片很大時，用 `-ss` 放在 `-i` 前面做快速定位：

```
ffmpeg -ss 00:12:25 -i "<影片>" -t 20 -vf fps=1 cand_%04d.png
```
