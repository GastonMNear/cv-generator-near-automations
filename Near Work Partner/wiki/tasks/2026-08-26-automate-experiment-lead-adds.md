---
type: task
title: "Automate weekly lead adding for low-volume experiment campaigns"
created: 2026-08-26
updated: 2026-09-01
priority: medium
status: open
from-meeting: "[[wiki/meetings/2026-08-21-weekly-check]]"
related: ["[[wiki/tasks/2026-08-24-justcall-metrics-via-api]]"]
sources: ["[[bibliography/2026-08-21 - Weekly Check - Meeting]]"]
---

# Automate the weekly experiment lead adds

Replace the manual weekly batch of leads into low-volume experiment campaigns (EXP009 and the like)
with an automated add.

**Why:** Daniel's words were "I strongly recommend, strongly suggest to automate the leads adding" —
he explicitly ruled out Gaston spending Monday time hand-adding leads to a low-volume campaign. The
EXP009 copy rework and lead add are now done ([[wiki/tasks/2026-08-19-experiment-9-inbox-switch-and-copy]]),
but they were done **by hand**, so the recurring cost Daniel objected to is still there and will
resurface next week.

**Done =** experiment campaigns receive their weekly leads without Gaston touching them.

> "I strongly recommend, strongly suggest to automate the leads adding"

## Update 2026-09-01 — the manual cost recurred, exactly as predicted
Two fresh instances of the work this task exists to eliminate:

- **Apollo needs a hand top-up** toward the 3,600-lead sample (currently 117 of 3,600) →
  [[wiki/tasks/2026-09-01-apollo-experiment-leads-and-gap]]. Doing this automation first would cover
  that top-up rather than repeating it.
- **The JustCall cold-calling lists have the same problem** on a different system →
  [[wiki/tasks/2026-08-31-daily-clay-sync-coldcall-lists]]. Daniel's framing there was blunter:
  after Aug 31, nobody should have to chase Gaston for a list again. **Manual uploads were the root
  cause of the No-HM list sitting unloaded while Ivan ran dry.**

These stay separate tasks — Smartlead experiment campaigns vs JustCall calling lists are different
destinations — but they likely **share a Clay pattern**, so whichever is built first should make the
other cheaper. Daniel's original objection ("I strongly recommend... automate the leads adding") has
now cost time three weeks running.

**Source:** [[wiki/meetings/2026-09-01-leadership-deck-build]] · [[wiki/meetings/2026-08-31-cold-calling-lists]]
