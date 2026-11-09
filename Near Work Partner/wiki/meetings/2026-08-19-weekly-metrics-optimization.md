---
type: meeting
title: "Weekly Metrics & Optimization — Cold Calling Rebuild"
created: 2026-08-19
updated: 2026-08-19
attendees:
  - "Gaston Murillo — GTM Engineer / SalesOps (email, lead loading)"
  - "Daniel Ardila — Campaign strategy / leadership reporting"
  - "Ivan Valenzuela — Cold calling"
  - "Mairol Sontay — LinkedIn outreach"
  - "Samuel Chapaval — LinkedIn outreach"
  - "Hector Melara — Reply handling"
meeting-type: internal
duration-min: 62
recording_id: 174843149
fathom-url: "https://fathom.video/calls/787480435"
tags: [type/meeting, meeting-type/internal]
status: mature
sources: ["[[bibliography/2026-08-19 - Weekly Metrics & Optimization - Meeting]]"]
---

# Weekly Metrics & Optimization — Cold Calling Rebuild

## TLDR
- **Cold calling was rebuilt from the ground up.** Dial lists stop being segmented by whether an
  email was found. All hiring managers go into one parallel-dialing list, prioritised by hiring
  role and title. Attempt cadence jumps from 4 touch points to ~20 per lead over two weeks
  (2 dials/day, morning + afternoon) — a middle ground between the 27-touch industry norm Mairol
  and Ivan cited and US state telemarketing harassment limits.
- **Gaston owns lead loading only; Ivan now owns JustCall configuration.** Daniel was explicit:
  "Gasti sí tiene que subirte los leads allá. Él es el encargado de que te aparezcan allá."
  Ivan is blocked until Gaston confirms the upload.
- **Gaston reported 396–400 hiring managers found in the last 7 days** — enough for ~4,000
  dials/week — but flagged the number swings (some weeks 390, some 200).
- **Email was called the worst-performing channel of the last two weeks** despite 6–7 positive
  replies this week. Structural response: candidate-lead is retired and routing becomes the single
  No-HM baseline; Experiment 9's baseline arm is dropped for multi-role savings; two new arms
  launch capped at 30% of volume.
- **BigQuery is still broken** on a payment-info problem Gaston cannot fix himself — needs Paz or
  Andrés. Blocks the net-new-jobs metric and the persona analysis.

## Key Decisions
- Cold calling no longer segments by email-found; prioritise by hiring role and title instead.
- Cold-call priority order: ghosted positive replies (single dial) → form submissions (single dial)
  → all hiring managers (parallel) → No-HM CEOs at companies under 50 employees.
- Attempt cadence raised to ~20 per lead over two weeks, 2 dials/day.
- Ivan, not Gaston, owns JustCall platform configuration going forward.
- Old JustCall campaigns get **archived, not deleted**, to preserve historical metrics — except the
  two Predictive campaigns, whose lists must be swapped in place because parallel dialing only
  works on pre-existing campaigns (known issue from the Ramón setup).
- Candidate-lead arm retired; routing becomes the single baseline for No-Hiring-Managers.
- Experiment 9 baseline arm dropped, all volume to multi-role savings; leads already in flight run out.

## Action Items
- [ ] Load all hiring managers + No-HM CEOs <50 into JustCall, then confirm to Ivan — *Gaston* — this week
- [ ] Swap lead lists inside the two Predictive JustCall campaigns — *Gaston* — this week
- [ ] Archive old JustCall campaigns except the two Predictive — *Gaston*
- [ ] Merge routing + candidate-lead into one No-HM baseline; launch 2 new arms capped at 30% — *Gaston*
- [ ] Rebuild co-workers Clay workflow to point at current experiment tables — *Gaston*
- [ ] Unblock BigQuery billing via Andrés/Paz — *Gaston*
- [ ] Automate pausing email sequences for booked cold-call leads — *Gaston*
- [ ] Check whether inbox switch is active on Experiment 9 — *Gaston*
- [ ] Post Experiment 9 copy to group channel for copywriting feedback — *Gaston*
- [ ] Configure JustCall (20 attempts / 2 weeks) once leads land — *Ivan*
- [ ] Review the ~210 no-email leads and pass to Sam/Mairol — *Felix* (Daniel pushing)
- [ ] Draft Apollo multi-role savings copy, share with Gaston to polish — *Daniel*

## Context
Daniel's core argument on cold calling: relevance does not imply pick-up rate. "Yo prefiero
marcarles un montón de veces y aunque el pick-up rate sea una porquería, tener la oportunidad de
hablar con ellos." Hence prioritising by role/title and dialing hard, rather than spreading thin
across the whole database.

Ivan raised that when he dials, most LinkedIn job posts already read "no longer accepting" —
the lead latency problem. Currently No-Email hiring managers load daily (~10–15/day, called within
a day of the job post), but hiring managers *with* email wait through the full email sequence
(now 7 emails) before reaching JustCall, so they arrive a week or more late. Daniel wants near
real-time loading; this is unresolved.

Mairol flagged that some US states treat more than 2–3 dials/day as borderline harassment, which
capped the cadence at 20 rather than 27.

## Open Questions
- What to do with hiring managers **who have** email — wait out the 7-email sequence, or load to
  JustCall in near real time? Daniel wants faster; no mechanism decided.
- Which extra LinkedIn account to activate (Sam's vs Laura's) — Sam/Mairol to decide.
- Whether spam deliverability explains Experiment 9's zero replies — depends on whether the inbox
  switch was ever configured on that campaign.

## Full Transcript
Not stored — see Fathom: https://fathom.video/calls/787480435 (62 min).
Fetch live via `get_meeting_transcript(recording_id: 174843149, url: ...)`. Conducted in Spanish.
