---
name: meeting-ingest
description: >
  Ingests a meeting transcript into the Near Work Partner vault. Given a transcript (from Fathom MCP, a file path, or pasted text), processes it into a structured vault note with a TLDR, key decisions, action items, and attendees. Auto-creates task entries for any action items found. Updates wiki/index.md, wiki/hot.md, and logs/ingest-log.md. Use this skill any time you receive a meeting transcript or are asked to "log this meeting", "save this call", or "ingest this transcript". Supports three input modes: Fathom MCP (already connected — start with get_identity), file path (.txt/.vtt), or direct paste.
---

# meeting-ingest

Ingests meeting transcripts into the vault.

## Input Modes

### Mode 1: Fathom MCP
If user says "pull from Fathom" or gives a Fathom meeting ID/URL:

1. `mcp__claude_ai_Fathom__get_identity()` — confirms who you're authenticated as. There is no
   `authenticate` tool; if this errors, the MCP connector needs re-authorising in Claude settings
   and you cannot fix it from here — fall back to Mode 3 (ask Gaston to paste).
2. Resolve the `recording_id`:
   - Gaston pasted a URL → `get_recording_by_url(url)`. **`/share/<token>` links can return "url not
     found or access denied"** (seen 2026-10-06, on both Fathom servers). This happens when someone else
     recorded the meeting and it doesn't appear in `list_meetings` either. **Don't guess by date:** on
     2026-10-06 that picked the wrong call. Open the share URL in the built-in browser and use
     `get_page_text`. The page title, AI summary and action items are all there.
   - Gaston gave a bare number → try `get_recording_by_call_id(call_id)` first, then treat it as
     a `recording_id` if that 404s
   - Neither → `list_meetings(created_after=..., ...)` and pick the match
3. `mcp__claude_ai_Fathom__get_meeting_transcript(recording_id, url)` — **pass `url` too**. It is
   what turns the output into clickable `[MM:SS](url?timestamp=N)` deep links, which is how a task
   later points at the exact moment a commitment was made.
4. Proceed to processing.

> [!important] The number in a `https://fathom.video/calls/<n>` URL is **not** the `recording_id`.
> They are different values. Never parse an ID out of a URL — always take `recording_id` from
> `list_meetings` / `get_recording_by_url`, and store **both** in the note's frontmatter.

Transcripts are heavy (~8-10k tokens for a 45-min call) and rate-limited to 30 requests/60s,
degradable to 5/60s. Fetch at most **3 transcripts per batch**.

> [!warning] **The Fathom MCP tools may be absent from the tool registry** even when
> `claude mcp list` reports `✓ Connected` (seen 2026-08-25). If `mcp__claude_ai_Fathom__*` /
> `mcp__fathom__*` cannot be loaded, the server is still reachable — **do not fall back to Mode 3**.
> Spawn `npx mcp-remote@latest https://api.fathom.ai/mcp` over stdio and speak JSON-RPC directly:
> `initialize` → `notifications/initialized` → `tools/call`. Allow ~2 min (npx cold start).
>
> Two schema corrections that apply either way:
> - `list_meetings` paginates with **`cursor`**, not `next_cursor` — the latter is rejected as a
>   disallowed property. Prefer `max_pages` (1–20, ~10 results/page) to sweep a date range.
> - `list_meetings` takes `recorded_by` (array of emails). **Use it.** The workspace feed is mostly
>   AE sales consultations Gaston did not attend — on a 4-day window, 21 of 23 results were noise.

### Mode 2: File Path
If user provides a file path (.txt, .vtt, .docx):
1. Read the file with the filesystem Read tool
2. Proceed to processing

### Mode 3: Paste
If user pastes transcript text directly:
1. Use the pasted content as-is
2. Proceed to processing

---

## Processing Steps

### Step 1: Extract metadata
From the transcript, identify:
- **Date**: when the meeting happened (default to today if unclear)
- **Topic**: 2-5 word description of the meeting (for filename)
- **Attendees**: names and roles present
- **Meeting type**: `internal` / `client` / `candidate` / `vendor`
- **Duration** (if available)

### Step 2: Generate TLDR
Write 3-5 bullets capturing the most important things that happened. The TLDR is the key output — it must be good enough that someone can decide whether to read the full transcript without reading it.

What makes a good TLDR bullet:
- Specific, not generic ("Acme Corp agreed to move forward" not "discussed partnership")
- Decision-oriented (what was decided, not what was discussed)
- Action-oriented (includes follow-up items with owners)
- Dates when relevant

### Step 3: Extract key sections
- **Key Decisions** — things decided in the meeting
- **Action Items** — specific tasks with owner (usually Gaston) and optional deadline
- **Context / Background** — relevant context that informed the discussion
- **Open Questions** — unresolved items, things to follow up on

### Step 4: Create bibliography entry

File: `bibliography/YYYY-MM-DD - {Topic} - Meeting.md`

```markdown
---
type: bibliography
source_type: meeting
title: "{Topic} — {Date}"
date: YYYY-MM-DD
date_ingested: YYYY-MM-DD
meeting-type: internal|client|candidate|vendor
attendees: ["Name", "Name"]
topics: ["[[wiki/meetings/filename]]"]
wiki_pages: ["[[wiki/meetings/filename]]"]
---

{2-3 sentence summary of what this meeting was about and its key outcome.}
```

### Step 5: Create meeting note

File: `wiki/meetings/YYYY-MM-DD-{topic-slug}.md`

```markdown
---
type: meeting
title: "{Topic}"
created: YYYY-MM-DD
updated: YYYY-MM-DD
attendees: ["Name — Role", "Name — Role"]
meeting-type: internal|client|candidate|vendor
duration-min: 30
recording_id: 166148624              # REQUIRED for Fathom-sourced meetings
fathom-url: "https://fathom.video/calls/756981297"
tags: [type/meeting, meeting-type/{type}]
status: mature
related: []                          # omit the key entirely if it stays empty
sources: ["[[bibliography/YYYY-MM-DD - Topic - Meeting]]"]
---

# {Topic}

## TLDR
- {Bullet 1 — most important}
- {Bullet 2}
- {Bullet 3}
- {Bullet 4 if needed}
- {Bullet 5 if needed}

## Key Decisions
- {Decision 1}
- {Decision 2}

## Action Items
- [ ] {Task description} — *{owner}* — due: {date if known}
- [ ] {Task description} — *{owner}*

## Context
{Relevant background discussed}

## Open Questions
- {Unresolved item 1}

## Full Transcript
{Paste transcript here, or note "See Fathom: {link}" if from recording}
```

`recording_id` + `fathom-url` are required for anything sourced from Fathom. They are what lets a
future question ("what did I actually mean by this task?") refetch the transcript live for ~0 stored
tokens. Without them, every refetch costs an extra `list_meetings` search. Store both — they are
different numbers.

**The `## Full Transcript` section stores a link, never the transcript.** A 45-min call is ~8-10k
tokens of low-density filler; the TLDR is what replaces it, and the vault is cold storage read on
demand. This is a hard rule in `WIKI.md`.

### Step 6: Create task entries for action items

For EACH action item where Gaston is the owner, create a task file. Format is owned by the
`task-manager` skill — read it if you need detail beyond this template.

File: `wiki/tasks/YYYY-MM-DD-{task-slug}.md`

```markdown
---
type: task
title: "{Task Description}"
created: YYYY-MM-DD
updated: YYYY-MM-DD
priority: high|medium|low
deadline: YYYY-MM-DD        # ONLY if a date was stated outright — omit the key otherwise
status: open
from-meeting: "[[wiki/meetings/YYYY-MM-DD-topic]]"
---

# {Task Description}

{1-3 lines: what it is and why it matters.}

**Why:** {who asked, what it unblocks, what "done" looks like}
**Timing:** {verbatim phrase, when no hard date was given}
```

**Frontmatter rules (trimmed 2026-08-19 — do not undo):**
- **No `tags:`** — redundant with `type` + `status` + `priority`.
- **No empty `related: []` / `sources: []`** — omit the key entirely rather than writing an empty
  list. Include them only when they actually point somewhere.
- **Never invent a `deadline`.** Only set it when a date was stated outright, and resolve relative
  days ("by Thursday") against the **meeting date**, not today's. Vague timing ("soon", "when you
  get a chance") → omit `deadline:`, put the phrase in `**Timing:**`, and ask Gaston. A guessed date
  looks authoritative and silently misleads.

**Quote budget: 2 lines max** of verbatim transcript per task, and link the Fathom timestamp for
anything deeper. Target **≤250 tokens per task file** — they are cold storage, and `_index.md` is
what actually gets read.

Then add to `wiki/tasks/_index.md` under the appropriate **time-horizon** section — `## This Week`
/ `## Next Week` / `## Backlog`, not priority buckets (restructured 2026-08-19; see `task-manager`
→ Index Format for the authoritative rules). Infer the horizon from the stated deadline; default to
**Backlog** when the meeting gave no timing, and flag those in your report so Gaston can place them.

### Step 7: Update vault navigation

1. **`wiki/index.md`** — Add meeting to Meetings section:
   ```
   - [[meetings/YYYY-MM-DD-topic]] — {Topic}, {Date}. Key: {1-sentence summary}. Tasks: {task list}.
   ```
   Add tasks to Tasks (Open) section.

2. **`wiki/hot.md`** — Overwrite completely with:
   - Last Updated: today + what was ingested
   - Key Recent Facts: top 2-3 things from the meeting
   - Recent Changes: meeting page + tasks created
   - Open Threads: action items still in flight

3. **`logs/ingest-log.md`** — Prepend new entry:
   ```markdown
   ## YYYY-MM-DD | meeting | {Topic}
   - Source: [[bibliography/YYYY-MM-DD - Topic - Meeting]]
   - Pages created: [[meetings/YYYY-MM-DD-topic]], [[tasks/task-1]], ...
   - Key insight: {One sentence on main outcome}
   ```

---

## Output to User

After ingestion, report:

```
Meeting ingested: {Topic} ({Date})
Attendees: {list}

TLDR:
• {bullet 1}
• {bullet 2}
...

Tasks created ({N}):
• [{task 1}] due {date}
• [{task 2}]

Vault updated: wiki/meetings/{filename}
```

---

## Error Handling

- If transcript is garbled/incomplete: note "Partial transcript" in the meeting note, ingest what's available
- If attendee names unclear: use "Unknown Attendee" and flag as open question
- If no action items: leave action items section empty, do not create task files
- If Fathom auth fails: fall back to asking user to paste transcript
