---
type: task
title: "Break same-week booking attribution down per campaign, into the Outbound Matrix sheet"
created: 2026-09-01
updated: 2026-10-05
priority: medium
status: done
completed: 2026-10-05
from-meeting: "[[wiki/meetings/2026-09-01-leadership-deck-build]]"
related: ["[[wiki/tasks/2026-09-01-package-attribution-analysis-as-skill]]", "[[wiki/tasks/2026-08-25-revisit-decision-making-unit]]"]
sources: ["[[bibliography/2026-09-01 - Leadership Deck Build - Meeting]]"]
---

# Per-campaign attribution rate, landed in the sheet

Extend the same-week/carried-over analysis so the rate is computed **per Smartlead campaign** — HM vs
No-HM, engineering, LATAM vs US — and get it into the Google Sheet so it can feed the Outbound Matrix.

**Why:** The blended rate hides which campaigns pull it up or down, so follow-up strategy can't be
made campaign-specific. Both Gaston and Daniel expect **HMs to convert same-week** while
**No-HM/engineering need more back-and-forth** — but that's a hypothesis nobody has measured. It also
pre-empts the "you aren't measuring properly" challenge from leadership. Daniel's call was direct:
*"lo queremos hacer, hagámoslo."*

**The unsolved part is the export path, not the metric.** Gaston confirmed the per-campaign figure is
derivable — the lead is already identified, so campaign follows — but *"lo que no sé bien es cómo
después... ¿Cómo bajarlo al Google Sheets?"*

**Also folded in here:** resolve the **2 of 13 bookings** last week's run could not attribute.
Expected causes are the lead booking under a **different company domain** than the one contacted, or
**forwarding the email to a colleague** who booked instead. This will recur every week, so it needs a
resolution rule rather than a manual fix each time.

**Done =** per-campaign rates land in the sheet, and unmatched bookings have a documented handling rule.

**Timing:** No date. Gaston flagged it as feasible but slow — *"de que se puede hacer, se puede
hacer... el tema es va a tomar es tiempo"*. **Needs a date from Gaston.**

**Source:** [[wiki/meetings/2026-09-01-leadership-deck-build]] · [Fathom @19:49](https://fathom.video/calls/806758340?timestamp=1189)

## Update 2026-10-05

**Partly working (Sep 28).** Per-campaign attribution of booked calls now comes through the sheet: calls are entered by hand in Daily Update, and formulas build a weekly by-campaign tab (US OJ No-HM 2, TAM HM 3, Canada HM 2, RB2B 1, Exp 6 / US OJ HM 1). *"Y así vamos a tener la atribución por campaña y por semana"* ([@37:45](https://fathom.video/calls/838138117?timestamp=2265)). **The same-week/prev split per campaign is still not automated.** Close if the manual tab is enough?

*From fathom-task-sync run 10 (Sep 28 – Oct 1 meetings).*

## Closed 2026-10-05

Gaston (Oct 5, after run 10): done.
