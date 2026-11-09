---
type: task
title: "Add breakage monitoring/alerting to the RB2B → Clay integration"
created: 2026-09-01
updated: 2026-09-11
priority: high
status: done
from-meeting: "[[wiki/meetings/2026-09-01-leadership-deck-build]]"
related: ["[[wiki/tasks/2026-09-01-rb2b-backfill-and-reactivate-sends]]"]
sources: ["[[bibliography/2026-09-01 - Leadership Deck Build - Meeting]]"]
---

# Make it impossible for the RB2B feed to die silently again

Find out whether RB2B — or the Clay webhook side — can **emit a notification when the integration
stops delivering leads**. Failing that, build a daily verification that it is still running (a Claude
routine checking for new RB2B rows in Clay would satisfy it).

**Why:** The integration broke with **zero notification** and went unnoticed for about **two weeks**,
silently zeroing remarketing sends while the RB2B bill kept running. Andres's question in the
readout was *"why didn't anyone tell us / who is reviewing this?"* — and the honest answer is that
nothing was watching. **This is the durable fix; the backfill is only the cleanup.**

**Done =** a broken RB2B feed surfaces within a day, without anyone remembering to look.

**Timing:** No date. Gaston stated it as an open unknown he has to resolve — *"que lo tengo que
averiguar"*. **Needs a date from Gaston.**

> "no hay ninguna notificación de que se haya roto, entonces no sé si se podrá agregar alguna
> notificación de alguna forma, que lo tengo que averiguar, o si de alguna forma tenemos alguna manera
> de saber si está corriendo bien o no"
> *"there's no notification that it broke, so I don't know if some notification can be added somehow —
> I have to find that out — or if there's some way for us to know whether it's running properly."*

**Worth generalising:** RB2B is the integration that happened to fail. Any other silent Clay feed has
the same exposure — consider whether the check should cover more than RB2B.

**Source:** [[wiki/meetings/2026-09-01-leadership-deck-build]] · [Fathom @1:02:00](https://fathom.video/calls/806758340?timestamp=3720)

---

## Completed 2026-09-11

**Done.** Integration monitoring is in place — built as the generalised version rather than RB2B-only, which is what the task argued for after three silent failures in three weeks (RB2B→Clay, the forms→Clay feed, and the Smartlead positive-reply Slack alert).

*Reported done by Gaston, 2026-09-11 status sweep (second pass).*
