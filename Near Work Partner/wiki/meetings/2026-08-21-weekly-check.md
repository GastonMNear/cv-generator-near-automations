---
type: meeting
title: "Weekly Check — Channel-by-Channel Review"
created: 2026-08-21
updated: 2026-08-21
attendees:
  - "Gaston Murillo — GTM Engineer / SalesOps (email, lead loading, Clay)"
  - "Daniel Ardila — Campaign strategy / leadership reporting"
  - "Felix Jourdain — LinkedIn outreach / list ownership"
  - "Mairol Sontay — LinkedIn outreach"
  - "Samuel Chapaval — LinkedIn outreach"
  - "Ivan Valenzuela — Cold calling"
  - "Hector Melara — Reply handling"
  - "Ramon Oliveira — Present, did not speak"
meeting-type: internal
recording_id: 175771267
fathom-url: "https://fathom.video/calls/792826882"
tags: [type/meeting, meeting-type/internal]
status: mature
related: ["[[wiki/meetings/2026-08-19-weekly-metrics-optimization]]", "[[wiki/meetings/2026-08-14-weekly-check]]"]
sources: ["[[bibliography/2026-08-21 - Weekly Check - Meeting]]"]
---

# Weekly Check — Channel-by-Channel Review

## TLDR
- **LinkedIn is the weak channel after two quiet weeks, and the fix is automated lists rather
  than more manual research.** Felix and Mairol get Clay/Sales-Nav-supplied lists —
  marketing hiring managers pulled from Clay, plus Gaston's already-delivered scored LinkedIn
  list, which Felix will manually filter to presidents/CEOs and start working Friday or Monday.
- **The parallel-dialing campaign has a hard bug: it reports a 31% connect rate while Ivan has
  had zero live conversations across 200+ dials.** Daniel will audit the call logs and take a
  JustCall plan upgrade to Andres, funded by dropping 20 unused numbers costing $120/mo.
- **A structural JustCall limit blocks the remaining cold-call work:** a lead already uploaded to
  one campaign cannot be uploaded to another. This kills the planned "ghosted high-intent leads"
  list until the overlap with the U.S. Open Jobs Hiring Managers campaign is solved.
- **Email is mid-flight across four fronts:** Exp 008 live on hiring managers with both arms
  (~1,800 leads added, 1–2 positive replies, no calls yet), Exp 009 sending but frozen on new
  leads pending a copy rework, Exp 010/Apollo working, and the co-workers Clay workflow still
  broken.
- **BigQuery queries are running again** (deleted tables were the cause) and the booked-call
  auto-pause is live twice a day at company level.

## Key Decisions
- **LinkedIn targeting shifts to Clay-supplied lists** — small-volume, high-relevance lists
  (marketing hiring managers; marketing leads at companies under 30–50 employees) to automate
  part of the SDRs' manual prospecting rather than chase raw volume.
  [05:04](https://fathom.video/calls/792826882?timestamp=304)
- **Felix uses the latest scored LinkedIn list as-is**, manually filtering to presidents/CEOs —
  only ~25% of the list, but those were "perfect matches". Rollout Friday or early Monday rather
  than waiting for better scoring. [16:35](https://fathom.video/calls/792826882?timestamp=995)
- **JustCall plan gets upgraded**, funded by dropping the 20 phone numbers costing $120/mo that
  showed no impact in 2–3 months — to raise attempts per lead and move to 2x/day dialing instead
  of one attempt per 24h. [23:50](https://fathom.video/calls/792826882?timestamp=1430)
- **Cold-call lists get fresh leads immediately on upload to email**, not after the email sequence
  completes. Daniel: "Let's try to work with fresh leads, please." This resolves the open question
  from 2026-08-19 about waiting out the 7-email sequence.
  [30:04](https://fathom.video/calls/792826882?timestamp=1804)
- **The "interested replies that ghosted us" cold-call list is blocked and deferred** — those leads
  are already in the U.S. Open Jobs Hiring Managers campaign and cannot be re-uploaded, so the
  overlap must be solved first. [30:17](https://fathom.video/calls/792826882?timestamp=1817)
- **Experiment 009 gets a copywriting rework first** (reviewed by Felix and Daniel), and only then
  automated lead adding — Daniel explicitly ruled out manual weekly lead adds for a low-volume
  campaign. [38:25](https://fathom.video/calls/792826882?timestamp=2305)
- **Preferred long-term fix for the co-workers campaign is sourcing lookups from BigQuery instead
  of Clay tables**, so experiment table churn stops breaking it — possibly extended to all
  open-jobs campaigns. [46:00](https://fathom.video/calls/792826882?timestamp=2760)
- **Company-level auto-pause on booked calls stands.** Daniel questioned the blast radius but
  concluded the multiple-hiring-managers-per-company case is probably rare; Gaston to review the
  edge case. [35:37](https://fathom.video/calls/792826882?timestamp=2137)

## Status Changes
- **BigQuery is working again** — the issue with deleted tables is resolved and queries run.
  Gaston attributes the fix to the deleted tables, *not* to the billing/payment escalation, which
  is not confirmed closed. [42:00](https://fathom.video/calls/792826882?timestamp=2520)
- **Booked-call auto-pause is LIVE** — runs twice a day, checks new booked calls, finds everyone
  from that company in Smartlead campaigns and pauses them, regardless of which channel booked the
  call. [31:57](https://fathom.video/calls/792826882?timestamp=1917)
- **Exp 009 inbox switch is done**; Apollo campaign (Exp 010) working; Exp 009 sending but no new
  leads pending the copy rework. [36:14](https://fathom.video/calls/792826882?timestamp=2174)
- **Exp 008 live on hiring managers, both arms** (2–3 personalized images, and the longer
  sequence). ~1,800 leads added against a ~2,000/week target cadence; 1–2 positive replies, zero
  calls booked yet. [37:36](https://fathom.video/calls/792826882?timestamp=2256)
- **Cold-call list source changed** — parallel dialing now uses the FULL hiring managers list
  rather than only HMs who finished the email sequence. Gaston offered to revert if the dialer
  issue persists. [18:44](https://fathom.video/calls/792826882?timestamp=1124)
- **Conversion gap improved** — roughly 60 positive replies against ~10–11 calls booked this week,
  recovered from prior weeks. Daniel asked Hector for a hard follow-up to get 2 more. Numbers
  stated loosely in the call — treat as approximate.
  [47:09](https://fathom.video/calls/792826882?timestamp=2829)
- **Persona underperformance re-scoped (correction to earlier reporting).** Marketing, engineering
  and sales personas are **not** underperforming in the hiring-manager campaign — they track the
  campaign benchmark. The earlier signal came from blended data. They **are** severely
  underperforming in the no-hiring-manager campaign, which is where persona-specific copy should
  go. [40:07](https://fathom.video/calls/792826882?timestamp=2407)
- **Spam tests capped at 5 concurrent** — only five placement tests can run simultaneously, forcing
  rolling weekly batches of five rather than testing ~500 inboxes at once. Results so far still
  clean. [42:00](https://fathom.video/calls/792826882?timestamp=2520)
- **JustCall duplicate-upload restriction confirmed** by hitting the error — a lead in one campaign
  cannot be uploaded to another. [28:45](https://fathom.video/calls/792826882?timestamp=1725)
- **LATAM hiring manager campaign 50-row limit** — Daniel raised it; Gaston confirmed it is
  distinct from the co-workers issue and **not** yet solved. Nobody was assigned it.
  [45:40](https://fathom.video/calls/792826882?timestamp=2740)
- **LinkedIn scored list reviewed** — scores not always accurate, only ~25% were C-level (HR people
  and low-level managers leaking through), but the CEOs/presidents on it were "perfect matches".
  Sorting by most recent job posting made filtering fast.
  [15:27](https://fathom.video/calls/792826882?timestamp=927)
- **Headcount data accuracy problem** — Sales Navigator's 1-10 / 1-50 employee filters are
  unreliable; companies showing 10 employees can actually have 400+. Daniel proposed cross-checking
  against Apollo headcount already in the shared playlist.
  [13:58](https://fathom.video/calls/792826882?timestamp=838)

## Action Items
- [ ] Finish the co-workers campaign fix, ideally via BigQuery lookup instead of Clay tables — *Gaston* — due: 2026-08-21
- [ ] Check the JustCall API for moving/resetting leads between campaigns — *Gaston*
- [ ] Build the two remaining cold-call lists (no-HM C-level <50 employees; ghosted leads) — *Gaston*
- [ ] Rework Exp 009 copy and share with Daniel + Felix — *Gaston*
- [ ] Automate Exp 009 lead adding once the copy is approved — *Gaston*
- [ ] Run Daniel's persona-analysis prompt and deliver copy — *Gaston* — due: 2026-08-24
- [ ] Run 5 more spam placement tests this week — *Gaston*
- [ ] Review the company-level scope of the booked-call auto-pause — *Gaston*
- [ ] Pull marketing hiring-manager lists from Clay for LinkedIn — *Gaston*
- [ ] Export last-7-day marketing hiring-manager raw data to Felix + Gaston — *Daniel*
- [ ] Finish and re-send the revised persona-analysis prompt (told Gaston to stop the version already sent) — *Daniel*
- [ ] Audit parallel-dialer logs and take the JustCall plan upgrade to Andres — *Daniel*
- [ ] Review the LinkedIn list, filter to C-level/founders, start outreach — *Felix*
- [ ] Give feedback on Exp 009 copy — *Felix*
- [ ] Friday blast of connection requests + 30 DMs + extra InMails to set up Monday — *Samuel*
- [ ] Hard follow-up on outstanding positive replies to book 2 more calls — *Hector*
- [ ] Consult on state call-attempt limits — *Mairol*

## Context
The meeting ran channel by channel — LinkedIn, cold calling, then email — rather than as a single
metrics review.

**LinkedIn.** Two quiet weeks. The team's read is that manual prospecting in Sales Navigator is
both slow and unreliable: the 1-10 and 1-50 employee filters misreport headcount badly enough that
a "10-employee" company can have 400+. The agreed direction is to hand the SDRs pre-built,
small-volume, high-relevance lists out of Clay, and to cross-check headcount against Apollo data
already sitting in the shared playlist. The scored LinkedIn list Gaston delivered is imperfect
(~25% C-level, HR and junior managers leaking in) but the CEOs and presidents on it were rated
perfect matches, so Felix takes it as-is and filters by hand rather than waiting for scoring to
improve.

**Cold calling.** The parallel-dialing campaign's reported 31% connect rate is not reconcilable
with Ivan's 200+ dials and zero conversations — this is being treated as a bug in the campaign or
the reporting, not a performance result. Two constraints came out of the discussion: the current
JustCall plan caps attempts per lead and holds dialing to one attempt per 24h, and JustCall refuses
to upload a lead that already exists in another campaign. The first is a spending decision (drop
the 20 idle numbers, upgrade the plan); the second is structural and blocks the ghosted-replies
list outright.

**Email.** Four workstreams in parallel. Exp 008 is live on hiring managers with both arms and is
hitting roughly its ~2,000 leads/week cadence but has yet to book a call. Exp 009 is sending on the
switched inboxes and is deliberately frozen on new leads until the copy is reworked — Daniel
refused to sanction manual weekly lead adds on a low-volume campaign. Exp 010/Apollo is working.
The co-workers Clay workflow remains broken and is the one item with a stated Aug 21 date; the
proposed fix is to stop pointing lookups at experiment tables that keep churning and read from
BigQuery instead, possibly across all open-jobs campaigns.

The persona finding from earlier in the month was corrected here: the underperformance signal came
from blended data, and the personas actually track benchmark inside the hiring-manager campaign.
The real gap is in the no-hiring-manager campaign, which is where persona-specific copy should be
aimed.

## Open Questions
- Why does the parallel dialer report a 31% connect rate against zero live conversations? Daniel is
  auditing the logs. [23:50](https://fathom.video/calls/792826882?timestamp=1430)
- How to get leads into a second JustCall campaign when they already exist in another — API move,
  reset, or a different segmentation. Blocks the ghosted-replies list.
  [30:17](https://fathom.video/calls/792826882?timestamp=1817)
- The LATAM hiring manager campaign's 50-row limit is unsolved and unowned.
  [45:40](https://fathom.video/calls/792826882?timestamp=2740)
- Whether the company-level blast radius of the booked-call auto-pause is acceptable when one
  company has multiple hiring managers in different campaigns. Judged rare, not verified.
  [35:37](https://fathom.video/calls/792826882?timestamp=2137)
- Whether the BigQuery billing/payment escalation is actually resolved — queries run again, but the
  fix is attributed to deleted tables, not to billing.
  [42:00](https://fathom.video/calls/792826882?timestamp=2520)

## Full Transcript
Not stored — see Fathom: https://fathom.video/calls/792826882.
Fetch live via `get_meeting_transcript(recording_id: 175771267, url: ...)`. Conducted in English.
