---
type: task
title: "Build the daily Apollo→Clay agent for newly-posted jobs"
created: 2026-09-04
updated: 2026-10-13
priority: high
status: open
from-meeting: "[[wiki/meetings/2026-09-04-new-oj-sources-triggers]]"
related: ["[[wiki/tasks/2026-09-01-apollo-experiment-leads-and-gap]]", "[[wiki/tasks/2026-09-04-no-new-sources-convert-existing-universe]]"]
---

# Automate the daily Apollo pull of companies that just posted jobs

Replace the manual Apollo-UI → CSV → Clay import with a daily automated pull of companies that
**posted** a job in the last 1–2 days (posted, not "active openings" — Daniel corrected this twice).

**Why:** the live test in the meeting validated the strategy well past expectations — 5.2k companies
posted in 2 days → 2,500 exported → **2,000 net-new after dedupe** → **~25% with a valid open job**
(Gaston predicted 2%, Daniel 30%). Forecast ~2,000–2,500/day, **~3,000 qualified opportunities/week**.
It also fixes the 2–3 week lead staleness that is the leading explanation for Apollo's ~88%
underperformance ([[wiki/tasks/2026-09-01-apollo-experiment-leads-and-gap]]).

**Mechanics to build:**
- **Adaptive backfill, not a fixed 2×2,500/day.** 2,500 is the **per-export** cap, not a daily ceiling.
  Expect ~2,000/day, so one export usually suffices; walk back to the previous day to top up, and use
  a second export only as the overflow valve for heavy days.
- **Dedupe, two layers:** company-level against the existing LinkedIn open-jobs universe (the
  2,500→2,000 step, ~20% overlap); and skip person-level enrichment for already-enriched companies —
  but **a returning company with a NEW job post is still a valid opportunity.**
- **Exclude remote roles, keep US-specific**, filtered in Clay at job-description level.

**⚠️ The blocker is the Apollo→Clay hop itself and it is unsolved.** Gaston: *"I would need to find a
way, like some sort of routine or agent... to go into Apollo, find the lead automatically, and then
send them to Clay, which I am not sure how we would do, to be honest."* He floated a 10-minute daily
manual fallback and **Daniel rejected it outright — "manually no."** Daniel offered faith rather than a
mechanism (*"we all know that we're going to find a solution"*).

**Constraint that may force the answer:** Apollo's plan allows exporting companies but **not** reading
job postings, and there are **no API credits** — *"our plan is too small."* Upgrading was raised,
answered *"probably"*, and never decided.

**Timing:** No deadline stated. Daniel deferred sequencing — *"we're going to align priorities next
week"* — and separately said *"we can start doing that on Monday with the new person"*, which refers to
**Lila starting on the manual version**, not this build. Gaston's own caveat: *"the only thing is that
it's going to take your time."*

**Watch for:** Gaston expects the ~25% match rate to **decay** under daily cadence as repeat companies
accumulate. The validating batch was still running when the call ended.

**Source:** [[wiki/meetings/2026-09-04-new-oj-sources-triggers]] · [Fathom @55:34](https://fathom.video/calls/810291056?timestamp=3334)

## Update 2026-10-13

**Oct 9 (Alexia sync):** Apollo Open Jobs 200–500 is now always-on. Daily manual run (~2 min): update the posting date on the saved search (last 3–4 days) → Net New → export → CSV by email → Import from CSV into the Apollo Companies table → save and run (~500–900 companies/day). Gaston called it an easy automation candidate, **possibly for Alexia**.
