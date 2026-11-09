---
type: task
title: "Fix the Smartlead reply-time tracking window: 09:00–19:00 → 10:00–19:00 ET"
created: 2026-08-27
updated: 2026-08-27
priority: medium
status: done
from-meeting: null
related: ["[[wiki/tools/smartlead]]", "[[wiki/tasks/done/2026-07-22-daily-weekly-response-time-reports]]", "[[wiki/tasks/done/2026-07-22-reply-time-reduction-plan]]"]
sources: []
---

# Fix the reply-time tracking window → 10:00–19:00 ET

The Smartlead response-time KPI counted business hours as **09:00–19:00 ET**. The response team's
actual hours are **10:00–19:00**, so the automation was crediting an hour the team wasn't working.
Requested by Gaston 2026-08-27.

Only the **open** hour moved — `OFFICE_CLOSE` was already `19` (7pm), so 7pm needed no change.

## Changed — `.claude/skills/smartlead-weekly-response-kpi/`
- `scripts/run_weekly_kpi.py` — `OFFICE_OPEN, OFFICE_CLOSE = 9, 19` → `10, 19`. This constant is
  the single source of truth; `business_hours()` derives everything from it.
- `scripts/run_weekly_kpi.py` — module docstring said `09:00-18:00`, which was **wrong in two ways**
  (stale close hour as well as open). Now `10:00-19:00`, matching the constant.
- `scripts/post_to_slack.py` — the Slack label and the CSV footnote both read `Mon–Fri 9–19 ET`
  → `10–19 ET`, so the posted report doesn't claim a window the maths no longer uses.
- `SKILL.md` — primary-metric definition and the `biz = 0.00h` note.

## Verified
Extracted `business_hours()` and ran it against the new constant — 6/6 boundary cases pass:

| Case | Result |
|---|---|
| 09:00 reply → 10:30 answer | 0.50h (was 1.5h) |
| 09:15 reply → 09:45 answer | 0.00h (was 0.5h) — now fully pre-window |
| 11:00 → 12:00 (mid-day) | 1.00h, unaffected |
| Full day 10:00 → 19:00 | 9.00h |
| Fri 18:00 → Mon 10:30 | 1.50h, overnight+weekend correct |
| Sat 12:00 → Mon 11:00 | 1.00h, weekend skipped |

## ⚠️ The reporting consequence — read before the next weekly report
A 10:00 open **removes one business hour per working day**. Replies landing 09:00–10:00 now start
their clock at 10:00 instead of counting immediately, so **business-hours averages will read lower
than before for identical team behaviour**.

**This is a definitional improvement, not an operational one.** Do not present a week-over-week drop
that straddles 2026-08-27 as faster response. The Jul 13–19 regression anchor in `SKILL.md`
(biz avg ~5.9h, median ~4.3h) was measured under the old window and is **no longer comparable** — a
warning callout now sits next to it. Re-baseline before any trend claim, and label the window on any
chart spanning the change.

Wall-clock metrics (`raw_hours`, `% under 5/10 min`) are **unaffected** — they never used the office
window, so they remain the clean cross-period comparison.

## Update 2026-08-27 — done
Change applied and verified. Not yet exercised against a live Smartlead run; the next weekly report
is the real confirmation. If the response team's hours shift again, `OFFICE_OPEN`/`OFFICE_CLOSE` in
`run_weekly_kpi.py` is the only place to edit, but the Slack label and SKILL.md prose must be updated
alongside it — they are hardcoded strings, not derived from the constant.
