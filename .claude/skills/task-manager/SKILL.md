---
name: task-manager
description: >
  Manages tasks in the Near Work Partner vault. Handles creating tasks, listing open tasks, marking tasks as done, and weekly review. Use this skill when asked to "add a task", "what do I have due", "mark X as done", "show my tasks", "weekly review", or any task/to-do related request. Tasks live in wiki/tasks/ (open) and wiki/tasks/done/ (archived). Uses filesystem tools (per obsidian-wiki) to read and write the vault.
---

# task-manager

Task CRUD for the Near Work Partner vault.

## Task File Structure

**Location**: `wiki/tasks/YYYY-MM-DD-{task-slug}.md` (open)
**Archived**: `wiki/tasks/done/YYYY-MM-DD-{task-slug}.md` (completed)

```markdown
---
type: task
title: "{Task Title}"
created: YYYY-MM-DD
updated: YYYY-MM-DD
priority: high|medium|low
deadline: YYYY-MM-DD        # ONLY if explicitly stated — never guess (see below)
status: open|in-progress|done
completed: YYYY-MM-DD       # only when done
from-meeting: "[[wiki/meetings/...]]"   # if from a meeting
related: ["[[...]]"]        # OMIT the key entirely if empty
sources: ["[[...]]"]        # OMIT the key entirely if empty
---

# {Task Title}

{Why this matters — 1-3 lines. Enough that "what did I mean by this?" is answerable later.}
```

### Frontmatter rules (trimmed 2026-08-19)

**Do NOT write `tags:`** — it is redundant with `type` + `status` + `priority` and was removed
from every task file. Do not re-add it.

**Do NOT write empty `related: []` / `sources: []`** — omit the key entirely.

**Never invent a `deadline`.** Only set it when a date was stated outright. If the timing was
vague ("when you get a chance", "soon"), leave `deadline` out and record the phrasing in the
body instead:
```markdown
**Timing:** "when you get a chance" — no date given. Ask Gaston to confirm.
```
A guessed date looks authoritative and silently misleads. Ask instead.

**Quote budget: 2 lines max.** When quoting a meeting for context, cap it at two lines and link
to the Fathom timestamp for anything deeper. Never paste transcript blocks into a task.

### Size budget

Target **≤250 tokens per task file**. Task files are cold storage read on demand; `_index.md`
is the file actually loaded, so keep it to one line per task. A task needing more than ~250
tokens of explanation is probably a project — write a `wiki/` page and link to it.

---

## Operations

### CREATE a task

Trigger: "add task", "remind me to", "I need to", "create a task for"

1. Ask if not provided: title, deadline (optional), priority (default: medium), context
2. Create `wiki/tasks/YYYY-MM-DD-{slug}.md`
3. Add to `wiki/tasks/_index.md` under the correct **time-horizon** section (This Week / Next
   Week / Backlog) — see Index Format. Infer the horizon from the deadline, or from what Gaston
   said ("this week", "next week"); default to **Backlog** when there's no signal, and say which
   section you chose so he can move it.
4. Update `wiki/index.md` Tasks section
5. Update `wiki/hot.md`
6. Confirm: "Task created: [{title}] — due {date if set}"

Priority inference (for frontmatter — the index section is a *horizon*, see Index Format):
- "urgent", "ASAP", "today", "tomorrow" → high
- Has a near deadline (< 3 days) → high
- "whenever", "low priority", "no rush" → low
- Default → medium

### LIST open tasks

Trigger: "what are my tasks", "show tasks", "what's due", "my todo list"

1. Read `wiki/tasks/_index.md` (quick mode)
2. If more detail needed, read individual task files
3. Format output as table:

```
OPEN TASKS

THIS WEEK ({dates})
[ ] {Task} — due {date} — from: {meeting}
[ ] {Task} — blocks {person}

NEXT WEEK ({dates})
[ ] {Task} — due {date}

BACKLOG
[ ] {Task}
```

Mirror the index's own sections — don't re-sort into priority buckets. Surface **blockers on other
people** first within a section; those are the lines with a cost to sitting.

For "what's due this week": read the `## This Week` section, and also scan the other two for any
deadline ≤ today + 7 (a Backlog item can still have a near date — flag the mismatch).

### MARK DONE

Trigger: "done with X", "mark X as done", "completed X", "finished X"

1. Find the task (search vault if needed)
2. Update frontmatter: `status: done`, `completed: YYYY-MM-DD`
3. Move to `wiki/tasks/done/` using `mv` (Bash)
4. Remove from `wiki/tasks/_index.md`
5. Update `wiki/index.md` (move to Tasks Done section)
6. Update `wiki/hot.md`
7. Confirm: "Marked done: [{title}]"

### WEEKLY REVIEW

Trigger: "weekly review", "what's coming up", "this week's tasks"

1. Read `wiki/tasks/_index.md`
2. Read all task files that are overdue or due within 7 days
3. **Roll the horizons forward** — last week's `## This Week` items that are still open either
   stay (with the heading re-dated) or drop to Next Week/Backlog; promote from Next Week. Ask
   Gaston before moving anything he flagged as committed.
4. Report:
   - **Overdue** (deadline < today)
   - **This Week** — what's carried vs. newly promoted
   - **Blocking someone else** — call these out regardless of section
   - Count in Next Week / Backlog

Format:
```
WEEKLY REVIEW — {date}

OVERDUE ({N})
[ ] {Task} — was due {date}

THIS WEEK ({N}) — {dates}
[ ] {Task} — due {date} | carried {N} weeks
[ ] {Task} — **blocks {person}**

NEXT WEEK ({N}) · BACKLOG ({N})
```

If This Week holds more than ~10 items, say so — an overloaded week is the signal to use
`priority:` from frontmatter and recommend what to push.

### EXPLAIN a task ("what did I mean by this?")

Trigger: "what was X about", "I don't remember what X meant", "give me context on X",
"why did I need to do X"

Progressive disclosure — stop as soon as the question is answered:
1. Read `wiki/tasks/_index.md` to locate the task.
2. Read the task file (~250 tok). Its body + `from-meeting` usually suffice.
3. Still unclear → read the linked meeting note's TLDR / Decisions (Tier 2).
4. Still unclear → fetch the transcript **live** from Fathom (Tier 3, 0 stored tokens):
   `mcp__claude_ai_Fathom__get_meeting_transcript(recording_id, url)` using `recording_id`
   from the meeting note's frontmatter. Never save the transcript into the vault.

Report: what the task is, why it exists, who asked, what "done" looks like, and the Fathom
deep link if a timestamp is relevant. If the task body lacks the *why*, say so and offer to
enrich it — a task you had to reconstruct should be improved so the next lookup is cheap.

### UPDATE a task

Trigger: "change deadline for X", "update priority", "add note to task"

1. Find the task
2. Edit frontmatter or append note section
3. Update `wiki/tasks/_index.md` if the priority **or the time horizon** changed (moving a task
   between This Week / Next Week / Backlog is an index edit, not a frontmatter one)
4. Update `wiki/hot.md` if significant change

---

## Index Format (`wiki/tasks/_index.md`)

**The sections are time horizons, not priorities** (restructured 2026-08-19 at Gaston's request).
The old `## High Priority` / `## Medium Priority` / `## Low Priority` split stopped carrying
information once the backlog was cleared — almost everything left was live work with a week
attached. **Do not reintroduce it.**

```markdown
## This Week (Aug 19–23)
- [[tasks/2026-06-05-follow-up-acme]] — Follow up Acme Corp | due: 2026-06-05 | **blocks Ivan**

## Next Week (Aug 24–30)
- [[tasks/2026-06-10-review-deck]] — Review Q3 deck | due: 2026-06-10

## Backlog
- [[tasks/2026-06-20-update-templates]] — Update email templates | no deadline
```

Each line: `[[link]] — {title} | due: {date} | from: {meeting if applicable}`

Rules:
- Put the **actual dates** in the two week headings (`## This Week (Aug 19–23)`) so a stale index
  is obvious on sight. Roll them forward during weekly review — never leave last week's dates.
- **Backlog is for work with no week assigned yet**, not a graveyard. An item carried there for
  more than a month is a triage prompt: raise it with Gaston rather than letting it sit.
- Group within a section by theme when a section runs long (e.g. `**Deliverability**`) — bold
  inline labels, not extra `##` headings.
- `priority:` stays in each task's **frontmatter**. The index answers *when*; priority answers
  *what to drop first* when a week is overloaded. Both are load-bearing — keep them in sync.
