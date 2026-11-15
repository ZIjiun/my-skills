#!/usr/bin/env python3
"""檢查 video-to-notes 需要的工具和繁中字型。只讀取、不安裝任何東西。

用法：python scripts/check_env.py      （macOS／Linux 用 python3）
"""
import glob
import os
import platform
import shutil
import subprocess
import sys

TOOLS = [
    # 指令, 用途, 是否必要
    ("yt-dlp", "下載線上影片、封面、字幕", "線上影片必要"),
    ("ffmpeg", "抽截圖、抽音訊、轉字幕", "必要"),
    ("ffprobe", "讀本地影片資訊", "必要"),
    ("xelatex", "編譯 PDF", "要 PDF 就必要"),
    ("magick", "拼縮圖、裁切、壓縮圖片", "建議"),
    ("whisper", "沒有字幕時語音轉文字", "沒字幕的影片才需要"),
]

# 範本依序嘗試的繁中字型（檔名關鍵字，小寫）
FONT_HINTS = {
    "Noto Serif CJK TC": ["notoserifcjk", "notoserifcjktc", "notoserifcjk-regular.ttc"],
    "Microsoft JhengHei（微軟正黑體）": ["msjh"],
    "PMingLiU（新細明體）": ["mingliu"],
    "Songti TC（宋體-繁）": ["songti"],
    "PingFang TC（蘋方-繁）": ["pingfang"],
}


def version(cmd):
    for flag in ("--version", "-version"):
        try:
            out = subprocess.run([cmd, flag], capture_output=True, text=True, timeout=20)
            line = (out.stdout or out.stderr).strip().splitlines()
            if line:
                return line[0][:80]
        except Exception:
            pass
    return "已安裝"


def font_dirs():
    sysname = platform.system()
    if sysname == "Windows":
        win = os.environ.get("WINDIR", r"C:\Windows")
        local = os.environ.get("LOCALAPPDATA", "")
        return [os.path.join(win, "Fonts"), os.path.join(local, "Microsoft", "Windows", "Fonts")]
    if sysname == "Darwin":
        return ["/System/Library/Fonts", "/System/Library/Fonts/Supplemental", "/Library/Fonts",
                os.path.expanduser("~/Library/Fonts")]
    return ["/usr/share/fonts", "/usr/local/share/fonts", os.path.expanduser("~/.local/share/fonts"),
            os.path.expanduser("~/.fonts")]


def find_fonts():
    names = []
    for d in font_dirs():
        if os.path.isdir(d):
            for p in glob.iglob(os.path.join(d, "**", "*"), recursive=True):
                if p.lower().endswith((".ttf", ".ttc", ".otf")):
                    names.append(os.path.basename(p).lower().replace(" ", ""))
    found = [label for label, keys in FONT_HINTS.items() if any(k in n for n in names for k in keys)]
    # macOS 的 PingFang 是系統字型，不一定看得到檔案；用 fc-list 再補查一次
    if shutil.which("fc-list"):
        try:
            out = subprocess.run(["fc-list", ":lang=zh-tw", "family"], capture_output=True, text=True,
                                 timeout=30).stdout
            for label in FONT_HINTS:
                if label.split("（")[0] in out and label not in found:
                    found.append(label)
        except Exception:
            pass
    if platform.system() == "Darwin" and not any("PingFang" in f for f in found):
        found.append("PingFang TC（蘋方-繁，macOS 內建，未直接偵測到檔案）")
    return found


def main():
    print(f"系統：{platform.system()} {platform.release()}，Python {sys.version.split()[0]}\n")
    missing_required = []
    for cmd, use, need in TOOLS:
        path = shutil.which(cmd)
        if path:
            print(f"  [OK]   {cmd:8s} {version(cmd)}")
        else:
            print(f"  [缺少] {cmd:8s} 用途：{use}（{need}）")
            if need in ("必要", "要 PDF 就必要"):
                missing_required.append(cmd)

    fonts = find_fonts()
    print()
    if fonts:
        print("  [OK]   繁中字型：" + "、".join(fonts))
    else:
        print("  [缺少] 繁中字型：找不到，PDF 會改用 FandolSong，部分繁體字可能缺字。")

    print()
    if missing_required:
        print("缺少必要工具：" + "、".join(missing_required) + "。安裝步驟見 references/setup.md。")
    else:
        print("必要工具都在。")


if __name__ == "__main__":
    main()
