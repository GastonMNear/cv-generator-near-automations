---
type: task
title: "Decide whether Viktor can own Clay workflow cleanups"
created: 2026-10-13
updated: 2026-10-23
priority: medium
status: open
from-meeting: "[[wiki/meetings/2026-10-09-sara-clay-workflow-maintenance]]"
---

# Can Viktor own Clay workflow cleanups?

Last week's prep is done: video tutorials sent, one test Clay workflow created for Viktor to own, and its accuracy validated (all ✅ per Gaston, Oct 13). What's left is the call itself.

**Done =** a yes/no on Viktor owning Clay workflow cleanups. If yes, its scope is written down.
**Context:** Sara takes over the daily manual maintenance checks from Oct 13: row cleanup (4 OR filters → CSV to Drive → delete), source resets near 50k, and company/lead-table source checks. The Oct 9 checklist is the natural spec for what Viktor would automate. On Oct 9 Gaston and Sara also floated *"tratar de automatizar algo con AI"* for these checks ([@1:07:13](https://fathom.video/calls/854742988?timestamp=4033)). **Viktor is an AI agent** (Gaston, Oct 13). Andrés mentions a "Victor" at [@32:48](https://fathom.video/calls/849739413?timestamp=1968) of the Oct 5 sync.
**Timing:** carried over from last week. No date given.

**Source:** Gaston's weekly focus message (2026-10-13) · [[wiki/meetings/2026-10-09-sara-clay-workflow-maintenance]]

## Update 2026-10-19

> [!contradiction] The Oct 13 ✅ on "test workflow created + validated" is contradicted by Gaston himself on Oct 16. He recorded the Looms and got Viktor's questions, then *"ahí quedó"* (it stalled there).

**Remaining deliverable ([@17:10](https://fathom.video/calls/865028769?timestamp=1030)):** *"termino este tema con Víctor y le creo el workflow este de pruebas y ya por lo menos arrancamos a probar"*. Build the Clay test workflow, validate Viktor's row cleanup/source reset on it, then grant production permission. Workflow selection should be dynamic (skip `old`-tagged workflows). Alexia reports that Viktor already asks for Slack approval before deletes. **Urgency up:** Alexia mentioned Sara may not be around long (@09:18), and Sara currently does these checks by hand.
*From fathom-task-sync run 12.*

## Update 2026-10-23

**Oct 21 Clay session with Alexia:** Alexia said leadership is *"medio hartos"* (kind of fed up) with Viktor because it bills by API and is getting expensive. She'd prefer Claude ([@57:00](https://fathom.video/calls/867098213?timestamp=3420)). Gaston restated maintenance as the first automation target because its rules are clear ([@55:38](https://fathom.video/calls/867098213?timestamp=3338)). **Deadline pressure: Sara's temporary contract ends Nov 12** ([@58:27](https://fathom.video/calls/867098213?timestamp=3507)). The test workflow still wasn't mentioned as built. Worth asking whether this should be Viktor or Claude.
*From fathom-task-sync run 13.*

## Update 2026-11-03 — rules settled, Claude skill instead of Viktor (phase 1)

Gaston answered Viktor's open questions:
- **Leads tables at 50k:** flag only, Gaston decides.
- **Protected rows:** created in the last **7 days**, plus any qualified row. Never delete these.
- **Source schedule:** Daily **9:30 AM EST**.
- **Exclusions:** no separate doc. Junk titles go in the saved search's *Job titles to exclude* → Update search; companies go through the Exclusion Lookup table.
- **Test Drive folder** (CSV backups): https://drive.google.com/drive/u/0/folders/1T3XpFo4C93ZIDFxJVQfNEDQAL7p02Xv4
- The test workflow is still to come from Gaston.

**Direction:** build a Claude skill. Phase 1 = read-only daily check + Slack report. Phase 2 = row cleanup gated by Slack approval. Source refresh and new company tables stay manual (flag only).
**Blocker (Nov 3):** Clay API login with `CLAY_USERNAME`/`CLAY_PASSWORD` from `.env` (kevin.dubon@) returns `400 Unable to login`.

## Update 2026-11-03 (later) — skill built, no Slack

Gaston chose an interactive skill over Viktor/Slack approvals: `.claude/skills/clay-daily-control/`. Gaston asks, the agent scans via his Google-SSO Clay session in the in-app browser (API calls from the page), reports, and asks before any write. The active-workflow registry is `references/active-workflows.md` (18 seeded, pending his confirmation). Phase 2 (filter/export/delete endpoints for row cleanup) is not mapped yet. First run: see `logs/clay-daily-control.md`.
