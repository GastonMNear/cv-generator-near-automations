---
type: meeting
title: "Lila working session — Cheap Inboxes CNAMEs, warm-up skill first run, Chili Piper size routing"
date: 2026-10-01
recording_id: 188879561
fathom-url: https://fathom.video/calls/845936235
attendees: [Gaston Murillo, Lila Lemus]
language: Spanish
tags: [meeting, one-on-one, smartlead, deliverability, cname, inboxes, warm-up, skills, chili-piper, booking-link, onboarding]
status: processed
related: ["[[wiki/meetings/2026-09-28-lila-weekly-1on1]]", "[[wiki/meetings/2026-09-25-lila-sync]]", "[[wiki/meetings/2026-09-17-lila-sync]]"]
sources: ["[[bibliography/2026-10-01 - Lila CNAMEs Warm-up Chili Piper - Meeting]]"]
---

# Lila working session — 2026-10-01

*(Fathom titled this "Impromptu Google Meet Meeting".)*

## TLDR

A ~38-minute working session. It delivered the CNAME walkthrough Gaston had owed Lila since Sep 25 and
handed the CNAME fix to her. **CNAMEs.** Inside a Smartlead campaign, **166 inboxes** are flagged as
missing a verified CNAME (the custom tracking domain). Filtering by provider showed that **all 166 are
Cheap Inboxes** and **no Premium Inboxes** inboxes are flagged. Premium domains sit in Cloudflare with a
`trk` CNAME pointing at Smartlead's `open.sleadtrack.com`. Cheap Inboxes has **119 domains on the Near
account + 50 on Hayden's = 169**. Minus the **3 "Do not use"** inboxes, which aren't in any campaign,
that is exactly 166. So none of the Cheap Inboxes domains appears to have the record. Open/click
tracking isn't used (to protect the inboxes), but campaigns keep asking for it. **Fix:** Lila contacts
Cheap Inboxes support (WhatsApp, a +63 Philippines number) with both domain CSVs and a sample record,
and asks them to add the DNS records and set the tracking domain on each inbox. Done = the campaign's
CNAME alert count reads **0**. Gaston will not add records himself. He also set forwarding on the
Cheap Inboxes domains during the call to clear a separate error. **Warm-up skill first run** (Lila's
"Inbox Efficiency"): **507 inboxes**, **30 critical, 6 declining, 26 recovering, 3 data issue,
1 stable, 438 healthy**. Gaston approved every recommendation, cuts and step-ups alike (for example
72–75% → 3/day, 82% → 7, 85% → 10, 91% from 7 → 10, 95% from 5 → 7). Lila runs it **twice a week**
(reminders set for **Mon and Fri**) for two weeks. If it never needs correcting, it becomes a routine.
**Chili Piper:** Lila's research says one link can ask for company size, then round-robin across the
AEs. Gaston would go straight to that option. Lila sends a tidied step-by-step doc, and Gaston and Lila
take it to Paz with a 30-minute meeting for the three of them. **Next:** a final Smartlead handover pass
plus the metrics topic Gaston still owes, probably next week. After that Lila owns Smartlead in full.

## Key Decisions

**Cheap Inboxes support fixes the CNAMEs. Near does not edit the DNS itself unless support refuses.**
> *"Yo no lo voy a agregar, sino que te voy a mandar esta foto."* (I won't add it; I'll send you this photo)
[@14:45](https://fathom.video/calls/845936235?timestamp=885) · ask support to do it [@20:00](https://fathom.video/calls/845936235?timestamp=1200)

**Lila owns the CNAME fix.**
> *"de este tema te vas a encargar vos."* (you'll be handling this one)
[@14:45](https://fathom.video/calls/845936235?timestamp=885)

**The CNAME fix is done when the campaign shows zero CNAME alerts.**
> *"ahí debería aparecer cero."* (it should show zero there)
[@24:27](https://fathom.video/calls/845936235?timestamp=1467)

**The warm-up skill's first set of recommendations is approved as is.** Gaston liked that step-ups
go one rung at a time (5 → 7, not 5 → 15).
> *"para mí está ok, yo le diría que... y va."* (it's fine by me; I'd tell it to go ahead)
[@29:00](https://fathom.video/calls/845936235?timestamp=1740) · [@29:44](https://fathom.video/calls/845936235?timestamp=1784)

**Twice-weekly manual runs for two weeks, then a routine that applies the changes itself.** Cuts
matter more than step-ups, because catching a drop at ~80% instead of ~50% stops inboxes from burning.
> *"Si vemos que siempre las recomendaciones están bien y no delira... lo podemos armar como una rutina."* (if the recommendations are always right and it doesn't go off the rails, we can make it a routine)
[@30:04](https://fathom.video/calls/845936235?timestamp=1804) · [@32:07](https://fathom.video/calls/845936235?timestamp=1927)

**For the booking link, go straight to Chili Piper's single link with company-size routing.**
> *"si se puede hacer desde Chili Piper directo, sería un golazo."* (if it can be done straight from Chili Piper, it'd be a huge win)
[@34:38](https://fathom.video/calls/845936235?timestamp=2078) · [@35:44](https://fathom.video/calls/845936235?timestamp=2144)

**Lila becomes full owner of Smartlead after one more handover pass.**
> *"así quedás como la owner full de todo lo que pasa en Smartlead"* (so you end up full owner of everything in Smartlead)
[@36:46](https://fathom.video/calls/845936235?timestamp=2206)

## Action Items

- **Lila**: message Cheap Inboxes support on WhatsApp. Send both domain CSVs (Near 119, Hayden 50)
  and the sample CNAME record, and ask them to add the DNS records and set the custom tracking domain
  on each inbox. If they refuse, get their instructions and do it domain by domain. Then check that
  the campaign's CNAME alerts read 0.
  [@20:00](https://fathom.video/calls/845936235?timestamp=1200) · [@24:27](https://fathom.video/calls/845936235?timestamp=1467)
- **Gaston**: give support the OK if they ask (the account sits under his Google login).
  Conditional. [@23:45](https://fathom.video/calls/845936235?timestamp=1425)
- **Gaston** (done in or right after the call): send Lila the CSVs, screenshots, account access and
  support number. Set forwarding on the Cheap Inboxes domains.
  [@00:30](https://fathom.video/calls/845936235?timestamp=30) · [@23:07](https://fathom.video/calls/845936235?timestamp=1387)
- **Lila**: run the warm-up skill twice a week (Mon and Fri reminders) and apply its recommendations
  for two weeks. Then she and Gaston decide whether to make it a routine.
  [@30:04](https://fathom.video/calls/845936235?timestamp=1804) · [@32:07](https://fathom.video/calls/845936235?timestamp=1927)
- **Lila**: put the Chili Piper step-by-step into a clean doc and send it to Gaston.
  [@35:44](https://fathom.video/calls/845936235?timestamp=2144) · [@36:42](https://fathom.video/calls/845936235?timestamp=2202)
- **Gaston**: forward that doc to Paz and propose a 30-minute meeting for the three of them to get it
  set up. [@35:44](https://fathom.video/calls/845936235?timestamp=2144)
- **Gaston + Lila**: final Smartlead handover pass, plus the metrics topic Gaston owes, *"seguramente
  la semana que viene"* (probably next week, i.e. Oct 5–9).
  [@36:46](https://fathom.video/calls/845936235?timestamp=2206)

## Context

- **What a CNAME is here:** Smartlead's custom tracking domain. Each domain needs a DNS record
  `trk.<domain>` (type CNAME) pointing at `open.sleadtrack.com`. All the inboxes on that domain then
  use it. Example: `trk.talentbynear.com` on Cloudflare. Premium Inboxes domains (e.g.
  `gettalentnear.com`) show "CNAME verified". Cheap Inboxes domains (e.g. `connectwithnear.com`) have
  A/MX/TXT records but no CNAME. Cheap Inboxes is one inbox per domain, so the per-inbox setting is a
  one-to-one job. [@02:39](https://fathom.video/calls/845936235?timestamp=159) · [@08:13](https://fathom.video/calls/845936235?timestamp=493)
- **Why it hadn't come up before:** opens and clicks aren't tracked, *"queremos cuidar las inboxes"*
  (we want to protect the inboxes). Gaston thinks the records were never set at purchase or something
  changed at Cheap Inboxes. [@02:39](https://fathom.video/calls/845936235?timestamp=159) · [@14:45](https://fathom.video/calls/845936235?timestamp=885)
- **Support note:** Gaston has found Cheap Inboxes support good, but they're in the Philippines, so
  replies can come at night or the next morning. [@20:00](https://fathom.video/calls/845936235?timestamp=1200) · [@24:27](https://fathom.video/calls/845936235?timestamp=1467)
- **This closes the loop from Sep 25 and Sep 28,** where the CNAME walkthrough was promised.
  The Campaign Center linking/formulas part ("métricas") is still pending on Gaston's side.
- **Lila's work for Daniel is delivered.** The Experiment 12 diagnostics for engineering and the
  positive-reply trends analysis were both sent as docs. [@32:54](https://fathom.video/calls/845936235?timestamp=1974)
- **The skill output had a garbled scope line.** It read "104 in scope, 3 out", but the total was 507
  with 3 excluded (Do not use). Its status buckets add up to 504. A couple of background-task failures
  showed on start. [@28:04](https://fathom.video/calls/845936235?timestamp=1684) · [@28:22](https://fathom.video/calls/845936235?timestamp=1702)
- **Chili Piper layering:** one link, then a company-size question, then distribution across the
  AEs ("los 6") via flexible round robin, without showing which AE it is. It still needs a test.
  Related: [[wiki/tasks/done/2026-09-17-ask-paz-size-routed-booking-link]].
  [@33:13](https://fathom.video/calls/845936235?timestamp=1993) · [@35:18](https://fathom.video/calls/845936235?timestamp=2118)

## Open Questions

- **Will Cheap Inboxes support set the records and the per-inbox tracking domains, or only advise?**
- **Mon/Thu or Mon/Fri?** Gaston suggested Mon and Thu. Lila set reminders for Mon and Fri.
- **Is the CNAME needed at all, given opens and clicks aren't tracked?** Gaston's reason was
  *"por un tema de traqueo... o por lo que sea"* (for tracking, or whatever). Campaigns flag it either
  way, and the effect on deliverability wasn't discussed.
- **Does the Chili Piper route need HubSpot changes on Paz's side?** That's not yet tested.
- **Why did the skill print "104 in scope"?** It may be a display bug Lila should check.
