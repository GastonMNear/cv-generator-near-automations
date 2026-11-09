---
type: task
title: "Re-export RB2B's missed mid-August leads to Clay and reactivate remarketing sends"
created: 2026-09-01
updated: 2026-09-11
priority: high
status: done
from-meeting: "[[wiki/meetings/2026-09-01-leadership-deck-build]]"
related: ["[[wiki/tasks/2026-09-01-rb2b-integration-monitoring]]", "[[wiki/tasks/2026-09-01-forms-and-visitors-to-calling-list]]"]
sources: ["[[bibliography/2026-09-01 - Leadership Deck Build - Meeting]]"]
---

# Backfill the RB2B leads the broken webhook dropped, and restart remarketing

Pull the RB2B website-visitor leads from roughly **the last two weeks** — the period the
RB2B→Clay webhook was dead — that never reached Clay. Push them into Clay for the normal enrichment
flow, add them to the remarketing campaign, and **restart sending**.

**Why:** The webhook broke around **mid-August** and nothing noticed for ~2 weeks. Remarketing sends
went to **zero** in the Outbound Tracker while Near keeps paying a **large RB2B bill** — which is the
real cause of the low RB2B volume and bookings Andres flagged. This is now written into the deck's
pending section as *"manual export of RB2B's missing leads to add to the campaign / reactivate the
sending"*, so it is a visible commitment to leadership, not an internal cleanup.

**Done =** the missed leads are enriched in Clay, loaded into the remarketing campaign, and sends are
confirmed running again in the Outbound Tracker.

**Timing:** No date set. Agreed on the call as *"algo que ya queda pendiente de hacer"* — logged as
pending rather than dated. **Needs a date from Gaston**; RB2B spend is accruing against zero output
in the meantime.

> "Igual, lo que podemos hacer es agarrar los leads de las últimas dos semanas que no se nos mandaron
> a Clay, y mandarles ahora."
> *"Either way, what we can do is take the leads from the last two weeks that never got sent to Clay,
> and send them now."*

**Note:** fixing the data without fixing the blind spot guarantees a repeat — the monitoring half is
[[wiki/tasks/2026-09-01-rb2b-integration-monitoring]].

**Source:** [[wiki/meetings/2026-09-01-leadership-deck-build]] · [Fathom @1:02:20](https://fathom.video/calls/806758340?timestamp=3740)

---

## Completed 2026-09-11

**Done.** RB2B's dropped leads backfilled and remarketing sends restarted, closing the commitment made to leadership after the webhook was found silently dead for ~2 weeks.

*Reported done by Gaston, 2026-09-11 status sweep (second pass).*
