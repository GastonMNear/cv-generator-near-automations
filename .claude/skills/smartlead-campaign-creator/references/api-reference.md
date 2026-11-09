# Smartlead API Reference — Campaign Creation

All facts here were verified live against the HireWithNear workspace on 2026-07-10 (probe campaign 3620378). Public docs: https://helpcenter.smartlead.ai/en/articles/125-full-api-documentation — but they are wrong/incomplete in places; trust this file where they disagree.

**Base URL:** `https://server.smartlead.ai/api/v1`
**Auth:** query param `?api_key=$SMARTLEAD_API_KEY` on every call.
**Transport:** `curl` only — Python urllib/requests get Cloudflare 403 (error code 1010).

## 1. Create campaign

```
POST /campaigns/create?api_key=...
{"name": "Campaign name"}
→ {"ok":true,"id":3620378,"name":"...","created_at":"..."}
```
New campaigns start as `DRAFTED`. Save the returned `id` — every subsequent call uses it.

## 2. Save sequences (emails + manual step)

```
POST /campaigns/{id}/sequences?api_key=...
{
  "sequences": [
    {
      "seq_number": 1,
      "seq_delay_details": {"delay_in_days": 0},
      "seq_type": "EMAIL",
      "variant_distribution_type": "MANUAL_EQUAL",
      "seq_variants": [
        {"subject": "Subject here", "email_body": "<div>HTML body</div>", "variant_label": "A"}
      ]
    },
    {
      "seq_number": 2,
      "seq_delay_details": {"delay_in_days": 3},
      "seq_type": "EMAIL",
      "variant_distribution_type": "MANUAL_EQUAL",
      "seq_variants": [
        {"subject": "", "email_body": "<div>Follow-up body</div>", "variant_label": "A"}
      ]
    },
    {
      "seq_number": 3,
      "seq_delay_details": {"delay_in_days": 1},
      "seq_type": "MANUAL",
      "subject": "Send Lead to Justcall",
      "email_body": "<div>Send to Clay - Add to JustCall</div>"
    }
  ]
}
→ {"ok":true,"data":{"sequences":[{"seqNumber":1,"id":...}, ...]}}
```

Rules discovered by probing the Joi validation:
- Variants array is `seq_variants`, NOT `variants` (docs are wrong — `variants` → 400 "not allowed").
- `seq_type` enum: `EMAIL` (default if omitted), `MANUAL`, `CALL` (fails: "No active dialer package subscription"). `TASK`/`LINKEDIN`/`SMS` rejected.
- **Manual step** = `seq_type: "MANUAL"` + top-level `subject` (task title) + `email_body` (task description). No `seq_variants`.
- `delay_in_days` is relative to the previous step (0–365). Empty `subject` on an EMAIL step = send in same thread ("Re:").
- Multiple A/B variants: add more objects to `seq_variants` with labels "B", "C"…
- POSTing sequences replaces the whole sequence list for the campaign — **but passing each existing
  step's `id` upserts it in place instead** (verified 2026-09-21 on probe campaign 3995845, then used
  to append step 8 to live campaign 3838665). Omit the `id`s and the old rows are **destroyed and new
  ids minted** (10893008-11 → 10893013-14 on the probe).
  ⚠️ **This is a data-loss trap on a live campaign.** Sent-email records reference the step row via
  `email_campaign_seq_id` (see `/campaigns/{id}/statistics`), so a no-id re-save orphans every lead's
  history and can re-send the whole sequence to leads who already got it. **Never POST sequences to a
  campaign with leads without including the `id` of every existing step.** Safe procedure: GET the
  sequence → snapshot it to disk → rebuild the payload *from that GET* (byte-identical bodies) with
  ids → append the new step(s) → POST → GET again and diff ids/created_at/subject/email_body.
- EMAIL steps come in two shapes and you must preserve the one already in use: **variant** steps
  (`seq_variants: [...]`, subject on the variant — GET shows step-level `subject: ''`) and
  **non-variant** steps (top-level `subject` + `email_body`, GET shows `sequence_variants: null`).
  A non-variant EMAIL step posts fine with `seq_type: "EMAIL"` + top-level subject/body and no
  `seq_variants` / no `variant_distribution_type` — round-trips exactly. Re-saving a non-variant step
  in variant shape would silently change the copy's structure.
- GET `/campaigns/{id}/sequences` returns steps but does NOT expose `seq_type` — a manual step comes back looking like an email with `sequence_variants: null`. Don't be fooled during verification.

## 3. Schedule

```
POST /campaigns/{id}/schedule?api_key=...
{
  "timezone": "America/New_York",
  "days_of_the_week": [1,2,3,4,5],
  "start_hour": "09:00",
  "end_hour": "18:00",
  "min_time_btw_emails": 20,
  "max_new_leads_per_day": 2000,
  "schedule_start_time": "2026-07-10T13:00:00.000Z"
}
→ {"ok":true}
```
- Days: 0=Sunday … 6=Saturday.
- POST names `min_time_btw_emails` / `max_new_leads_per_day` → GET returns `min_time_btwn_emails` / `max_leads_per_day` (verified both apply).
- `schedule_start_time`: ISO 8601. Standard = today's date.

## 4. General settings

```
POST /campaigns/{id}/settings?api_key=...
{
  "track_settings": ["DONT_TRACK_EMAIL_OPEN", "DONT_TRACK_LINK_CLICK"],
  "stop_lead_settings": "REPLY_TO_AN_EMAIL",
  "send_as_plain_text": false,
  "follow_up_percentage": 30,
  "enable_ai_esp_matching": false,
  "unsubscribe_text": ""
}
→ {"ok":true}
```
- POST values are `DONT_TRACK_EMAIL_OPEN`/`DONT_TRACK_LINK_CLICK`; the GET echoes them back as `DONT_EMAIL_OPEN`/`DONT_LINK_CLICK`. Posting the GET spelling fails ("Invalid track_settings value").
- `stop_lead_settings` enum: `REPLY_TO_AN_EMAIL` (standard), `CLICK_ON_A_LINK`, `OPEN_AN_EMAIL`.
- `follow_up_percentage: 30` = the UI slider "30% follow ups, 70% new leads".
- If settings are never posted, `follow_up_percentage` defaults to 100 — always post settings.
- NOT settable via public API: variant distribution mode (pattern/randomized), SmartInfra, company-level auto-pause, bounce auto-protection, domain rate limiting. Those follow workspace UI defaults.
- Settable via `POST /settings` (verified 2026-11-06, campaigns 4341415/4341416): `add_unsubscribe_tag` (bool; **new campaigns default to `true`**, our live ones are `false`), `ai_categorisation_options` (array of category ids, e.g. `[4,5,6,7,1,2,3,8,31756,9]`; new campaigns default to `[]`), `out_of_office_detection_settings` (`{ignoreOOOasReply, autoCategorizeOOO, autoReactivateOOO, reactivateOOOwithDelay}`, but **rejects `autoCategorizeOOO` + `autoReactivateOOO` both true**, the combo our live campaigns use; set that one in the UI).
- Saving sequences by API fills `follow_up_subject` on in-thread steps with the first step's subject (live campaigns show `null`). Cosmetic: replies still thread.
- Start/pause is `POST /campaigns/{id}/status {"status":"START"|"PAUSED"|"STOPPED"}`. This skill must never call it; documented only so a reader recognises it.

## 5. Email accounts (inboxes)

```
GET  /email-accounts/?api_key=...&offset=0&limit=100     # all accounts, paginate by 100 (507 total as of 2026-07-10)
GET  /campaigns/{id}/email-accounts?api_key=...          # accounts on a campaign (read-only, fine on any campaign)
POST /campaigns/{id}/email-accounts?api_key=...          # attach accounts to OUR new campaign only
{"email_account_ids": [18454841, 18454655]}
→ {"ok":true,"result":[...]}
```
Account objects carry `tags: [{tag_name: "A" | "B" | "Premium Inboxes" | "Near - CI" | ...}]`, `from_email`, `from_name`. Inbox groups in campaign names ("A Inboxes") map to tag names. Attach in batches of 100.

## 6. Verify (read-only)

```
GET /campaigns/{id}?api_key=...            # settings + schedule as stored
GET /campaigns/{id}/sequences?api_key=...  # steps (remember: seq_type not shown)
GET /campaigns/{id}/email-accounts?api_key=...
```

## Endpoints this skill must NEVER call

- `POST /campaigns/{id}/status` (start/pause/stop)
- Any DELETE
- Any write against a campaign ID not created in the current run (except reads)

## Spec JSON schema for scripts/create_campaign.py

```json
{
  "name": "US OJ | Example | A Inboxes",
  "start_date": "2026-07-10",
  "emails": [
    {"day": 1, "subject": "Subject line", "body_html": "<div>...</div>"},
    {"day": 4, "subject": "", "body_html": "<div>follow-up, same thread</div>"},
    {"day": 8, "subject": "New thread subject", "body_html": "<div>...</div>",
     "variants": [{"subject": "alt subject", "body_html": "<div>variant B</div>"}]}
  ],
  "manual_step": {
    "title": "Send Lead to Justcall",
    "description": "Send to Clay - Add to JustCall",
    "delay_after_last_email_days": 1
  },
  "email_account_ids": [18454841, 18454655],
  "schedule_overrides": {},
  "settings_overrides": {}
}
```
- `day` is the absolute send day (Day 1 = first day). The script converts to relative delays.
- `manual_step` may be `null` ONLY if Gaston explicitly said to skip it; omitting the key uses the standard step above.
- `schedule_overrides` / `settings_overrides` accept the exact POST field names from sections 3–4.
