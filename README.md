# Claude Code Skills

A small, opinionated collection of [Claude Code](https://claude.com/claude-code) **skills** for working with AI like a craftsperson, not a button-masher.

A skill is just a folder with a `SKILL.md` inside. Claude Code reads it and gains a new, reliable behavior you can invoke by name. These four are battle-tested in daily use and stripped of anything personal, so you can drop them straight into your own setup.

## What's inside

| Skill | What it does | Invoke with |
|-------|--------------|-------------|
| **working-with-claude** | Anthropic's official best practices, distilled from all nine Anthropic Academy courses into one reference: the 4D framework, what the model can and can't do, the prompting techniques that actually move quality, and Claude Code operating discipline. | `/working-with-claude` |
| **build-mode** | A teach-while-building mode. Claude explains each non-trivial change in plain English, surfaces design decisions as options-with-tradeoffs for *you* to pick, and runs a short gut-check at the end so you actually understand what got built. | `/build-mode` |
| **no-bullshit** | Forces the model to verify before it claims. Bans fabricated APIs, file paths, and citations. Blocks "it works" without execution proof. Requires an inline uncertainty label on every shaky claim. | `/no-bullshit` |
| **generate-system-map** | Scans your skills and scheduled agents and generates a standalone interactive HTML map of your whole automation setup: a radial mind-map, a schedule view, and a feedback panel that outputs copy-ready fix prompts. | `/generate-system-map` |

## Why these exist

Most "prompt tips" lists go stale the moment a new model ships. These skills encode the parts that *don't* change: how to delegate well, how to tell good output from confident-sounding output, and how to keep your own judgment in the loop. Two of them (`working-with-claude`, `no-bullshit`) are pure working philosophy. Two (`build-mode`, `generate-system-map`) are practical tools you run.

## Install

A skill is a folder. Installing one is copying that folder into your skills directory.

**For all your projects (user-level):**
```bash
git clone https://github.com/nataliacorrea03/claude-code-skills.git
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

Restart Claude Code (or run `/reload`) and the skill is live. The folder name is the command, so `skills/no-bullshit/` becomes `/no-bullshit`.

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
