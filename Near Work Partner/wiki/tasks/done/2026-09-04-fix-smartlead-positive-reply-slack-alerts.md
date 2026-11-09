---
type: task
title: "Fix the broken Smartlead positive-reply Slack notification"
created: 2026-09-04
updated: 2026-09-11
priority: high
status: done
from-meeting: "[[wiki/meetings/2026-09-04-weekly-check]]"
related: ["[[wiki/tasks/2026-09-01-rb2b-integration-monitoring]]"]
---

# The positive-reply Slack alert stopped firing and nobody noticed

The automation that posts to Slack and tags the reply-handler when a new **positive reply** lands in
Smartlead has stopped delivering. Restore it.

**Why:** whoever is working positive replies depends on this to react quickly, and **response time is
already under scrutiny from Andres**. With no notification, reply latency degrades invisibly — and the
weekly response-time KPI (`smartlead-weekly-response-kpi`) measures exactly that gap.

**⚠️ Root cause is unknown and the obvious suspect is ruled out.** Gaston: *"no tengo muy claro por qué
se rompió, porque no cambiamos los webhooks desde Smartlead."* So this is not a webhook edit — start
elsewhere (Smartlead-side delivery, the Slack app/token, or the receiving automation).

**This is the third silent failure in three weeks** — after the RB2B→Clay webhook (dead ~2 weeks
unnoticed) and the suspected forms→Clay feed. Daniel had not registered this one either: *"la verdad,
no me había fijado."* Strongly suggests [[wiki/tasks/2026-09-01-rb2b-integration-monitoring]] should be
generalised into integration monitoring rather than built RB2B-only.

**Note on the handoff:** the reply-handling owner is changing (Hector out, Lila in, Gaston covering the
gap), so route the tag to whoever is actually on replies rather than restoring the old target blindly.

**Timing:** No date stated. Verbatim: *"ahí hay que hacer algo"* / *"hay que solucionarlo."* Gaston
mentioned a small task that slid Wed → Thu → Fri but said *"no me acuerdo"* twice about what it was, so
**it is unconfirmed whether that slippage refers to this.**

**Source:** [[wiki/meetings/2026-09-04-weekly-check]] · [Fathom @20:11](https://fathom.video/calls/810291115?timestamp=1211)

---

## Update 2026-09-11

**Still broken as of Sep 10** — six days after this task was opened, with **no diagnosis attempted**.
Gaston to Lila: *"Esto no está funcionando en este momento porque algo se rompió, tengo que ver qué
pasó, pero idealmente hoy o mañana ya lo deberíamos tener funcionando de vuelta."* New soft target:
**by Sep 11**. Cause remains unknown.

**⚠️ New: a design limitation separate from the bug.** Even when working, the alert fires **only on a
lead's FIRST positive reply**. Subsequent positive replies in an existing thread never notify, and
Gaston does not know how to change that. **So the Master Inbox must be checked manually regardless of
whether this bug is fixed** — don't treat restoring the alert as full coverage.

**Possible partial cause worth investigating — NOT confirmed.** The Sep 10 Untracked Replies session
established that some genuine positive replies never associate to a campaign/lead at all (cause
unknown), and land in Smartlead's Untracked Replies inbox where they cannot even be answered. **A
reply that never gets classified as a positive reply would never fire this alert.** This connection
was not drawn on the call — it is an inference to test, not a diagnosis.

**Tension to reconcile:** the same Sep 10 call treats the Slack channel as **live and expected to
fire** — Gaston tells Lila to configure an @-mention sound for it so she notices incoming positive
replies. That is hard to square with the channel being dead since Sep 4. Possibilities: it fires
intermittently, it fires for some campaigns only, or the break is narrower than recorded. **Check
whether anything has landed in the channel since Sep 4 before debugging blind.**

**Now also blocking:** Lila's entire reply workflow and the new under-10-minute reply-time KPI
([[wiki/meetings/2026-09-10-lila-replies-and-reply-time]]). Without the alert she polls the Master
Inbox by hand.

**Source:** [[wiki/meetings/2026-09-10-lila-replies-and-reply-time]] · [Fathom @23:09](https://fathom.video/calls/818704052?timestamp=1389) · [[wiki/meetings/2026-09-10-untracked-replies-walkthrough]]

---

## Completed 2026-09-11

**Fixed.** The Smartlead positive-reply Slack notification is delivering again, ending the third of the three silent integration failures.

**Two things recorded here that outlive the fix:**
- **The first-reply-only design limit still applies** — the alert fires only on a lead's *first* positive reply, so follow-up replies in an existing thread never notify. The Master Inbox still needs manual checking. This was never a bug and the fix does not change it.
- **The untracked-replies hypothesis was never confirmed or refuted.** Whether unassociated replies contributed is still unknown; if positive replies go missing again, that is the first place to look.

*Reported done by Gaston, 2026-09-11 status sweep.*
