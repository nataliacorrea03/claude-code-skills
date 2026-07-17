# problem-log daily sweep (headless)

Your job: read today's Claude Code sessions and append an entry for each genuine problem-solving arc to the log file. Silent run, no questions.

The log file path is given in the invoking prompt as LOG_FILE. If it does not exist yet, create it with a `# Problem Log` heading.

## Step 1 — Read the digest
Read `session-digest.txt` in this skill's folder. Each session starts with `## Session <id> (last active YYYY-MM-DD HH:MM)`. If it is empty, print `problem-log: nothing to log` and stop.

## Step 2 — Find the arcs (be selective)
An ARC is a session where a real problem, bug, blocker, or hard decision got worked through to a resolution or a clear next step.
CAPTURE: debugging journeys, a build that iterated through versions, a design/architecture decision with tradeoffs, a diagnosis that overturned a first guess, a messy cleanup reasoned through.
SKIP (write nothing): routine drafting, simple lookups/Q&A, status checks, anything with no friction. When in doubt, SKIP. An empty run is fine. Usually one arc per session. Ground every field in the transcript, never invent.

## Step 3 — Append one entry per arc
Read LOG_FILE, then append (do not overwrite) one block per arc, newest at the top under the heading:

```
## <short arc title>  ·  <YYYY-MM-DD>
- **Problem:** <the friction in one line>
- **Approach & iteration:** <how it was worked, including dead ends and pivots, 2-4 sentences>
- **Outcome:** <what actually resolved it>
- **Tools:** <comma-separated, e.g. Claude Code, Python, git>
- _session: <id>_
```

Skip any session id already present in the log (dedup).

## Step 4 — One stdout line
`problem-log: N arc(s) logged from M session(s)` (or `problem-log: nothing to log`).
