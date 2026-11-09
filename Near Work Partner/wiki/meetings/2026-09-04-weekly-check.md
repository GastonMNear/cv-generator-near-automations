---
type: meeting
title: "Weekly Check"
created: 2026-09-04
updated: 2026-09-08
attendees: ["Daniel Ardila — outbound lead", "Gaston Murillo — outbound automation", "Ivan Valenzuela — cold calling", "Hector Melara — email replies / bookings", "Samuel Chapaval", "Mairol Sontay", "Felix Jourdain"]
meeting-type: internal
duration-min: 24
recording_id: 180236327
fathom-url: "https://fathom.video/calls/810291115"
tags: [type/meeting, meeting-type/internal]
status: mature
related: ["[[wiki/meetings/2026-09-04-new-oj-sources-triggers]]"]
sources: ["[[bibliography/2026-09-04 - Weekly Check - Meeting]]"]
---

# Weekly Check

## TLDR
- **Cold calling hit its 4,000-dial weekly target** on the new No-HM list (CEOs at companies under 50),
  configured Monday and loaded into Parallel Dialing — 1 call booked from dialing.
- **Email booked 4 calls**, recovering from a slow start (Mon 2 → Fri 4), mostly LATAM and No-HM segments.
- **Segment order settled: Sales > Marketing > Engineering.** Marketing has 2 positive replies / 2
  bookings, Sales 1, and **engineering has more volume than marketing but zero positive replies** —
  so volume is already ruled out as the cause. Daniel took the diagnosis for the week of Sep 8.
- **Apollo daily scraping is the big new bet and is NOT yet running.** Projection off a 2-day sample:
  ~500–600 opportunities/day → ~12,000/month → **~5 calls booked/month** if it converts like HMs.
  Daniel hedged hard: *"puede cambiar, quiero ser súper claro en esto."*
- **The Smartlead positive-reply Slack notification is broken and nobody noticed.** Gaston does not
  know why — *"no cambiamos los webhooks desde Smartlead"* — and Daniel had not even registered it.

## Key Decisions
- **Cold-call priority order unchanged:** Form Submissions + People Who Ghosted Us → Hiring Managers → No-HM.
- **Widen the website form net:** *all* website forms now feed the cold-call list, not just the
  "request a free consultation" button.
- **Website visitors get enriched in Clay** and, where a phone number is found, pushed to Ivan's dial list.
- **Baseline overrides segment in Experiment 12 routing:** anyone matching the baseline profile
  (CEO/founder at under 50 employees) goes to baseline regardless of segment; marketing/sales titles
  or larger companies go to Exp 12.
- **Outbound metrics hierarchy is Daily → Weekly → Monthly, auto-fed** — only Daily is entered by hand.
- **Cold-call objection-handling decision tree adopted:** diagnose the need first, pitch last, then map
  the pain to one of three selling points — candidate quality, payroll savings, or timezone/LATAM.

## Action Items
- [ ] Align the new Weekly/Monthly metric columns to Daily conventions so the auto-pull works — *Gaston*
- [ ] Fix the broken Smartlead positive-reply Slack notification (Hector tagging) — *Gaston*
- [ ] Verify whether Apollo daily scraping is running; activate if not — *Gaston (ownership unconfirmed)*
- [ ] Finish website-visitor → Clay enrichment → cold-call list — *Gaston*
- [ ] Assign the Luma Nutrición deal to Sales in HubSpot — *Hector*
- [ ] Analyse the engineering arm's volume/performance — *Daniel* — *"la otra semana"* (week of Sep 8)
- [ ] Finish the two HubSpot analyses: title↔role↔company-size pattern for finding the HM inside the
      No-HM universe, and separating the hiring manager from the economic decision-maker — *Daniel*

## Context
Same-week booking attribution was **reported as done** — the routine tracking booked calls and whether
the contact came from that week or a prior one *"ya está"*. Daniel restated the goal as automating
*"cuántas por follow up, cuántos por esta semana."*

Daniel's decision-maker finding, from 68 qualified calls out of ~120–140 No-HM bookings this year: the
hiring manager often does not negotiate or even ask about fees — **the CEO does, especially under 50
employees.**

Daniel flagged the metrics sheet as bus-factor-1: *"la única persona que le mete mano a eso es Gasti...
solamente es él o es la IA."*

Hector participated normally here and took a forward-looking action item — **hours after his termination
was rehearsed in that morning's 1:1** ([[wiki/meetings/2026-09-04-new-oj-sources-triggers]]).

## Open Questions
- **Engineering: message fit or something else?** Volume is ruled out; no alternative hypothesis offered.
- **Nobody asked whether Ivan's dialing or reply-handling can absorb ~12,000 Apollo opportunities/month.**
  The only capacity question raised was whether the scrape can be made to run at all.
- **Two manual bookings on Pedro's calendar** may not exist in HubSpot. Daniel: *"esas no están contadas
  en el HubSpot"*; Hector: *"no sé si están en el HubSpot, la verdad."* Charlie said he would fix the
  cause; Hector is not confident he will.
- **Writer Media has no deal in the pipeline at all**, so it will not count — a counting problem with no
  owner, unlike Luma Nutrición's assignment problem.
- **Form Submissions / High Intent volume was very low this week** — raised, not resolved.
- **A carried-over "routine" task** moved Wed → Thu → Fri and Gaston twice said *"no me acuerdo"*.
  Never identified. Possibly the Slack metrics routine from the morning 1:1.
- **Why the week started slow** (Mon 2 bookings) was never diagnosed.

## Full Transcript
See Fathom: https://fathom.video/calls/810291115

> [!warning] Diarization drift is visible before 13:00 — the block at 01:33 labelled Daniel actually
> contains Ivan's weekly recap. Attribution here is grounded in content. Apollo-scraping ownership is
> the one item content could not settle: the *"tengo que ver"* reply sits in a block labelled Daniel,
> while Fathom's summary assigned it to Gaston. Hector's day-by-day booking recount does not reconcile —
> he lands on 4 but names 8+ companies, some likely positive replies rather than bookings.
> **Ivan left at ~07:34. Samuel, Mairol and Felix never speak and are never addressed.**
