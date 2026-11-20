#!/usr/bin/env python3
"""請 Antigravity CLI（agy）裡的 Gemini 把總覽圖逐張讀成文字索引，讓 Claude 不用自己看圖。

用途：scan_frames.py 產生的 sheet_XX.jpg 很佔 token（每張一張大圖，之後每一步都會重讀）。
這支腳本把每張總覽圖交給 Gemini，產出 sheet_index/sheet_XX.md，再合併成 sheet_index.md：
每一格的時間、畫面類型、投影片標題和看得清楚的大字；看不清的一律標「看不清」，不准猜。

索引只用來「找位置」。要寫進筆記的數字、表格、小字，一律回原解析度截圖由 Claude 親自確認。

用法：python scripts/index_sheets.py frames_scan [--model gemini-4-neon-medium] [--jobs 4]
  - 已經有索引的總覽圖會跳過，中斷後可以直接重跑續做。
  - 找不到 agy 時結束碼 3，這時改回 SKILL.md 第 4 步的做法：Claude 自己看總覽圖。
  - 一律用 --model 指定 Gemini；不指定時 agy 會用介面上選的模型，可能是 Claude。
注意：總覽圖會傳給 Google 處理。影片不方便外傳時，不要跑這支腳本。
"""
import argparse
import concurrent.futures as cf
import glob
import os
import shutil
import subprocess
import sys
import time

PROMPT = """打開這個資料夾裡的圖片 {name}。它是影片畫面的 6x6 總覽圖：36 個小畫面，每格下面印著它在影片裡的時間（時:分:秒.毫秒）。
請依時間順序，每一格輸出一列 markdown 表格，欄位：時間｜畫面類型｜標題與大字｜看不清。
- 時間：照抄該格下面印的時間，不要改。
- 畫面類型：投影片、網站或軟體畫面、影片轉場或黑畫面、桌面、其他，擇一。
- 標題與大字：只寫你能清楚讀出的標題、大字和數字，照原文寫，中文維持原本的字。
- 看不清：小字、表格裡的數字、模糊的字，一律寫「看不清」並簡述是什麼東西（例如「績效表的數字」）。看不清就標看不清，絕對不要猜或補完。
連續幾格畫面幾乎一樣時，每格仍要各列一列，標題欄可以寫「同上」。
只輸出表格，不要其他說明。"""


def one(sheet, outdir, model, workdir, timeout):
    name = os.path.basename(sheet)
    out = os.path.join(outdir, name[:-4] + ".md")
    if os.path.isfile(out) and os.path.getsize(out) > 0:
        return name, "skip", 0.0
    t0 = time.time()
    for attempt in range(2):
        try:
            r = subprocess.run(["agy", "-p", PROMPT.format(name=name), "--model", model],
                               cwd=workdir, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            continue
        if r.returncode == 0 and r.stdout.strip() and "|" in r.stdout:
            with open(out, "w", encoding="utf-8") as f:
                f.write(r.stdout.strip() + "\n")
            return name, "ok", time.time() - t0
    return name, "fail", time.time() - t0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("frames_dir", help="scan_frames.py 的輸出資料夾（裡面有 sheet_XX.jpg）")
    ap.add_argument("--model", default="gemini-4-neon-medium")
    ap.add_argument("--jobs", type=int, default=4, help="同時跑幾張（預設 4）")
    ap.add_argument("--timeout", type=int, default=300, help="每張的秒數上限")
    a = ap.parse_args()

    if not shutil.which("agy"):
        print("找不到 agy（Antigravity CLI）；改由 Claude 自己看總覽圖。", file=sys.stderr)
        sys.exit(3)
    if "claude" in a.model.lower() or "gpt" in a.model.lower():
        sys.exit("--model 要指定 Gemini，不要用 Claude 或 GPT 的模型。")
    sheets = sorted(glob.glob(os.path.join(a.frames_dir, "sheet_*.jpg")))
    if not sheets:
        sys.exit(f"{a.frames_dir} 裡沒有 sheet_*.jpg")
    outdir = os.path.join(a.frames_dir, "sheet_index")
    os.makedirs(outdir, exist_ok=True)

    failed = []
    with cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        futs = [ex.submit(one, s, outdir, a.model, a.frames_dir, a.timeout) for s in sheets]
        for i, f in enumerate(cf.as_completed(futs), 1):
            name, status, sec = f.result()
            print(f"[{i}/{len(sheets)}] {name} {status} {sec:.0f}s", flush=True)
            if status == "fail":
                failed.append(name)

    merged = os.path.join(a.frames_dir, "sheet_index.md")
    with open(merged, "w", encoding="utf-8") as f:
        f.write("# 畫面索引（由 Gemini 產生，只用來找位置；小字和數字以原解析度截圖為準）\n\n")
        for s in sheets:
            p = os.path.join(outdir, os.path.basename(s)[:-4] + ".md")
            if os.path.isfile(p):
                f.write(f"## {os.path.basename(s)}\n\n{open(p, encoding='utf-8').read()}\n")
    print(f"合併索引：{merged}")
    if failed:
        print("這幾張失敗，請重跑或由 Claude 自己看：" + " ".join(failed), file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
