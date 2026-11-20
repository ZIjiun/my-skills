#!/usr/bin/env python3
"""截圖第一段：產生「看圖用」的候選畫面，不產生最後放進筆記的圖。

做兩件事，結果放在 <輸出資料夾>：
1. 逐幀場景變化偵測 → segments.txt（每個畫面段落的起訖秒數），以及每段中間一格的縮圖。
   停留不到 1 秒的段落，把該段每一格都抽出來，避免短暫閃過的畫面（例如提示詞）被漏掉。
   但連續好幾秒都是短段落（捲動網頁、動畫）時，只抽停下來的最後一格，避免產生上千張捲到一半的縮圖。
2. 每秒一格的保底抽樣，抓慢慢捲動、逐字打出這類變化太小、偵測不到的畫面。
兩邊合併後，去掉和前一張幾乎相同的縮圖，再拼成總覽圖 sheet_XX.jpg（每張 6x6，左上角印時間）。

用總覽圖決定要哪些畫面後，回原影片用原解析度抽格、裁切（見 SKILL.md 第 4 步）。

需要：ffmpeg、ffprobe；拼總覽圖需要 ImageMagick（magick 或 montage）。
用法：python scripts/scan_frames.py video.mp4 frames_scan [--threshold 0.02] [--burst-max 1.5] [--width 466]
"""
import argparse
import glob
import os
import re
import shutil
import subprocess
import sys


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def duration(video):
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video])
    return float(out.stdout.strip())


def grab(video, t, path, width):
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", video, "-frames:v", "1",
         "-vf", f"scale={width}:-1", path])


def name(t):
    return "t_%02d-%02d-%02d_%03d.jpg" % (t // 3600, t // 60 % 60, t % 60, round(t * 1000) % 1000)


def signature(path):
    """64x36 灰階縮圖的像素，用來判斷兩張圖是否幾乎相同。"""
    out = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", "scale=64:36,format=gray",
                          "-f", "rawvideo", "-"], capture_output=True)
    return out.stdout


def similar(a, b, max_changed=0.004):
    """變動超過門檻的像素比例很低（預設 0.4%，約 9 個像素）才算重複。"""
    if not a or not b or len(a) != len(b):
        return False
    changed = sum(1 for x, y in zip(a, b) if abs(x - y) > 24)
    return changed / len(a) <= max_changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("outdir")
    ap.add_argument("--threshold", type=float, default=0.02,
                    help="場景變化門檻。投影片捲動、螢幕錄影用 0.02；剪接明顯的影片可提高到 0.1–0.3")
    ap.add_argument("--burst-max", type=float, default=1.5,
                    help="連續短畫面總長在這個秒數內才逐格抽；更長的視為捲動或動畫，只抽最後一格（預設 1.5）")
    ap.add_argument("--width", type=int, default=466, help="縮圖寬度（只用來看圖，不是最後用圖）")
    a = ap.parse_args()

    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            sys.exit(f"缺少 {tool}")
    os.makedirs(a.outdir, exist_ok=True)
    thumbs = os.path.join(a.outdir, "thumbs")
    os.makedirs(thumbs, exist_ok=True)
    total = duration(a.video)

    # 1. 逐幀場景偵測
    out = run(["ffmpeg", "-i", a.video, "-vf", f"scale=320:-2,select='gt(scene,{a.threshold})',showinfo",
               "-an", "-f", "null", "-"])
    cuts = [float(x) for x in re.findall(r"pts_time:([0-9.]+)", out.stderr)]
    bounds = [0.0] + cuts + [total]
    segs = [(s, e) for s, e in zip(bounds, bounds[1:]) if e - s >= 0.05]
    with open(os.path.join(a.outdir, "segments.txt"), "w", encoding="utf-8") as f:
        f.write("# 起(秒) 迄(秒) 長度(秒)\n")
        for s, e in segs:
            f.write(f"{s:.3f} {e:.3f} {e - s:.3f}\n")

    # 要抽的時間點：(秒, 是否可去重複)。短暫畫面的格不去重複，那正是要找的東西。
    # 連續的短段落合成一串（burst）。一串總長不超過 BURST_MAX 秒，是「閃過的畫面」（標題卡、提示詞），
    # 每一格都抽；更長的一串是捲動網頁、動畫這類「一直在變」的畫面，每一格都抽會產生上千張幾乎
    # 一樣、捲到一半的縮圖，所以只抽停下來的最後一格，中間靠每秒一格的保底。
    picks, burst = {}, []

    def flush():
        if not burst:
            return
        if burst[-1][1] - burst[0][0] <= a.burst_max:
            for s, e in burst:  # 短暫畫面：每一格都抽（以 30fps 計）
                t = s + 1 / 60
                while t < e:
                    picks[round(t, 3)] = False
                    t += 1 / 30
        else:
            picks[round(max(burst[-1][1] - 1 / 60, burst[-1][0]), 3)] = False
        burst.clear()

    for s, e in segs:
        if e - s < 1.0:
            burst.append((s, e))
        else:
            flush()
            picks.setdefault(round((s + e) / 2, 3), True)
    flush()
    # 2. 每秒一格保底（一次 ffmpeg 抽完，比逐一跳轉快很多）
    base = os.path.join(thumbs, "b_%05d.jpg")
    out = run(["ffmpeg", "-v", "info", "-y", "-i", a.video, "-vf",
               f"select='isnan(prev_selected_t)+gte(t-prev_selected_t\\,1)',showinfo,scale={a.width}:-1",
               "-vsync", "vfr", "-q:v", "3", base])
    base_times = [float(x) for x in re.findall(r"pts_time:([0-9.]+)", out.stderr)]
    files = sorted(glob.glob(os.path.join(thumbs, "b_*.jpg")))
    cands = []
    for t, p in zip(base_times, files):
        q = os.path.join(thumbs, name(t))
        os.replace(p, q)
        cands.append((t, q, True))
    for t, dedup in picks.items():
        q = os.path.join(thumbs, name(t))
        grab(a.video, t, q, a.width)
        if os.path.isfile(q):
            cands.append((t, q, dedup))
    cands.sort()

    # 去重複：只拿掉和前一張「幾乎一模一樣」的保底格。比對用 64x36 灰階，
    # 門檻很嚴，多一行字或游標移開都會留下；寧可多看幾張，也不要漏。
    kept, last_sig = [], None
    for t, p, dedup in cands:
        sig = signature(p)
        if dedup and similar(sig, last_sig):
            os.remove(p)
            continue
        last_sig = sig
        kept.append((t, p))

    montage = shutil.which("magick") or shutil.which("montage")
    if montage:
        for i in range(0, len(kept), 36):
            labeled = []
            for t, p in kept[i:i + 36]:
                lp = p[:-4] + "_lb.jpg"
                cmd = ([montage] if montage.endswith("montage") else [montage, "montage"])
                subprocess.run(cmd + ["-label", "%02d:%02d:%06.3f" % (t // 3600, t // 60 % 60, t % 60),
                                      p, "-geometry", "+0+0", "-pointsize", "16", lp], capture_output=True)
                labeled.append(lp if os.path.isfile(lp) else p)
            cmd = ([montage] if montage.endswith("montage") else [montage, "montage"])
            subprocess.run(cmd + labeled + ["-tile", "6x6", "-geometry", "+3+3",
                                            os.path.join(a.outdir, "sheet_%02d.jpg" % (i // 36))],
                           capture_output=True)
            for lp in labeled:
                if lp.endswith("_lb.jpg") and os.path.isfile(lp):
                    os.remove(lp)
    short = sum(1 for s, e in segs if e - s < 1.0)
    print(f"影片 {total:.1f} 秒；場景段落 {len(segs)} 個（其中 {short} 個不到 1 秒）；"
          f"去重複後候選縮圖 {len(kept)} 張；總覽圖 {len(glob.glob(os.path.join(a.outdir, 'sheet_*.jpg')))} 張"
          + ("" if montage else "（沒有 ImageMagick，未拼總覽圖，請直接看 thumbs 資料夾）"))


if __name__ == "__main__":
    main()
