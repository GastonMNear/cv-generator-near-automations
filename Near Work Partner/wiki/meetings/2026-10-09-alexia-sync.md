---
type: meeting
title: "Ale – Gasti sync: Alexia Galeana's Clay onboarding and what to automate first"
created: 2026-10-13
updated: 2026-10-13
attendees: ["Gaston Murillo — Outbound", "Alexia Galeana Castro — moving to help Gaston (Clay/automation)"]
meeting-type: internal
duration-min: 42
recording_id: 191355753
fathom-url: "https://fathom.video/calls/855003268"
tags: [type/meeting, meeting-type/internal]
status: mature
related: ["[[wiki/meetings/2026-08-18-kpi-deck-prep]]"]
sources: ["[[bibliography/2026-10-09 - Alexia Sync - Meeting]]"]
---

# Ale – Gasti sync — 2026-10-09

*(Fathom title: "Ale - Gasti Sync". Conducted in Spanish. The recording starts mid-conversation; the first ~11 min are one long Gaston segment.)*

## TLDR
- **Who Alexia is:** Franco has been telling her for ~3 months that she would move over to help Gaston, but gave her **no brief at all** [@11:17](https://fathom.video/calls/855003268?timestamp=677). She has an engineering degree and says she is no longer being used as a lawyer. She likes learning systems. Her exact title/team was not stated.
- **Where Gaston wants automation help:** start with **maintenance of the existing Clay workflows**, not building new ones. First step: a **read-only check** that each workflow ran, its steps happened and leads reached the campaign, alerting a human to fix it. Auto-fixing would be a second step. One-off campaigns (e.g. "contact this company's competitors") are easier to automate than the Open Jobs core, which has too much cross-table context and changes with every experiment. The workflow list must be dynamic (swap links when tables change).
- **Easy first candidate:** the **Apollo Open Jobs (200–500 employees) daily input**. Gaston's routine: update posting date on the saved search (last 3–4 days), Net New → export → CSV from email → *Import from CSV* into the Apollo Companies table → save and run. About 2 min a day. It was manual because the campaign was a trial. **It is now planned to be always-on.**
- **Clay walkthrough** (US No-HM Open Jobs): HM vs No-HM, source filters (remote in JD, US, full time, no recruiter, posted ≤1 day, max 10 roles/company), enrichments, AI web-research steps, variables, run conditions, HubSpot "can contact" check. Plus the **company-table dedup pattern**: send each company once to a deduped company table, enrich there, look it back up. This avoids paying N credits for N roles at one company (Alexia's question [@25:00](https://fathom.video/calls/855003268?timestamp=1500)).
- **Training approach agreed:** Gaston sends the **Clay playbook** (written) plus the **Sara training recordings** (~5 h; Alexia will read the transcripts). After that, live sessions. Sales also asks for Clay help (account expansion), which is another reason for her to learn it.

## Key Decisions
- Alexia's onboarding = Clay playbook + recordings first, then live/practical sessions.
- Automation focus is maintenance/monitoring of existing workflows, read-only first. Building new workflows comes later and is limited to one-offs.
- Apollo Open Jobs becomes an always-on campaign.

## Action Items
**Gaston**
- [ ] Send Alexia the Clay playbook + the Sara training recordings [@39:34](https://fathom.video/calls/855003268?timestamp=2374)
- [ ] *(implicit)* Tell Alexia clearly what she should own. She asked for this directly [@39:00](https://fathom.video/calls/855003268?timestamp=2340). Gaston: understand Clay first, then "veremos" what to automate or hand over.

**Alexia**
- [ ] Read the playbook / recordings and come back with questions.

**Follow-up:** Alexia proposed reconnecting **Monday**. The call closed with *"hasta el martes"* (long weekend), so the next touchpoint is **Tue Oct 13**.

## Context
- Same day, Gaston had a session with Paz to build a new campaign together so she learns Clay, and he runs ongoing training with Sara.
- Fathom's action items said "Monday follow-up". The actual sign-off says Tuesday.

## Open Questions
- Alexia's formal role/team, and whether Franco has defined her scope. Still undefined, as in [[meetings/2026-08-18-kpi-deck-prep]].
- Which Clay workflows go on the monitored list, and who acts on alerts (Paz already owns Clay campaign health).

## Full Transcript
See Fathom: https://fathom.video/calls/855003268
