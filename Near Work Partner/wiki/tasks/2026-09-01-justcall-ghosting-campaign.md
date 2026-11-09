---
type: task
title: "Create a separate JustCall campaign for ghosting leads to enable repeat dialing"
created: 2026-09-01
updated: 2026-09-11
priority: medium
status: in-progress
from-meeting: "[[wiki/meetings/2026-09-01-leadership-deck-build]]"
related: ["[[wiki/tasks/2026-08-21-justcall-api-move-reset-leads]]", "[[wiki/tasks/2026-08-31-load-no-hm-ceos-to-parallel-dialer]]"]
sources: ["[[bibliography/2026-09-01 - Leadership Deck Build - Meeting]]"]
---

# Stand up a ghosting-leads campaign in JustCall

Create a **brand-new JustCall campaign** for leads who ghosted us, and load them by **associating
existing lead IDs to the new campaign** — the method already validated on Friday, when leads were
transferred without being removed from their prior campaign. This lets Ivan run reattempts without
creating duplicate campaign records.

**Why:** Reported to leadership as Work In Progress — *"Enable repeat dialing of previously contacted
leads in JustCall without creating duplicate campaign records."* Daniel has called the
interested-then-ghosted segment the **highest-intent segment available**, and repeat dialing of it is
blocked until this campaign exists.

**Accepted constraint: it will not run on Parallel** — there is no Parallel capacity left (JustCall
allows only 2, and the second is going to No-HM CEOs). Volume was judged low enough that this doesn't
matter.

**Done =** the campaign exists, ghosting leads are in it, and Ivan can dial them without duplicate
records appearing.

**Timing:** No date. *"no está hecho, pero se puede"* — feasible, unscheduled. **Needs a date from Gaston.**

> "hay que crear una nueva campaña para las personas que nos están gosteando y subir ahí esos leads"
> *"we have to create a new campaign for the people who are ghosting us and upload those leads there."*

**Still unresolved (raised three times now, decided never):** whether a lead who already replied "no"
should be excluded. Same open question as in
[[wiki/tasks/2026-08-21-justcall-api-move-reset-leads]] and
[[wiki/tasks/2026-08-24-smartlead-remove-recontact-limit]].

**Source:** [[wiki/meetings/2026-09-01-leadership-deck-build]] · [Fathom @51:00](https://fathom.video/calls/806758340?timestamp=3060)

---

## Update 2026-09-11 — in progress

Gaston is actively building this: adding cold-email **interested leads who then ghosted us** into a
JustCall campaign so Ivan can run cold-call follow-ups on them.

**This is the highest-intent segment available** (Daniel's own framing), so it stays high-value even
though it runs off Parallel.

**Still unfinished** — the process is not yet complete end to end.

*Status reported by Gaston, 2026-09-11 status sweep.*

---

## Update 2026-09-11 (evening) — now explicitly BLOCKED, with a named cause

Daniel asked directly whether the ghosted-leads lists had been uploaded. They have not, and Gaston
named the blocker:

> *"No todavía... se rompió la notificación en Slack de Interested Replies... hay un quilombo con los
> webhooks de Smart Lead, entonces cuando agrego uno, se rompe el otro."*

**Root cause: an apparent Smartlead plan-level cap on webhooks/tasks.** Adding a new one breaks an
existing one, so the upload cannot proceed without sacrificing the Interested Replies Slack alert.

**This is now gated on [[wiki/tasks/2026-09-11-centralize-smartlead-clay-workflow]]** — the single
centralizing Clay workflow is the fix Gaston proposed, and this task resumes once it exists.

**Daniel explicitly tabled the Slack-notification repair** for the meeting — *"no lo vamos a
solucionar ahorita"* — folding it into the same centralizing fix rather than patching it twice.

**Status: still blocks Ivan.**

**Source:** [[wiki/meetings/2026-09-11-weekly-check]] · [Fathom @06:16](https://fathom.video/calls/818357203?timestamp=376)
