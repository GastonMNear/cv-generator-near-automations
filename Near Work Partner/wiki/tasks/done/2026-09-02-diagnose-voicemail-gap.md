---
type: task
title: "Diagnose the machine-pickup vs voicemail-left gap"
created: 2026-09-02
updated: 2026-10-05
priority: medium
status: done
completed: 2026-10-05
from-meeting: "[[wiki/meetings/2026-09-02-cold-call-reporting]]"
related: ["[[wiki/tasks/2026-08-31-voicemail-to-email-automation]]"]
---

# ~3,269 machine pickups, ~301 voicemails left — why?

The cold-call data shows **1,780–3,269 machine pickups** across different windows against only
**118–301 voicemails actually left**. Root cause was never found in a 76-minute review.

**Why it matters:** machine pickups are 75% of all dials. If most of them could carry a voicemail and
don't, that is the single largest untapped touch volume in the cold-call channel — and it silently
inflates any rate computed off dials. Daniel raised it **three separate times** without resolution:
*"no sé por qué putas no estamos dejando los 3.269 voicemail... no sé si hay un límite o algo, no lo sé."*

**Partial explanations surfaced, none quantified:**
- **Silent calls** — Ivan revealed he'd been classifying these as "no contact / left voicemail" without
  knowing where they belonged. One bucket of 301 was **all** silent calls.
- **Full mailboxes** — *"the mailbox is full and cannot accept any messages"* heard on a recording.
- **Possible platform limit** on voicemail drops — unverified, and the reason for the JustCall support call.

**Owner note:** the JustCall support call is **Ivan's** to book (voicemail limits + how to change
dispositions). Fathom's summary claimed Gaston should be invited; **the transcript does not say that** —
*"metámonos"* was addressed to Ivan and Daniel. Worth joining anyway given the API question.

**A second unanswered question from the same thread:** Daniel asked whether attempts 1, 2 and 3 should
leave *different* voicemails, having noticed many third attempts leaving identical ones. **Nobody
answered.** That's adjacent to [[wiki/tasks/2026-08-31-voicemail-to-email-automation]].

**Timing:** No date stated; punted to the JustCall support call.

**Source:** [[wiki/meetings/2026-09-02-cold-call-reporting]] · [Fathom @14:25](https://fathom.video/calls/807325013?timestamp=865)

---

## Update 2026-09-11 — largely RESOLVED: the VM Drop column was there all along

The weekly check found the answer. **The dialer call logs carry a `VM Drop` column**, and it shows
**1,197 voicemails dropped in the last 7 days** — against ~3,047 dials and 2,419 machine pickups.

> *"hay una columna, la columna dice VM Drop... Se han dejado 1,197... En los últimos siete días."*

**So the gap was mostly a reporting gap, not an execution gap.** The earlier figures (~301 voicemails
against ~3,269 machine pickups) were reading the wrong source. ~1,197 of ~2,419 machine pickups
carrying a voicemail is roughly **half**, not the near-zero the old numbers implied.

**What this does NOT resolve:**
- Why the other ~half of machine pickups still get no voicemail (full mailboxes, silent calls, and a
  possible platform cap remain unquantified).
- Daniel's second question — whether attempts 1, 2 and 3 should leave **different** voicemails.
  Still unanswered.

**Consequence: the number immediately became a growth motion.** Daniel sized the voicemail→email
follow-up off this figure — see [[wiki/tasks/2026-09-11-voicemail-motion-inbox-budget]] and
[[wiki/tasks/2026-08-31-voicemail-to-email-automation]].

**Recommend closing this** and tracking the residual half-gap under the voicemail-to-email work, unless
Gaston wants the remaining ~1,200 silent pickups chased separately.

**Source:** [[wiki/meetings/2026-09-11-weekly-check]] · [Fathom @13:07](https://fathom.video/calls/818357203?timestamp=787)

## Update 2026-10-05

**Reopened by the dialer switch (Sep 29).** CallTools isn't leaving pre-recorded voicemails like JustCall did, its reports don't break down outcomes, and its pick-up rate is far below JustCall's. *"Aquí no los tiene. Entonces tampoco está dejando voicemails"* ([@15:30](https://fathom.video/calls/840247722?timestamp=930)). Daniel asked Ivan and Gaston to email CallTools support (see the run report). The JustCall VM Drop resolution no longer applies.

*From fathom-task-sync run 10 (Sep 28 – Oct 1 meetings).*

## Closed 2026-10-05

**Not Gaston's task.** Per Gaston (Oct 5) this belongs to Carlos/Ivan (dialer side). Removed from his board, not completed by him.
