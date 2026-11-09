---
type: task
title: "MoltSets coverage test on older data (no-company / no-email leads)"
created: 2026-10-23
updated: 2026-10-27
priority: medium
status: done
completed: 2026-10-27
from-meeting: "[[wiki/meetings/2026-10-19-marketing-stand-up]]"
sources: ["[[bibliography/2026-10-19 - Marketing Stand Up - Meeting]]"]
related: ["[[wiki/tools/moltsets]]", "[[wiki/tasks/2026-10-23-hirebase-net-new-readout-to-andres]]"]
---

# MoltSets coverage test

Run MoltSets (free tier) on older data where Clay, AI and Apollo found no person at a company or no email for a lead. Measure how much coverage it adds.

**Done =** coverage gain measured (people found + valid emails found on previously-failed rows) and recorded in [[wiki/tools/moltsets]].
**Ownership:** Gaston, on his week's plan: *"the idea would be to test on previous data... if in older data where we were unable to get leads from a company or get emails from specific leads, if MoltSets can actually come and cover some of that and increase our coverage"* [Fathom @12:48](https://fathom.video/calls/865018408?timestamp=768)
**Timing:** "this week" (week of Oct 19), no date.
**Test plan already written (Oct 23):** US first. `search_people` with `limit: 1` on companies with no one found, then remaining tokens on `linkedin_to_business_email`. Only A/B counts as valid. Free plan = 1k tokens, 100 search results. See [[wiki/tools/moltsets]].

*From fathom-task-sync run 13.*

## Closed 2026-10-27

Gaston confirmed done (Oct 27 weekly check-in).
