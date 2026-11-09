---
type: task
title: "Validate the KPI deck numbers before the leadership meeting"
created: 2026-08-25
updated: 2026-08-26
priority: high
status: done
deadline: 2026-08-25
from-meeting: "[[wiki/meetings/2026-08-25-kpi-deck-prep]]"
sources: ["[[bibliography/2026-08-25 - KPI Deck Prep - Meeting]]"]
---

# Validate the deck numbers — three known-bad figures

Daniel's AI rewrites the email-overview and email-capacity-split slides tonight; Gaston reviews
**first thing in the morning**, before the meeting. Three specific figures are known wrong:

1. **Net new open jobs — the 7,000 on the slide is invented.** Daniel confirmed his AI could not have
   sourced it ("no lo puede sacar la AI, se la inventa porque es una mentirosa"). Query BigQuery for
   the real number, now that it's working.
2. **Non-open-jobs email count is roughly double.** The slide says ~9,000 and implies Open Jobs is
   only 56.5% of volume; Gaston's own count is ~4,500, putting Open Jobs near 75%. Likely cause:
   **LATAM Open Jobs was split out into "others"** instead of counting as Open Jobs. Daniel's rule —
   everything Open Jobs across **all regions**, HM and No-HM, counts as Open Jobs.
3. **Email-experiment slide lead counts were never checked.** Gaston assumed they were fine. Daniel
   asked for validated numbers.

**Why:** Andres is watching the email number week over week, and the deck goes to leadership. A
fabricated figure surviving into the presentation is the kind of thing that costs credibility on a
week where the volume target was finally hit.

**Also for the slides (Daniel writing, Gaston reviewing):**
- Notes/context framing: two brutal weeks to open August, then **two weeks above the 10-call target**
  (11, then 12), with this week starting at 4.
- Learning to add: of 10 experiments launched, **only 6 have concluded** — none beat baseline. The
  other 4 are too young. Nobody should claim 30 things were tested.
- Learning to add: the **No-HM manager-identity problem** (see
  [[wiki/tasks/2026-08-24-review-conversion-improvement-strategy]]).
- Conclusion: kill the underperforming experiment; the rest need patience.
- Active-test order: form submissions → ghosted leads → hiring managers → No-HM under-50
  **founders/presidents only**.

## Update 2026-08-26 — done
Numbers validated and the slides reviewed ahead of the leadership meeting. The three known-bad
figures — the AI-invented 7,000 net-new-open-jobs, the non-open-jobs email count (LATAM Open Jobs
miscounted as "others"), and the unchecked experiment-slide lead counts — were corrected.
