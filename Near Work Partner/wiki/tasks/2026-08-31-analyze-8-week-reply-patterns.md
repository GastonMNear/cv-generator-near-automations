---
type: task
title: "Analyse 8 weeks of email replies — find what the sub-40 weeks have in common"
created: 2026-08-31
updated: 2026-09-01
priority: high
status: open
from-meeting: "[[wiki/meetings/2026-08-31-marketing-standup]]"
related: ["[[wiki/tasks/2026-08-13-cross-reference-calls-to-sending-domains]]", "[[wiki/tasks/2026-08-27-launch-no-hm-motion-segment-copy]]", "[[wiki/tasks/2026-08-13-run-spam-tests-all-inboxes]]"]
sources: ["[[bibliography/2026-08-31 - Marketing Stand Up - Meeting]]"]
---

# Find the pattern behind the sub-40-reply weeks

Pull the last **8 weeks** of email positive replies and identify what the weeks at or below **40
positive replies** share, versus the weeks above it. Output = named root causes, not a chart.

**Why:** This is the constraint on the whole channel. Conversion from positive reply to booked call
runs **~20%**, so a week under 40 replies mechanically drops booked calls under the **10-call
"endangered territory"** benchmark. August was a record month at **291 calls booked**, and the *only*
reason the team missed the all-time weekly record of **47** (set in March) was a mid-month reply dip.
Volume is already being hit — 23,900 emails the prior week — so the problem is **consistency, not
throughput**. Fixing the floor is worth more than raising the ceiling.

**Done =** a written readout naming what drives the bad weeks, specific enough to act on.

**Candidate hypotheses to test** (none of these was settled in the meeting):
- **Segment mix** — how much of that week's volume sat in known-weak arms. The No-HM positive rate
  fell 1.46% → 0.53% as volume went 7k → 17k while HMs stayed flat, so mix is the leading suspect.
- **Deliverability** — largely ruled out on Aug 13 (clean bounces, neutral blacklists, 0% spam in a
  live test), but worth re-checking per-week rather than in aggregate. Overlaps
  [[wiki/tasks/2026-08-13-run-spam-tests-all-inboxes]].
- **Sending domain** — which domains carried each week. Directly overlaps
  [[wiki/tasks/2026-08-13-cross-reference-calls-to-sending-domains]]; consider doing them together.
- **The Friday drop-off**, called a recurring pattern in the meeting: strong Mon–Thu, then a fall.
  Determine whether it's mechanical (send scheduling, AE availability) or demand-side.

**Timing:** No date set. Raised at the Aug 31 stand-up as the week's analytical focus, and Daniel's
September deck will want an answer — but nobody named a deadline. **Needs a date from Gaston.**

**Source:** [[wiki/meetings/2026-08-31-marketing-standup]] · [Fathom @04:01](https://fathom.video/calls/802752585?timestamp=241)
