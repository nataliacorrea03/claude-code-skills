#!/bin/zsh
# build-capture daily sweep. Runs hands-off via a cron/LaunchAgent, or by hand.
#
# Manual:   ./daily-sweep.sh        (log now)
#           ./daily-sweep.sh dry    (print only, write nothing)
#
# Linux cron (7:35am daily): add to `crontab -e`:
#   35 7 * * *  /path/to/skills/build-capture/daily-sweep.sh
#
# Config (env or edit here):
#   WATCH_DIR  folder you build in (default ~/.claude/skills)
#   LOG_FILE   where entries go (default ~/build-log.md)

export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
DIR="$(cd "$(dirname "$0")" && pwd)"
export WATCH_DIR="${WATCH_DIR:-$HOME/.claude/skills}"
LOG_FILE="${LOG_FILE:-$HOME/build-log.md}"

# 1. Build today's digest (local only, no LLM).
python3 "$DIR/build_digest.py"

# 2. Headless pass: read the digest + prompt, append builds to the log file.
MODE=""
[ "$1" = "dry" ] && MODE="DRY RUN: print the entries you would append, write NOTHING. "
claude -p "${MODE}Read $DIR/SWEEP_PROMPT.md and execute it exactly. LOG_FILE is $LOG_FILE. Silent background run." \
  --allowedTools "Read Edit Write"
