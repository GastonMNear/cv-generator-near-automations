---
type: task
title: "Build one centralizing Clay workflow that routes all Smartlead events"
created: 2026-09-11
updated: 2026-09-11
priority: high
status: open
from-meeting: "[[wiki/meetings/2026-09-11-weekly-check]]"
related: ["[[wiki/tasks/2026-09-01-justcall-ghosting-campaign]]"]
---

# One Clay workflow in, everything routed out

**Done =** adding a new Smartlead destination no longer breaks an existing one.

Build a **single Clay workflow** that receives everything from Smartlead, then routes downstream to
each destination — the Slack message, cold calling, the reactivation campaign, and whatever comes next
— instead of a separate per-destination webhook for each.

**Why: it is currently an active blocker, not a tidiness project.** Smartlead appears to cap the number
of webhooks/tasks on the current plan, so *"cuando agrego uno, se rompe el otro."* That breakage:
- broke the **Interested Replies Slack notification**, and
- is **blocking the ghosted-leads upload** ([[wiki/tasks/2026-09-01-justcall-ghosting-campaign]]),
  which Daniel calls the highest-intent segment available.

Every new integration from here on hits the same ceiling until this exists.

**⚠️ The cap is a hypothesis, not a confirmed fact.** Both Gaston and Daniel hedged — *"debe ser un
límite... Puede ser, pero entonces no sé bien cómo ser."* Worth confirming with Smartlead before
building around it, in case the real cause is something cheaper to fix.

**Timing: no estimate given.** Daniel asked directly how long it would take; Gaston answered *"capaz
no tanto."* **Needs a date** — several stalled items are queued behind it.

> Gaston: *"un solo workflow que abarque todo junto y que después rutee a tipo el mensaje de Slack o a
> cold calling o a una reactivation campaign o lo que sea. Entonces me parece que tendría que armar
> este workflow que centralice todo en Clay"*

**Source:** [[wiki/meetings/2026-09-11-weekly-check]] · [Fathom @06:16](https://fathom.video/calls/818357203?timestamp=376) · [@07:25](https://fathom.video/calls/818357203?timestamp=445)
