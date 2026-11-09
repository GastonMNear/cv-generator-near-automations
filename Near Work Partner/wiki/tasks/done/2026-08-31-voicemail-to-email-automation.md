---
type: task
title: "Automate voicemail-to-email follow-up, sent from Ivan's inbox"
created: 2026-08-31
updated: 2026-10-19
priority: medium
status: done
completed: 2026-10-19
from-meeting: "[[wiki/meetings/2026-08-31-cold-calling-lists]]"
related: ["[[wiki/tasks/2026-08-24-justcall-metrics-via-api]]", "[[wiki/tasks/2026-08-31-expand-title-exclusions-cold-call-lists]]"]
sources: ["[[bibliography/2026-08-31 - Listas Cold Calling - Meeting]]"]
---

# Email the leads who only got a voicemail

Build a **Claude routine** (or a JustCall-native automation if one exists) that on weekdays, **every
1–2 hours**, hits the JustCall API for leads with the **"no contact / left voicemail"** disposition and
sends them a short email **from Ivan's own mailbox** — referencing the call attempt and offering a
booking link or callback number. **Drafting the subject line is part of this** — Daniel handed that
thinking to Gaston explicitly.

**Why:** Proven live on the call — a prospect **emailed back mid-meeting asking for a booking link**.
The lesson Daniel drew: *"we don't die on the call alone"*, multi-channel is required. A voicemail is
currently a dead end.

**Deliberately not assigned to Ivan.** He must stay at **800 dials/day**, so the work lands on Gaston
as automation rather than on Ivan as manual follow-up.

**Done =** voicemail-dispositioned leads receive an email from Ivan's inbox without manual work.

**Timing:** Gaston scoped it to **later in the week** — he wanted to launch the pending email items
first. No firm date. **Needs a date from Gaston.**

> "Yo lo puedo hacer también, pero bueno, más a fin de la semana creo, porque ahora quiero tratar de
> lanzar las cosas que tenemos pendientes de email"
> *"I can do it too, but more toward the end of the week I think, because right now I want to launch
> the pending email items."*

**Ivan's side:** he creates a Gmail filter/label for the JustCall emails so his inbox stays usable.

**Source:** [[wiki/meetings/2026-08-31-cold-calling-lists]] · [Fathom @45:00](https://fathom.video/calls/805161647?timestamp=2700)

---

## Update 2026-09-28

**Gaston's Sep 28 status: ❌ not done** ("add Ivan's inboxes to Smartlead; configure subsequences to re-activate those leads"). **Sep 15**: framed in the deck as the "multi-channel follow-up infrastructure" item, running on the 17 Ample-Market inboxes [@50:56](https://fathom.video/calls/824198711?timestamp=3056). **Sep 18**: runs from Smartlead with Lila on replies, attribution deferred, **deprioritised behind the Clay investigation** [@21:00](https://fathom.video/calls/827666818?timestamp=1260).

*From fathom-task-sync run 9 (Sep 14–25 meetings) + Gaston's Sep 28 status.*

## Update 2026-10-05

**Rescheduled Sep 29 onto CallTools.** Once the API feed lands, an automation pulls the leads CallTools left a voicemail for and sends them follow-ups. Daniel: *"mañana podrías programar la automatización"*. Gaston: *"Ah, hacerlo mañana, sí… No puedo prometerlo, pero voy a intentarlo"* (I can't promise, but I'll try). Target Sep 30, hedged, now past. [@12:08](https://fathom.video/calls/840247722?timestamp=728). Sep 30 he bundled an *"email forward, ida y vuelta"* with the CallTools work, possibly this ([@50:00](https://fathom.video/calls/844117752?timestamp=3000)). **Caveat:** CallTools isn't leaving pre-recorded voicemails yet (see [[tasks/2026-09-02-diagnose-voicemail-gap]]), so there may be few voicemail leads to follow up.

*From fathom-task-sync run 10 (Sep 28 – Oct 1 meetings).*

## Status 2026-10-05 (Gaston)

**Not done.** Still open.

## Status 2026-10-13 (Gaston)

**❌ Not done last week. Back on this week's focus.** Done since then: the analysis of automatic lead upload from CallTools to Smartlead ✅, which is the input this automation runs on. Oct 5 stand-up: Andrés was to sync with Carlos on CallTools lists/dispositions to unblock the pre-recorded voicemail + auto email follow-ups (Fathom action item, Marketing Stand Up 189592482 @07:56; not transcript-verified).

## Done 2026-10-19 (Gaston)

✅ Automated email follow-ups from Ivan's side to leads who got a voicemail. The cold-calling follow-up *campaigns* are still to design → [[wiki/tasks/2026-10-19-design-cold-calling-followup-campaigns]]. Reported in Gaston's week-of-Oct-12 focus recap.
