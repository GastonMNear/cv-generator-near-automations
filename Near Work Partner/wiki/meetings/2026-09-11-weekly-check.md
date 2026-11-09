---
type: meeting
title: "Weekly check — cold calling, voicemail motion, experiment 12"
date: 2026-09-11
recording_id: 182391956
fathom-url: https://fathom.video/calls/818357203
attendees: [Gaston Murillo, Daniel Ardila, Ivan Valenzuela, Lila Lemus]
language: Spanish
tags: [meeting, weekly-check, cold-calling, email, experiments]
status: processed
related: ["[[wiki/meetings/2026-09-11-outbound-metrics-follow-ups]]", "[[wiki/meetings/2026-09-02-cold-call-reporting]]"]
sources: ["[[bibliography/2026-09-11 - Weekly Check - Meeting]]"]
---

# Weekly check — 2026-09-11

## TLDR

Weekly outbound review with Daniel, Ivan and Lila. **The headline is the voicemail discovery:** the
dialer logs a `VM Drop` column showing **1,197 voicemails in the last 7 days** — answering a question
Daniel had raised three times without resolution. Daniel immediately turned it into a motion: email
every lead who received a voicemail, from an Ivan-branded inbox, to drive **inbound** calls. That
needs ~30 domains/inboxes at **~$1,593/year**, and Gaston owes the budget in Slack. Cold calling is
improving on a bad ratio (3,047 dials, **79% machine pickups**, ~120 human contacts, but 2 meetings
booked from 5 role-play conversations). Experiment 12 / No-HM priority segments are producing positive
replies from Sales and Marketing and *appear* to beat baseline — Daniel does the formal readout Monday.
Month-to-date is **7 booked calls** (19 with the prior period), projecting 40–45 against a 47 record.
Lila's onboarding is **complete** and she is handling replies solo.

## Key Decisions

**Abandon TrueDial, migrate to CallTools.** Daniel takes the approval to Franco and Andrés. TrueDial
bills Oct 3 and has been double-charging ($25 plan-change charge, plus ~$20 parallel-dialing top-ups
2–3×/week). A month of overlap is accepted.
> *"Vamos a abandonar True Call y activar Call Tools, que cumple con todo lo que necesitamos."*
[@03:18](https://fathom.video/calls/818357203?timestamp=198)

**Build a voicemail → email follow-up motion.** Everyone who receives a voicemail gets an email from
an Ivan-branded inbox, so the callback lands as **inbound**. Sized at ~2,000 messages/week (~8,000/mo).
> *"que automaticemos al que le hayamos dejado un voicemail le mandemos un correo... y que eso genere llamadas inbound a ti"*
[@11:00](https://fathom.video/calls/818357203?timestamp=660)

**Reusing existing active inboxes was rejected** — both a deliverability-reputation risk and a brand
mismatch (*"me parece raro que te llegue un inbox de Hayden diciendo, Iván te llamó"*). Idle
ex-Ample-Market inboxes are the one permitted exception.
[@18:18](https://fathom.video/calls/818357203?timestamp=1098)

**CV-sent follow-ups go aggressive: ~5 consecutive daily touches**, not 3 spaced emails, plus later
spaced nurture touches asking about *new* openings (identifiable from Clay) rather than the original role.
> *"Pues hagámonos agresivos porque estamos a punto de cerrarlo, yo diría que hagamos aunque sea cinco días seguidos."*
[@37:00](https://fathom.video/calls/818357203?timestamp=2220)

**Experiment 12 judgment is deferred to Monday.** Too young to call. Daniel downloads all leads and
runs the comparative readout against baseline.
> *"Muy joven todavía, muy joven todavía."*
[@31:36](https://fathom.video/calls/818357203?timestamp=1896)

**Process learning — escalate to the group, not to one person.** Daniel's same-day follow-up blast was
blocked on Gaston's availability when it needn't have been.
> *"hubiera podido no pedirte el favor a ti, sino haber dejado el mensaje en el grupo... es un aprendizaje para todos"*
[@21:20](https://fathom.video/calls/818357203?timestamp=1280)

## Status Round-Up — what Gaston reported

**Done:**
- **LinkedIn Clay hiring-manager filter fixed** — a filter was cutting part of the HM leads, which is
  why Felix reported low volume. Fixed, but **not announced to Felix's group** at the time.
  [@08:16](https://fathom.video/calls/818357203?timestamp=502)
- **HM re-engagement campaign is sending.** [@27:00](https://fathom.video/calls/818357203?timestamp=1620)
- **Co-workers subsequence active.** RB2B active. All campaigns active with leads added since Wednesday.
- **Email timing fix + Slack reply notification** — *"eso está también."*
- **Routing fix for the old group** (last week and this week) — done.
- **All experiments through; positive + untracked reply handling handed to Lila.**

**Outstanding / blocked:**
- **Ghosted-leads upload → blocked on the Smartlead webhook limit.** Adding one webhook breaks another.
- **AI-field workflows for LATAM, Canada and Asia** — cause diagnosed, fix **not applied**, committed
  *"para la reunión"* rather than same-day.
- **Sara's Clay training** — she is stuck on an exercise Gaston sent; they need to meet.

## Metrics

| Metric | Value |
|---|---|
| Ivan's dials, week (vs 4,000 target) | ~3,047 *(Monday was a holiday)* |
| Machine pickups | **79%** — 2,419 of 3,047 |
| Human contacts | ~120 |
| **Voicemails dropped (VM Drop, 7d)** | **1,197** |
| Projected voicemail-email volume | ~2,000/week (~8,000/month) |
| Inboxes needed | ~26–27 → rounded to **30 domains / 30 inboxes** @ 15 sends/inbox/day |
| Domain cost | $11.10/yr each → $333/yr |
| Inbox cost | $3.50/mo each → $1,260/yr |
| **Total voicemail-motion budget** | **~$1,593/year** |
| Reusable ex-Ample-Market inboxes | 17 *(would leave 13 to buy)* |
| Booked calls MTD | **7** (+11 prior period = 19) |
| Projected month | 40–45 *(first 2 weeks historically = 40% of month)* |
| Record month / target | 47 / 60 |
| Engineering segment positive replies | 4 *(weakest segment)* |
| Positive-reply → booking | ~60 positives → ~10 bookings; ~30–40 of the other 50 get CVs |
| Current CV-sent cadence | 3 emails at day 1 / 2 / 3 gaps |
| Cold-call role plays | 2 completed; **2 meetings booked from 5 conversations** |

## Open Questions

- **Are the 17 ex-Ample-Market inboxes actually idle?** Determines whether 30 or only 13 inboxes get
  bought — a material swing on the $1,593 ask. **Gaston to resolve.**
- **How long does the centralizing Clay workflow take?** Daniel asked directly; Gaston answered
  *"capaz no tanto"* with no estimate. It unblocks several stalled items.
- **Is the Smartlead breakage genuinely a plan-level webhook cap?** Both treated it as a hypothesis —
  *"debe ser un límite... Puede ser, pero entonces no sé bien cómo ser."*
- **Is the No-HM copy really beating baseline, and is engineering's weakness real or a weak baseline?**
  Deferred to Daniel's Monday readout.
- **What exact copy for the extended CV-sent follow-ups?** Daniel sketched four angles (what happened /
  still open / shall I proceed / just say yes and I'll tell the team); nothing finalised.
- **Will Franco and Andrés approve** CallTools and the ~$1,593/year inbox spend?

## Waiting On

- **Daniel** — Franco/Andrés approval for CallTools; dispute the duplicate $25 TrueDial charge by email;
  **send Gaston the No-HM 50+ message doc** (CEO / HR / Head of Department lines) for Monday-early
  reading *(blocks Gaston)*; Monday experiment-12 comparative readout.
- **Franco + Andrés** — approve the inbox/domain spend *(blocks the whole voicemail motion)*.
- **Lila** — continues clearing replies; one item pending a conversation with Charly.
- **Ivan** — finish the week's dial target (640/800 at time of call).
