---
type: task
title: "Verify whether Apollo daily scraping is actually running; activate if not"
created: 2026-09-04
updated: 2026-09-11
priority: high
status: done
from-meeting: "[[wiki/meetings/2026-09-04-weekly-check]]"
related: ["[[wiki/tasks/2026-09-04-build-daily-apollo-clay-agent]]"]
---

# Is the Apollo daily scrape live, or not?

Confirm whether the daily open-jobs scrape from Apollo is running. If not, activate it.

**Why:** everything in the Apollo projection presented at the weekly check — ~500–600 opportunities/day,
~12,000/month, **~5 calls booked/month** — is gated on this being live. Nothing downstream can be
measured until it runs. Asked directly in the meeting, the answer was *"no, no, tengo que ver."*

**⚠️ Ownership is unconfirmed.** The *"tengo que ver"* sits in a transcript block labelled **Daniel**,
while Fathom's summary assigned this to Gaston. Diarization had clearly drifted by that point. Content
suggests it's Gaston's lane (Clay/Apollo automation) even if Daniel owes the status answer —
**confirm with Daniel rather than assuming.**

**Relationship to the build task:** this is the *status check* on whatever exists today.
[[wiki/tasks/2026-09-04-build-daily-apollo-clay-agent]] is the *automation* of the Apollo→Clay hop,
which is still unsolved. If nothing is running at all, these collapse into one piece of work.

**Caveat on the projection:** every number came from a 2-day sample and Daniel hedged hard —
*"puede cambiar, quiero ser súper claro en esto"* — closing with *"ahora hay que hacerlo funcionar. Esa
es la parte difícil."*

**Timing:** No deadline stated.

**Source:** [[wiki/meetings/2026-09-04-weekly-check]] · [Fathom @21:26](https://fathom.video/calls/810291115?timestamp=1286)

---

## Completed 2026-09-11

**Verified and running — manually.** Gaston is running the Apollo daily scrape by hand this week as a stopgap until the automation exists. The projection this task gated (~500–600 opps/day, ~12,000/month) now has live input.

**Note:** the manual run is deliberately temporary. [[wiki/tasks/2026-09-04-build-daily-apollo-clay-agent]] stays open and is now the load-bearing item — every day it is unbuilt is a day of manual work.

*Reported done by Gaston, 2026-09-11 status sweep.*
