#!/usr/bin/env python3
"""把音訊轉成帶時間戳的 SRT。用 sherpa-onnx 跑 SenseVoice 或 whisper，模型都從 GitHub 下載。

選哪個引擎（見 SKILL.md「語音轉文字」）：
  sensevoice：中文、粵語、日文、韓文、英文首選（快、會加標點）
  whisper   ：其他語言（法文、西班牙文等）只能用它；英文腔調重、術語多時當備案（慢很多）

需要：pip install sherpa-onnx soundfile numpy

模型（每種只要下載一次，全部放在同一個 <模型資料夾> 裡解壓）：
  語音段落偵測（兩種引擎都要）：
    https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/silero_vad.onnx
  SenseVoice（約 1GB）：
    https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17.tar.bz2
  whisper large-v3-turbo（約 560MB，準確度接近 large、速度快很多）：
    https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-turbo.tar.bz2

這些網址在 GitHub 上。OpenAI 官方和 Hugging Face 的模型網址在雲端環境常被擋，所以不用。

用法：
  python scripts/transcribe.py audio.wav <模型資料夾> subs.srt --engine sensevoice [--lang auto]
  python scripts/transcribe.py audio.wav <模型資料夾> subs.srt --engine whisper [--lang en]

audio.wav 必須是 16 kHz 單聲道：ffmpeg -i <影片> -vn -ac 1 -ar 16000 audio.wav
時間戳以語音段落為單位（每段最長約 12 秒）。
"""
import argparse
import glob
import os
import sys


def find(model_dir, pattern):
    hits = sorted(glob.glob(os.path.join(model_dir, "**", pattern), recursive=True))
    return hits[0] if hits else None


def build_recognizer(engine, model_dir, lang, threads, sherpa_onnx):
    if engine == "sensevoice":
        tokens = None
        for t in sorted(glob.glob(os.path.join(model_dir, "**", "tokens.txt"), recursive=True)):
            if "sense-voice" in t or "sensevoice" in t.lower():
                tokens = t
                break
        if not tokens:
            sys.exit("模型資料夾裡找不到 SenseVoice（sherpa-onnx-sense-voice-…/tokens.txt），下載網址見本檔開頭。")
        d = os.path.dirname(tokens)
        model = os.path.join(d, "model.int8.onnx")
        if not os.path.isfile(model):
            model = os.path.join(d, "model.onnx")
        return sherpa_onnx.OfflineRecognizer.from_sense_voice(
            model=model, tokens=tokens, num_threads=threads, use_itn=True,
            language=("auto" if lang in ("", "auto") else lang))

    enc = find(model_dir, "*-encoder.int8.onnx") or find(model_dir, "*-encoder.onnx")
    if not enc:
        sys.exit("模型資料夾裡找不到 whisper（sherpa-onnx-whisper-…/*-encoder*.onnx），下載網址見本檔開頭。")
    prefix = os.path.basename(enc).split("-encoder")[0]
    d = os.path.dirname(enc)
    dec = os.path.join(d, os.path.basename(enc).replace("-encoder", "-decoder"))
    tokens = os.path.join(d, f"{prefix}-tokens.txt")
    if not (os.path.isfile(dec) and os.path.isfile(tokens)):
        sys.exit(f"whisper 模型不完整，需要 {os.path.basename(dec)} 和 {prefix}-tokens.txt。")
    return sherpa_onnx.OfflineRecognizer.from_whisper(
        encoder=enc, decoder=dec, tokens=tokens, num_threads=threads,
        language=("" if lang in ("", "auto") else lang), task="transcribe")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("wav")
    ap.add_argument("model_dir")
    ap.add_argument("out_srt")
    ap.add_argument("--engine", choices=["sensevoice", "whisper"], required=True)
    ap.add_argument("--lang", default="auto",
                    help="sensevoice：zh、yue、ja、ko、en 或 auto；whisper：en、fr、es… 或 auto（自動判斷）")
    ap.add_argument("--threads", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    a = ap.parse_args()

    try:
        import numpy  # noqa: F401
        import sherpa_onnx
        import soundfile as sf
    except ImportError:
        sys.exit("缺少套件：pip install sherpa-onnx soundfile numpy")

    vad_model = find(a.model_dir, "silero_vad.onnx")
    if not vad_model:
        sys.exit("模型資料夾裡找不到 silero_vad.onnx，下載網址見本檔開頭。")
    rec = build_recognizer(a.engine, a.model_dir, a.lang, a.threads, sherpa_onnx)

    cfg = sherpa_onnx.VadModelConfig()
    cfg.silero_vad.model = vad_model
    cfg.silero_vad.min_silence_duration = 0.3
    cfg.silero_vad.max_speech_duration = 12  # whisper 一次最多處理 30 秒，切短一點也讓時間戳比較準
    cfg.sample_rate = 16000
    vad = sherpa_onnx.VoiceActivityDetector(cfg, buffer_size_in_seconds=120)

    audio, sr = sf.read(a.wav, dtype="float32")
    if sr != 16000 or getattr(audio, "ndim", 1) != 1:
        sys.exit("音訊要是 16 kHz 單聲道：ffmpeg -i <影片> -vn -ac 1 -ar 16000 audio.wav")

    segs = []

    def drain():
        while not vad.empty():
            s = vad.front
            st = rec.create_stream()
            st.accept_waveform(16000, s.samples)
            rec.decode_stream(st)
            start = s.start / 16000
            segs.append((start, start + len(s.samples) / 16000, st.result.text.strip()))
            vad.pop()

    w = cfg.silero_vad.window_size
    for i in range(0, len(audio), w):
        vad.accept_waveform(audio[i:i + w])
        drain()
    vad.flush()
    drain()

    def fmt(t):
        ms = int(round(t * 1000))
        return "%02d:%02d:%02d,%03d" % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)

    n = 0
    with open(a.out_srt, "w", encoding="utf-8") as f:
        for s, e, t in segs:
            if t:
                n += 1
                f.write(f"{n}\n{fmt(s)} --> {fmt(e)}\n{t}\n\n")
    print(f"完成（{a.engine}）：{n} 段，寫入 {a.out_srt}")


if __name__ == "__main__":
    main()
