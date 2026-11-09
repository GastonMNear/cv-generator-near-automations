---
type: meeting
title: "Weekly Metrics & Optimization — broken Smartlead subsequences, CallTools FDNC block, Ivan out of leads"
date: 2026-09-29
recording_id: 187888026
fathom-url: https://fathom.video/calls/840247722
attendees: [Gaston Murillo, Daniel Ardila, Ivan Valenzuela, Lila Lemus]
language: Spanish
tags: [meeting, weekly-metrics, smartlead, subsequences, calltools, cold-calling, fdnc, rb2b, dmu, experiment-12]
status: processed
related: ["[[wiki/meetings/2026-09-22-weekly-metrics-optimization]]", "[[wiki/meetings/2026-09-25-lila-sync]]", "[[wiki/meetings/2026-09-15-weekly-metrics-optimization]]"]
sources: ["[[bibliography/2026-09-29 - Weekly Metrics Optimization - Meeting]]"]
---

# Weekly Metrics & Optimization — 2026-09-29

## TLDR

A ~33-minute weekly with three fires and one win. **The win:** of the **16 calls booked last week, 10
came from earlier weeks' replies**, and **9 of those 10** were from before last week and had received
the **hard follow-up**. Daniel reads that as proof the hard follow-up works and wants to keep pushing it.
**Fire 1: Smartlead subsequences.** Lila found that only about **half of the 27 campaigns** still had
their follow-up subsequences. The rest had vanished. Gaston thinks the cause was the AI-assisted
deletion of the one-off *Weekends Follow Up* subsequence, which likely wiped the other campaigns'
subsequences too. Lila is rebuilding them with Claude (~50% done: info-request follow-up in progress,
interested follow-up still to do) and sending manual follow-ups meanwhile. Daniel made it **priority #1**
and wants a video walkthrough once it's fixed. **Fire 2: CallTools.** Most loaded leads are being
dropped by the **Federal Do Not Call (FDNC)** filter, so Ivan ran out of his ~200 leads and sat idle.
Pick-up rate is far below JustCall, CallTools isn't leaving pre-recorded voicemails, and its reports
don't break down outcomes. The FDNC fix is a form only the account owner (**Hayden**) can submit, and
login needs an emailed code. Gaston will ask Hayden. Daniel called it **"priority 0001"**. As a stopgap,
Daniel said to use **JustCall single-dialing** for a few days. **Fire 3: lead feed.** Gaston committed
to finishing the **CallTools API** lead load **that day**, with the voicemail follow-up automation the
next day, and hedged on the deadline. **Also:** RB2B DMU is "done and scheduled" but Gaston hadn't
checked sends. Clay credits are running out (both he and Daniel messaged Andrés). In Exp 12,
**Engineering has 7 positive replies on ~1,700 leads but zero bookings**, while Sales (9 / ~1,900) and
Marketing (3) have booked. Lila is analysing why. A call was booked during the meeting.

## Key Decisions

**Fixing the Smartlead subsequences is priority #1.**
> *"si me dice que eso está roto, prioridad número uno, arreglar eso."* (if it's broken, priority number one is fixing it)
[@05:14](https://fathom.video/calls/840247722?timestamp=314)

**Leads that missed their subsequence get re-triggered, not just followed up by hand.** They are moved to
Interested and back to their original category, because the subsequence only fires when the category is
assigned. Lila's manual first follow-up is fine, but the later steps should run from the subsequence.
> *"habría que volver a pasarlos a interested y volver a pasarlos a la categoría que tenían."* (move them back to Interested and then to the category they had)
[@07:30](https://fathom.video/calls/840247722?timestamp=450) · [@08:48](https://fathom.video/calls/840247722?timestamp=528)

**Fixing the FDNC block in CallTools is "priority 0001", ahead of everything except the subsequences.**
> *"Eso queda prioridad número 0001, mientras Lila termina de solucionar los email sequence."* (that's priority 0001 while Lila finishes fixing the email sequences)
[@24:07](https://fathom.video/calls/840247722?timestamp=1447)

**JustCall single-dialing as a temporary fallback** while the FDNC issue is fixed for good.
[@02:19](https://fathom.video/calls/840247722?timestamp=139)

**CSV uploads to CallTools are a one-off.** Ivan loads today's leads by hand (tag
*US Open Jobs Hiring Managers*), with Gaston walking him through it, because the API integration is
meant to make it automatic from then on.
> *"la idea es que hoy ya quede hecha la integración para que suceda automático"* (the idea is the integration is done today so it happens automatically)
[@10:01](https://fathom.video/calls/840247722?timestamp=601) · [@10:46](https://fathom.video/calls/840247722?timestamp=646)

**Daniel writes the copy for the new non-hiring-manager experiment; Gaston works out the operations.**
The new segment is routed by the *lead's* title (HR to one table, founders to another), not by the job
posting, so the workflows would need rebuilding.
> *"me voy a sentar a hacer la nueva propuesta de copywriting mientras tú vas pensando cómo operativamente funciona"* (I'll sit down and do the new copy proposal while you think through how it works operationally)
[@32:35](https://fathom.video/calls/840247722?timestamp=1955) · routing idea [@29:00](https://fathom.video/calls/840247722?timestamp=1740)

## Action Items

**Gaston**
- Finish the **CallTools API** integration so leads load automatically (no more CSVs). *"Hoy se va a
  llegar."* (it'll get there today) [@11:26](https://fathom.video/calls/840247722?timestamp=686) · [@11:39](https://fathom.video/calls/840247722?timestamp=699)
- Next day: schedule the automation that pulls voicemail-left leads for follow-up. Hedged: *"No puedo
  prometerlo, pero voy a intentarlo"* (can't promise, but I'll try). [@12:08](https://fathom.video/calls/840247722?timestamp=728) · [@12:32](https://fathom.video/calls/840247722?timestamp=752)
- Get the CallTools email code from **Hayden**, submit the **FDNC** form as account owner, and tell
  Daniel before messaging Hayden. [@19:25](https://fathom.video/calls/840247722?timestamp=1165) · [@23:00](https://fathom.video/calls/840247722?timestamp=1380) · [@24:07](https://fathom.video/calls/840247722?timestamp=1447)
- With Ivan: email **CallTools support** (cc'ing past Chase, the sales contact) about pre-recorded
  voicemails, outcome breakdowns in reports, and making Ivan admin while he's an agent. [@15:30](https://fathom.video/calls/840247722?timestamp=930) · [@17:14](https://fathom.video/calls/840247722?timestamp=1034)
- Run Daniel's RB2B and hiring-manager/DMU conversion prompts in Clay once he sends them, and return the
  results. [@32:35](https://fathom.video/calls/840247722?timestamp=1955)
- Same day: send Ivan today's CSVs and load them with him; check RB2B DMU sends and confirm to Daniel;
  message Andrés about Clay credits; send Daniel the list of high human-hours processes on Slack.
  [@10:01](https://fathom.video/calls/840247722?timestamp=601) · [@13:10](https://fathom.video/calls/840247722?timestamp=790) · [@13:26](https://fathom.video/calls/840247722?timestamp=806) · [@23:00](https://fathom.video/calls/840247722?timestamp=1380)

**Lila**
- Finish rebuilding the missing subsequences (interested follow-up still pending), re-trigger affected
  leads, then record a walkthrough video. [@05:32](https://fathom.video/calls/840247722?timestamp=332) · [@07:23](https://fathom.video/calls/840247722?timestamp=443)
- Qualitative analysis of the **7 Engineering positive replies** in Exp 12 (CV requests? in the hard
  follow-up?) and message Daniel. [@26:34](https://fathom.video/calls/840247722?timestamp=1594) · [@27:56](https://fathom.video/calls/840247722?timestamp=1676)

**Daniel**
- Send Gaston the RB2B and DMU analysis prompts (Wednesday end of day). [@32:35](https://fathom.video/calls/840247722?timestamp=1955)
- Write the copy proposal for the new non-HM experiment. [@32:35](https://fathom.video/calls/840247722?timestamp=1955)

**Ivan**
- Get CallTools running at full capacity this week: call Gaston, Chase and support as needed. [@25:22](https://fathom.video/calls/840247722?timestamp=1522)

## Context

- **Diarization is unreliable on this call.** Several of Gaston's answers are labelled Daniel (for
  example the "can't promise" at 12:32 and "I'll check the sends" at 13:10), and Daniel's hard
  follow-up data is labelled Lila at 03:55. Ownership above is based on content.
- **Ivan ran out of leads and went quiet**, which scared the team (the "stolen computer" opener).
  Daniel would rather send him a full two-week backlog than leave him idle. Gaston: they already load
  3–4× more leads than get called, but most are dropped by the FDNC list. [@18:05](https://fathom.video/calls/840247722?timestamp=1085)
- **The FDNC fix:** CallTools shows "FDNC calling has been disabled". The account owner has to tick a box
  and sign a form. Gaston tried and got locked out. Daniel has asked Chase to change the owner email
  from Hayden's to Andrés's. Hayden has said he wants no part of tooling and already pushed back when
  Gaston asked him for a code privately. [@19:25](https://fathom.video/calls/840247722?timestamp=1165) · [@21:00](https://fathom.video/calls/840247722?timestamp=1260) · [@22:38](https://fathom.video/calls/840247722?timestamp=1358)
- **CallTools quality:** pick-up rate is much lower than JustCall's, there's no visible breakdown of
  abandoned calls or other outcomes, and pre-recorded voicemail drops aren't working (Chase seemed to
  misunderstand the question). Earlier attempts to make Ivan admin while he's an agent failed. The
  "20 attempts" issue is reported solved. [@14:46](https://fathom.video/calls/840247722?timestamp=886) · [@15:30](https://fathom.video/calls/840247722?timestamp=930)
- **JustCall access:** Ivan can no longer dial from JustCall (errors). Felix gave Ivan's JustCall access
  to Mairol and Sam. Ivan booked a lead for Mairol on Pedro's calendar. [@01:24](https://fathom.video/calls/840247722?timestamp=84)
- **Retargeting lists produced nothing:** Gaston loaded two SBA retargeting lists to the dialer and got
  **0 leads**, possibly FDNC. The form-submissions list is still missing, and only one or two leads
  arrived. Two hiring-manager CSVs were sent; the non-hiring-manager CSVs were being prepared. [@30:21](https://fathom.video/calls/840247722?timestamp=1821) · [@31:01](https://fathom.video/calls/840247722?timestamp=1861)
- **Exp 12 by segment:** Marketing has small volume and 3 positives (~0.40%); Sales ~1,900 leads and 9
  positives (~0.45%); Engineering ~1,700 leads and 7 positives. Sales and Marketing have booked calls,
  Engineering hasn't. That's why Daniel no longer wants to rewrite the Engineering email 1. [@26:34](https://fathom.video/calls/840247722?timestamp=1594)
- **The non-HM market:** Gaston predicted this a year ago (November). At the time he chose to bundle
  everything together. Now it needs title-based routing and rebuilt workflows. He admitted it's a chore. [@29:00](https://fathom.video/calls/840247722?timestamp=1740) · [@29:46](https://fathom.video/calls/840247722?timestamp=1786)
- **Sara:** the latest session finished covering all the workflows. Gaston has handed her Clay table
  maintenance but thinks she's far from handling something like the new routing. Daniel: go slowly.
  [@31:01](https://fathom.video/calls/840247722?timestamp=1861) · [@32:35](https://fathom.video/calls/840247722?timestamp=1955)
- **Felix and the Clay bases:** nobody knows if he's using them. He said Mairol would start. [@13:48](https://fathom.video/calls/840247722?timestamp=828) · [@14:30](https://fathom.video/calls/840247722?timestamp=870)
- **A mistaken booking:** Randy Simonian booked, then emailed because he thought Lila was trying to
  hire him. [@03:35](https://fathom.video/calls/840247722?timestamp=215)
- **Daniel's repeated ask:** *"que me cierres los loops"* (close the loops with me) so he isn't caught
  out in his own meetings. [@13:10](https://fathom.video/calls/840247722?timestamp=790)

## Open Questions

- **What actually deleted the subsequences?** Gaston's theory (the AI-assisted Weekends Follow Up
  cleanup) is unconfirmed. Lila was still looking for the root cause.
- **Can the FDNC form be submitted without Hayden?** That depends on whether the owner email change to
  Andrés goes through.
- **Why is the CallTools pick-up rate so low?** Too many attempts, configuration, or something else.
  Ivan couldn't tell from the reports.
- **When do the Clay credits get topped up?** It's with Andrés. No answer during the call.
- **When are Daniel's prompts due back?** He said "end of day, or Saturday, or Thursday". No firm date.
- **How will the non-HM experiment be routed and staffed?** It would mean rebuilding the workflows. No
  owner or date beyond Gaston "thinking it through".
