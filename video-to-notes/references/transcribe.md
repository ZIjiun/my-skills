# 語音轉文字（沒有字幕時）

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
