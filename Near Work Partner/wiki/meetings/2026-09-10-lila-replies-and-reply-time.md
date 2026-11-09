---
type: meeting
title: "Lila <> Gasti — Live Reply Triage and the Reply-Time KPI"
created: 2026-09-10
updated: 2026-09-11
attendees: ["Gaston Murillo — cold email lead", "Lila Lemus — email replies"]
meeting-type: internal
duration-min: 62
recording_id: 181861588
fathom-url: "https://fathom.video/calls/818704052"
tags: [type/meeting, meeting-type/internal, topic/email-replies, topic/metrics]
status: mature
related: ["[[wiki/meetings/2026-09-09-smartlead-cv-workflow-training]]", "[[wiki/meetings/2026-09-11-outbound-metrics-follow-ups]]"]
sources: ["[[bibliography/2026-09-10 - Lila Replies and Reply Time - Meeting]]"]
---

# Lila <> Gasti — Live Reply Triage and the Reply-Time KPI

## TLDR
- Triaged two live replies and set the **reply-speed KPI: maximise the share of replies under 10
  minutes** (not 100% — a rising percentage), with under-5-minutes and median as secondary metrics.
  **Measured in business hours only** — overnight replies don't count against the tracker.
- **The Smartlead positive-reply Slack alert is STILL broken** six days after it was first logged. *(Oct 5: Gaston says the alert was later **killed on purpose**, so it is no longer an open issue.)*
  Cause still unknown; no diagnosis attempted. New soft target: *"idealmente hoy o mañana."*
- **Separate design limitation, not a bug:** even when working, the alert fires **only on a lead's
  first positive reply**. Follow-up replies in an existing thread never notify, so the Master Inbox
  must still be checked manually. Gaston does not know how to change this.
- Taught the **post-booking Google Doc SOP**: when Near Bot tags you in the Sales channel, open the
  auto-filled doc immediately and manually complete the Cold Email Activity section, the Drive-hosted
  CV link, and the job URL.

## Key Decisions
- **Referral requests are a separate track from AE sales calls.** Gaston escalates to Andrés and
  Daniel to establish who owns a referral conversation before Lila replies; fallback is booking a
  normal AE call.
- **On-site posts that are remote-capable by nature stay in the list.** The Outside Sales Rep post
  said on-site, but Gaston ruled the role remote-capable: acknowledge the posting, pitch remote LATAM
  on cost-savings and no-cost-to-evaluate grounds, and **keep the lead Interested** — only downgrade
  to Unqualified if they push back.
- **Roles on-site *by nature*** (e.g. nursing assistant) get their title added to the Clay exclusion
  list so the next daily search skips them. Lila is now a reporting channel for that list.
- **Lila is not measured on reply time during her first days** while ramping.
- **CC the assigned AE on the Smartlead reply thread** when a call is booked, so lead and AE are in
  contact before the call.
- **Positive replies always take priority over doc completion**, but all of a day's booked-call docs
  must be finished that day, and always before the call itself.

## Why Reply Speed
Gaston's cited article stats: replying within 5 minutes gives **21x higher odds** of closing; after 5
minutes booking rate drops 80%; after 10 minutes it drops 400%. **He explicitly hedges that Near has
not measured an effect this large** — treat as directional motivation, not a Near benchmark.

## A Known Data-Quality Trap
The **Clay remote-role filter keyword-matches "remote"** in the job description, which false-positives
on posts saying *"this is an in-person role, not remote or hybrid."* The only mitigation is the manual,
iterative title-exclusion list — which is why Lila flagging leaks matters.

## Action Items
- **Gaston** — ask Andrés + Daniel who owns referral calls, then reply to Matt Gray →
  [[wiki/tasks/2026-09-10-resolve-referral-call-ownership]]
- **Gaston** — fix the positive-reply Slack alert → [[wiki/tasks/2026-09-04-fix-smartlead-positive-reply-slack-alerts]]
- **Gaston** — add Lila to the Smartly Positive Replies channel; send the reply-time article
- **Gaston** — share the Drive "Sample Profiles" folder
- **Lila** — reply to Moshe Furnestame; research ways to cut response time further

## Open Questions
- **Healthcare reimbursement and the bi-weekly Near meeting** are open items on Lila's onboarding
  sheet, deferred to a follow-up ~1 hour after this call. **No content on either was captured** in
  any recording this window.

**Source:** [Fathom recording](https://fathom.video/calls/818704052) · `recording_id: 181861588`
