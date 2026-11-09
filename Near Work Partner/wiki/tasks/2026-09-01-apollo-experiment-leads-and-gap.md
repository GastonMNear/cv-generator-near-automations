---
type: task
title: "Top up the Apollo experiment to 3,600 leads and diagnose the No-HM performance gap"
created: 2026-09-01
updated: 2026-10-19
priority: medium
status: open
from-meeting: "[[wiki/meetings/2026-09-01-leadership-deck-build]]"
related: ["[[wiki/tasks/2026-08-26-automate-experiment-lead-adds]]", "[[wiki/tasks/2026-08-27-launch-no-hm-motion-segment-copy]]"]
sources: ["[[bibliography/2026-09-01 - Leadership Deck Build - Meeting]]"]
---

# Fill the Apollo sample, then explain 0.22 vs 1.3

Add leads to the Apollo-sourced No-HM experiment until it reaches the **3,600-lead** sample the other
experiments are being pushed to — one experiment currently sits at **117 of 3,600**. Then investigate
why **Apollo's No-HM performance is 0.22 against 1.3 for hiring managers**, far below the No-HM
benchmark.

**Why:** Experiments are held to a 3,600-lead sample before conclusions are drawn, so Apollo cannot
be judged yet — but it's badly underperforming and **nobody knows why**. The sample has to be filled
before the gap can be diagnosed, and until then it drags the experiment slide without explanation.

**Done =** Apollo at ~3,600 leads, plus a stated cause (or ruled-out list) for the 0.22.

**Timing:** No date. Stated flatly as *"Tengo que sumar más leads a Apolo"*. **Needs a date from Gaston.**

> Gaston: "Tengo que sumar más leads a Apolo." — Daniel: "Ahora, Apolo está súper por debajo del
> benchmark de no hiring manager. Está a 0.22 y hiring manager está a 1.3."

**Connection worth making:** this is the second time this window that experiment leads had to be added
by hand. [[wiki/tasks/2026-08-26-automate-experiment-lead-adds]] exists precisely to stop that, and
doing the automation first would cover this top-up too.

**Source:** [[wiki/meetings/2026-09-01-leadership-deck-build]] · [Fathom @12:53](https://fathom.video/calls/806758340?timestamp=773)

## Update 2026-09-04 — the gap has a leading diagnosis: lead staleness
The "explain 0.22 vs 1.3" half of this task got a real answer in
[[wiki/meetings/2026-09-04-new-oj-sources-triggers]], and the number moved: Daniel now states Apollo
is underperforming the No-HM baseline by **~88%**.

**Daniel's diagnosis: the Apollo opportunities are 2–3 weeks stale.** Low acceptance is likely a
**lead-freshness artifact, not a message failure** — which makes the daily-pull build
([[wiki/tasks/2026-09-04-build-daily-apollo-clay-agent]]) the actual fix for this gap, not a separate
initiative.

**Gaston's "unfair comparison" defence was raised and refuted.** The argument was that Apollo leads
haven't completed the full sequence. Daniel pre-empted it: **over 80% of booked calls come from email
1**, so an incomplete sequence cannot explain the gap. Gaston did not carry the point.

**A real constraint this task should record:** Apollo's plan permits exporting companies but **not
reading their job postings**, and there are **no API credits** — *"our plan is too small."* Gaston
raised upgrading the plan as the clean fix; Daniel said **"probably"** and never decided, pivoting to
the underperformance argument against spending more on Apollo. **That decision is still open and it
gates how cleanly the daily pull can be built.**

**Note on the 3,600-lead top-up:** untouched in these meetings. Still pending.

**Source:** [[wiki/meetings/2026-09-04-new-oj-sources-triggers]] · [Fathom @26:38](https://fathom.video/calls/810291056?timestamp=1598) and [@27:46](https://fathom.video/calls/810291056?timestamp=1666)

## Update 2026-10-19

**Oct 13 huddle:** Apollo is running at ~1 booked call/wk on ~4k emails/wk. That's *"not on par with the baseline"* but good enough to justify testing new sources (it's the cited precedent for HireBase). Volume may fall because not all companies are new.
*From fathom-task-sync run 12.*
