#!/usr/bin/env python3
"""Turn a WebVTT caption file into clean, deduped, timestamped lines.
Usage: vtt2txt.py file.vtt  ->  stdout:  [MM:SS] text
No deps. Local only."""
import re, sys

def secs(ts):
    # 00:01:23.456 -> 83
    h, m, s = ts.split(":")
    return int(int(h) * 3600 + int(m) * 60 + float(s))

def mmss(t):
    return f"{int(t)//60:02d}:{int(t)%60:02d}"

def main(path):
    txt = open(path, encoding="utf-8", errors="ignore").read()
    out, last = [], None
    cue_time = None
    for line in txt.splitlines():
        m = re.match(r"(\d{2}:\d{2}:\d{2}[.,]\d{3})\s*-->", line)
        if m:
            cue_time = secs(m.group(1).replace(",", "."))
            continue
        if "-->" in line or line.strip() in ("", "WEBVTT") or line.strip().isdigit():
            continue
        # strip vtt inline tags like <00:00:01.000><c> ... </c>
        clean = re.sub(r"<[^>]+>", "", line).strip()
        if not clean or clean == last:
            continue
        # drop VTT header metadata lines
        if re.match(r"^(Kind|Language|NOTE|STYLE|Region)\s*[:=]", clean):
            continue
        last = clean
        out.append((cue_time if cue_time is not None else 0, clean))
    for t, line in out:
        print(f"[{mmss(t)}] {line}")

if __name__ == "__main__":
    main(sys.argv[1])
