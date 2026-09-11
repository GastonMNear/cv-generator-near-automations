---
type: task
title: "Revert the Smartlead reply-time tracking window: 10:00–19:00 → 09:00–18:00 ET"
created: 2026-09-11
updated: 2026-09-11
priority: medium
status: done
from-meeting: null
related: ["[[wiki/tools/smartlead]]", "[[wiki/tasks/done/2026-08-27-fix-reply-time-tracking-window]]", "[[wiki/tasks/done/2026-07-22-daily-weekly-response-time-reports]]"]
sources: []
---

# Revert the reply-time tracking window → 09:00–18:00 ET

Gaston confirmed the intended window for both the daily and weekly reply-time reports is
**9 am – 6 pm ET**. The 2026-08-27 change had moved it to 10:00–19:00, so it was reverted.

## Both hours moved this time

The August change only touched the **open** hour (`OFFICE_CLOSE` was already `19`). Reverting to
9–18 therefore moves **both** ends: open `10 → 9` and close `19 → 18`. The close hour had been
`19` since the original build, so 18:00 is a genuinely new boundary — replies answered between
18:00 and 19:00 now roll to the next morning instead of counting the same day.

## Daily and weekly are one code path

Both routines run `scripts/run_weekly_kpi.py` (the daily just passes `--daily`), and
`business_hours()` reads `OFFICE_OPEN`/`OFFICE_CLOSE` with no hardcoded hours. Changing the one
constant covers both reports — there is no separate daily window to keep in sync.

## What changed

- `scripts/run_weekly_kpi.py` — `OFFICE_OPEN, OFFICE_CLOSE = 10, 19` → `9, 18`, plus the module
  docstring.
- `scripts/post_to_slack.py` — both `Mon–Fri 10–19 ET` labels (headline + CSV footnote) → `9–18 ET`,
  so the posted report states the window the maths actually uses.
- `SKILL.md` — the "Primary metric" line, the `biz = 0.00h` note, and the regression-anchor warning,
  which now carries the full window history instead of only the August change.
- `wiki/tools/smartlead.md` — the KPI-window callout.

## Watch-outs

- **The send window is a different 09:00–18:00.** Campaigns send 09:00–18:00 as a per-campaign
  Smartlead setting. The two windows now share the same hours by coincidence; they are unrelated
  and must never be edited together.
- **The Jul 13–19 regression anchor is now doubly stale** — it was measured under 9–19. Against the
  current 9–18 window, identical behaviour reads **higher** (one hour less credit per day). Do not
  read a WoW change across 2026-08-27 or 2026-09-11 as a performance shift.
- The weekly Google Sheet accumulates columns across all three window regimes. Any chart spanning
  those dates needs the window noted.

## Verification

`business_hours()` re-tested after the change: a 17:30 → 18:30 same-day gap now counts 0.5 h (was
1.0 h under a 19:00 close), and an 09:15 reply answered at 09:45 counts 0.5 h (was 0.0 h under a
10:00 open). A live run against Smartlead is the real confirmation.
