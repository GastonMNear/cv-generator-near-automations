---
type: meeting
title: "Smartlead Replies Working Session — Reply Workflow Demo"
created: 2026-09-09
updated: 2026-09-11
attendees: ["Gaston Murillo — cold email lead", "Lila Lemus — email replies (new hire)"]
meeting-type: internal
duration-min: 71
recording_id: 181398637
fathom-url: "https://fathom.video/calls/817171205"
tags: [type/meeting, meeting-type/internal, topic/onboarding, topic/email-replies, topic/smartlead]
status: mature
related: ["[[wiki/meetings/2026-09-09-lila-onboarding-sync]]", "[[wiki/meetings/2026-09-09-smartlead-cv-workflow-training]]"]
sources: ["[[bibliography/2026-09-09 - Smartlead Replies Working Session - Meeting]]"]
---

# Smartlead Replies Working Session — Reply Workflow Demo

> [!note] Fathom titles this **"Impromptu Google Meet Meeting"**. Second session of Sep 9, between
> the morning onboarding sync and the afternoon hands-on training.

## TLDR
- End-to-end walkthrough of Smartlead (Master Inbox, Untracked Replies, sequences, reply tagging)
  plus a live demo of the full positive-reply workflow.
- **The lead lookup key is the email the lead is *registered* under in Smartlead** — the address
  email 1 was sent to, **never** the address they replied from. Replies can arrive from a forwarded
  mailbox and the skill lookup will silently fail.
- **AE booking links are assigned by company size:** Laura ≤10 employees, Gianluca 10–50, Pedro 50+ —
  a prioritisation guideline, not a hard rule. **Availability overrides size**, and Pedro is
  deliberately reserved for larger companies.
- Always offer **two concrete slots on two different days**, as close to today as possible, in
  explicit US format, converted to the lead's time zone.
- Cut short at 1:10 when Lila had a conflicting meeting with Paz.

## Key Decisions
- **No spintaxing in the main campaigns** — copy is AI-generated per lead in Clay and pushed to
  Smartlead as `{{email_1}}` / `{{email_2}}` / `{{subject_line}}` variables, so spintax is redundant.
- **Smartlead's AI reply categories get manually corrected when wrong** (an "information request" was
  re-tagged to "not interested" live) to keep reporting data clean.
- **Tag the lead `candidate sent / follow-up`** after sending a CV.
- Lila uses the **Claude desktop app, not Antigravity** — Gaston keeps Antigravity only because he
  builds and edits the skills.

## How the Sample CV Is Framed
- The CV sent on a positive reply is **not a real candidate** — it is an AI-generated sample resume,
  presented to the lead as a past placement (*"just for you to get a feel for the level of talent we
  are able to place"*). Gaston calls the "we have a candidate" hook in email 1 *"una mentirita
  piadosa"*, justified because recruiting can source 3–5 qualified candidates in 3–5 days.
- Sample CVs deliberately use **first name only**, no email, phone or LinkedIn, and place the
  candidate at large employers — specifically so the lead cannot verify or fail to find the person.
- Pipeline: Google Doc output → manual edit → download PDF → Near Resume Builder → rename to
  "Near Sample Profile" → attach the **formatted** PDF.

## Copy & Experiment Context
- Campaigns run A/B tests named **Experiment N**; the winner becomes the baseline. Live at the time:
  *US Open Jobs, No Hiring Managers — Candidate Lead Angle* vs *Routing CTA Angle*.
- **Email 2 uses Chris Voss-style no-oriented questions** — tested over months across thousands of
  emails for a measured **10–15% lift in positive replies** versus yes-oriented phrasing.
- **Reply mailboxes are personas** — sign as "Hayden" or "Franco" depending on the sending inbox.

## Action Items
- **Gaston** — send the AE booking-link assignment table over Slack →
  [[wiki/tasks/2026-09-09-send-lila-ae-booking-link-table]]
- **Gaston** — finish the in-progress `/email-replies-workflow` + `clay-api` refactor →
  [[wiki/tasks/2026-09-09-finish-email-replies-skill-refactor]]
- **Gaston** — eventually extend the reply agent to handle non-positive/edge replies

## Open Questions
- **"EI" in Fathom's Spanish action items is a transcription artifact of "AE"** (Account Executive) —
  the transcript even renders it once as *"el AI que yo decidí asignarle."* No "Employer of Interest"
  concept exists.
- The size tiers name **three** AEs, but a **fourth AE** was due to start taking calls ~Sep 12
  (per the morning session). The table Gaston is sending may already be stale — and Fred Delvaux,
  who appears throughout the Sep 8–11 sales calls, is absent from the tiers entirely.

**Source:** [Fathom recording](https://fathom.video/calls/817171205) · `recording_id: 181398637`
