#!/bin/zsh
# Score your Claude Code sessions by token spend, from the local transcripts.
# Usage: ./scan-sessions.sh [model-filter] [since-date]
#   model-filter  regex matched against the model name (default: all models)
#   since-date    only sessions modified after YYYY-MM-DD (default: all time)
# Example: ./scan-sessions.sh opus 2026-07-01
#
# Units: 1 unit = 1M input-equivalent tokens, weighted by standard API price
# ratios (input x1, cache write x1.25, cache read x0.1, output x5).
# Relative comparison only, not dollars. Requires jq. macOS stat syntax;
# on Linux swap `stat -f '%Sm' -t '%Y-%m-%d'` for `date -r "$f" +%Y-%m-%d`.

MODEL="${1:-.}"
SINCE="${2:-0000-00-00}"

echo "Columns: date | session | msgs | units | units_per_msg | lean_used"
for f in "$HOME"/.claude/projects/*/*.jsonl; do
  [ -e "$f" ] || continue
  fdate=$(stat -f '%Sm' -t '%Y-%m-%d' "$f")
  [[ "$fdate" > "$SINCE" ]] || continue
  lean="no"
  grep -qE 'skills/lean/SKILL\.md|"skill"[: ]+"lean"' "$f" && lean="yes"
  jq -r --arg m "$MODEL" 'select(.message.usage != null) | select(.message.model // "" | test($m)) | [(.message.usage.input_tokens // 0), (.message.usage.cache_creation_input_tokens // 0), (.message.usage.cache_read_input_tokens // 0), (.message.usage.output_tokens // 0)] | @tsv' "$f" 2>/dev/null |
  awk -v d="$fdate" -v f="$f" -v lean="$lean" '{i+=$1;cc+=$2;cr+=$3;o+=$4;n++} END{if(n>5){w=(i + cc*1.25 + cr*0.1 + o*5)/1000000; split(f,a,"/"); id=substr(a[length(a)],1,8); printf "%s | %s | %d | %.1f | %.4f | %s\n", d, id, n, w, w/n, lean}}'
done | sort -t'|' -k4 -rn
