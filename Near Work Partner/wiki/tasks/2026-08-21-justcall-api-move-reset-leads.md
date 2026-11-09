---
type: task
title: "Check the JustCall API for moving/resetting leads between campaigns"
created: 2026-08-21
updated: 2026-08-26
priority: high
status: open
from-meeting: "[[wiki/meetings/2026-08-21-weekly-check]]"
related: ["[[wiki/tasks/2026-08-19-load-coldcall-lists-to-justcall]]", "[[wiki/tasks/2026-08-19-swap-predictive-justcall-lists]]"]
sources: ["[[bibliography/2026-08-21 - Weekly Check - Meeting]]"]
---

# JustCall API: can a lead be moved or reset?

Read the JustCall API docs for a way to **move a lead from one campaign to another and reset its
attempt count to zero** — or failing that, delete and re-upload it.

**Why:** Confirmed by hitting the error in the UI: a lead already uploaded to one JustCall campaign
**cannot be uploaded to a second one**. That structurally kills the planned "interested replies that
then ghosted us" list, which Daniel called the highest-intent segment available — those leads are
already sitting in the U.S. Open Jobs Hiring Managers campaign. The same wall will hit the no-HM
list wherever it overlaps. Until this is answered, two of the four agreed cold-call lists cannot
exist and Ivan can't reach the 2,000-dial mark. Done = a documented yes/no, and if yes, the
move-and-reset path written down.

**Timing:** No date given — offered as "I could check the API documentation".

> "I could check the API documentation to see if we can move them from one campaign to another one
> and reset them maybe, like reset them back to zero"

**Source:** [[wiki/meetings/2026-08-21-weekly-check]] · [Fathom @28:45](https://fathom.video/calls/792826882?timestamp=1725)

## Update 2026-08-25 — ranked priority 5, and it grew a second question
Daniel ranked this **5 of 5**. Framing sharpened: the goal is to **bypass the duplicate-upload
block** so a lead can sit in a new campaign without deleting the existing record and losing its
history.

**Second question to answer in the same pass:** a lead who already replied "no" should probably not
be dialed. So the move/reset path needs a way to exclude prior explicit rejections, not just
de-duplicate. The same question applies to
[[wiki/tasks/2026-08-24-smartlead-remove-recontact-limit]].

Metrics export via the same API is split out into
[[wiki/tasks/2026-08-24-justcall-metrics-via-api]].

## Update 2026-08-26 — API canary succeeded

The duplicate-upload block can be bypassed without removing the lead from the original campaign.
Using Sales Dialer contact ID `135907187` as the canary, the API added the existing contact to
campaign `3306236` while leaving it in campaign `3319305`.

- Original campaign: still `Active` / `To be reattempted`; original added-at timestamp unchanged.
- Target campaign: `Active` / `Undialed`; new campaign association created successfully.
- Master contact: default fields and all 20 custom fields unchanged before versus after.
- API path: `POST /v2.1/sales_dialer/campaigns/contact` with `campaign_id` + existing `contact_id`.

This proves that one Sales Dialer contact can sit in both campaigns and receive a fresh target-
campaign enrollment. Still open before a bulk run: confirm that the target campaign's current
reattempt rules schedule the expected follow-up after the canary's next call, and finalize the
exclusions for DNCA, booked, uninterested, restricted, and non-eligible outcomes.

## Update 2026-08-26 — bulk association completed and verified

At Gaston's explicit request, associated every currently eligible contact from source campaign
`3319305` with target campaign `3306236`, without removing or deleting any source association.
The target campaign's live rules were used as the authority:

- Dispositions: Contacted - Worth Follow Up; Contacted - Hung Up/Busy; No Contact/Left VM; Silent
  Call; Left VM; Contacted - Email Follow Up; No connect on 2x Dial; Decision Maker Unavailable.
- Call statuses: Unanswered; Busy; Abandoned; Voicemail; Machine Pickup.
- Undialed source contacts also qualified.
- Excluded: non-Active/DNCA, Restricted, a nonempty `Original discovery call date`, terminal
  dispositions (including not interested/DNCA/bad number/wrong person/not eligible/not hiring now/
  booked), no qualifying condition, and contacts already at the fourth-call ceiling.

Pre-write classification: 1,066 eligible contacts — 921 by call status only, 9 by both disposition
and status, 6 by disposition only, and 130 undialed. The canary was already in the target, so the
bulk run added 1,065 existing contact IDs. All 1,065 API writes succeeded; there were no failures,
rate-limit interruptions, missing eligible IDs, or unexpected new IDs.

Fresh post-write audit:

- Source: 1,152 total (1,115 Active, 37 DNCA); source membership was not modified.
- Target: 1,154 total — 1,066 eligible Active contacts plus 88 pre-existing historical DNCA rows.
- Eligible target progress: 886 Undialed, 17 Dialed, 163 To be reattempted.
- Excluded from the active transfer set: 37 non-Active/DNCA, 2 booked discovery dates, 31 without
  an eligible condition, 13 terminal dispositions, and 3 Restricted.

The target campaign was live during the batch, so the 163 `To be reattempted` records are direct
evidence that the new-campaign retry workflow is applying. An optional later audit can follow one
contact through all remaining retry levels, but the reset path and first retry scheduling are now
proven at bulk scale.
