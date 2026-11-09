---
type: task
title: "Align Weekly/Monthly metric conventions to the Daily tab"
created: 2026-09-04
updated: 2026-10-19
priority: medium
status: open
from-meeting: "[[wiki/meetings/2026-09-04-weekly-check]]"
---

# Make Weekly and Monthly match the new Daily columns

The metrics newly added to the **Daily** tab don't exist in **Weekly** and **Monthly**, so the
auto-pull formulas can't reach them. Make the column/naming conventions match.

**Why:** the sheet is designed to cascade Daily → Weekly → Monthly with only Daily entered by hand.
Until the conventions line up, the automated rollups are broken and the stated goal of the metrics
rework — *"análisis más asertivos, más claros, más precisos"* — doesn't land. Scope is narrower than
"rewrite the formulas": it's naming alignment so the existing pull works.

**Bus-factor risk worth recording:** Daniel flagged that only Gaston touches these formulas —
*"la única persona que le mete mano a eso es Gasti... solamente es él o es la IA."*

**Timing:** No deadline stated. Gaston's only timing words were *"easy peasy."*

**Source:** [[wiki/meetings/2026-09-04-weekly-check]] · [Fathom @06:56](https://fathom.video/calls/810291115?timestamp=416)

---

## Update 2026-09-11

**Intended design confirmed** on the Sep 11 metrics walkthrough: everything builds from the **Daily
Update**, which is updated daily from Smartlead, and the **Weekly and Monthly tabs are meant to be
identical in layout**, differing only in period. That is the target state this task is aligning to.

**A live discrepancy surfaced:** weekly rows sum to **38 calls booked vs 46 for the month**. Gaston
diagnosed it as a **week-boundary artifact** — weeks straddle the August/September boundary — and
called it explainable rather than a bug. Worth confirming that fully accounts for the gap of 8.

**He did not commit to the naming alignment** this task covers, and did not reference the task. So it
remains open and unscheduled.

**Also noted, separately broken and deprioritised:** the **Placements** metric in Command Center
Import is mostly zeros — *"yo creo que esto se rompió"* — but explicitly not a priority
(*"los placements tanto no nos interesan"*). Don't fold it into this task.

**Source:** [[wiki/meetings/2026-09-11-outbound-metrics-follow-ups]] · [Fathom @48:30](https://fathom.video/calls/819051439?timestamp=2910)

---

## Update 2026-09-28

**Sep 28 status: ❌ not done.** It was on last week's priority list as "Reporting / operational cleanup — Cold Calling weekly/monthly formulas from raw data", which is wider than the naming-alignment scope here. The cold-calling tabs now need their rollups built from raw data too.

*From fathom-task-sync run 9 (Sep 14–25 meetings) + Gaston's Sep 28 status.*

## Update 2026-10-19

**Oct 16 ([@18:48](https://fathom.video/calls/863650212?timestamp=1128)):** keep the current structure (days in columns on Daily Raw Data). Weekly/Monthly build from Daily via date-matching IFs, and Gaston said they need little change. Per-campaign Weekly/Monthly follow once Paz's automated daily import exists.
*From fathom-task-sync run 12.*
