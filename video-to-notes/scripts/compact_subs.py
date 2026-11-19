#!/usr/bin/env python3
"""把 SRT／VTT 字幕壓成精簡的文字檔，給寫筆記和審查時讀，省 token。

每一句一行，保留這句自己的開始時間（不合併句子，時間戳精確度不變）：
    [12:31] 這句話
    [1:02:31] 超過一小時的寫法
去掉 SRT 的編號、結束時間、空行和 VTT 的樣式標籤。

YouTube 自動字幕是「滾動式」的：每一條會把上一句再顯示一次，還有只停留 10 毫秒的重複條目。
同一行文字如果剛剛才出現過（前 2 行內），就不再輸出，避免同一句讀兩遍。

用法：python scripts/compact_subs.py subs.srt subs.txt
"""
import html
import re
import sys

TIME = r"(?:(\d+):)?(\d{1,2}):(\d{2})[,.](\d{3})"
TIMING = re.compile(TIME + r"\s*-->\s*" + TIME)
TAG = re.compile(r"<[^>]+>|\{\\[^}]*\}")


def seconds(h, m, s, ms):
    return int(h or 0) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def stamp(t):
    t = int(t)
    h, m, s = t // 3600, t // 60 % 60, t % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def cues(text):
    """依序回傳 (開始秒數, [文字行])。"""
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        m = TIMING.search(lines[i])
        if not m:
            i += 1
            continue
        start = seconds(*m.groups()[:4])
        i += 1
        body = []
        while i < len(lines) and lines[i].strip() and not TIMING.search(lines[i]):
            body.append(lines[i])
            i += 1
        yield start, body


def compact(text, window=2):
    out, recent = [], []
    for start, body in cues(text):
        for raw in body:
            line = html.unescape(TAG.sub("", raw)).strip()
            if not line or line in recent:
                continue
            out.append(f"[{stamp(start)}] {line}")
            recent = (recent + [line])[-window:]
    return out


def main():
    if len(sys.argv) != 3:
        sys.exit("用法：python scripts/compact_subs.py <字幕.srt|.vtt> <輸出.txt>")
    src, dst = sys.argv[1], sys.argv[2]
    with open(src, encoding="utf-8-sig") as f:
        text = f.read()
    out = compact(text)
    with open(dst, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print(f"{len(text)} 字元 → {sum(len(x) + 1 for x in out)} 字元（{len(out)} 行）")


if __name__ == "__main__":
    main()
