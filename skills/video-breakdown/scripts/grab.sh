#!/usr/bin/env bash
# grab.sh: download a video, rip scene-change frames + a timestamped transcript.
# Usage: grab.sh <url-or-local-path> [slug] [--start MM:SS] [--end MM:SS] [--every N]
# Output: ~/claude-watch/library/<slug>/  with frames/ + transcript.txt + meta.txt
# No third-party code. Only yt-dlp + ffmpeg + python3 (all local).
set -euo pipefail

SRC="${1:?usage: grab.sh <url-or-path> [slug]}"
SLUG=""
START=""; END=""; EVERY=""
shift || true
# Only consume $1 (was $2) as the slug when it's a real slug, not an option flag.
if [ "${1:-}" ] && [ "${1#--}" = "$1" ]; then SLUG="$1"; shift; fi
while [ $# -gt 0 ]; do
  case "$1" in
    --start) START="$2"; shift 2;;
    --end)   END="$2";   shift 2;;
    --every) EVERY="$2"; shift 2;;
    *) shift;;
  esac
done

# Derive a slug if none given.
if [ -z "$SLUG" ]; then
  SLUG=$(echo "$SRC" | sed -E 's#https?://##; s#[^a-zA-Z0-9]+#-#g' | cut -c1-50)
  [ -z "$SLUG" ] && SLUG="clip"
fi

WORK="$HOME/claude-watch/library/$SLUG"
rm -rf "$WORK"; mkdir -p "$WORK/frames"
cd "$WORK"

echo ">> fetching: $SRC"
if [ -f "$SRC" ]; then
  cp "$SRC" "video.mp4"
else
  # 1) video first: this must succeed.
  yt-dlp -f "bv*[height<=720][vcodec^=avc]+ba/bv*[height<=720]+ba/b[height<=720]/b" \
    --no-playlist -o "video.%(ext)s" \
    --print-to-file "%(title)s" meta.txt "$SRC"
  # 2) captions are best-effort; a failure here must never block the run.
  yt-dlp --skip-download --write-auto-subs --write-subs \
    --sub-langs "en" --sub-format vtt \
    --no-playlist -o "video.%(ext)s" "$SRC" || echo ">> no captions (continuing)"
fi

VIDEO=$(ls video.* 2>/dev/null | grep -ivE '\.(vtt|srt|txt)$' | head -1 || true)
if [ -z "${VIDEO:-}" ]; then echo "!! no video downloaded"; exit 1; fi

# Optional trim window.
TRIM=()
[ -n "$START" ] && TRIM+=(-ss "$START")
[ -n "$END" ]   && TRIM+=(-to "$END")

echo ">> ripping scene-change frames"
# Scene detection: grab a frame whenever the picture changes enough, log timestamps.
ffmpeg -hide_banner -loglevel error ${TRIM[@]+"${TRIM[@]}"} -i "$VIDEO" \
  -vf "select='gt(scene,0.3)',metadata=print:file=frames/times.txt,format=yuvj420p" \
  -vsync vfr -q:v 4 "frames/frame_%04d.jpg" || true

COUNT=$(find frames -maxdepth 1 -name '*.jpg' 2>/dev/null | wc -l | tr -d ' ')
# Fallback: too few scene cuts (static talking-head) -> sample on an interval.
if [ "$COUNT" -lt 6 ]; then
  echo ">> few scene cuts ($COUNT); sampling every ${EVERY:-3}s instead"
  rm -f frames/*.jpg frames/times.txt
  ffmpeg -hide_banner -loglevel error ${TRIM[@]+"${TRIM[@]}"} -i "$VIDEO" \
    -vf "fps=1/${EVERY:-3},metadata=print:file=frames/times.txt,format=yuvj420p" \
    -q:v 4 "frames/frame_%04d.jpg" || true
  COUNT=$(find frames -maxdepth 1 -name '*.jpg' 2>/dev/null | wc -l | tr -d ' ')
fi

# Hard cap so a long video doesn't flood the folder: keep ~80 evenly.
if [ "$COUNT" -gt 80 ]; then
  echo ">> $COUNT frames; thinning to ~80"
  i=0; keep=$(( (COUNT + 79) / 80 ))
  for f in frames/frame_*.jpg; do
    [ $(( i % keep )) -ne 0 ] && rm -f "$f"
    i=$((i+1))
  done
  COUNT=$(find frames -maxdepth 1 -name '*.jpg' 2>/dev/null | wc -l | tr -d ' ')
fi

echo ">> building transcript"
VTT=$(ls *.vtt 2>/dev/null | head -1 || true)
WHISPER_MODEL="$HOME/.cache/whisper-cpp/ggml-small.en.bin"
if [ -n "${VTT:-}" ]; then
  python3 "$(dirname "$0")/vtt2txt.py" "$VTT" > transcript.txt || echo "(caption parse failed)" > transcript.txt
elif command -v whisper-cli >/dev/null 2>&1 && [ -f "$WHISPER_MODEL" ]; then
  # no captions: transcribe locally with whisper.cpp (no API key, nothing leaves the machine)
  echo ">> no captions, transcribing with whisper-cli"
  ffmpeg -y -loglevel error -i "$VIDEO" -ar 16000 -ac 1 _audio16k.wav \
    && whisper-cli -m "$WHISPER_MODEL" -f _audio16k.wav -np -otxt -of _whisper 2>/dev/null \
    && sed 's/^ *//' _whisper.txt > transcript.txt \
    || echo "NO_CAPTIONS: whisper transcription failed. On-screen text in frames still readable." > transcript.txt
  rm -f _audio16k.wav _whisper.txt
  [ -s transcript.txt ] || echo "NO_CAPTIONS: whisper produced no text (video may have no speech)." > transcript.txt
else
  echo "NO_CAPTIONS: spoken transcript unavailable (no captions on source, whisper-cli not installed). On-screen text in frames still readable." > transcript.txt
fi

echo ">> measuring cut rhythm"
# Free pacing signal: detect scene cuts, compute rhythm. Heuristic, not a motion read.
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$VIDEO" 2>/dev/null || echo "")
ffmpeg -hide_banner -loglevel error ${TRIM[@]+"${TRIM[@]}"} -i "$VIDEO" \
  -vf "select='gt(scene,0.3)',metadata=print:file=pacing_raw.txt" -an -f null - 2>/dev/null || true
python3 - "$DUR" > pacing.txt <<'PY'
import sys, re
dur = 0.0
try: dur = float(sys.argv[1])
except (IndexError, ValueError): pass
cuts = []
try:
    with open("pacing_raw.txt") as f:
        for line in f:
            m = re.search(r'pts_time:([0-9.]+)', line)
            if m: cuts.append(float(m.group(1)))
except FileNotFoundError:
    pass
cuts = sorted(set(round(c, 2) for c in cuts))
print("PACING (cut rhythm from ffmpeg scene detection; heuristic, not a true motion read)")
print(f"duration: {dur:.1f}s" if dur else "duration: unknown")
print(f"cuts detected: {len(cuts)}")
first_cut = cuts[0] if cuts else None
print(f"first cut at: {first_cut}s" if first_cut is not None else "first cut at: none")
bounds = [0.0] + cuts + ([dur] if dur else [])
gaps = [round(bounds[i+1] - bounds[i], 2) for i in range(len(bounds) - 1)] if len(bounds) > 1 else []
avg = sum(gaps) / len(gaps) if gaps else 0.0
if gaps:
    longest = max(gaps); li = gaps.index(longest)
    print(f"avg time between cuts: {avg:.2f}s")
    print(f"longest static stretch: {longest:.2f}s (from {bounds[li]:.1f}s to {bounds[li+1]:.1f}s)")
flags = []
if dur >= 5 and (first_cut is None or first_cut > 3):
    flags.append("slow open: no visual change in the first 3s")
if gaps and avg > 4: flags.append("static or slow pace: few cuts")
if gaps and avg < 0.7: flags.append("very fast cuts: may feel frantic")
if not cuts: flags.append("no cuts detected: single continuous shot")
print("flags: " + ("; ".join(flags) if flags else "none, pacing looks normal"))
PY
rm -f pacing_raw.txt

echo "frames: $COUNT" >> meta.txt
echo "source: $SRC"   >> meta.txt
echo
echo "DONE -> $WORK"
echo "  frames:     $COUNT in frames/"
echo "  transcript: $(wc -l < transcript.txt | tr -d ' ') lines"
echo "  frame times: frames/times.txt"
echo "  pacing:     pacing.txt"
