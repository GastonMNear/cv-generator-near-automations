---
type: meeting
title: "Priority Alignment Huddle — Top-5 Ranking & Parallel Dialer Fix"
created: 2026-08-24
updated: 2026-08-25
attendees:
  - "Daniel Ardila — Campaign strategy / reporting"
  - "Gaston Murillo — GTM Engineer / SalesOps"
  - "Ivan Valenzuela — Cold calling (first half only)"
meeting-type: internal
recording_id: null
fathom-url: null
tags: [type/meeting, meeting-type/internal]
status: mature
related: ["[[wiki/meetings/2026-08-25-kpi-deck-prep]]", "[[wiki/meetings/2026-08-24-marketing-standup]]", "[[wiki/meetings/2026-08-21-weekly-check]]"]
sources: ["[[bibliography/2026-08-24 - Priority Alignment & Cold Call Huddle - Meeting]]"]
---

# Priority Alignment Huddle — Top-5 Ranking & Parallel Dialer Fix

> [!warning] **Not a Fathom recording.** Transcript pasted by Gaston (11:35–12:17 ET), so there is
> no `recording_id` and no timestamped deep links.

## TLDR
- **Daniel ranked Gaston's work into an explicit top 5.** This is now the authoritative ordering and
  supersedes any earlier list. See the table below.
- **The parallel-dialer mystery was solved live on the call — it was a misconfigured setting, not a
  list or data problem.** Ivan had set abandon-after to 10 seconds, so JustCall was hanging up before
  anyone could pick up; he also had the abandoned-call action set to voicemail rather than connect.
  He raised abandon to 20s mid-call and **immediately got a live answer** — the first in 880 dials.
- **A dialer switch was considered and rejected for now.** Ivan pitched Tless (~$150/seat) as better
  than JustCall; Daniel refused to spend 2–3 days migrating for an unproven gain, especially since
  the real cause turned out to be a setting. Fallback agreed: **call JustCall support** for a
  configuration review instead.
- **Daniel's strategy doc reframes No-HM around routing.** The transversal element in everything
  that works is *reaching the actual manager* — so stop writing to 4–5 people as if each were the
  hiring manager, and instead ask them to point to the right one. Doc: "Conversion Improvement
  Strategy", already in Gaston's email.
- **Daniel named his own deadline: ~30 days to move the numbers.** "Si en 30 días no lo logramos…
  me mandan para la calle." That's the pressure behind the ranking.
- **Daniel already wrote the top-3-personas copy** — so Gaston's task there collapses to reviewing
  it and giving feedback, not writing it.

## The Ranked Top 5
| # | Priority | Note |
|---|---|---|
| 1 | **Review Daniel's Conversion Improvement Strategy doc + No-HM copy, give feedback** | Delivered today. Daniel wrote the copy already. |
| 2 | **Rework Experiment 009 copy → hand to Felix → load new leads** | Daniel: proceed on *his* feedback; don't block waiting on Felix. |
| 3 | **Fix the co-workers campaign** | Daniel wants to "apretar ahí" this week. |
| 4 | **Remove the Smartlead re-contact limitation** | Re-contact people from the last year (3+ months back) who have **reopened a role**. New work. |
| 5 | **JustCall: bypass the duplicate-upload block** | So ghosted leads can be loaded into a new campaign. |
| 6 | JustCall metrics export via API | Explicitly last. |

Gaston proposed 1–3 as the highest call-generating items; Daniel agreed and appended 4–5, then
metrics last. Both said "coincido."

## Key Decisions
- **Protect the hiring-manager segment — do not experiment on it.** It converts well and testing
  there would damage current rates. All experimentation goes to No-HM, except **No-HM CEOs/founders
  under 50 employees**, which also performs and must be left alone.
- **The No-HM copy strategy changes from assuming to asking.** New structure: acknowledge they're
  hiring, mention the teammates also contacted, include a job-description snippet to prove
  relevance, offer profiles, and **ask to be pointed to whoever owns the process**. Opens from
  honesty rather than presuming the recipient is the manager.
- **Segment selection stays narrow, not universal.** Daniel floated dropping role segmentation
  entirely; Gaston argued for keeping engineering/marketing/sales as the test bed — high volume,
  known-bad performance, so pulling those leads costs at most one booked call while giving enough
  flow to reach significance. Daniel agreed, and framed the doc's **50 underperforming segments** as
  the expansion path *after* the first three prove out.
- **No dialer migration now.** Confirm-before-switch; JustCall support call first.
- **Ivan fills the Outbound Metrics daily sheet at the general level**, not per campaign. Per-campaign
  breakdown waits for Gaston's API work.
- **Daniel's AI drafts the deck slides tonight; Gaston reviews first thing tomorrow.**

## Action Items
- [ ] **Read the Conversion Improvement Strategy doc and give Daniel concrete feedback** — *Gaston* —
      **priority 1**, doc already in his email
- [ ] **Rework Experiment 009 copy, send to Daniel + Felix, then load new leads** — *Gaston* —
      priority 2, tracked as [[wiki/tasks/2026-08-19-experiment-9-inbox-switch-and-copy]]
- [ ] **Fix the co-workers campaign** — *Gaston* — priority 3, tracked as
      [[wiki/tasks/2026-08-13-fix-coworkers-clay-workflow]]
- [ ] **Remove the Smartlead re-contact block** so previously-contacted people who reopened a role in
      the last year can be re-engaged — *Gaston* — priority 4, **new**
- [ ] **Find a way past JustCall's duplicate-upload block** — *Gaston* — priority 5, tracked as
      [[wiki/tasks/2026-08-21-justcall-api-move-reset-leads]]
- [ ] **Pull JustCall metrics via API** — dials are safe to automate; connection/conversation counts
      were historically unreliable — *Gaston* — last
- [ ] **Experiment 010 readout** — ownership left unresolved ("hay que verlo"); Gaston wanted it out
      to the group before tomorrow's meeting — *Gaston or Daniel*
- [ ] **Book a JustCall support call** to audit the parallel-dialer settings — *Daniel / Ivan*
- [ ] **Fill the Outbound Metrics daily sheet** for last week, general level — *Ivan*
- [ ] **More role-plays on objection handling** — Ivan froze on the "US-based candidates only"
      objection despite a play existing for it — *Daniel + Ivan*
- [ ] Check the Outbound Metrics formula — someone had been filling cells manually — *Gaston*

## Context
**The dialer story matters beyond the fix.** 880 dials with zero conversations had been treated as a
possible list-quality or data problem, and Ivan was ready to argue for replacing JustCall over it.
The actual cause was two settings — abandon-after at 10s, and the abandoned-call action pointed at
voicemail instead of connect. Ivan's read of the UI: the options were labelled only "Voicemail for…"
and "Abandon Calls…" with no explanation. The setting caps at 20s, so that is now the value. Daniel
immediately set a target of 10 booked calls for the week, then pushed for 20; Ivan committed to 5.

**On segmentation, Gaston's argument is the one that carried:** engineering and marketing have
thousands of leads and known-poor performance, which makes them the ideal test bed — enough volume
to reach significant numbers, and little downside if they're pulled from baseline, unlike hiring
managers where volume is scarce and every lead counts. That reasoning is why the test stays narrow
rather than sweeping all 50 underperforming segments at once.

**Daniel's admission on co-workers:** "nosotros la cagamos dejando caer la campaña Coworkers."
Since nobody knows who the hiring manager is in No-HM, routing — which is what co-workers does — is
where most of the effort should have gone all along. That's the strategic reason the fix is
priority 3 rather than a maintenance chore.

Gaston raised one open flaw in the new copy structure: mentioning teammates only works when several
contacts were actually found at the company, and sometimes only one exists. Daniel accepted —
drop the teammate mention in that case. Also noted: co-workers has an advantage the new approach
lacks, in that it fires only *after* the hiring manager was emailed and didn't reply.
