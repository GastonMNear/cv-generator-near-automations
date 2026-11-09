---
type: task
title: "Analyze why lead supply isn't filling email capacity (market drop vs source issue)"
created: 2026-11-09
updated: 2026-11-09
priority: high
status: open
from: "Andrés's reply to the Nov 6 catch-up (Slack)"
related: ["[[logs/weekly-updates/2026-11-06]]", "[[wiki/meetings/2026-10-13-outbound-volume-session]]", "[[wiki/tasks/2026-09-01-apollo-experiment-leads-and-gap]]", "[[wiki/tasks/2026-10-29-hirebase-trial-readout-and-plan]]", "[[wiki/tasks/2026-10-29-moltsets-paid-test-workflow]]"]
---

# Analyze why lead supply isn't filling email capacity

Andrés asked (reply to the Nov 6 catch-up) for **insight into whether the volume of available job posts has dropped**. We keep adding lead sources (HireBase, MoltSets, Apollo) but still aren't filling sending capacity. Is it a drop in the LinkedIn job market, an Apollo problem, or something else?

**Why:** Lead supply, not inboxes, is what caps volume (Oct 13 huddle: ~18–21k/wk). If the cause is the market we need different sources; if it's our pipeline (filters, exclusions, dedup, Clay limits) the fix is internal. Gaston isn't replying yet; this is to analyze first.
**Done =** a short answer for Andrés: the trend in job posts / leads per source over the last ~8–12 weeks, where the drop (if any) sits, and the likely cause.

## Questions to answer
1. **Market:** has the raw number of matching job posts gone down? (LinkedIn Find Jobs source counts in Clay, HireBase daily volume estimates.)
2. **Per source:** leads produced per week by source (LinkedIn OJ, Apollo, HireBase, MoltSets, HubSpot cold accounts, Coworkers): which ones fell?
3. **Funnel loss:** where do jobs drop out on the way to Smartlead: company filters, Exclusion Lookup, HubSpot 2-month rule, no contact found, already in another campaign?
4. **Capacity side:** did capacity grow (more inboxes / higher limits) so the gap is partly us sending more?

## Known context
- Apollo: ~88% gap blamed on lead staleness; ~1 call/wk on ~4k emails/wk. See [[wiki/tasks/2026-09-01-apollo-experiment-leads-and-gap]].
- Sep 18: opportunities −20% since EXP-012, all segments, which was escalated as a Clay issue and not the market.
- Coworkers US OJ HMs dead since Aug 31 (133 → 0); HubSpot Cold Accounts No HMs B fed once Oct 30, 0 since (Nov 4 check).
- EXP-014 Sales/GTM reach low because most leads are already in other campaigns, which points to overlap/saturation and not the market.
- Nov 4 leads-added check: 1,346 enrolled in one day across 23 campaigns (baseline for comparison).

## 2026-11-09 — Analysis done (draft reply not sent)
See [[outbound/oj-lead-supply-analysis-2026-11-09]]. Short answer for Andrés:
- **No broad LinkedIn job drop:** US No-HM and LATAM jobs are flat or up. US HM is −19% and Canada No-HM −24% (L4W).
- **The loss is saturation:** companies reaching lead search are −22% vs Jun–Aug, and ~40% of found leads are already in Smartlead.
- **LinkedIn OJ uploads ~6.0k → ~4.2k/wk.** New sources (~1.75k/wk) only offset that.
- **Gap ≈ 1,870 leads/wk** (5.6k emails at 3.0 emails/lead).

Fixes: re-route already-contacted companies (+0.8–1.5k), restore Apollo/HubSpot/Coworkers (+1.0–1.3k), daily-control guard rails.
