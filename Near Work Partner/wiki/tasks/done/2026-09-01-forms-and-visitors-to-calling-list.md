---
type: task
title: "Feed the cold-calling list from all website form submissions and RB2B visitors"
created: 2026-09-01
updated: 2026-10-19
priority: medium
status: done
completed: 2026-10-19
from-meeting: "[[wiki/meetings/2026-09-01-leadership-deck-build]]"
related: ["[[wiki/tasks/2026-09-01-rb2b-backfill-and-reactivate-sends]]", "[[wiki/tasks/2026-08-31-daily-clay-sync-coldcall-lists]]"]
sources: ["[[bibliography/2026-09-01 - Leadership Deck Build - Meeting]]"]
---

# Route every non-client HubSpot contact into the calling list

Enrich and route **all** website form submissions — not just the free-consultation form —
plus **calendar-abandoners** and **RB2B visitors** with phone numbers into the cold-calling list.
**Prioritise form submissions**, which are the warmest of the three.

**Why:** Andres raised this directly on Aug 31. There is callable inbound volume being left unworked,
and Near is **already paying for the RB2B visitor data**. Gaston's own framing of the rule:
*"básicamente debería ser todo lo que llegue a HubSpot que no es cliente"* — anything reaching HubSpot
that isn't already a client is a callable lead.

**Deliberate wording:** this is a named deck initiative — *"Increase the calling list by adding leads
from all form submissions and visitors from the website"* — phrased as **"calling list" rather than
"inbound"** so credit isn't reassigned to another team. Keep that framing.

**Done =** non-client HubSpot contacts flow into the calling list with phone numbers, form submissions
first.

**Timing:** No date. Discussed as possibly landing by the next leadership meeting, with Daniel noting
*"Podemos cambiar la fecha"* — so the deck date is soft. **Needs a date from Gaston.**

> "cuando mandan el form, entonces tenemos una email sequence, lo que quiero es enriquecerles el form
> number para mandárselos a cold calling"
> *"when they submit the form we have an email sequence; what I want is to enrich their phone number
> and send them to cold calling."*

**Dependency:** the RB2B half of this is worthless until the broken webhook is fixed —
[[wiki/tasks/2026-09-01-rb2b-backfill-and-reactivate-sends]] and
[[wiki/tasks/2026-09-01-rb2b-integration-monitoring]].

**Source:** [[wiki/meetings/2026-09-01-leadership-deck-build]] · [Fathom @1:03:00](https://fathom.video/calls/806758340?timestamp=3780)

## Update 2026-09-02 — now dated: Thursday Sep 3
Daniel assigned this to **Thursday** (he first said Wednesday, then corrected himself). Gaston read the
scope back as: **cold calling — add all visitors, plus other form submissions, to campaigns.** That
answers the "needs a date from Gaston" note above.

**Still gated** on the RB2B webhook fix for the visitor half —
[[wiki/tasks/2026-09-01-rb2b-backfill-and-reactivate-sends]] — and now also on
[[wiki/tasks/2026-09-02-verify-form-submissions-clay-feed]], since the forms half is the part Daniel
flagged as possibly broken. **Form submissions first**, per the priority above.

**Source:** Huddle 2026-09-01 (Daniel + Gaston), ~[36:10]

---

## Update 2026-09-28

**Sep 15** — form submissions became Ivan's **top** calling priority (forms → HMs → No-HMs). 189 of 406 form leads had been called [@10:50](https://fathom.video/calls/824288870?timestamp=650). **Sep 18** — form follow-ups took over half of Ivan's day, leaving him at 3,538 dials vs the 4,000 target [@13:07](https://fathom.video/calls/827666818?timestamp=787). Retargeting lists are loaded in the new dialer (Gaston, Sep 28). **The lead flow is working, so this may be closeable.**

*From fathom-task-sync run 9 (Sep 14–25 meetings) + Gaston's Sep 28 status.*

## Update 2026-10-05

**Not closeable yet (Sep 29).** The dialer still has no form-submissions list (*"nos falta la de Subformation"*), and only one or two leads are coming in. The 2 SBA retargeting lists loaded into the dialer left **0 leads**, possibly because of FDNC ([@31:01](https://fathom.video/calls/840247722?timestamp=1861)). Sep 30: Chase has to swap Hayden's email for Andrés's and turn on a checkbox, tied to *"lo del formulario"* ([@37:05](https://fathom.video/calls/844117752?timestamp=2225)).

*From fathom-task-sync run 10 (Sep 28 – Oct 1 meetings).*

## Status 2026-10-05 (Gaston)

**Rescoped by Gaston.** His job is to **split form submissions and retargeting (RB2B visitors) into separate lists/campaigns** in the dialer, not one combined campaign. **Done =** form submissions and retargeting each feed their own CallTools list/campaign.

## Update 2026-10-06 (huddle to-do slide)

Two rows on the slide:
- **Carlos + Gaston:** review the calling lists so that **form submissions take priority no matter which list Carlos is calling**.
- **Split retargeting and form submissions into 2 separate Cold Calling campaigns.** The slide gives no owner. The vault has it as Gaston's, with Paz loading the lists.

**Done =** two CallTools campaigns (forms, retargeting), with forms always dialed first.

## Owner confirmed 2026-10-07 (Gaston)
**Gaston + Charlie** own this together, so it stays open on Gaston's list. Fathom's huddle summary credits the split and the 5-min form calls to Carlos alone, but Gaston's call overrides that.

## Update 2026-10-13

**Oct 5 Andrés sync (@42:42):** Gaston named the forms-vs-retargeting split into 2 cold-calling campaigns as pending. **Andrés wants Paz to own this kind of cold-calling/LinkedIn list admin**, so this is a candidate to hand to Paz.

## Update 2026-10-19

**Oct 13 huddle ([@01:46](https://fathom.video/calls/858323233?timestamp=106)):** Gaston said splitting the CallTools retargeting campaign into **Form Submissions + General Retargeting** is *"some setup that I need to do on Call Tools, which will be done and ready for today."* That makes it Gaston's, not Carlos's as the Oct 6 note said. **Done?** It was the only unfinished Oct 6 to-do.
*From fathom-task-sync run 12.*

## Done 2026-10-19 (Gaston)

✅ The forms vs retargeting split is done (Gaston).
