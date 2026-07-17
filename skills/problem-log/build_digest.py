#!/usr/bin/env python3
"""
Build a digest of the last day's Claude Code sessions for problem-log.
Pure local filesystem work: no LLM, no network.

Reads every session transcript touched in the window, keeps only user +
assistant text (tool dumps dropped), skips trivial short sessions, and writes
one digest file the daily sweep hands to a headless model.

Env:
  WINDOW_HOURS=N   how far back to look (default 26)
  MIN_CHARS=N      skip sessions with less than this much text (default 2000)
  MIN_TURNS=N      skip sessions with fewer turns than this (default 6)
"""
import glob
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECTS = os.path.expanduser("~/.claude/projects")
WINDOW_H = float(os.environ.get("WINDOW_HOURS", "26"))
MIN_CHARS = int(os.environ.get("MIN_CHARS", "2000"))
MIN_TURNS = int(os.environ.get("MIN_TURNS", "6"))
MAX_MSG = 600
MAX_SESSION = 9000
SKIP_PREFIXES = ("<system-reminder", "<command-", "<local-command",
                 "Base directory for this skill")


def text_blocks(msg):
    c = msg.get("content")
    if isinstance(c, str):
        return [c]
    out = []
    if isinstance(c, list):
        for b in c:
            if isinstance(b, dict) and b.get("type") == "text":
                out.append(b.get("text", ""))
    return out


def session_excerpt(path):
    lines, turns, size = [], 0, 0
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if size >= MAX_SESSION:
                    break
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                if rec.get("type") not in ("user", "assistant"):
                    continue
                for txt in text_blocks(rec.get("message") or {}):
                    txt = txt.strip()
                    if not txt or txt.startswith(SKIP_PREFIXES):
                        continue
                    snip = " ".join(txt[:MAX_MSG].split())
                    lines.append(f"{rec['type'].upper()}: {snip}")
                    turns += 1
                    size += len(snip)
    except OSError:
        return 0, ""
    return turns, "\n".join(lines)


def main():
    cutoff = time.time() - WINDOW_H * 3600
    chunks = []
    for d in sorted(glob.glob(os.path.join(PROJECTS, "*"))):
        if not os.path.isdir(d):
            continue
        for f in glob.glob(os.path.join(d, "*.jsonl")):
            try:
                m = os.path.getmtime(f)
            except OSError:
                continue
            if m < cutoff:
                continue
            turns, exc = session_excerpt(f)
            if turns < MIN_TURNS or len(exc) < MIN_CHARS:
                continue
            sid = os.path.basename(f).replace(".jsonl", "")
            chunks.append((m, f"\n## Session {sid} (last active "
                              f"{time.strftime('%Y-%m-%d %H:%M', time.localtime(m))})"
                              f"\n{exc}"))
    chunks.sort(reverse=True)
    out = os.path.join(HERE, "session-digest.txt")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(f"# Session digest {time.strftime('%Y-%m-%d %H:%M %Z')} "
                 f"(window {WINDOW_H:g}h, {len(chunks)} session(s))\n")
        fh.write("\n".join(c for _m, c in chunks) + "\n")
    print(f"[problem-log] {len(chunks)} session(s) -> {out}")


if __name__ == "__main__":
    main()
