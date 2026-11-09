---
type: meeting
title: "Weekly 1:1 Gasti + Lila — Paz booking-link research, month-end record push, booked-call attribution walkthrough"
date: 2026-09-28
recording_id: 187426434
fathom-url: https://fathom.video/calls/838138117
attendees: [Gaston Murillo, Lila Lemus]
language: Spanish
tags: [meeting, one-on-one, booked-calls, attribution, outbound-metrics, hubspot, onboarding]
status: processed
related: ["[[wiki/meetings/2026-09-25-lila-sync]]", "[[wiki/meetings/2026-09-17-lila-sync]]"]
sources: ["[[bibliography/2026-09-28 - Weekly 1on1 Gasti + Lila - Meeting]]"]
---

# Weekly 1:1 Gasti + Lila — 2026-09-28

## TLDR

A ~40-minute Monday one-on-one. Most of it was Gaston walking Lila through how booked calls get
attributed to campaigns and dates in the Outbound Metrics sheet. **Booking link.** Paz has to check
whether a link that routes by employee count (as the website does) can work without building a new
HubSpot landing page. Gaston offered that he and Lila could do the research for her. Paz had not
answered yet, and Gaston said he would chase her the next day (Sep 29) if she stayed quiet.
**Numbers.** September stood at **42** booked calls against a monthly record of **47**, with Mon–Wed
left. About two a day would beat it, and none had booked yet that day. Last week booked **16**
(Command Center), a weekly record. Of those, **11** came in through a subsequence, and the routine
split them **7 same-week / 9 previous-week**. The routine showed 17 rows because Quieto, a returning
lead, was listed. Last week also had **9 calls held (4 qualified, 4 unqualified, 1 with no outcome
tag)** and **7 roles sourced, worth $63k ACV**. **The attribution process.** Command Center Import
is the source of truth. The weekly attribution routine gives each booker's campaign and booking date.
Gaston then types a 1 into *Calls Booked* in *Email Campaign Statistics Daily Update*, on the main
campaign's row (never the subsequence) for the **exact booking date**. Weekly and monthly totals come
from formulas. Done live, monthly went **26 → 42** and weekly **0 → 16**, which matched Command
Center. **Still owed to Lila:** the CNAME walkthrough and the Campaign Center linking/formulas, both
"in the next few days".

## Key Decisions

**Command Center Import is the source of truth for booked calls. A mismatch means fixing HubSpot,
not the sheet.**
> *"lo que dice acá que hay de calls booked es lo que nos van a contabilizar como calls booked."* (what this says for calls booked is what we'll be credited with)
[@11:53](https://fathom.video/calls/838138117?timestamp=713) · HubSpot rule [@12:35](https://fathom.video/calls/838138117?timestamp=755) · restated [@37:45](https://fathom.video/calls/838138117?timestamp=2265)

**A booking from a subsequence counts for the parent campaign, never the subsequence.**
> *"Las subsecuencias no las contabilizamos como Calls Book... la Calls Book se la voy a atribuir a Apolo."* (we don't count subsequences as booked calls; I credit it to Apollo)
[@18:12](https://fathom.video/calls/838138117?timestamp=1092)

**Only a contact's first booking counts.** That first booking is the one that creates the pre-sales deal.
> *"lo me interesa es cuándo fue la primer call que buqueó para crear el pre-sales deal."* (what matters is when they booked the first call that created the pre-sales deal)
[@21:58](https://fathom.video/calls/838138117?timestamp=1318)

**A call gets the exact booking date, not just any day in its week.** A week can straddle two months
(Sep 28 – Oct 4 does), and the monthly tab reads that date.
[@29:23](https://fathom.video/calls/838138117?timestamp=1763)

**Gaston and Lila research the routed booking link for Paz instead of waiting on her.**
> *"capaz nosotros lo podemos ayudar con ese research, como para acelerar un poco ese proceso."* (maybe we can help with that research to speed things up)
[@00:17](https://fathom.video/calls/838138117?timestamp=17)

**The automated follow-ups stay the default.** Lila only steps in by hand when a thread becomes
very specific.
[@03:16](https://fathom.video/calls/838138117?timestamp=196)

## Action Items

- **Gaston**: if Paz has not answered about the routed booking link, message her again on Sep 29,
  then pass her requirements to Lila for the research.
  [@00:17](https://fathom.video/calls/838138117?timestamp=17)
- **Gaston**: check the schedules of the three subsequences that sent on Sat/Sun (Sep 26–27) and,
  ideally, set them to weekdays only.
  [@22:26](https://fathom.video/calls/838138117?timestamp=1346)
- **Gaston + Lila**: meet "in the next few days" for the two leftover topics. One is the CNAME
  walkthrough. The other is linking Campaign Center to each campaign's monthly metrics section and
  building the missing formulas for new campaigns. Lila offered to help bring the page up to date.
  [@09:12](https://fathom.video/calls/838138117?timestamp=552) · [@38:46](https://fathom.video/calls/838138117?timestamp=2326)
- **Gaston** (done same day): fix the attribution routine so Quieto's repeat booking doesn't read
  as an error. The returning-lead exclusion already existed. On Sep 28 (commit `30e5415`) the sheet
  label changed from `REVIEW – PREV` to `RETURNING – first booked <date>`.
  [@19:55](https://fathom.video/calls/838138117?timestamp=1195)
- **Lila**: test the inbox warm-up skill regularly this week, finish Daniel's request (she expected
  to finish it that day), and keep doing email replies.
  [@02:22](https://fathom.video/calls/838138117?timestamp=142) · [@38:25](https://fathom.video/calls/838138117?timestamp=2305)
- **Lila**: save the Outbound Metrics tracker as a favourite. It is where metrics and Daniel's data
  requests get answered. [@38:46](https://fathom.video/calls/838138117?timestamp=2326)

## Context

- **Why the routed link matters:** AE availability is set up in HubSpot by employee-count range.
  The website's landing page asks for headcount and shows the matching calendar. Putting a link like
  that in the follow-ups *"estaría muy copado"* (would be great). See
  [[wiki/tasks/done/2026-09-17-ask-paz-size-routed-booking-link]].
  [@00:17](https://fathom.video/calls/838138117?timestamp=17)
- **Seasonality:** September was slow apart from last week. Gaston expects Q4/Q1 to be the strongest
  period, and this week's follow-ups go to last week's leads.
  [@06:20](https://fathom.video/calls/838138117?timestamp=380)
- **The weekly routine** (the `booked-call-attribution` skill) runs every Monday. It pulls Email
  Outreach bookings from HubSpot and matches each booker to Smartlead campaigns and their first
  reply. The *Email Lead Conversion Analysis* tab began with the Aug 24–30 week. Worked examples:
  Megan Hindrum first replied and booked on Sep 21 (SAME). A lead who first replied on Sep 14 and
  booked on Sep 21 counts as PREV. [@13:00](https://fathom.video/calls/838138117?timestamp=780) · [@19:55](https://fathom.video/calls/838138117?timestamp=1195)
- **Typing the calls in by hand takes about 10 minutes a week**, because Gaston hasn't found a
  reliable way to automate it. It usually happens Monday morning, once Sales has updated Command
  Center. [@25:14](https://fathom.video/calls/838138117?timestamp=1514)
- **Last week by campaign (weekly tab):** US OJ No-HM 2, US OJ HM (now running as Exp 6) 1, TAM HM 3,
  Canada HM 2, RB2B 1, among others. [@37:00](https://fathom.video/calls/838138117?timestamp=2220)
- **Searching the Daily Update for a campaign can land on an old campaign.** One booker had been
  contacted again under Experiment 12, so Gaston credited it to Sales GTM. He also caught one call
  he had entered by mistake and removed it. [@29:23](https://fathom.video/calls/838138117?timestamp=1763) · [@36:11](https://fathom.video/calls/838138117?timestamp=2171)
- **Campaign Center has fallen behind.** Rows for new campaigns have empty metrics and aren't linked
  to their *Email Campaign Metrics Monthly* sections. It gets updated when a campaign launches or
  pauses. [@09:12](https://fathom.video/calls/838138117?timestamp=552)
- There are also imports from SAM (LinkedIn) and possibly MyWorld. Only Command Center Import
  matters for cold email.

## Open Questions

- **What does Paz need to check, and can the link work without a new HubSpot landing page?** She
  hadn't replied as of the call.
- **Who adds the missing outcome tag on the 9th call held last week?** Qualified + unqualified +
  long-term should equal calls held, and one is untagged. Gaston blamed whoever is responsible
  (garbled as "los seis"). Nobody was assigned. [@13:00](https://fathom.video/calls/838138117?timestamp=780)
- **Which three subsequences sent at the weekend?** They were on screen, not named.
- **Did September beat 47?** It needed about 6 bookings Mon–Wed.
- **Can the Daily Update's Calls Booked column be automated?** No reliable method yet.
