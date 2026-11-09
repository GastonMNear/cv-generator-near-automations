# WIKI.md — Schema Reference

Read this before any vault operation. It defines structure, frontmatter, naming, and conventions.

---

## Vault Layers

### Layer 1: `bibliography/`
Source registry — metadata only, never raw content.

One file per source. Naming: `YYYY-MM-DD - {Author or Topic} - {Short Title}.md`

Required frontmatter:
```yaml
---
type: bibliography
source_type: meeting|article|video|transcript|other
title: "Full Title"
author: ""
date: YYYY-MM-DD
date_ingested: YYYY-MM-DD
url: ""              # if applicable
topics: ["[[Wiki Page]]"]
wiki_pages: ["[[Page Created]]", "[[Page Updated]]"]
---
```
Body: 2-3 sentence summary of what this source contributed.

### Layer 2: `wiki/`
Synthesized knowledge. One concept per page. Atomic notes.

Subfolders:
- `meetings/` — Processed meeting notes with TLDRs (transcripts live in Fathom, never here)
- `tasks/` — **Live working set only.** One actionable task per file. `tasks/done/` holds
  archived completed tasks (never indexed, never read unless asked about finished work).
  Weekly/periodic roll-ups are **not** tasks → `logs/weekly-trackers/`.
- `ai-learnings/` — AI insight pages + improvement backlog
- `context/` — HireWithNear company context, Gaston's role, outreach playbook
- `tools/` — Tool references (Clay, Smartlead, Fathom, etc.)
- `outbound/` — Living outbound performance state. `campaign-insights.md` is **rewritten** each
  Monday by `outbound-campaign-review` (standing, watchlist, campaign change log); history goes
  to `logs/campaign-reviews/`.

Special files (always keep current):
- `hot.md` — ~500-word recent context cache. Completely overwritten after each ingest.
- `index.md` — Master catalog. One line per page, newest at top within sections.

### Layer 3: `logs/`
Append-only activity record. New entries at TOP.

- `ingest-log.md` — Every ingest/creation session
- `session-log.md` — Notable session events, decisions
- `campaign-reviews/` — One immutable snapshot per Monday campaign review (`YYYY-MM-DD.md`,
  the reporting week's Monday). Read only for trend/history questions.
- `weekly-trackers/` — Archived weekly task snapshots (`type: tracker`). History, not live
  state — see that folder's `README.md`. Never use these to answer "what's pending".

---

## Frontmatter Schemas

### All pages must have:
```yaml
---
type: meeting|task|learning|context|source|tool|meta
title: "Human-Readable Title"
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [type/meeting, status/open]
status: open|done|seed|developing|mature
related: ["[[Other Page]]"]
sources: ["[[bibliography/filename]]"]
---
```

### Meeting pages additionally:
```yaml
attendees: ["Name — Role", "Name — Role"]
meeting-type: internal|client|candidate|vendor
duration-min: 30
```

### Task pages additionally:
```yaml
priority: high|medium|low
deadline: YYYY-MM-DD      # ONLY if explicitly stated. Never guess — see below.
completed: YYYY-MM-DD     # only when done
from-meeting: "[[meeting note]]"
```

**Task frontmatter is deliberately minimal (trimmed 2026-08-19).** Do not re-add:
- `tags:` — redundant; derivable from `type` + `status` + `priority`.
- `related: []` / `sources: []` — omit the key entirely when empty, don't write an empty list.

**Deadlines must never be invented.** If a due date was not stated outright, leave `deadline`
out of the frontmatter and put the timing language in the body (`Timing: "when you get a
chance" — no date given`). A guessed date in `deadline:` looks authoritative and silently
misleads. Surface the uncertainty to Gaston and ask instead.

### Meeting pages additionally (Fathom):
```yaml
recording_id: 123456789    # REQUIRED for Fathom-sourced meetings
fathom-url: "https://fathom.video/calls/..."
```
`recording_id` is what the Fathom MCP needs to fetch a transcript on demand
(`get_meeting_transcript`). Without it, retrieving the transcript costs an extra
`list_meetings` search. **Note:** the number in a Fathom `/calls/<n>` URL is NOT the
`recording_id` — they are different values, so store both.

### Learning pages additionally:
```yaml
category: prompting|tools|architecture|integrations|workflow
actionable: true|false
```

---

## Context Budget & Reading Order

The vault is **cold storage read on demand**, not context that loads every session. Only
`CLAUDE.md` is auto-injected. Everything else must be *deliberately* opened, cheapest first:

| Tier | File | Budget | Read when |
|---|---|---|---|
| 0 | `wiki/hot.md` | ≤600 tok | Start of any vault question |
| 1 | `wiki/index.md`, `wiki/*/_index.md` | ≤2,000 / ≤1,000 tok | Deciding *which* page matters |
| 2 | One specific page | ≤800 tok/meeting, ≤250 tok/task | That page is relevant |
| 3 | Fathom transcript (MCP, live) | **0 tok stored** | Verbatim wording needed |

**Rules**
- **Never store transcripts in the vault.** Store `recording_id` + `fathom-url` and fetch
  live via `mcp__claude_ai_Fathom__get_meeting_transcript`. A 45-min meeting is ~8–10k
  tokens of low-density filler; the note's TLDR replaces it.
- **Quote budget: max 2 lines** of verbatim transcript per task/meeting section. For anything
  deeper, link to the Fathom timestamp — don't copy.
- **Never read `wiki/tasks/done/`** unless asked about completed work.
- **Never read `logs/weekly-trackers/`** to answer "what's pending" — use `wiki/tasks/_index.md`.
- **`wiki/tasks/_index.md` is grouped by time horizon** — `## This Week (<dates>)` · `## Next Week
  (<dates>)` · `## Backlog` — **not** by High/Medium/Low priority (changed 2026-08-19 at Gaston's
  request; the priority split stopped carrying information once the backlog was cleared). `priority:`
  remains in task frontmatter for deciding what to drop when a week is overloaded. Authoritative
  rules: `task-manager` skill → Index Format.
- **Index lines must be decision-grade** — specific enough to answer or to justify opening the
  page. `"discussed deadlines"` is useless; `"4 deliverables due Jul 24; Clay credits → Aug 1"`
  is not.

---

## Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Meeting notes | `YYYY-MM-DD-topic-keywords.md` | `2026-06-03-weekly-team-sync.md` |
| Task files | `YYYY-MM-DD-task-description.md` | `2026-06-05-follow-up-acme-corp.md` |
| Learning pages | `YYYY-MM-DD-{title-slug}.md` | `2026-06-03-agentic-loops-best-practices.md` |
| Context pages | Descriptive title | `company.md`, `outreach-playbook.md` |
| Bibliography | `YYYY-MM-DD - Author - Title.md` | `2026-06-03 - Fathom - Weekly Sync.md` |

All filenames: lowercase, hyphens, no spaces.

---

## Obsidian Markdown Standard

| Element | Syntax |
|---------|--------|
| Wikilink | `[[Page Name]]` — always, never markdown links |
| Wikilink with alias | `[[Page Name\|Display Text]]` |
| Tag | `#type/meeting`, `#status/open` (hierarchical) |
| Callout | `> [!note]`, `> [!contradiction]`, `> [!action]` |
| Frontmatter links | Must be quoted: `"[[Page Name]}"` |
| Tags in frontmatter | List form: `- type/meeting` |
| Dates | `YYYY-MM-DD` only |

---

## Hot Cache Format (`wiki/hot.md`)

Completely overwritten after every ingest. Never appended.

```markdown
---
type: meta
title: Hot Cache
updated: YYYY-MM-DDTHH:MM:SS
---

# Recent Context

## Last Updated
[Date] — [What happened: meeting ingested, task created, article learned]

## Key Recent Facts
- [Most important thing to know right now]
- [Second most important]

## Recent Changes
- Created: [[New Page 1]], [[New Page 2]]
- Updated: [[Existing Page]] (added X)
- Tasks created: [[Task 1]], [[Task 2]]

## Open Threads
- [Unresolved items, follow-ups in flight]
```

---

## Index Format (`wiki/index.md`)

One line per page. Read before reading full pages.

```markdown
## Meetings
- [[2026-06-03-weekly-sync]] — Weekly team sync, 2026-06-03. Tasks: follow up on X, review Y.

## Tasks (Open)
- [[2026-06-05-follow-up-acme]] — Follow up Acme Corp | deadline: 2026-06-05 | this week

## AI Learnings
- [[2026-06-03-agentic-loops]] — Best practices for agentic loops. Actionable: update meeting-ingest skill.

## Context
- [[context/company]] — HireWithNear overview, ICP, business model
- [[context/my-role]] — Gaston's responsibilities, KPIs, daily workflow
- [[context/outreach-playbook]] — Outreach sequences, messaging, templates
```

---

## Ingest Log Format (`logs/ingest-log.md`)

New entries at TOP. Append-only — never edit past entries.

```markdown
## YYYY-MM-DD | [type] | [Short Description]
- Source: [[bibliography/filename]]
- Pages created: [[Page 1]], [[Page 2]]
- Pages updated: [[Page 3]]
- Tasks created: [[Task 1]]
- Key insight: One sentence on what is new.
```
