---
type: meeting
title: "Listas Cold Calling — Re-contact Subsequence, List Quality, Dialer Capacity"
created: 2026-08-31
updated: 2026-09-01
attendees:
  - "Gaston Murillo — Cold Email Lead (recorder)"
  - "Daniel Ardila — Outbound Lead"
  - "Ivan Valenzuela — Cold caller"
meeting-type: internal
duration-min: 49
recording_id: 178357794
fathom-url: "https://fathom.video/calls/805161647"
tags: [type/meeting, meeting-type/internal]
status: mature
related: ["[[wiki/meetings/2026-08-24-priority-alignment-huddle]]", "[[wiki/meetings/2026-08-21-weekly-check]]", "[[wiki/meetings/2026-08-31-weekly-planning-cold-email]]"]
sources: ["[[bibliography/2026-08-31 - Listas Cold Calling - Meeting]]"]
---

# Listas Cold Calling — Re-contact Subsequence, List Quality, Dialer Capacity

> [!note] Language: Spanish. Fathom's diarization **drifts after ~13:00** — several Gaston lines are
> labeled Daniel and vice versa. Ownership below is grounded in content and in who owns each system,
> not on speaker labels.

## TLDR
- **Daniel's priority 4 got its design.** Re-contacting leads who reopen a role will work by having
  Clay **update `lead_category` to a "new job posting" value on the existing lead**, which fires a
  Smartlead **subsequence** with AI-written `subsequence_email_1/2/3` variables — all inside the
  *same* campaign. This replaces the rejected approach of spinning up a new campaign per re-contact.
- **Why that matters:** duplicating a lead across campaigns 3–5 times would destroy the metrics —
  *"one lead is one lead, not multiple leads"*. The `lead_category` field doubles as attribution,
  showing **which attempt finally converted**.
- **Ivan's bad week was the list, not effort.** 18 of ~40 conversations died on **on-site roles**;
  ~95% of his "Hiring Manager not eligible" dispositions were on-site. He still dialed **2,514**
  times that week and hit 800 on Thursday.
- **Clay cannot filter job-description text at all**, and AI can't read LinkedIn's remote/on-site tag
  because LinkedIn blocks it. So **job-title exclusions are the only usable lever** — Gaston will
  mine the 1,000+ lead list with ChatGPT for more exclusion keywords.
- **Dialer capacity is the structural constraint:** JustCall allows **4 reattempts** where the team
  wants **20**, and a maximum of **2 Parallel dialers**. Gaston talks to PhoneBurner
  ($140/user annual, $165 monthly); Ivan evaluates Deep Blue.
- **A third motion was agreed:** auto-email leads who received a voicemail, **sent from Ivan's own
  inbox**. Justified live — a prospect emailed mid-call asking for a booking link.

## Key Decisions
- **Re-contact via `lead_category` → Smartlead subsequence, not new campaigns.** Preserves
  one-lead-one-record metrics and yields per-attempt attribution.
- **Roll out to Hiring Managers first**, then extend only to the best No-HM segment (CEOs/founders at
  companies under 50). Broad No-HM rollout judged not worth the metric noise.
- **Delete the TrueDial "Unlikely to Pick Up" campaign and its 1,065 leads, and rename it**, to free
  one of the two Parallel slots for No-HM CEOs — but **only after Ivan finishes in-flight
  reattempts**. Those 1,065 leads are Hiring Manager universe and already exist elsewhere; leaving
  them would duplicate leads across two campaigns.
- **Expand job-title exclusions first;** hold the "has Near ever placed this role?" AI filter as a
  **fallback only** (*"de última instancia"*) — it risks over-restricting a list Ivan needs volume from.
- **Voicemail follow-up is built as an automation, not assigned to Ivan** — he must stay at 800
  dials/day.
- **Daniel owns the single final leadership deck.** Both he and Gaston had unsent versions; Gaston
  stood his down rather than duplicate the work.

## Action Items
- [ ] Build the `lead_category` → Smartlead subsequence re-contact flow — *Gaston* — folded into
      [[wiki/tasks/2026-08-24-smartlead-remove-recontact-limit]] as the agreed design
- [ ] Load No-HM CEOs (under 50) into the Parallel dialer — *Gaston* — due: 2026-08-31 →
      [[wiki/tasks/2026-08-31-load-no-hm-ceos-to-parallel-dialer]]
- [ ] Delete the TrueDial campaign + 1,065 leads and rename it — *Gaston* — due: 2026-08-31, gated on
      Ivan → same task as above
- [ ] Mine the JustCall report + 1,000-lead list with ChatGPT for title-exclusion keywords, apply to
      **both** campaigns — *Gaston* → [[wiki/tasks/2026-08-31-expand-title-exclusions-cold-call-lists]]
- [ ] Book a PhoneBurner sales call re: parallel dialing + 20 reattempts — *Gaston* →
      [[wiki/tasks/2026-08-31-evaluate-dialer-capacity-phoneburner]]
- [ ] Automate voicemail-to-email follow-up from Ivan's inbox, incl. subject line — *Gaston* →
      [[wiki/tasks/done/2026-08-31-voicemail-to-email-automation]]
- [ ] Enable the daily automatic Clay sync for both cold-calling lists — *Gaston* →
      [[wiki/tasks/2026-08-31-daily-clay-sync-coldcall-lists]]
- [ ] Restructure Ivan's recurring meetings so he can drop off early — *Gaston* (low priority,
      noted in the Ivan-capacity thread below)
- [ ] Finish in-flight reattempts, then notify Gaston — *Ivan* (gates the campaign deletion)
- [ ] Review the Deep Blue dialer service and report back — *Ivan*
- [ ] Hit 800 dials/day this week — *Ivan*
- [ ] Share the final leadership deck with Gaston + Ivan — *Daniel*
- [ ] Create a Gmail filter/label for JustCall emails — *Ivan* (own inbox hygiene)

## Context

### The re-contact design, in detail
Clay finds an existing Smartlead lead in a target segment with a **new job posting**, writes
`subsequence_email_1/2/3` as AI-generated variables onto that lead, and flips `lead_category` to the
"new job posting" value — which is what triggers subsequence enrollment. Standard sequences are 3
emails, hence the three variables. Gaston raised a scoping requirement Fathom's extractor missed:
**check the lead's upload date** so re-contact only fires if the previous touch was ~2–3 months back.
The cadence assumption is that hiring managers reopen roles **every 2–3 months, not weekly**.

### Why list quality is hard here
The chain of constraints is worth recording because it eliminates the obvious fixes: Clay's source
**cannot access job-description text**, so "exclude on-site roles" can't be filtered on the
description. AI can't read LinkedIn's own remote/on-site tag either, because **LinkedIn blocks it**.
That leaves job titles. Gaston's plan is to download the JustCall report plus the 1,000+ lead list —
focusing on the leads Ivan dispositioned "Hiring Manager not eligible" — and have ChatGPT propose
further exclusion keywords, applied to **both** cold-calling campaigns.

### Ivan's capacity is a real constraint, not an excuse
He dialed 2,514 times over Aug 24–28 (318 / 325 / 421 / 800 / 600) and **lost 2–3 hours to meetings
on Friday**, which is what broke the 800 target. Gaston committed to trimming Ivan out of meetings
that don't need him. Of ~40 conversations, 26 were positive, 18 died on on-site, 20 were
not-interested or other.

## Open Questions
- **Does one PhoneBurner seat suffice**, given JustCall's two-dialer limit? Unanswered — part of what
  Gaston is asking sales.
- **Is the on-site problem a bad sample or a real list defect?** Only Ivan's 800/day volume will
  tell, and that determines whether the new title exclusions actually worked.
- **The re-contact recency window is still loose** — ~2–3 months was assumed here, but Daniel's
  earlier phrasing was "desde tres meses atrás en el último año". Unresolved, and it matters for
  how many leads qualify.
- **Whether a prior explicit "no" excludes a lead** — raised again, decided again nowhere. Same open
  question as in [[wiki/tasks/2026-08-21-justcall-api-move-reset-leads]].

## Full Transcript
See Fathom: https://fathom.video/calls/805161647
