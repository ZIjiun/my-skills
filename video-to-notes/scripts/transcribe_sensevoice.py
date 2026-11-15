#!/usr/bin/env python3
"""用 SenseVoice（sherpa-onnx）把音訊轉成帶時間戳的 SRT。中文、粵語、日文、韓文、英文適用。

需要：pip install sherpa-onnx soundfile numpy
模型（第一次下載一次，約 1 GB，從 GitHub 下載）：
  https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17.tar.bz2
  https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/silero_vad.onnx
把 tar.bz2 解壓到 <模型資料夾>，silero_vad.onnx 也放在 <模型資料夾>。

用法：
  python scripts/transcribe_sensevoice.py audio.wav <模型資料夾> subs.srt [--lang zh|yue|ja|ko|en|auto]

audio.wav 必須是 16 kHz 單聲道：ffmpeg -i <影片> -vn -ac 1 -ar 16000 audio.wav
時間戳以語音段落為單位（每段最長約 12 秒）。
"""
import argparse
import glob
import os
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("wav")
    ap.add_argument("model_dir")
    ap.add_argument("out_srt")
    ap.add_argument("--lang", default="auto", help="zh、yue、ja、ko、en 或 auto（預設）")
    ap.add_argument("--threads", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    a = ap.parse_args()

    try:
        import numpy  # noqa: F401
        import sherpa_onnx
        import soundfile as sf
    except ImportError:
        sys.exit("缺少套件：pip install sherpa-onnx soundfile numpy")

    sv = glob.glob(os.path.join(a.model_dir, "**", "tokens.txt"), recursive=True)
    vad_model = glob.glob(os.path.join(a.model_dir, "**", "silero_vad.onnx"), recursive=True)
    if not sv or not vad_model:
        sys.exit("模型資料夾裡找不到 SenseVoice（tokens.txt）或 silero_vad.onnx，下載方式見本檔開頭。")
    sv_dir = os.path.dirname(sv[0])
    model = os.path.join(sv_dir, "model.int8.onnx")
    if not os.path.isfile(model):
        model = os.path.join(sv_dir, "model.onnx")

    rec = sherpa_onnx.OfflineRecognizer.from_sense_voice(
        model=model, tokens=sv[0], num_threads=a.threads, use_itn=True, language=a.lang)
    cfg = sherpa_onnx.VadModelConfig()
    cfg.silero_vad.model = vad_model[0]
    cfg.silero_vad.min_silence_duration = 0.3
    cfg.silero_vad.max_speech_duration = 12
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
    print(f"完成：{n} 段，寫入 {a.out_srt}")


if __name__ == "__main__":
    main()
