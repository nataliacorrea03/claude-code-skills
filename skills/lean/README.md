# lean — token-efficiency mode for Claude Code

A skill that makes Claude execute with the least possible tokens without sacrificing quality: plan-first, ask-don't-guess, grep-before-read, cheap-model subagents only, diff edits, scoped verification, and session hygiene with a concrete context threshold. It also improves itself: every correction gets logged to `LEARNINGS.md` and applied on the next invocation.

## Setup (2 minutes)
1. Copy this folder to `~/.claude/skills/lean/`.
2. `chmod +x ~/.claude/skills/lean/scan-sessions.sh`
3. That's it. No accounts, no APIs, no config.

## Usage
- Invoke with `/lean`, or say "save tokens" / "cheap mode" at the start of a big task.
- When Claude does something wasteful, correct it once. The skill logs the lesson to `LEARNINGS.md` and applies it next time.

## Measure it
```
./scan-sessions.sh              # all sessions, all models
./scan-sessions.sh opus         # only messages from models matching "opus"
./scan-sessions.sh . 2026-07-01 # all models, sessions after July 1
```
Scores each local session in weighted token units (output weighted 5x, cache reads 0.1x, matching standard API price ratios). Capture a baseline before adopting lean, rerun after two weeks, compare units per message. The `lean_used` column flags which sessions ran the skill.

## How it works
`SKILL.md` is a strict protocol with a rationalization table and red-flags list, so the model catches itself mid-excuse instead of negotiating. `LEARNINGS.md` is a capped, self-consolidating memory (20 entries max) so the skill gets smarter without getting heavier. `scan-sessions.sh` reads the per-message usage that Claude Code already logs in `~/.claude/projects/*/*.jsonl`.
