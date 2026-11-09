---
name: meeting-ingest
description: >
  Ingests a meeting transcript into the Near Work Partner vault. Given a transcript (from Fathom MCP, a file path, or pasted text), processes it into a structured vault note with a TLDR, key decisions, action items, and attendees. Auto-creates task entries for any action items found. Updates wiki/index.md, wiki/hot.md, and logs/ingest-log.md. Use this skill any time you receive a meeting transcript or are asked to "log this meeting", "save this call", or "ingest this transcript". Supports three input modes: Fathom MCP (authenticate first), file path (.txt/.vtt), or direct paste.
---

# meeting-ingest

Ingests meeting transcripts into the vault.

## Input Modes

### Mode 1: Fathom MCP
If user says "pull from Fathom" or gives a Fathom meeting ID/URL:
1. Use `mcp__claude_ai_Fathom__authenticate` if not authenticated
2. Pull the meeting transcript
3. Proceed to processing

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
tags: [type/meeting, meeting-type/{type}]
status: mature
related: []
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

### Step 6: Create task entries for action items

For EACH action item where Gaston is the owner, create a task file:

File: `wiki/tasks/YYYY-MM-DD-{task-slug}.md`

```markdown
---
type: task
title: "{Task Description}"
created: YYYY-MM-DD
updated: YYYY-MM-DD
priority: high|medium|low
deadline: YYYY-MM-DD
status: open
from-meeting: "[[wiki/meetings/YYYY-MM-DD-topic]]"
tags: [type/task, status/open, priority/{level}]
related: []
sources: []
---

# {Task Description}

{Optional additional context from the meeting}
```

Then add to `wiki/tasks/_index.md` under the appropriate priority section.

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
