---
type: task
title: "Rebuild the co-workers campaign Clay workflow to point at current experiment tables"
created: 2026-08-13
updated: 2026-08-26
priority: high
status: done
from-meeting: "[[wiki/meetings/2026-08-13-deliverability-root-cause]]"
related: ["[[wiki/tools/clay]]"]
sources: ["[[bibliography/2026-08-13 - Deliverability Root Cause - Meeting]]", "[[bibliography/2026-08-19 - Weekly Metrics & Optimization - Meeting]]"]
---

# Fix the co-workers campaign Clay workflow

Update the co-workers campaign's Clay lookup to query the **current per-experiment tables** instead
of the tables that existed when it was first configured, then re-enable lead addition.

**Why:** The campaign (fall back to a hiring manager's colleagues when the HM doesn't reply) is
technically active but has effectively stopped adding leads — volumes fell to ~51/143/405 and then
near zero. Diagnosis: after the experiment churn (workflow 5 → 6 → 8) the lookup was never
repointed, so no leads are found. Raised Aug 13 and again Aug 19, so it has now survived two
meetings unfixed. Daniel asked for it to be run internally and **kept out of reports**.
Done = workflow repointed and leads loading again.

> "Entonces lo que tengo que hacer es actualizar ese workflow para buscar en las tablas nuevas que
> tenemos creadas ahora con los experimentos."

**Source:** [[wiki/meetings/2026-08-13-deliverability-root-cause]] · [Fathom @41:37](https://fathom.video/calls/784480827?timestamp=2497)
· restated [[wiki/meetings/2026-08-19-weekly-metrics-optimization]] · [Fathom @59:03](https://fathom.video/calls/787480435?timestamp=3543)

## Update 2026-08-21 — third mention, and a better fix

Gaston named this as the one thing he had to finish **that day** (Aug 21). Raised now in three
consecutive meetings (Aug 13, Aug 19, Aug 21).

**The approach changed.** Swapping in the current experiment tables is only the quick fix — it will
re-break every time a new experiment table is created. The intended fix is to **re-point the
hiring-manager email lookup at BigQuery** instead of Clay tables, so experiment churn stops
breaking it. If that works, the same pattern should extend to **all the open-jobs campaigns** (no
one committed to that extension, so it is not a separate task yet).

BigQuery is working again as of this call, so the BigQuery route is actually available.

> "The only thing that I want to... One I have pending that I need to finish today is fixing the
> co-workers campaign"

**Source:** [[wiki/meetings/2026-08-21-weekly-check]] · [Fathom @42:00](https://fathom.video/calls/792826882?timestamp=2520) · BigQuery route [@46:00](https://fathom.video/calls/792826882?timestamp=2760)

## Update 2026-08-25 — ranked priority 3, and the strategic case for it

Daniel ranked this **3 of 5** and wants to push on it this week.

**Why it matters more than a maintenance fix.** Daniel's own words: *"nosotros la cagamos dejando
caer la campaña Coworkers."* Since nobody knows who the hiring manager is in No-HM — only ~1.4 people
are reached per company — **routing is the strategy**, and co-workers is the routing mechanism that
already exists. Letting it lapse cost the segment its best lever.

It also has an advantage the new No-HM routing copy lacks: co-workers only fires **after** the hiring
manager was emailed and didn't reply, so the ask is earned rather than cold. See
[[wiki/tasks/2026-08-24-review-conversion-improvement-strategy]].

## Update 2026-08-26 — done
Fixed. Closes **priority 3 of 5**, after being raised in four consecutive meetings (Aug 13, 19, 21,
and the Aug 24 huddle where Daniel called letting it lapse a mistake).

This matters beyond the fix itself: routing *is* the No-HM strategy, and co-workers is the routing
mechanism that already existed. With it live again, the segment has its best lever back.

**Not committed, still open:** extending the BigQuery lookup pattern to **all open-jobs campaigns**
so experiment churn stops breaking them. Floated Aug 21, nobody took it. Remains in the backlog.
