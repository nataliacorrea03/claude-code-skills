# build-capture daily sweep (headless)

Your job: read today's building activity and append an entry for each real build to the log file. Silent run, no questions.

The log file path is given in the invoking prompt as LOG_FILE. If it does not exist yet, create it with a `# Build Log` heading.

## Step 1 — Read the digest
Read `build-digest.txt` in this skill's folder. It has the last day's session text, the files that changed, and recent git commits. If empty, print `build-capture: nothing to log` and stop.

## Step 2 — Extract builds
List what actually got built, shipped, progressed, or meaningfully changed today: skills, scripts/tools, apps, features, cloud jobs, infra, notable bug-fix or refactor sweeps. Use the changed files and commits as evidence, and the session text for what and why.
SKIP: pure Q&A, research, reading, and routine chatter with nothing built. When unsure, DROP it, conservative beats noisy.

## Step 3 — Append one entry per build (dedup)
Read LOG_FILE first. Match each build to an existing entry by name (case- and hyphen-insensitive). If it exists, update that entry's **Latest** line and date. If it is new, append a block at the top:

```
## <short-kebab-name>  ·  <Skill|Script|App|Fix|Other>  ·  <YYYY-MM-DD>
- **What it is:** <one plain sentence a stranger would understand>
- **Latest:** <YYYY-MM-DD: what happened today>
```

Additive only. Never delete or rewrite past entries beyond updating an existing build's Latest line. Cap at 8 builds per run.

## Step 4 — One stdout line
`build-capture: N logged` (or `build-capture: nothing to log`).
