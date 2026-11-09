---
type: meeting
title: "Smartlead CV Workflow Training — Full Tool Provisioning"
created: 2026-09-09
updated: 2026-09-11
attendees: ["Gaston Murillo — cold email lead", "Lila Lemus — email replies (new hire)"]
meeting-type: internal
duration-min: 145
recording_id: 181505730
fathom-url: "https://fathom.video/calls/817374239"
tags: [type/meeting, meeting-type/internal, topic/onboarding, topic/email-replies, topic/security]
status: mature
related: ["[[wiki/meetings/2026-09-09-smartlead-replies-working-session]]", "[[wiki/meetings/2026-09-10-lila-replies-and-reply-time]]"]
sources: ["[[bibliography/2026-09-09 - Smartlead CV Workflow Training - Meeting]]"]
---

# Smartlead CV Workflow Training — Full Tool Provisioning

> [!warning] **Diarization is badly inverted after ~1:37.** The follow-up sub-sequence explanation,
> the fee-format guidance and the salary-reply scripting are all labelled "Lila Lemus" but are
> unambiguously Gaston's — he owns the system and is teaching. Ownership grounded in content.

## TLDR
- ~2.4-hour hands-on session that **provisioned Lila's entire tool stack live**: Smartlead, the shared
  Claude account, Claude Code desktop, GitHub access to the CV Generator repo, and the `.env`
  credential bundle.
- Walked the complete Master Inbox reply workflow: triage → qualify → run `/email-replies-workflow`
  → export PDF as "Near sample profile" → reply-all with two booking slots → re-tag as
  candidate-sent-followup. **Lila ended the session handling live replies herself.**
- **⚠️ Security: the Smartlead password *and the full `.env` bundle* (Smartlead API key, Google Docs
  and Clay credentials) were pasted into Slack and are still there.** →
  [[wiki/tasks/2026-09-09-purge-credentials-from-slack]]
- The CV Generator project was **moved to GitHub** so Lila can clone it and run the skill herself
  rather than requesting CVs from Gaston.

## Key Decisions
- **Priority order for Lila:** Interested / Information Request / Meeting Request are worked first.
  Not-interested and auto-reply categories are read-and-tagged only, not worked.
- **The CV is strictly a past-placement sample, never a live candidate.** Any lead asking for "the
  candidate's salary" gets an explicit clarification plus a range derived from the email-1 figure ±10–15%.
- **Tag `candidate-sent-followup` whenever a CV is sent** (it fires a 3-step automated sub-sequence)
  and **pull the lead out the moment they reply**, or they receive nonsensical follow-ups.
- **If a lead offers a call before accepting a CV, skip the CV and book the call.** The CV is only a
  hook to book calls.
- **Reply tone is deliberately terse** — never volunteer fees, models or process detail the lead
  did not ask about.
- Gaston stays **live/on-call for Lila's first days**, moving to async Slack review as she ramps.
  This is the concrete exit condition for him covering replies.

## Reference — Pitch Facts Lila Now Has
Fees 20–30%, two models (recruiting and staffing), **no upfront fees**, first candidate batch in 3–5
days, all candidates pre-vetted for skills and English fluency, ~21 days average time to hire, free
replacement policy. Supporting assets: G2 reviews, website case studies, candidate demo videos, and a
Canva business deck (select slides, export as PDF).

## Action Items
- **Gaston** — purge credentials from Slack and rotate the exposed keys →
  [[wiki/tasks/2026-09-09-purge-credentials-from-slack]]
- **Gaston** — send the saved objection-handling kit (fees, models, process, G2, case studies, deck)
- **Gaston** — follow up with Paz on Lila's revoked HubSpot viewer access
- **Gaston** — rework the candidate-sent follow-up copy with Lila → superseded by the Sep 11 redesign
- **Lila** — install Python so the CV Generator runs; save booking links to a personal doc

## Notable Operating Details
- **Smartlead 2FA codes are automated into the #sales Slack channel**, so Lila can self-serve a login
  code when Gaston is unavailable.
- Lila is running **Claude Code in bypass-permissions mode** on Gaston's recommendation, which he
  acknowledged is not the most advisable setting.
- **Always verify which inbox the reply sends from before signing off** — Gaston has previously
  signed with the wrong name while sending from Franco's inbox.
- Smartlead's built-in AI Reply Agent (blue suggestions) is **deliberately ignored** — not configured.

**Source:** [Fathom recording](https://fathom.video/calls/817374239) · `recording_id: 181505730`
