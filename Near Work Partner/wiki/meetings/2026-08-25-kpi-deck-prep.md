---
type: meeting
title: "KPI Deck Prep — No-HM Targeting Hypothesis & Slide Corrections"
created: 2026-08-25
updated: 2026-08-25
attendees:
  - "Daniel Ardila — Campaign strategy / reporting"
  - "Gaston Murillo — GTM Engineer / SalesOps"
meeting-type: internal
recording_id: null
fathom-url: null
tags: [type/meeting, meeting-type/internal]
status: mature
related: ["[[wiki/meetings/2026-08-24-marketing-standup]]", "[[wiki/meetings/2026-08-21-weekly-check]]", "[[wiki/meetings/2026-08-18-kpi-deck-prep]]"]
sources: ["[[bibliography/2026-08-25 - KPI Deck Prep - Meeting]]"]
---

# KPI Deck Prep — No-HM Targeting Hypothesis & Slide Corrections

> [!warning] **Not a Fathom recording.** Transcript pasted directly by Gaston, so there is no
> `recording_id` and no timestamped deep links. Quotes are from the pasted text.

## TLDR
- **The No-HM problem may be a targeting problem, not a copywriting problem.** Daniel's framing: the
  baseline works *supremely well* on hiring managers regardless of whether that's the functional
  owner or the CEO — but the copy **assumes the recipient is the hiring manager**, and in No-HM we
  don't know who is. "Estamos dando una ruleta rusa." Gaston added a second hypothesis: in companies
  over ~50, the process is usually run by **HR**, and HR is barely targeted (8.2% of No-HM leads).
- **Daniel's proposed fix — stop guessing, ask.** Rather than emailing 4–5 people hoping one is the
  manager, mail all of them and **ask them to point to the right person**. Once identified, send
  candidates: "una vez lo identifiquemos, le mandamos los candidatos y ahí funciona."
- **Volume target hit for the first time.** 23,900 emails sent last week ("por fin, felicitaciones").
  But positive replies came in at **67 against a 72 target**, and Daniel refused to call that close:
  "no estamos ahí. Necesito mejorar esos cinco putas números."
- **The experiment narrative needs correcting.** Of 10 experiments launched, only **6 have actually
  concluded** — none beat baseline. The other 4 are still young. Daniel wants this stated as a
  learning so nobody claims 30 things were tested.
- **LinkedIn's numbers are bad** (364; 0 booked for Samuel in the core arm) and Daniel is
  deliberately **not reviewing Felix's slides** any more — that ownership moves to Felix.
- Several slides carry **AI-generated numbers that are wrong** — the 7,000 new-open-jobs figure was
  invented, and the non-open-jobs email count (9,000) is roughly double Gaston's 4,500, likely
  because LATAM Open Jobs was split out as "others".

## Key Decisions
- **Kill the underperforming experiment**; the remaining experiments stay alive as too young to
  judge. Conclusion for the slide: be patient, wait for results.
- **Mail the full candidate set simultaneously** in No-HM with a routing ask, instead of sequential
  guessing. Under-50 companies get mailed **indiscriminately across HM and No-HM**, and Andres wants
  the same tried on hybrid managers to see if their rate improves.
- **Pause the rest of the account on booking, not on reply.** Gaston pushed back on pausing at first
  reply — a "not interested" from one person shouldn't kill outreach to the others. Daniel accepted:
  "menos cuando busqué entonces." Both agreed it needs more thought.
- **Cohorts must be activated** — "sí o sí toca activarla."
- **Active-test priority order** (agreed sequence): form submissions → people who ghosted us →
  hiring managers → No-HM under-50 **C-level only** (founders/presidents, not just any C-level).
- **LinkedIn slides delegated to Felix** outright. Daniel is not editing them.
- Daniel's AI rewrites the email-overview and email-capacity-split slides tonight; **Gaston reviews
  first thing tomorrow morning** before the meeting.

## Action Items
- [ ] Query BigQuery for the **real net-new-open-jobs number** — the 7,000 on the slide was
      AI-invented — *Gaston*
- [ ] Fix the **non-open-jobs email count**: verify whether LATAM Open Jobs was wrongly split into
      "others", producing 9,000 vs Gaston's 4,500 — *Gaston / Daniel's AI*
- [ ] **Validate the email-experiment slide numbers** (lead counts etc.) — Gaston assumed they were
      fine and did not check — *Gaston*
- [ ] **Review the AI-rewritten slides first thing tomorrow morning** — *Gaston*
- [ ] **Revisit the Decision Making Unit** — which roles we target in No-HM, and run a BigQuery
      analysis of how HR profiles perform — *Gaston*
- [ ] Confirm whether the **HR-as-second-target** finding was blended or hiring-manager-only —
      *Daniel*
- [ ] Complete the **company-size performance table** for 50–199 (10% of No-HM leads) — positive
      reply rates — *Daniel*
- [ ] Add **"what we learned"** items: only 6 of 10 experiments concluded; the No-HM manager-identity
      problem — *Daniel / Gaston*
- [ ] **Relaunch the co-workers campaign** this week — already tracked as
      [[wiki/tasks/2026-08-13-fix-coworkers-clay-workflow]] — *Gaston*

## Numbers Reviewed
| Metric | Value |
|---|---|
| Emails sent last week | 23,900 (target hit for the first time) |
| Positive replies | 67 vs **72 target** |
| Positive-to-booked-call | 17.9% |
| Calls booked (email) | 12 |
| Lead-to-conversation | 0.19% |
| Reply rate | 3.4% |
| Median reply time | 13 min |
| Replies under 10 min / under 5 min | 30.6% / 12.9% (under-5 is a subset of under-10) |
| Cold calling | 880 dials, 66 reported conversations, 1.5% conversation-to-booked |
| LinkedIn | 364; Samuel 0 booked in core, 2 in experiment |
| HR / Talent share of No-HM leads | 8.2% (Jan–Aug 13) |
| No-HM leads at 50–199 employees | 10% |
| Avg people reached per No-HM company | 1.4 |

## Context
Daniel's central learning, stated twice: the baseline **works** on hiring managers — functional
owner or CEO, it doesn't matter — and on **CEOs under 50 employees** in No-HM. Everywhere else in
No-HM it underperforms. That asymmetry is what drives the reframe from copy to targeting.

Gaston's counter-hypothesis is the more actionable half: the No-HM playbook goes after *functional
owners*, and in larger companies (over 50, or over ~150) the hiring process is typically owned by
**HR** — a profile the team doesn't systematically target. There was a **Decision Making Unit**
document defining role targeting; neither could remember where it lives. It is referenced in
[[wiki/context/my-role]] and [[wiki/tools/clay]] as a Clay targeting concept but has no page of its
own in the vault.

Daniel also aired frustration about **BigQuery data completeness** — hiring managers missing job
titles, older leads missing open-role fields — which undercuts trusting it as a source. Gaston
confirmed: the gaps are concentrated in hiring managers (titles) and older leads (open role).

Separately, both discussed that the **Clay scoring-system idea originated with Daniel**, that Felix
has had the list for over a week without using it, and Daniel's concern that the expansion strategy
will be re-executed later and credited to Felix. Gaston noted he had already told Andres where the
scoring system came from. Recorded as context on a live interpersonal thread, not as an action.
