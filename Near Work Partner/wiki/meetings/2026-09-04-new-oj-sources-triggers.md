---
type: meeting
title: "New OJ Sources + New Triggers"
created: 2026-09-04
updated: 2026-09-08
attendees: ["Gaston Murillo — outbound automation", "Daniel Ardila — outbound lead / manager"]
meeting-type: internal
duration-min: 67
recording_id: 180156988
fathom-url: "https://fathom.video/calls/810291056"
tags: [type/meeting, meeting-type/internal]
status: mature
sources: ["[[bibliography/2026-09-04 - New OJ Sources and Triggers - Meeting]]"]
---

# New OJ Sources + New Triggers

## TLDR
- **Daniel reversed the sourcing strategy at the end of the call and this is the most important thing
  in the window:** stop hunting new lead sources, convert the universe already owned. *"We should not
  be spending our time finding a new source... we have a big universe and we are not converting 1% of
  that."* If job volume exceeds capacity, **cut jobs-per-company and contacts-per-company to cover
  more companies**. Gaston agreed. **It has no owner, no date, and appears in none of Fathom's summary items.**
- **Apollo daily pull proved viable on a live test:** 5.2k companies posted jobs in 2 days → 2,500
  exported (per-export cap) → **2,000 net-new after dedupe (~20% overlap)** → **~25% with a valid open
  job**. Gaston had predicted 2%, Daniel 30%. Forecast ~2,000–2,500/day, ~3,000 qualified opportunities/week.
- **The Apollo→Clay automation path is unsolved and manual is forbidden.** Gaston: *"I am not sure how
  we would do [it], to be honest."* Daniel rejected the 10-minutes-a-day fallback outright — *"manually no."*
- **Hector's termination was rehearsed here** (first 2.5 min). Gaston argued successfully to remove the
  "we're hiring someone to help Gaston" line. **No last day, no access/offboarding logistics discussed.**
- **Gaston takes over email replies** until Lila ramps (2–3 days estimated), and Daniel admitted he is
  **deliberately stalling Sara's training** — *"as soon as she is not ready to replace you, I'm earning time."*

## Key Decisions
- **No new lead sources.** Optimise messaging within the existing universe; trade depth for breadth.
- **Apollo daily pull approved to build** — framed as a cadence change on an existing source, not a new one.
- Export mechanic is an **adaptive backfill**, not a fixed 2×2,500/day: ~2,000 expected daily, 2,500 is
  the **per-export** cap, so one export normally suffices and it walks back to the previous day to top up.
  A second export is the overflow valve for heavy days.
- **Dedupe has two layers:** company-level against the existing LinkedIn open-jobs universe (the
  2,500→2,000 step), and person-level enrichment is not re-spent on known companies — **a returning
  company with a new job post is still a valid opportunity.**
- **Remote roles are excluded, US-specific kept**, filtered in Clay at job-description level.
- **Lila's hours are 9–6 EST** (not Hector's 10–7); the response-time metric re-bases to that window.
  Daniel confirmed the metric had been fair, explicitly closing Hector's excuse.
- **RB2B visitors and HubSpot form submissions stay as two separate campaigns** — merging destroys the
  intent signal, since RB2B alone cannot tell you a visitor submitted anything. Visitors who also
  submitted a form are excluded from the RB2B list.
- **HM subsequence is tagged Experiment 13 in reporting only**, not in Smartlead — a subsequence cannot
  carry an experiment name natively. Numbering: 10 = Apollo, 11 = CEOs under 50 in HM, 12 = No-HM
  priority segments, 13 = HM subsequence.
- **AI-written replies and AI CV creation agreed as medium-term direction**, gated on Gaston's time,
  with a QA step before send as the mitigation.

## Action Items
- [ ] Build the daily Apollo→Clay agent — *Gaston* — no deadline stated
- [ ] Activate RB2B visitor retargeting, excluding form submitters — *Gaston* — due: 2026-09-04
- [ ] Slack routine posting week-over-week metrics to Daniel — *Gaston* — needed before Mon Sep 7 deck build
- [ ] Show Daniel how to export subsequence lead lists from Smartlead — *Gaston*
- [ ] Confirm whether subsequence data reaches BigQuery at all — *Gaston*
- [ ] Take over email replies until Lila ramps — *Gaston*
- [ ] Re-base response-time metric to 9–6 EST and set Lila's hours — *Gaston*
- [ ] Deliver Hector's termination conversation — *Daniel*
- [ ] Build the volunteer-session deck Mon Sep 7; sync with Gaston first thing Tue Sep 8 — *Daniel*
- [ ] Prepare the Andres narrative for why Apollo-daily wasn't done sooner — *Daniel*
- [ ] Align priorities with Gaston, week of Sep 7 — *Daniel*

## Context
Apollo's plan is the root constraint: it permits exporting companies but **not** reading their job
postings, and there are **no Apollo API credits** — *"our plan is too small."* That is why job-post
detection is stitched together from Prospeo, PredictLeads and an AI website scraper. Gaston raised
upgrading the plan; Daniel said *"probably"* and never decided, pivoting instead to Apollo's ~88%
underperformance versus the No-HM baseline. Daniel pre-empted the "unfair comparison" defence and won
the point: over 80% of booked calls come from email 1, so an incomplete sequence cannot explain the gap.
His counter-theory is lead staleness — Apollo opportunities run 2–3 weeks old — which is exactly what
the daily cadence fixes.

Roughly 12 minutes of the recording (43:09–54:38) is dead air while the Clay workflow ran on screen.

## Open Questions
- **How Apollo→Clay gets automated.** The central blocker; no mechanism identified, manual forbidden.
- **Whether to upgrade the Apollo plan** — answered *"probably"*, abandoned.
- **Whether Smartlead subsequence data reaches BigQuery.** Gaston identified the real risk: the sync
  operates at **campaign** granularity and a subsequence is not a campaign, so the data may never
  arrive. Exchange ended in *"I don't know. I don't know."* This also blocks Daniel's export route.
- **Whether the ~25% match rate survives daily cadence** — the batch was still running at call's end,
  and Gaston expects decay from repeat companies.
- **Whether Gaston attends Hector's termination** — asked directly at the top, never answered.
- **Why Apollo underperforms by ~88%** — candidate causes listed, none chosen.
- **The nominal topic, "new OJ sources", was never answered** — Daniel declared the question itself wrong.

## Full Transcript
See Fathom: https://fathom.video/calls/810291056

> [!warning] Diarization drifts after ~13:00. Attribution in this note is grounded in content, not
> speaker labels. Two figures are unrecoverable from the transcript: a "6.56" that should be ~25% of
> 2,000, and a garbled reference to speaking with a vendor about BigQuery.
