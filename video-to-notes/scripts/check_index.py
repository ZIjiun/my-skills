#!/usr/bin/env python3
"""用腳本（不靠 AI）核對 Gemini 的畫面索引有沒有漏格。

scan_frames.py 抽出的每一格縮圖檔名帶著時間（thumbs/t_HH-MM-SS_mmm.jpg，總覽圖裡每格下面也印同一個時間）。
這支腳本檢查：每一格的時間，是不是都出現在 sheet_index.md 裡。沒出現的就是索引漏掉的格，
Claude 要自己打開那張總覽圖補看。

另外統計「看不清」的列數，讓你知道有多少要回原圖確認。

用法：python scripts/check_index.py frames_scan
結束碼：0 = 每一格都有索引；1 = 有漏格（清單印在畫面上，也寫進 frames_scan/index_missing.txt）。
"""
import glob
import os
import re
import sys

STAMP = re.compile(r"(\d{2}):(\d{2}):(\d{2})\.(\d{3})")


def secs(h, m, s, ms):
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def main():
    if len(sys.argv) != 2:
        sys.exit("用法：python scripts/check_index.py <frames_scan 資料夾>")
    d = sys.argv[1]
    index = os.path.join(d, "sheet_index.md")
    if not os.path.isfile(index):
        sys.exit(f"找不到 {index}，先跑 scripts/index_sheets.py")
    text = open(index, encoding="utf-8").read()
    indexed = {round(secs(*m.groups()), 3) for m in STAMP.finditer(text)}

    tiles = []
    for p in glob.glob(os.path.join(d, "thumbs", "t_*.jpg")):
        m = re.match(r"t_(\d+)-(\d+)-(\d+)_(\d+)", os.path.basename(p))
        if m:
            tiles.append(round(secs(*m.groups()), 3))
    tiles.sort()
    if not tiles:
        sys.exit(f"{d}/thumbs 裡沒有縮圖；scan_frames.py 要保留 thumbs 資料夾才能核對")

    missing = [t for t in tiles if not any(abs(t - x) < 0.0015 for x in indexed)]
    unclear = sum(line.count("看不清") for line in text.splitlines() if line.startswith("|"))
    fmt = lambda t: "%02d:%02d:%06.3f" % (t // 3600, t // 60 % 60, t % 60)
    print(f"縮圖 {len(tiles)} 格，索引涵蓋 {len(tiles) - len(missing)} 格，漏 {len(missing)} 格；「看不清」{unclear} 處（要回原圖確認）")
    if missing:
        out = os.path.join(d, "index_missing.txt")
        with open(out, "w", encoding="utf-8") as f:
            f.write("\n".join(fmt(t) for t in missing) + "\n")
        print("漏掉的格（前 20 個）：" + " ".join(fmt(t) for t in missing[:20]))
        print(f"完整清單：{out}。請 Claude 打開這些時間所在的總覽圖補看。")
        sys.exit(1)


if __name__ == "__main__":
    main()
