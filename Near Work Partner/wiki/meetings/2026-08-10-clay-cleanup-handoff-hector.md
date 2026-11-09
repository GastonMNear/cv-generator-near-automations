---
type: meeting
title: "Clay Cleanup Handoff to Hector"
created: 2026-08-10
updated: 2026-08-19
attendees:
  - "Gaston Murillo — GTM Engineer / SalesOps"
  - "Hector Melara — Reply handling, now Clay cleanup owner"
meeting-type: internal
duration-min: 52
recording_id: 171832590
fathom-url: "https://fathom.video/calls/776255275"
tags: [type/meeting, meeting-type/internal]
status: mature
sources: ["[[bibliography/2026-08-10 - Clay Cleanup Handoff - Meeting]]"]
---

# Clay Cleanup Handoff to Hector

Live hands-on-keyboard training session transferring ownership of the recurring Clay table cleanup
to Hector — an instance of Gaston's standing goal of building repeatable workflows teammates run.

## TLDR
- **Hector now owns the recurring Clay source/table cleanup**, reviewing workflows ~3x/week
  (Mon/Wed/Fri), prioritising the US and Latam No-Hiring-Managers tables.
- They worked the Latam Hiring Managers and Latam No-HM workflows together end to end: filter out
  recruiting companies, unqualified rows, and pre-July rows → export CSV → delete → re-add source
  with refreshed job-title exclusions → set daily 9:00 AM CST schedule.
- **Gaston's residual is small**: share the Google Drive backup folder, and stay available for
  questions.
- US Experiment 5 left for Hector to do immediately; the other US, Canada and Asia campaigns
  confirmed as not yet needing cleanup.

## Key Decisions
- The standard cleanup filter set: the three recruiting-company signals combined with **OR** —
  Previously Found Recruiting Companies has-results, Exclusion Lookup has-results, Write to Other
  Table / Write to Exclusion Lookup has-results — plus unqualified rows and rows created before
  July 1.
- **Every batch must be exported as CSV to a shared Drive folder, organised per campaign, before
  deletion from Clay.**
- After re-adding a source: schedule daily 9:00 AM CST, and force-run the Previously Found column
  on leftover unqueued rows.
- Latam job-title exclusions must be added in **Spanish and Portuguese** as well as English
  (e.g. *mesero* alongside *maceiro*); overly niche one-off titles aren't worth excluding.

## Action Items
- [ ] Create + share the Drive folder for deleted Clay rows (per campaign) — *Gaston* — blocks Hector
- [ ] Clean US No-HM Clay table (Experiment 5) — *Hector*
- [ ] Take over recurring cleanup 3x/week (Mon/Wed/Fri) — *Hector*
- [ ] Check Canada and Asia campaigns; repeat cleanup if they approach 50,000 rows — *Hector*
- [ ] Clear the backlog of pending reply-handling items from last week — *Hector*

## Context
The 50,000-row Clay table limit is the forcing function — cleanup is what keeps the tables under it.
Gaston explicitly offered to be pinged and review together if Hector hits a doubt or if a pass
fails to free enough rows (e.g. still 40k left).

Gaston also noted the previous week's cold email was "un poco rara" — unusually bad with no known
cause — but that this week started better, with a call booked and replies coming in. That thread
was picked up properly in the Aug 13 root-cause session.

## Full Transcript
Not stored — see Fathom: https://fathom.video/calls/776255275 (52 min).
Fetch live via `get_meeting_transcript(recording_id: 171832590, url: ...)`. Conducted in Spanish.
