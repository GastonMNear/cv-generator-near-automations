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
deadline: YYYY-MM-DD        # required if known
status: open|in-progress|done
completed: YYYY-MM-DD       # only when done
from-meeting: "[[wiki/meetings/...]]"   # if from a meeting
tags: [type/task, status/open, priority/high]
related: []
sources: []
---

# {Task Title}

{Optional context: why this task matters, links, notes}
```

---

## Operations

### CREATE a task

Trigger: "add task", "remind me to", "I need to", "create a task for"

1. Ask if not provided: title, deadline (optional), priority (default: medium), context
2. Create `wiki/tasks/YYYY-MM-DD-{slug}.md`
3. Add to `wiki/tasks/_index.md` under the correct priority section
4. Update `wiki/index.md` Tasks section
5. Update `wiki/hot.md`
6. Confirm: "Task created: [{title}] — due {date if set}"

Priority inference:
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

HIGH PRIORITY
[ ] {Task} — due {date} — from: {meeting}
[ ] {Task} — due {date}

MEDIUM PRIORITY
[ ] {Task} — due {date}

LOW PRIORITY
[ ] {Task}
```

For weekly review or "what's due this week": filter to deadline ≤ today + 7 days, plus overdue.

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
3. Report:
   - **Overdue** tasks (deadline < today)
   - **Due this week** (deadline ≤ today + 7)
   - **High priority** tasks (regardless of deadline)
   - Count of remaining medium/low tasks

Format:
```
WEEKLY REVIEW — {date}

OVERDUE ({N})
[ ] {Task} — was due {date}

DUE THIS WEEK ({N})
[ ] {Task} — due {date}

HIGH PRIORITY ({N})
[ ] {Task} — due {date or "no deadline"}

OTHER: {N} medium, {N} low priority tasks open
```

### UPDATE a task

Trigger: "change deadline for X", "update priority", "add note to task"

1. Find the task
2. Edit frontmatter or append note section
3. Update `wiki/tasks/_index.md` if priority changed
4. Update `wiki/hot.md` if significant change

---

## Index Format (`wiki/tasks/_index.md`)

```markdown
## High Priority
- [[tasks/2026-06-05-follow-up-acme]] — Follow up Acme Corp | due: 2026-06-05

## Medium Priority  
- [[tasks/2026-06-10-review-deck]] — Review Q3 deck | due: 2026-06-10

## Low Priority
- [[tasks/2026-06-20-update-templates]] — Update email templates | no deadline
```

Each line: `[[link]] — {title} | due: {date} | from: {meeting if applicable}`
