# Meta AI Prompt Library

Every prompt here is built for **meta.ai (Muse Spark)** and only uses **verified** capabilities:
reading public Instagram, Threads, and Facebook content, semantic search over posts since Jan 2025,
creator discovery, trend/comment reading, and brand-mention search.

## Template standard (every entry follows this)

Built on the prompting practices in `working-with-claude` (section 3), applied as model-general
engineering (Muse Spark's exact preferences are unverified, so the self-test is the backstop):

1. **Directive first line.** An action verb stating the task and hinting at the output. Biggest lever.
2. **Decomposed steps**, numbered, capability check always step 1.
3. **Interpolated inputs wrapped in a named tag** (`<brief>`, `<inputs>`) so meta.ai knows what is data.
4. **Explicit `<output_format>`**: exact columns, sort order, and how to mark uncertainty.
5. **A one-shot `<example>`** showing an ideal row (for table outputs).
6. **Honesty rules**: never fabricate a handle, number, or link; label estimates; cite real links.
7. **No em dashes**, ever (user rule).

Variables are `{{like_this}}`. The skill fills them and updates the example if a variable changes its shape.

---

## A1: Micro-influencer / ambassador finder
**Use when:** finding small creators to recruit for an ambassador program or partnership.
**Fills:** `{{niche}}`, `{{location}}` (optional), `{{follower_min}}`, `{{follower_max}}`, `{{vibe}}`, `{{count}}`

```
Act as my Instagram research analyst. Read public Instagram directly and find {{count}} creators who match the brief below. Work in three numbered steps and do not skip step 1.

1. Capability check. Before searching, state plainly whether you can return, for public Instagram creators: (a) follower counts, (b) what their content is about, (c) links to recent posts. Answer yes or no for each. If you cannot do (a) or (c), say so and continue with what you can, flagging lower confidence. Never invent a handle, number, or link. Label any estimate as an estimate.

2. Find creators who meet EVERY line in this brief:
<brief>
- Niche: {{niche}}
- Location or audience: {{location}}
- Followers: between {{follower_min}} and {{follower_max}}
- Vibe and fit: {{vibe}}
</brief>
Prefer genuine, watchable accounts over polished ad-style ones. Exclude any account you cannot actually see.

3. Output. Return a markdown table sorted best-fit first, columns exactly:
<output_format>
| Handle | Followers | What they post | Sample reel (link) | Why they fit |
Rules: real links only; if a field is uncertain write "unsure", not a guess; below the table, list anyone you flagged as uncertain and why.
</output_format>

<example>
| @examplewander | 24k | solo female city guides, honest safety tips | https://instagram.com/reel/xxxx | real solo traveler who films herself, warm and specific, not ad-style |
</example>

Do not use em dashes. Use periods or line breaks.
```

---

## A2: Existing-fan creator finder
**Use when:** finding people who ALREADY posted about a brand and make decent content (best ambassador candidates).
**Fills:** `{{brand}}`, `{{brand_urls}}`, `{{window}}`, `{{follower_min}}`

```
Find real Instagram creators who already post about my brand and could become ambassadors. Read public Instagram directly. Work in three numbered steps, step 1 first.

1. Capability check. State yes or no: can you find posts that mention a specific brand, and can you see the poster's follower count and content? Do not fabricate posts or handles. Label estimates.

2. Find creators who, in the last {{window}}, posted a reel or post mentioning the brand, and who fit this brief:
<brief>
- Brand: {{brand}}
- Brand handles or URLs: {{brand_urls}}
- Minimum followers: {{follower_min}}
</brief>
Prioritize genuine fans with watchable content over one-off tags.

3. Output. Markdown table, sorted by best ambassador fit first:
<output_format>
| Handle | Followers | Post that mentions the brand (link) | What they generally post | Sentiment (positive/neutral/negative) |
Rules: real links only; mark uncertain fields "unsure"; if you find none, say so plainly.
</output_format>

<example>
| @realtraveler | 12k | https://instagram.com/reel/xxxx | carry-on packing, airport tips | positive |
</example>

Do not use em dashes.
```

---

## A3: Handle verification + profile snapshot
**Use when:** confirming a list of handles is real and current before following, studying, or sending to a client.
**Fills:** `{{handles}}`

```
Verify a list of Instagram accounts for me before I use them. Read public Instagram directly. Step 1 first.

1. Capability check. State yes or no: can you look up real Instagram accounts and their follower counts? If you cannot verify an account, say so instead of guessing.

2. Verify each handle in this list:
<inputs>
Handles: {{handles}}
</inputs>

3. Output. Markdown table, one row per handle, same order as given:
<output_format>
| Handle | Exists and active? | Followers | Mostly about | Recent post (link) | Flags |
Rules: flag anything inactive, private, renamed, or unconfirmable in the Flags column; never invent follower numbers; mark unknowns "unsure".
</output_format>

<example>
| @examplesolo | yes | 120k | solo female travel, honest safety tips | https://instagram.com/reel/xxxx | active, verified I can see it |
</example>

Do not use em dashes.
```

---

## B1: Reaction / stitch target finder
**Use when:** finding specific videos in a niche worth reacting to, stitching, or responding to.
**Fills:** `{{topic}}`, `{{window}}`, `{{count}}`, `{{angle}}` (optional)

```
Find {{count}} Instagram reels worth reacting to. Read public Instagram directly. Step 1 first.

1. Capability check. State yes or no: can you find recent reels on a specific topic and return their links and view counts? Do not fabricate videos. Label estimates.

2. Find reels matching this brief:
<brief>
- Topic: {{topic}}
- Window: last {{window}}
- Angle I care about: {{angle}}
</brief>
Prioritize reels getting real traction, not tiny posts.

3. Output. Markdown table, sorted by traction (highest first):
<output_format>
| Reel (link) | Handle | Followers | Views (if visible) | Reaction angle |
Rules: real links only; the reaction angle names the specific claim worth agreeing with, pushing back on, or adding to; mark uncertain fields "unsure".
</output_format>

<example>
| https://instagram.com/reel/xxxx | @packpro | 88k | 1.2M | claims you never need a checked bag, good setup to counter with the one exception |
</example>

Do not use em dashes.
```

---

## B2: Niche trend scan
**Use when:** learning what is actually gaining traction in a niche right now.
**Fills:** `{{niche}}`, `{{window}}`

```
Tell me what is actually gaining traction in a niche right now, from real posts, not old blog knowledge. Read public Instagram directly, including captions and comments. Step 1 first.

1. Capability check. State yes or no: can you see current posts, engagement, and comments in this niche? Do not invent trends or examples.

2. Scan this niche and window:
<brief>
- Niche: {{niche}}
- Window: last {{window}}
</brief>

3. Output. Two labeled sections, "Clearly trending" and "Early signal", each a markdown table:
<output_format>
| Angle or topic | Example post (link) | Why it seems to be landing |
Rules: real links only; base every row on a post you can point to; 3 to 5 rows per section.
</output_format>

<example>
| "airport outfit that doubles as pajamas" | https://instagram.com/reel/xxxx | comfort plus practicality, high save rate in comments |
</example>

Do not use em dashes.
```

---

## B3: Saturation & gap check
**Use when:** deciding what NOT to make (overdone) and where the openings are.
**Fills:** `{{niche}}`

```
Show me what is overdone versus underserved in a niche, so I can avoid making content everyone already makes. Read public Instagram directly. Step 1 first.

1. Capability check. State yes or no: can you see current content volume and engagement in this niche? Do not guess.

2. Assess this niche:
<brief>
- Niche: {{niche}}
</brief>

3. Output. Two labeled markdown tables:
<output_format>
Saturated (overdone right now):
| Angle or format | Example (link) | Note |
Underserved (audience clearly wants it, few cover it well):
| Angle or format | Evidence (link or comment) | Note |
Rules: real links only; cite the comment or post that is your evidence for "underserved".
</output_format>

<example>
| generic "pack a capsule wardrobe" listicles | https://instagram.com/reel/xxxx | everywhere, low saves |
</example>

Do not use em dashes.
```

---

## B4: Comment mining
**Use when:** pulling real audience questions and pain points to seed content ideas.
**Fills:** `{{niche_or_handles}}`, `{{window}}`

```
Mine real audience questions and complaints from Instagram comments for me. Read public Instagram comments directly. Step 1 first.

1. Capability check. State yes or no: can you read comments on public posts? If no, say so and stop.

2. Look at high-engagement posts matching this brief:
<brief>
- Niche or handles: {{niche_or_handles}}
- Window: last {{window}}
</brief>

3. Output. Markdown table, top 10 recurring themes, most common first:
<output_format>
| Theme | Example comment (verbatim) | Post (link) | How common |
Rules: quote comments verbatim, never paraphrase or invent; real links only; group similar themes into one row.
</output_format>

<example>
| does it fit under the seat | "but will this actually fit under a United seat??" | https://instagram.com/reel/xxxx | very common |
</example>

Do not use em dashes.
```

---

## C1: Brand mention monitor
**Use when:** tracking who is talking about a brand, sentiment, and what to respond to.
**Fills:** `{{brand}}`, `{{brand_urls}}`, `{{window}}`

```
Track mentions of my brand across Instagram, Threads, and Facebook. Read these platforms directly. Step 1 first.

1. Capability check. State yes or no: can you search brand mentions across these platforms, including in comments? Do not fabricate posts.

2. Find mentions matching this brief:
<brief>
- Brand: {{brand}}
- Handles or URLs: {{brand_urls}}
- Window: last {{window}}
</brief>

3. Output. Markdown table, "respond-worthy" ones first:
<output_format>
| Post (link) | Platform | Handle | Followers | Sentiment | One-line summary | Respond? (yes/no + why) |
Rules: real links only; mark uncertain fields "unsure"; if there are none, say so.
</output_format>

<example>
| https://instagram.com/p/xxxx | Instagram | @happycustomer | 4k | positive | loves the bag on her Tokyo trip | yes, thank her and reshare |
</example>

Do not use em dashes.
```

---

## C2: Competitor account teardown
**Use when:** studying a competitor's Instagram to learn what works in the space.
**Fills:** `{{competitor_handles}}`, `{{window}}`

```
Break down a competitor's Instagram account for me. Read public Instagram directly. Step 1 first.

1. Capability check. State yes or no: can you see the account's posts and their relative performance? Do not invent numbers.

2. Analyze this brief:
<brief>
- Competitor handle(s): {{competitor_handles}}
- Window: last {{window}}
</brief>

3. Output. Use these labeled sections:
<output_format>
Top posts (markdown table): | Post (link) | Views (if visible) | Why it worked |
What works: 3 to 5 bullets on the formats and topics that clearly land for them.
Positioning: 2 to 3 lines on how they present themselves.
Cadence: how often they post.
The opening: one thing they are clearly NOT doing that is a gap for someone else.
Rules: real links only; base every claim on a post you can cite; mark uncertain numbers "unsure".
</output_format>

<example>
Top posts row: | https://instagram.com/reel/xxxx | 900k | founder on-camera origin story, high completion |
</example>

Do not use em dashes.
```

---

## D1: Creator voice study before pitch
**Use when:** preparing to reach out to a creator for a partnership.
**Fills:** `{{handle}}`

```
Study a creator's voice before I pitch them a partnership. Read public Instagram directly. Step 1 first.

1. Capability check. State yes or no: can you read this creator's recent feed? If the account is private or you cannot see it, say so and stop.

2. Study this account:
<inputs>
Handle: {{handle}}
</inputs>

3. Output. Use these labeled sections, and cite a specific post for each claim:
<output_format>
Tone and personality: 2 to 3 lines.
Recurring themes: bullets.
What they clearly care about: bullets.
How they open their videos: the pattern, with one example link.
Words or phrases they reuse: short list.
Brands they already work with: list, or "none I can see".
How to approach them: two sentences that fit their vibe.
Rules: cite real post links; if you cannot confirm something, say "unsure", do not guess.
</output_format>

Do not use em dashes.
```
