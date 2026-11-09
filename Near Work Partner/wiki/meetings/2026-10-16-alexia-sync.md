---
type: meeting
title: "Ale – Gasti sync: Viktor for Clay maintenance, onboarding docs, Tuesday live session"
created: 2026-10-19
updated: 2026-10-19
attendees: ["Gaston Murillo — Outbound", "Alexia Galeana Castro — helping Gaston (Clay/automation)"]
meeting-type: internal
duration-min: 20
recording_id: 193609565
fathom-url: "https://fathom.video/calls/865028769"
tags: [type/meeting, meeting-type/internal]
status: mature
related: ["[[wiki/meetings/2026-10-09-alexia-sync]]", "[[wiki/meetings/2026-10-09-sara-clay-workflow-maintenance]]"]
sources: ["[[bibliography/2026-10-16 - Alexia Sync - Meeting]]"]
---

# Ale – Gasti sync — 2026-10-16

*(Fathom title: "Ale <> Gasti". Conducted in Spanish, with some English from Alexia. ~20 min. Diarization drifts in places; ownership below is grounded in content.)*

## TLDR
- **Docs still not sent:** Gaston opened by admitting he never sent Alexia the **consolidated training doc** [@00:15](https://fathom.video/calls/865028769?timestamp=15). The **Sara training recordings were already sent** [@11:02](https://fathom.video/calls/865028769?timestamp=662). He also offered the **Loom videos he recorded for Viktor** on row/source maintenance. At sign-off Alexia asked him to promise the manuals, and he said *"dale, lo paso"* ("ok, I'll send it") [@18:55](https://fathom.video/calls/865028769?timestamp=1135).
- **First automation target = daily Clay table maintenance**, which Sara now owns 100% and which is repetitive (~20 min/day). Gaston restated the two separate **50k limits**: rows per table and records imported per source. Hitting either one stops the workflow. The fix is to export unwanted rows to CSV in Drive and delete them, or delete the source and recreate it so the count resets [@04:00](https://fathom.video/calls/865028769?timestamp=240). The workflow list changes over time, so the agent should pick workflows dynamically, e.g. skip anything tagged "old". Viktor already did that on its own.
- **Viktor test workflow is NOT done.** Gaston connected Viktor to Clay, recorded the Looms and got a batch of questions back, then *"ahí quedó"* ("it stalled there"). The plan is still: build a **test workflow**, validate Viktor on it, and only then give it permission on production workflows. He committed to *"termino este tema con Víctor y le creo el workflow este de pruebas"* ("I'll finish the Viktor thing and create the test workflow") [@17:10](https://fathom.video/calls/865028769?timestamp=1030). **This contradicts the Oct 13 ✅ "test workflow created and validated".**
- **Viktor vs Claude Code:** Alexia finds Viktor much easier to connect. She asks Franco for a permission and he grants it, while Claude Code needs APIs and code setup. She uses it for daily HubSpot meeting-source checks and duplicate-company cleanup. **Deletions go through a Slack approval with a summary of the criteria** [@08:22](https://fathom.video/calls/865028769?timestamp=502).
- **Sara-departure risk:** Alexia warned that Franco could say *"adiós, Sara"* any day (he gave a range, possibly within two weeks), and Gaston's workload won't let him take maintenance back [@09:18](https://fathom.video/calls/865028769?timestamp=558). This is the stated reason to speed up her ramp.
- **Live working session: Tue Oct 20, afternoon, after Alexia's lunch** [@15:59](https://fathom.video/calls/865028769?timestamp=959). Alexia says she has time because Viktor automated her biggest time sinks. She asked to be sent calendar invites directly rather than coordinating by message.

## Key Decisions
- Start with automating Clay maintenance via Viktor: test workflow first, production permission only after validation.
- Alexia ramps on Clay in parallel (recordings via AI transcripts, then live/joint build sessions) so she can build workflows and campaigns too.
- Practical live session set for **Tue Oct 20 afternoon**.
- Alexia gets **her own login, not a shared one**. Gaston: *"no, te paso los tuyos... te mando un invite al mail"* ("no, I'll give you your own... I'll send an invite to your email") [@18:55](https://fathom.video/calls/865028769?timestamp=1135). The tool isn't named, but the context is Clay.

## Action Items
**Gaston**
- [ ] Send Alexia the consolidated training doc / manuals + the Viktor maintenance Loom links [@00:15](https://fathom.video/calls/865028769?timestamp=15), [@18:55](https://fathom.video/calls/865028769?timestamp=1135)
- [ ] Finish the Viktor setup: create the Clay test workflow and validate Viktor on maintenance before production access [@17:10](https://fathom.video/calls/865028769?timestamp=1030)
- [ ] Run the live Clay working session with Alexia, Tue Oct 20 afternoon [@15:59](https://fathom.video/calls/865028769?timestamp=959)
- [ ] *(in-call)* Email Alexia an invite for her own account [@18:55](https://fathom.video/calls/865028769?timestamp=1135)

**Alexia**
- [ ] Go through the Sara training recordings. She added them to her to-do list, and Gaston suggested feeding them to an AI and reading them [@12:48](https://fathom.video/calls/865028769?timestamp=768)
- [ ] Message Gaston with doubts. She also offered to help with Viktor.

## Context
- Fathom's action items (doc + Looms, Viktor test workflow, "email Clay credentials") match the transcript. The "credentials" item is a **per-user account invite to Alexia's email**. No credential values were spoken or shared in the call.
- This bears on the Oct 9 ⚠️ (2FA disabled on a shared account so Sara + Ale could log in): Alexia getting her own seat reduces the need for the shared login.
- Alexia's "mil dólares al día" ("a thousand dollars a day") rates line was a joke.

## Open Questions
- Is Sara actually leaving, and when? Franco "gave a range". If she leaves, daily Clay maintenance has no human owner unless Viktor or Alexia is ready.
- Was any Viktor test workflow ever built? The Oct 13 ✅ and this call disagree.
- Once Alexia has her own seat, should 2FA be re-enabled on the shared account?
- Alexia's formal scope is still not defined by Franco. Gaston's framing: automations + new workflows/campaigns in Clay.

## Full Transcript
See Fathom: https://fathom.video/calls/865028769
