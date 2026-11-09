---
type: meeting
title: "Deliverability & Root-Cause Diagnosis w/ Daniel"
created: 2026-08-13
updated: 2026-08-19
attendees:
  - "Gaston Murillo — GTM Engineer / SalesOps"
  - "Daniel Ardila — Campaign strategy"
meeting-type: internal
duration-min: 65
recording_id: 173235273
fathom-url: "https://fathom.video/calls/784480827"
tags: [type/meeting, meeting-type/internal]
status: mature
sources: ["[[bibliography/2026-08-13 - Deliverability Root Cause - Meeting]]"]
---

# Deliverability & Root-Cause Diagnosis

Factor-by-factor working session on why booked calls have flatlined at 30–46/month all year
despite roughly doubling sending capacity since December.

## TLDR
- **Deliverability was largely ruled out as the primary cause.** Bounce rates are healthy;
  blacklisted domains show the same reply and bounce rates as clean ones. A live 10-inbox Smartlead
  spam test started during the call showed zero spam placement — though 2–3 inboxes sit at only
  ~60% warmup reputation.
- **The real signal is segment composition.** Hiring-manager positive rate held steady (3.58% →
  3.31% Jan–Jun) while **non-hiring-managers collapsed from 1.46% to 0.53%** as that segment's
  volume ballooned from ~7,000 to ~17,000 leads.
- **Gaston doubts the earlier BigQuery finding** that the CEO/founder share stayed stable through
  that expansion — the math doesn't work unless many genuinely new companies were loaded.
- **The overdue inbox-group switch (A→B) was executed** — last done in April, ~3 months overdue.
- **Core strategic conclusion: the baseline message has hit its ceiling.** More volume will not
  produce more calls. Future gains must come from niche segmentation and hyper-personalised copy.

## Key Decisions
- Do **not** upgrade Smartlead to the $379/mo plan just to unlock bulk spam testing (vs $174 now) —
  run ~50 batches of 10 inboxes on the current plan instead.
- Switch inbox groups now (A out, B in) and run the spam tests on the **retiring** group, since
  resting inboxes should be clean.
- Cap spam-test sends at ~2 emails per inbox per day, run periodically (end of month) rather than
  continuously, to protect real sending capacity.
- Focus the root-cause investigation on the non-hiring-manager segment.
- Delegate the spam-test grind to Héctor (10–20/day, 3–5 min each) until a new hire arrives.

## Action Items
- [x] Switch Smartlead inbox groups A → B — *Gaston* — 2026-08-14
- [ ] Run spam tests across all ~500 inboxes (~50 batches of 10) — *Gaston*
- [ ] Confirm whether spam-test emails consume sending capacity; cap ~2/inbox/day — *Gaston*
- [ ] Research an external bulk inbox-placement testing tool — *Gaston*
- [ ] Re-run BigQuery persona analysis for CEOs/founders to verify prior result — *Gaston*
- [ ] Build BigQuery report isolating HM vs No-HM across regions, by company-size bucket — *Gaston*
- [ ] Cross-reference booked calls against sending domains via Smartlead API — *Gaston*
- [ ] Fix co-workers campaign broken Clay workflow lookup — *Gaston*
- [ ] Train Héctor to run daily spam tests — *Gaston*
- [x] Cover Daniel's duties Monday — *Gaston* — 2026-08-17
- [ ] Check whether the reply-rate metric filters by campaign type — *Gaston*
- [ ] Re-send the Baseline Control vs Challengers table — *Gaston*

## Context
Volumes on the co-workers campaign (fall back to a hiring manager's colleagues when the HM doesn't
reply) fell to ~51/143/405 and then near zero. Gaston's diagnosis: the campaign looks leads up in
Clay workflows, and after the experiment churn (workflow 5 → 6 → 8) it was never repointed at the
current tables, so leads aren't found.

January and February were skewed by highly relevant sends (Open Jobs and webinar campaigns,
30k–35k emails against a 50k target), which is why Gaston wants to know whether the reply-rate
metric filters by campaign type before trusting month-over-month comparisons.

Daniel is blocked writing the "These are the reasons" section of his email outreach context
document, which Andrés has been waiting on for ~2 weeks.

Week-to-date at the time: 49 replies but only 6 booked calls, when 7–8 would be expected.
Following up on interested replies is the initiative Gaston credits for July being the best month
of the year (18.04% positive-reply-to-call).

## Open Questions
- Whether the reply-rate metric counts only Open Jobs campaign leads or all leads.
- Whether Smartlead caps the number of simultaneously active spam tests.
- Whether the newer inbox stack converts worse than the original — to be tested by cross-
  referencing booked calls against sending domains.

## Full Transcript
Not stored — see Fathom: https://fathom.video/calls/784480827 (65 min).
Fetch live via `get_meeting_transcript(recording_id: 173235273, url: ...)`. Conducted in Spanish.
Note: Fathom speaker attribution is unreliable in places; ownership was grounded on content.
