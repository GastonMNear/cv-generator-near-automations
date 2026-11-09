---
type: task
title: "Give Daniel a subsequence lead-list export, and confirm subsequences reach BigQuery"
created: 2026-09-04
updated: 2026-09-11
priority: medium
status: done
from-meeting: "[[wiki/meetings/2026-09-04-new-oj-sources-triggers]]"
related: ["[[wiki/tasks/2026-09-01-per-campaign-attribution-breakdown]]", "[[wiki/tasks/2026-09-02-bigquery-replies-vs-open-jobs]]"]
---

# Daniel needs subsequence lead lists without downloading campaign by campaign

Daniel asked how to export the subsequence lead list from Smartlead and **pre-rejected the manual
route**: *"don't tell me that I have to go campaign per campaign, downloading the list in the original
way."* Gaston's non-answer — *"I won't tell you that, but..."* — confirms that currently **is** the only
way.

**Why:** he needs it for the **Tue Sep 8** volunteer-session deck, which he plans to build **Mon Sep 7**
(a holiday he intends to work). Manual per-campaign downloads is exactly the time sink he has
complained is stopping Gaston from doing architectural work.

**⚠️ The proposed route may not exist.** Gaston offered BigQuery as the export path, then identified the
blocker himself: **the BigQuery sync operates at campaign granularity, and a subsequence is not a
campaign** — so subsequence data may never arrive there at all. The exchange ended unresolved:
*"no. Oh, I don't know. I don't know."*

**So this is two questions, in order:**
1. **Does subsequence data reach BigQuery at all?** Verify before designing anything on top of it.
2. **If not**, find another export path — Smartlead API, or the undocumented endpoint already used for
   the attribution analysis.

**Related constraint:** the HM subsequence is tagged **Experiment 13 in Daniel's reporting only**,
because a subsequence can't carry an experiment name in Smartlead. Any export needs to make
subsequences distinguishable without that native tag.

**Timing:** No deadline stated; explicitly deferred to an afternoon meeting — *"this is not a weekly
check. We're going to talk about that in the afternoon meeting."* The **Mon Sep 7 / Tue Sep 8** deck is
the real forcing function.

**Source:** [[wiki/meetings/2026-09-04-new-oj-sources-triggers]] · [Fathom @13:05](https://fathom.video/calls/810291056?timestamp=785)

---

## Completed 2026-09-11

**Done.** The Smartlead subsequence export for Daniel is delivered.

**Resolves an open vault question:** the task carried a warning that subsequence data **might not reach BigQuery at all**, since the sync is campaign-granular and a subsequence is not a campaign. That concern is now moot for this deliverable.

*Reported done by Gaston, 2026-09-11 status sweep (second pass).*
