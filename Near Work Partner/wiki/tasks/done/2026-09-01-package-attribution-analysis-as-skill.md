---
type: task
title: "Package the same-week booking attribution analysis as a reusable skill"
created: 2026-09-01
updated: 2026-09-08
priority: medium
status: done
from-meeting: "[[wiki/meetings/2026-09-01-leadership-deck-build]]"
related: ["[[wiki/tasks/2026-09-01-per-campaign-attribution-breakdown]]", "[[wiki/tasks/2026-08-31-analyze-8-week-reply-patterns]]"]
sources: ["[[bibliography/2026-09-01 - Leadership Deck Build - Meeting]]"]
---

# Turn the attribution analysis into a skill, and document it

Convert the ad-hoc Smartlead **first-positive-reply-date** analysis into a repeatable skill or cloud
routine — the same pattern already used for the booked-call pause routine — so the weekly metric can
be produced without a manual run. Then **write it into the Outbound Matrix doc**, which Daniel
explicitly asked for.

**Why:** Same-Week Booking Attribution is now a **committed weekly report line**. Producing it by
hand every Tuesday under deck pressure is exactly the time sink Daniel has complained is stopping
Gaston from doing architectural work. It relies on an **undocumented Smartlead endpoint**, so the
method also needs to be written down before it's forgotten.

**Done =** the weekly split runs on demand (or on schedule) without hand-assembly, and the Outbound
Matrix doc describes it.

**Timing:** No date. Raised as *"seguramente podamos armarlo como un skill"* with Daniel agreeing it
belongs in the Outbound Matrix doc. **Needs a date from Gaston.**

> Gaston: "Ahora que ya estoy haciendo esto con la AI, seguramente podamos armarlo como un skill o algo
> y después subirlo a..." — Daniel: "Sí, que quede en el Outbound Matrix Doc, debería quedar así."

**Method to preserve:** find each booked lead's first positive reply date via the undocumented
Smartlead endpoint, compare against the booking week; same-week = both in one week, carried-over =
reply predates the booking week.

**Source:** [[wiki/meetings/2026-09-01-leadership-deck-build]] · [Fathom @15:51](https://fathom.video/calls/806758340?timestamp=951)

## Update 2026-09-02 — dated to Thursday, after the Sarah training session
Gaston raised it as the week's available "quick" item and Daniel sequenced it explicitly: *"train this
girl and then you can work on the routine."* → **Thu Sep 3, afternoon.**

Gaston's own framing of the deliverable: a **routine** that reports weekly whether a booked call came
from **this week's sending** or from **previous weeks' pipeline**, landing in the **Outbound Metrics**
doc automatically. That matches the design already recorded above.

**Check before building:** the `booked-call-attribution` skill already exists in this repo and may
cover most of this — verify what's live before writing anything new.

**Source:** Huddle 2026-09-01 (Daniel + Gaston), ~[34:40] and ~[37:20]

## Closed 2026-09-04 — reported done
Gaston reported the routine complete in [[wiki/meetings/2026-09-04-weekly-check]]: the routine that
tracks booked calls and whether the contact came from that week or a prior week *"ya está"*, giving
the same-week booking percentage and lead maturity time. Daniel confirmed the goal as automating
*"cuántas por follow up, cuántos por esta semana."*

**Verified 2026-09-08:** the `booked-call-attribution` skill exists in this repo and covers the full
scope — HubSpot booked calls filtered to 'Email Outreach', matched to Smartlead leads, first-reply
lookup, same-week vs previous-week bucketing, append to the Outbound metrics Google Sheet, and a Slack
headline. Its git history shows the weekly routine recorded as live.

**Remaining scope moved, not dropped:** the **Outbound Matrix doc write-up** Daniel asked for is not
confirmed done, and **per-campaign** attribution stays open in
[[wiki/tasks/2026-09-01-per-campaign-attribution-breakdown]] (export path still unsolved).

**Source:** [[wiki/meetings/2026-09-04-weekly-check]] · [Fathom @15:14](https://fathom.video/calls/810291115?timestamp=914)
