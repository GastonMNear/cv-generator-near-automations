---
type: meeting
title: "Leadership Deck Build — Same-Week Booking Attribution & the Broken RB2B Webhook"
created: 2026-09-01
updated: 2026-09-01
attendees:
  - "Gaston Murillo — Cold Email Lead (recorder)"
  - "Daniel Ardila — Outbound Lead"
meeting-type: internal
duration-min: 69
recording_id: 178722833
fathom-url: "https://fathom.video/calls/806758340"
tags: [type/meeting, meeting-type/internal]
status: mature
related: ["[[wiki/meetings/2026-08-31-cold-calling-lists]]", "[[wiki/meetings/2026-08-31-marketing-standup]]", "[[wiki/meetings/2026-08-25-kpi-deck-prep]]"]
sources: ["[[bibliography/2026-09-01 - Leadership Deck Build - Meeting]]"]
---

# Leadership Deck Build — Same-Week Booking Attribution & the Broken RB2B Webhook

> [!warning] **Titled "Impromptu Google Meet Meeting" in Fathom** — it was actually the working
> session building the Tuesday leadership readout deck. Language: Spanish with English deck/metric
> terminology. Diarization **drifts badly after ~20:00** — large blocks labeled Daniel clearly
> contain Gaston's voice (notably the 8-week range analysis ~55:01 and the RB2B webhook explanation).
> Ownership below is grounded in who could have known the content.

## TLDR
- **A new headline metric was born: Same-Week Booking Attribution.** Andres had challenged that 13
  bookings against 46 positive replies is meaningless without knowing which bookings came from *that
  week's* first touches. Gaston used the undocumented Smartlead endpoint to split them.
- **Last week: 13 booked, 11 traceable — 7 same-week, 6 carried over (54/46).** An 8-week backfill
  run live during the call gave **74 calls, 57% same-week / 43% carried over**.
- **The weekly rate is noisy and they knew it:** it swings **40–86%**, and the two best-looking weeks
  (80%, 86%) were the two **smallest samples** (5 and 7 calls), where a single booking moves the rate
  **14–20 points**. Target set at **55% same-week / 45% pipeline**, deliberately framed as a *range*
  to stop Andres hardening one number into a KPI.
- **The RB2B→Clay webhook has been silently broken since ~mid-August** — roughly two weeks — zeroing
  out remarketing sends while Near keeps paying a large RB2B bill. **There was no notification of any
  kind.** This is the actual cause of the low RB2B volume Andres flagged. Gaston owns the backfill,
  the reactivation, and finding a way to be alerted next time.
- **Two re-contact motions stay Work In Progress, not done** — deliberately. The API lead-ID
  re-association is *"un invento"*, not a Smartlead feature, so it must be proven before it's claimed.
- **New initiative from Andres:** pull **all** website form submissions plus RB2B visitors into the
  cold-calling list — not just the free-consultation form.

## Key Decisions
- **Report same-week vs carried-over attribution weekly**, replacing the old "positive-to-book
  attribution is not readable" language. It makes the funnel projectable.
- **Target = 55% same-week / 45% previous-week pipeline, stated as a range.** The 8-week blend is 57%,
  but small-sample weeks make any single week unreliable.
- **Move the attribution slide immediately after the headline slide**, and retire it from the dense
  metrics section after this presentation — it's the week's framing insight and gets lost mid-deck.
- **Report RB2B remarketing metrics on the readout going forward**, and log the RB2B backfill as an
  openly pending item rather than quietly fixing it. Visibility is the point.
- **Keep both re-contact items as WIP:** "recontact previously enriched leads on a new hiring trigger"
  and "repeat dialing in JustCall without duplicate records". Preferred path is now a **sub-sequence**.
- **For ghosting-lead repeat dialing, create a brand-new JustCall campaign** rather than re-adding
  leads to the existing one. It **cannot run on Parallel** — no capacity left — but volume will be low
  enough not to matter.
- **Feed the calling list from all HubSpot non-clients** — every form submission, calendar-abandoners,
  and RB2B visitors. Worded as "calling list" rather than "inbound" so credit isn't reassigned to
  another team.

## Action Items
- [ ] Re-export RB2B's missed mid-August leads to Clay + reactivate remarketing sends — *Gaston* →
      [[wiki/tasks/2026-09-01-rb2b-backfill-and-reactivate-sends]]
- [ ] Add breakage monitoring/alerting to the RB2B→Clay integration — *Gaston* →
      [[wiki/tasks/2026-09-01-rb2b-integration-monitoring]]
- [ ] Package the attribution analysis as a reusable skill + document in the Outbound Matrix doc —
      *Gaston* → [[wiki/tasks/2026-09-01-package-attribution-analysis-as-skill]]
- [ ] Break the attribution rate down per campaign, land it in the Google Sheet — *Gaston* →
      [[wiki/tasks/2026-09-01-per-campaign-attribution-breakdown]]
- [ ] Top up the Apollo experiment toward 3,600 leads + diagnose the 0.22 vs 1.3 gap — *Gaston* →
      [[wiki/tasks/2026-09-01-apollo-experiment-leads-and-gap]]
- [ ] Test the Smartlead sub-sequence re-contact path — *Gaston* → folded into
      [[wiki/tasks/2026-08-24-smartlead-remove-recontact-limit]]
- [ ] Create the new JustCall campaign for ghosting leads — *Gaston* →
      [[wiki/tasks/2026-09-01-justcall-ghosting-campaign]]
- [ ] Ship the soft technical landing deploy — *Gaston* — due: 2026-09-05
- [ ] Build the all-forms + RB2B-visitors feed into the calling list — *Gaston* →
      [[wiki/tasks/done/2026-09-01-forms-and-visitors-to-calling-list]]
- [ ] Resolve the 2 of 13 unattributed bookings — *Gaston* (folded into the per-campaign task)
- [ ] React to the three readouts Daniel sent — *Gaston* — due: 2026-09-01
- [ ] Finalise slide text, fix formatting (overflowing boxes, 12.5 vs 14 font), present in English —
      *Daniel*

## Context

### How the attribution metric works
Gaston used the undocumented Smartlead endpoint to find each booked lead's **first positive reply
date**, then compared it to the booking week. Same-week = the first touch and the booking landed in
one week; carried-over = the reply predates the booking week. **2 of 13 could not be matched** —
expected causes are the lead booking under a **different company domain** than the one contacted, or
**forwarding the email to a colleague** who booked instead. That gap will recur weekly, so it needs a
resolution rule rather than a one-off fix.

### Why the range framing matters
Weekly booking volume runs **5–13 calls**. At that sample size one booking swings the rate 14–20
points, which is why Daniel wanted the target explicitly presented as a band. Worst carried-over
weeks were Aug 3 and Aug 10 (1 each). **Jul 13 and Jul 27 were the only weeks where follow-up
bookings exceeded same-week** (Jul 27: 4 same-week vs 6 carried over).

### The RB2B failure mode is the durable lesson
The integration broke with **zero notification** and went unnoticed for ~2 weeks. Andres's question
was *"why didn't anyone tell us / who is reviewing this?"* — and the honest answer is that nothing
was watching. That's why the monitoring task is filed separately from the backfill: fixing the data
without fixing the blind spot guarantees a repeat.

### Numbers going into the deck
Last week 13 booked / 46 positive replies (prior month: 32 positive replies); prior week 12 booked.
**Reply-rate goal is 4.2%** — never yet achieved — which is what email needs to contribute toward the
**30 calls-booked** goal, also never achieved. Apollo No-HM sits at **0.22 vs 1.3** for hiring
managers, far below benchmark, with one experiment at **117 of a 3,600-lead** target. Campaign 009
(CEO) had its CTA changed Aug 27, deliberately timed for the next lead batch.

## Open Questions
- **Will Andres accept 55% as a range rather than a hard KPI?** If he hardens it, the per-campaign
  breakdown becomes mandatory rather than exploratory.
- **Why is Apollo's No-HM performance 0.22 against a 1.3 hiring-manager benchmark?** Nobody knows;
  the sample has to be filled before it can be diagnosed.
- **How does the per-campaign metric reach Google Sheets?** Gaston confirmed the metric is derivable
  (the lead is identified, so campaign follows) — the **export path is the unsolved part**.
- **Felix reported the call list is poor quality, mainly too few leads**, and Gaston conceded that's
  on his side (*"está de mi lado"*). Why so few leads are loading is unresolved.

## Full Transcript
See Fathom: https://fathom.video/calls/806758340
