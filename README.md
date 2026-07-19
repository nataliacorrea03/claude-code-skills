# Claude Code Skills

A small, opinionated collection of [Claude Code](https://claude.com/claude-code) **skills** for working with AI like a craftsperson, not a button-masher.

A skill is just a folder with a `SKILL.md` inside. Claude Code reads it and gains a new, reliable behavior you can invoke by name. These are skills I use daily, stripped of anything personal, so you can drop them straight into your own setup.

## What's inside

| Skill | What it does | Invoke with |
|-------|--------------|-------------|
| **working-with-claude** | Anthropic's official best practices, distilled from Anthropic's Academy courses into one reference: the 4D framework, what the model can and can't do, the prompting techniques that actually move quality, and Claude Code operating discipline. | `/working-with-claude` |
| **build-mode** | A teach-while-building mode. Claude explains each non-trivial change in plain English, surfaces design decisions as options-with-tradeoffs for *you* to pick, and runs a short gut-check at the end so you actually understand what got built. | `/build-mode` |
| **no-bullshit** | Forces the model to verify before it claims. Bans fabricated APIs, file paths, and citations. Blocks "it works" without execution proof. Requires an inline uncertainty label on every shaky claim. | `/no-bullshit` |
| **lean** | Token-efficiency mode: a strict waste-cutting protocol (plan first, ask don't guess, grep before read, cheap-model subagents only, diff edits, scoped verification) that never trades away quality. Self-improving: corrections accumulate in a learnings log it reads on every run. Ships with a script that scores your real sessions so you can measure the savings. | `/lean` |
| **generate-system-map** | Scans your skills and scheduled agents and generates a standalone interactive HTML map of your whole automation setup: a radial mind-map, a schedule view, and a feedback panel that outputs copy-ready fix prompts. Most useful once you run several skills or scheduled agents. | `/generate-system-map` |
| **imessage** | Read and send iMessages from your Mac using built-in macOS tools, no third-party app. Drafts only by default, sends on your explicit "send it." Send mode needs one scoped permission; read mode (pulling past threads) needs Full Disk Access and warns you first. | `/imessage` |
| **plain-english** | Rewrites Claude's last answer (or any text you point it at) into something short and jargon-free. Fire it the moment a reply is too long or too technical. It also nudges the rest of the session to stay plain. | `/plain-english` |
| **swipe** | Turns digital cleanup into a Tinder-style swipe deck on your phone. Point it at a folder (or your unread texts), swipe each card left or right on your phone over local WiFi, and the actions run in one reversible batch (files to Trash, replies staged, never auto-sent). Built for the task paralysis where a folder of 300 screenshots is easier to ignore than to face. macOS. | `/swipe` |
| **ai-writing-qa** | Scrubs scripts and copy for AI tells before they ship, then hands back a clean rewrite in your voice. Catches em dashes, blacklisted buzzwords, "not X it's Y" contrasts, tricolons, warmup, hedging, and dated short-form hooks. Auto-detects register (client-facing / internal / creative) and rewrites every line that trips. Draft only, never sends. | `/ai-writing-qa` |
| **meta-prompt** | Builds ready-to-paste prompts for Meta AI (Muse Spark), which can read public Instagram, Facebook, and Threads directly in ways Claude can't. Describe a research goal (find micro-influencers, videos to react to, brand mentions, niche trends, competitor teardowns, a creator's voice before you pitch them), answer a couple of questions, and get a copy-paste prompt for the meta.ai app. Also hands out the Hook Machine, a full multi-turn workflow that analyzes a creator's top reels, extracts why the winners win, builds a grading rubric, then generates, grades, and rewrites hooks. Every prompt self-tests so the model admits what it can't pull instead of faking it. Never fetches data itself, never invents capabilities. | `/meta-prompt` |
| **build-capture** | A hands-off daily log of everything you build in Claude Code. Once a day a cron reads that day's sessions and the files that changed, figures out what you actually built or shipped, and appends a short entry per build to a local markdown file. No manual step, no `/wrap`. Great for standups, changelogs, or just remembering what you made. | daily cron |
| **problem-log** | A hands-off daily log of *how you solve problems*. Once a day a cron reads that day's sessions and writes a short entry per real problem-solving arc (the problem, how you worked it including dead ends, the outcome) to a local markdown file. Skips routine chatter. Gold for standups, reviews, and interviews. | daily cron |
| **video-breakdown** | Break down any video (YouTube, Loom, Instagram, TikTok, or a local file) frame by frame. Downloads it, rips scene-change frames plus a timestamped transcript locally, then Claude reads the visuals and the words together to teardown the hooks, structure, on-screen moves, and why it works. In-house, just yt-dlp + ffmpeg, nothing leaves your machine. | `/video-breakdown` |
| **pressure-test** | A brutally honest cofounder that stress-tests a business idea against Sam Altman's Startup Playbook. Not a yes-machine: grades it across five areas, names the most likely way you quietly kill it yourself, and ends with three ranked weaknesses and the one thing to do first. | `/pressure-test` |

## Why these exist

Most "prompt tips" lists go stale the moment a new model ships. These skills encode the parts that *don't* change: how to delegate well, how to tell good output from confident-sounding output, and how to keep your own judgment in the loop. Some change how Claude communicates with you (`working-with-claude`, `no-bullshit`, `plain-english`); the rest are practical tools you run (`build-mode`, `generate-system-map`, `imessage`).

## Looking for build recipes?

These are skills you install and invoke. If you instead want prompts you paste once to *build* something (a tool, an automation, a custom skill), see the companion repo: [claude-code-recipes](https://github.com/nataliacorrea03/claude-code-recipes).

## Install

A skill is a folder. Installing one is copying that folder into your skills directory.

**For all your projects (user-level):**
```bash
git clone https://github.com/nataliacorrea03/claude-code-skills.git
mkdir -p ~/.claude/skills
cp -r claude-code-skills/skills/* ~/.claude/skills/
```

**For a single project (project-level, shareable with your team):**
```bash
cp -r claude-code-skills/skills/* /path/to/your-project/.claude/skills/
```

Pick only the ones you want, e.g. just one:
```bash
cp -r claude-code-skills/skills/no-bullshit ~/.claude/skills/
```

Restart Claude Code and the skill is live. The folder name is the command, so `skills/no-bullshit/` becomes `/no-bullshit`.

**Confirm it worked:** run `ls ~/.claude/skills` to see the installed folders, then type the command (e.g. `/no-bullshit`) inside Claude Code.

**Remove one:** delete its folder, e.g. `rm -rf ~/.claude/skills/no-bullshit`.

## Using them

- Type the command (e.g. `/build-mode`) to invoke a skill directly.
- Most also trigger on natural language. `no-bullshit` fires on phrases like "be rigorous" or "are you sure"; `build-mode` on "teach me as you build."
- `working-with-claude` is a reference. Pull the section that fits the moment instead of reading it top to bottom.

## Who this is for

Anyone using Claude Code who wants higher-quality, more trustworthy output, and wants to come out of each build understanding more than they did going in. No prior skill-authoring knowledge needed.

## License

MIT. Use them, fork them, adapt them. See [LICENSE](LICENSE).

## Credits

Built and maintained by [Natalia Correa](https://github.com/nataliacorrea03). The `working-with-claude` skill is a distillation of the publicly available [Anthropic Academy](https://www.anthropic.com/learn) courses.
