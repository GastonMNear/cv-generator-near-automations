---
name: smartlead-campaign-creator
description: Creates a new Smartlead cold-email campaign from Gaston's spec — campaign name, email copy per step, send-day schedule, inbox selection, and the standard "Send Lead to Justcall" manual step at the end. Use this skill whenever asked to create, set up, spin up, clone, or launch a Smartlead campaign, add a new email sequence/campaign, or replicate an existing campaign onto other inboxes. Create-only — this skill must never edit, pause, delete, or start any existing campaign.
---

# Smartlead Campaign Creator

Creates ONE new campaign in Smartlead from a spec Gaston gives in chat. The campaign is created in `DRAFTED` status with sequences, schedule, settings, and inboxes fully configured. Gaston (or a separate workflow) adds leads and launches it from the UI.

**Hard safety rule:** this skill only ever *creates*. Never call update/delete/status endpoints on any campaign that this run did not just create. Never write to an existing campaign ID, even if asked to "fix" one — surface that as out of scope for this skill.

## What Gaston provides

1. **Campaign name**
2. **Emails**: for each email — the day it sends (Day 1, Day 4, …) and the copy (subject + body). Follow-ups with no subject send in-thread (empty subject = "Re:" threading).
3. **Inboxes**: which to include or exclude — usually a tag ("A inboxes"), "same as campaign X", or explicit addresses/domains.
4. Optionally: any setting that deviates from the standard defaults below.

**If any of these is missing or ambiguous, ask before creating.** Don't guess copy, send days, or inbox selection. Settings that Gaston doesn't mention use the standard defaults silently — those never need asking.

## Standard defaults (verified against live campaigns 2026-07-10)

| Setting | Default |
|---|---|
| Timezone | `America/New_York` |
| Send days | Mon–Fri (`[1,2,3,4,5]`) |
| Sending window | 09:00–18:00 |
| Minutes between emails | 20 |
| Max new leads/day | 2000 |
| Campaign start date | **Today** (the day the campaign is created) |
| Stop on | Lead replies (`REPLY_TO_AN_EMAIL`) |
| Tracking | DON'T track opens, DON'T track clicks |
| Plain text mode | Off (HTML) |
| Follow-up vs new leads | 30% follow-ups / 70% new (`follow_up_percentage: 30`) |
| AI ESP matching | Off |
| Unsubscribe text | None (empty) |
| Manual step at end | Title `Send Lead to Justcall`, description `Send to Clay - Add to JustCall`, 1 day after the last email — **always added** unless Gaston says otherwise |

UI-only settings (AI lead categorisation list, pattern-based variant distribution, SmartInfra=None, company auto-pause off, bounce auto-protection off) are workspace UI defaults and are **not settable via the public API**. If Gaston asks to change one of those, say it has to be done in the UI — don't pretend to set it.

## Workflow

1. **Parse the spec.** Convert send days to per-step delays (Day 1 → delay 0; delay = current day − previous day). Ask about anything missing (see above).
2. **Resolve inboxes** with `scripts/list_inboxes.py`:
   - By tag: `python3 scripts/list_inboxes.py --tag "A"` (known tags: `A`, `B`, `Premium Inboxes`, `Near - CI`, `Internally managed`, `AI Eng Service | Founders`, `Unify`; avoid `[Don't use] Sales Inbox AEs`)
   - Same as an existing campaign: `python3 scripts/list_inboxes.py --campaign <id>` (read-only)
   - Filter/exclude: `--match <substring>` and `--exclude <substring>` on the email address, repeatable.
   - Sanity-check the count with Gaston's expectation (tag `A` ≈ 165 inboxes). Zero matches = stop and ask.
3. **Write the spec JSON** (see schema in `references/api-reference.md`) to the scratchpad, with `start_date` set to **today**.
4. **Create:** `python3 scripts/create_campaign.py spec.json`. The script creates the campaign, saves sequences (emails + manual step), applies schedule + settings, attaches inboxes, then re-fetches everything and prints a verification summary. Non-zero exit = something failed; read the output, fix, and re-run **with `--campaign-id <id>` of the just-created campaign** so it repairs instead of creating a duplicate.
5. **Report back:** campaign ID, name, step count with send days, inbox count, and status (`DRAFTED`). Remind Gaston it needs leads + manual launch.
6. **Log it:** append one line to `Near Work Partner/logs/smartlead-campaign-log.md` (create if missing): date, campaign ID, name, #emails, inbox count, requested by.

## Environment

`SMARTLEAD_API_KEY` lives in the project `.env`. Scripts load it themselves (they read `.env` from the project root). Run scripts from this skill's directory or pass absolute paths.

## Quirks (learned the hard way — keep current)

- **Cloudflare blocks Python urllib/requests default user-agents (403 error 1010).** All API calls must go through `curl` (the bundled scripts do this).
- POST field names differ from GET names: post `track_settings: ["DONT_TRACK_EMAIL_OPEN","DONT_TRACK_LINK_CLICK"]` — GET returns them as `DONT_EMAIL_OPEN`/`DONT_LINK_CLICK`. Posting the GET names fails validation.
- Sequence variants go in `seq_variants` (the docs say `variants` — that gets rejected with "variants is not allowed").
- Manual task step: `"seq_type": "MANUAL"` with `subject` = task title, `email_body` = task description. Valid `seq_type` values: `EMAIL` (default), `MANUAL`, `CALL` (rejected — no dialer subscription).
- Schedule POST uses `min_time_btw_emails` / `max_new_leads_per_day`; GET returns `min_time_btwn_emails` / `max_leads_per_day`.
- Sequences cannot be modified while a campaign is ACTIVE — irrelevant here since we only touch the fresh DRAFTED campaign.

Full endpoint payloads and the spec JSON schema: `references/api-reference.md`.
