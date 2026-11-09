---
type: task
title: "Load hiring managers + No-HM CEOs <50 into JustCall, then confirm to Ivan"
created: 2026-08-19
updated: 2026-08-24
priority: high
status: done
from-meeting: "[[wiki/meetings/2026-08-19-weekly-metrics-optimization]]"
related: ["[[wiki/tasks/2026-08-19-swap-predictive-justcall-lists]]", "[[wiki/tasks/2026-08-19-archive-old-justcall-campaigns]]"]
sources: ["[[bibliography/2026-08-19 - Weekly Metrics & Optimization - Meeting]]"]
---

# Load cold-call lists into JustCall

Two segments, one list each: **all hiring managers** (with *and* without email, ~396–400/week) and
**No-Hiring-Manager CEOs at companies under 50 employees** as the volume backstop. Then confirm to
Ivan that the leads are up.

**Why:** Daniel named this the week's priority and made ownership explicit — Ivan now owns JustCall
configuration, Gaston owns getting leads in. **Ivan is blocked until the confirmation lands:** he
can't set up his 20-attempts-over-two-weeks cadence without leads. The old email-found vs
no-email-found split is retired; priority now comes from hiring role and title. The hiring-managers
workflow already exists, so Gaston expected this to be quick. Done = both lists loaded and Ivan told.

**Timing:** "Esa es la prioridad de esta semana" — this week, no specific day given.

> "Eso sí lo tiene que hacer Gasti. Gasti sí tiene que subirte los leads allá. Él es el encargado
> de que te aparezcan allá."

**Source:** [[wiki/meetings/2026-08-19-weekly-metrics-optimization]] · [Fathom @28:00](https://fathom.video/calls/787480435?timestamp=1680)

## Update 2026-08-21 — half done, two lists still missing

Gaston confirmed he had not finished this: **two of the four lists do not exist yet** — the
no-hiring-managers list (to be narrowed to C-levels/founders at companies under 50) and the
"interested replies that then ghosted us" list.

**The ghosted list is structurally blocked**, not just pending: a lead already uploaded to one
JustCall campaign cannot be uploaded to another, and those leads already sit in the U.S. Open Jobs
Hiring Managers campaign. See [[wiki/tasks/2026-08-21-justcall-api-move-reset-leads]].

Two other changes: parallel dialing now runs on the **full** hiring-managers list rather than only
HMs who finished the email sequence and came back (Gaston offered to revert if the dialer problem
persists). And the open question about waiting out the 7-email sequence is **settled** — cold-call
lists get fresh leads immediately on upload to email. Daniel: "Let's try to work with fresh leads,
please."

Ivan says he cannot hit the 2,000-dial mark until the missing lists land and the parallel-dialer bug
is fixed.

> "Well, because I didn't get to do them yet, basically. But we are missing... We're missing two
> lists, which is... No Hiring Managers and the other one... People who ghosted us."

**Source:** [[wiki/meetings/2026-08-21-weekly-check]] · [Fathom @27:07](https://fathom.video/calls/792826882?timestamp=1627) · fresh leads [@30:04](https://fathom.video/calls/792826882?timestamp=1804)

## Update 2026-08-24 — done
List cleanup finished, the new list uploaded, and parallel-dialing slots in use. Ivan is unblocked.

**Residual work moved out, not dropped:** the "interested HMs who ghosted us in email" list is still
structurally blocked — a lead already in one JustCall campaign cannot be uploaded to another. That
lives in [[wiki/tasks/2026-08-21-justcall-api-move-reset-leads]].
