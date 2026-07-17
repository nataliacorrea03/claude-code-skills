#!/usr/bin/env python3
"""
Build a digest of the last day's building activity for build-capture.
Pure local filesystem work: no LLM, no network.

Collects three things into one digest file:
  1. user + assistant text from session transcripts touched in the window
  2. files changed under WATCH_DIR in the window
  3. recent git commits in WATCH_DIR (if it is a repo)

Env:
  WINDOW_HOURS=N   how far back to look (default 26)
  WATCH_DIR=path   folder you build in (default ~/.claude/skills)
  MIN_CHARS=N      skip sessions with less than this much text (default 1500)
"""
import glob
import json
import os
import subprocess
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECTS = os.path.expanduser("~/.claude/projects")
WATCH_DIR = os.path.expanduser(os.environ.get("WATCH_DIR", "~/.claude/skills"))
WINDOW_H = float(os.environ.get("WINDOW_HOURS", "26"))
MIN_CHARS = int(os.environ.get("MIN_CHARS", "1500"))
MAX_MSG = 500
MAX_SESSION = 8000
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
    lines, size = [], 0
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
                    size += len(snip)
    except OSError:
        return ""
    return "\n".join(lines)


def main():
    cutoff = time.time() - WINDOW_H * 3600
    parts = [f"# Build digest {time.strftime('%Y-%m-%d %H:%M %Z')} (window {WINDOW_H:g}h)"]

    # 1. sessions
    sess = []
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
            exc = session_excerpt(f)
            if len(exc) < MIN_CHARS:
                continue
            sess.append((m, f"\n## Session {os.path.basename(f).replace('.jsonl','')}\n{exc}"))
    sess.sort(reverse=True)
    parts += [c for _m, c in sess]

    # 2. files changed under WATCH_DIR
    changed = []
    for root, _dirs, files in os.walk(WATCH_DIR):
        if "/." in root or "node_modules" in root or "__pycache__" in root:
            continue
        for fn in files:
            p = os.path.join(root, fn)
            try:
                if os.path.getmtime(p) >= cutoff:
                    changed.append(os.path.relpath(p, WATCH_DIR))
            except OSError:
                pass
    parts.append("\n## Files changed under WATCH_DIR in window:\n"
                 + ("\n".join(sorted(changed)[:200]) if changed else "none"))

    # 3. git commits in WATCH_DIR
    try:
        gl = subprocess.run(
            ["git", "-C", WATCH_DIR, "log", f"--since={int(WINDOW_H)} hours ago",
             "--format=%ad %s", "--date=short"],
            capture_output=True, text=True, timeout=15).stdout.strip()
        parts.append("\n## git commits in window:\n" + (gl or "none"))
    except Exception:
        pass

    out = os.path.join(HERE, "build-digest.txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(parts) + "\n")
    print(f"[build-capture] {len(sess)} session(s), {len(changed)} changed file(s) -> {out}")


if __name__ == "__main__":
    main()
