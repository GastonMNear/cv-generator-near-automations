---
type: tool
title: Smartlead — Reference
created: 2026-06-03
updated: 2026-09-01
tags: [tool, smartlead]
status: active
related: ["[[tools/clay]]", "[[context/outbound-engine]]", "[[tools/make]]"]
---

# Smartlead

Cold email sending + inbox/domain infrastructure. Gaston owns this end of the engine: inboxes, domains, campaign setup, sending capacity, deliverability/volume constraints. See [[context/outbound-engine]].

## Access

- Auth: API key (`SMARTLEAD_API_KEY` env var)
- Webhooks: Reply events can trigger downstream workflows
- API feeds reporting sync. As of July 2026, lead sync should use Paz's SmartLead batch-fetch action rather than Clay imports to BigQuery.

## Campaign Creation (agent skill)

The `smartlead-campaign-creator` skill creates new campaigns via API (sequences, schedule, settings, inboxes, ending manual "Send Lead to Justcall" step). Create-only — never edits existing campaigns. Verified API quirks (curl-only, `seq_variants`, `seq_type: MANUAL`, POST-vs-GET field names) live in the skill's `references/api-reference.md`. Creations are logged in `logs/smartlead-campaign-log.md`.

## Campaign Architecture

- **Baseline vs. Challenger** A/B split test, with **routing logic built in Clay**.
- US Open Jobs +50; US Open Jobs <50 (baseline + direct-booking variants).
- Replicating responsive campaigns onto new inbox sets (e.g. **Aniwa inboxes**) then re-positioning (those roles were on-site; Near's offer is usually remote).
- Fallback campaigns used so sending capacity isn't wasted when a test pauses.

## Reporting Sync Decision (July 2026)

Do **not** use Clay imports to BigQuery for lead sync anymore.

Current path:
- Paz's SmartLead batch-fetch action fetches leads directly from Smartlead.
- It uploads missing leads into the reporting system.
- It updates existing lead rows when Smartlead data changes.

Operational notes:
- Confirm the latest batch run before using BigQuery/reporting for leadership decisions.
- Monitor run time, error logs, missing-lead count, and changed-lead count.
- Add/verify `LeadSource` in the synced fields so reporting can compare contact quality by source: Clay vs AI researcher vs Apollo.
- Keep Smartlead campaign names aligned with the Outbound Metrics / Command Center names.

## Capacity & Cost

- Monitor sending volume vs. **max capacity**; decide whether to add inboxes/domains.
- Cost types are distinct — **inbox cost ≠ domain cost ≠ Smartlead sending cost ≠ Clay credits.** Roll up to cost per lead / per call booked.
- Don't expand capacity unless added volume reaches high-intent opportunities.

## Platform Analysis (alternatives)

- **Instantly** judged the strongest Smartlead alternative on **UX & variant management** — *not migrated.*
- Conclusion: **Clay layered on top of Smartlead** remains best for firmographic segmentation.

## Quirks / Notes

- **Expired API keys broke Make.com automations** — check key validity when scenarios silently fail. See [[tools/make]].
- QA rendered emails before launch: unfilled placeholders, grammar, spintax. See [[context/outreach-playbook]].
- Smartlead search can be imperfect for calls-booked attribution. Search by partial company name, lead name, and domain before marking attribution unresolved.
- Current known workflow gap: no-reply leads can enter Calling Sequences through Smartlead step/webhook logic; replied-then-ghosted leads need investigation for webhook or batch return to calling.

## Reporting API — verified endpoints (for automations)

Verified live 2026-07 while building the response-time KPI. Base `https://server.smartlead.ai/api/v1`, auth `?api_key=`. **curl only** — python-requests get a Cloudflare 403. Full, maintained reference lives in the `smartlead-weekly-response-kpi` skill (`.claude/skills/.../SKILL.md`, "Known API facts"); this is the quick pointer.

- **Rate limit: 200 requests/min** (account-wide). Throttle bulk scans (~175/min) with backoff.
- `GET /leads/fetch-categories` → categories with `sentiment_type` (`positive` / `negative` / null). Positive = Interested, Meeting Request, Information Request, Meeting Booked, Candidate sent - Follow Up, Send to Cold Call.
- `GET /campaigns/{id}/statistics?offset=&limit=` → per-email rows with `reply_time`, `lead_category`, `lead_email`, `sent_time`. Best way to find who replied + when, per campaign. `total_stats` can come back as a **string** (cast to int when paging). Also accepts `sent_time_start_date` / `sent_time_end_date` (YYYY-MM-DD) to window the rows server-side — but `sent_time` is **UTC (`...Z`)**, so for ET week boundaries pull unfiltered and bucket client-side.
- `GET /leads/?email=` → lead object incl. `id` (needed for message-history).
- `GET /campaigns/{id}/leads/{lead_id}/message-history` → `{history:[...]}`, each msg has `type` (`SENT`/`REPLY`), `time`, `email_seq_number`. **Manual Master-Inbox replies show as `type: SENT` with `email_seq_number: null`** — that's how we can measure our own reply times.
- **Categorization is live**: querying a past window later gives different counts as leads get re-categorized. For stable KPIs, measure on a fixed cadence and freeze the snapshot (we write it to a Google Sheet). See the KPI skill.
### "Leads added today" + "has email 1 gone out" (verified 2026-10-22)

- `GET /campaigns/{id}/leads?created_at_gt=<ISO UTC>` filters server-side on the lead's campaign-enrolment
  `created_at`, and `total_leads` returns the filtered count. One call with `limit=1` per campaign gives a cheap
  "leads added since X" across all ~60 active parents. ART midnight = `T03:00:00.000Z`.
- Lead `status` on that endpoint: `STARTED` = enrolled, email 1 not sent yet; `INPROGRESS` = at least email 1 sent.
  Cross-checked against `/statistics` seq-1 sends on 865 leads: matched, apart from leads that sent in the
  minutes between the two pulls.
- `/statistics?sent_time_start_date=` is slow across 20+ campaigns (>5 min). Use `status` for a quick answer.
- Active parent campaigns = `status == ACTIVE` and no `parent_campaign_id` (skips subsequences).
- Per-day adds: query several `created_at_gt` thresholds (one per ART midnight) and diff the totals. ~8 calls × 72 campaigns at 8 workers hits **429**; 3 workers + backoff on 429 finishes in ~1–2 min (2026-11-09).

### Renaming a campaign / subsequence (verified 2026-09-21)

`POST /campaigns/{id}/settings` accepts a **`name`** field, and it is a true **partial update** — posting
`{"name": "..."}` alone renames the campaign and leaves `track_settings`, `stop_lead_settings`,
`send_as_plain_text`, `follow_up_percentage`, `unsubscribe_text`, schedule, sequences, trigger and status
untouched (probed on a throwaway DRAFTED campaign before running it on 32 live subsequences). There is no
separate rename endpoint; the public docs don't list `name` on this route.

### Subsequence send timing — measured, not inferred (verified 2026-09-22, n=30 leads)

**First email = enrolment + 24h**, then clamped forward to the next slot inside the campaign's send
window (ours: Mon–Fri 09:00–18:00 America/Argentina). Steps 2–5 then follow at +1 day each.

- The **trigger delay** ("Add leads to subsequence after the delay (in days)") is the ONLY wait before
  email 1. **Step 1's own `delay_in_days` is NOT an additional wait** — it does not stack. 30 leads
  enrolled Mon 21 Sep 10:34–12:51 AR all received email 1 on Tue 22 Sep at gaps of 1.00–1.08 days.
- Sends fire at roughly `enrolment time + 24h`, **not** only at the 09:00 window opening — observed
  sends at 10:43, 11:23, 13:43 AR. A lead only sends at 09:00 when its due time fell outside the
  window (e.g. over a weekend) and it is waiting for the window to reopen.
- **Cadence is 5 business days, not 5 calendar days** — a due time landing Sat/Sun or after 18:00 rolls
  to the next weekday 09:00.
- A reply stops the sequence (`stop_lead_settings: REPLY_TO_AN_EMAIL`), so most leads never see all 5.

⚠️ **Don't infer this model from one or two leads.** Weekend clamping makes a 1-day and a 2-day model
predict the same send date for anything enrolled Fri; and a lead that looks "overdue" may simply be
minutes away from its send. Pull enrol→first-send for every lead and only trust the rows where no
weekend falls in between.

### Subsequence enrolment fires on category SET, not continuously (verified 2026-09-21)

A subsequence only picks up a lead at the instant its `lead_category_id` is written. A subsequence created
today will **never** look back at leads already carrying its trigger category — they sit tagged forever and
never enter it. After creating a subsequence, backfill by re-writing the category on the existing leads:

```
POST /campaigns/{campaign_id}/leads/{lead_id}/category   {"category_id": <id>}
```

- **This route has no validation** — it accepted `{"category_id": -1}` and silently cleared the lead's
  category, returning `{"ok":true}`. Never "probe" it; it always writes. Read the current value first
  (`GET /campaigns/{id}/leads` returns `lead_category_id` per row) so you can restore.
- Re-setting is enough to enrol: clearing then re-writing the original value enrolled the lead. A round trip
  through a neutral category and back also works, and is what we use.
- **Before choosing the intermediate category, check every subsequence on that campaign for a trigger on it** —
  otherwise the hop enrols leads into the wrong subsequence, which cannot be undone once it starts sending.
  Triggers are UI-only, so this check is a browser job.
- `GET /campaigns/{id}/leads` paginates at 100 and returns `lead_category_id`, `campaign_lead_map_id`,
  `status` and the nested `lead` object — the cheapest way to find every lead in a given category per campaign.
- The category lives on the campaign↔lead mapping, so a lead enrolled into a subsequence shows
  `lead_category_id: null` inside that subsequence while still holding its category on the parent.

### Reading a subsequence's TRIGGER — the internal app API (verified 2026-09-23)

**Supersedes the old "triggers are UI-only, confirm in the browser" note below.** Triggers are fully
readable, and auditing 40 of them takes seconds instead of 40 page loads.

```
GET https://server.smartlead.ai/api/email-campaigns/{parentId}/subsequence/{subId}/conditions
→ {"data":{"email_campaign_sub_seq_conditions":[
     {"id":…, "event_type":"CATEGORY", "event_sub_type":null,
      "category_id":101821, "delay_for_new_leads":1, "text":null}]}}

GET https://server.smartlead.ai/api/email-campaigns/lead-categories   → id ↔ name map
```

- This is the **internal app API** (`/api/`, no `/v1`) — a different surface from the public
  `server.smartlead.ai/api/v1`. It authenticates with a **`Bearer` token**, not the `api_key` query param.
- Run it **from inside a logged-in app.smartlead.ai page**. Grab the token by patching
  `XMLHttpRequest.prototype.setRequestHeader` and letting the app make one call, then reuse the header.
- ⚠️ **Do NOT set `withCredentials = true`** — the server sends `Access-Control-Allow-Origin: *`, and the
  browser rejects that combination with an opaque `status: 0` / `onerror`. This cost real time; the
  plain `fetch()` with a custom header fails the same way. Use `XMLHttpRequest` with only `Authorization`.
- The **UI cannot show you this for a running subsequence**: `/subsequence/{id}/lead-condition` renders
  the stored values only while the sub is `DRAFTED`; once it is ACTIVE/COMPLETED the app redirects to
  `/leads` and there is no Lead Condition tab. The subsequences list and `get-all-campaigns
  ?parentCampaignId=` carry name/status/sequence_count but **no condition**. So the API above is the
  only practical audit route.
- **Workspace category ids** (internal = same ids the public API returns): 1 Interested, 2 Meeting Request,
  3 Not Interested, 4 Do Not Contact, 5 Information Request, 6 Out Of Office, 7 Wrong Person,
  8 Uncategorizable by Ai, 9 Sender Originated Bounce, 31756 Asked to Circle Back Later,
  **101821 Candidate sent - Follow Up**, 101822 Meeting Booked, 127523 CV Sent - Opp Lost,
  133363 Send to Cold Call, 167092 Not Qualified, 177715 HM Reactivation | New Job Post,
  181675 Meeting Request - Follow up, 181810 Info Requested/Interested - Follow Up, 182137 Weekend Follow Up.

**Found on the first run (2026-09-23):** all 35 pre-existing `Candidate sent` subs had
`delay_for_new_leads: 2` while the source and Gaston's spec are **1**. Category was right on 40/40.
Audit the delay, not just the category — a wrong delay is invisible in every other view.

### Creating a subsequence in the UI — working recipe (verified 2026-09-23, 5 created)

Confirms and sharpens the 2026-09-21 notes:
- `POST /campaigns/create` still rejects `parent_campaign_id`/`subsequence_of`/`parent_id`/
  `sub_sequence_id`/`lead_condition`/`trigger` ("is not allowed"), and every `subsequences`/
  `lead-condition`/`trigger` route 404s on **POST as well as GET**. Re-verified — the create really is UI-only.
- Dialog: click **Add Subsequence** → focus `.q-dialog input` via JS, then send a real `type` action
  (setting `.value` does not register with Vue) → assert the value → click **Create SubSequence**.
  The new id arrives in `location.href` (`/subsequence/{newId}/lead-condition`).
- On the condition page the **category `.q-select` must be clicked open** before its `.q-item` options
  exist. The delay field is `input[type=number]`: focus it, `cmd+a`, then `type` the digit.
- **The page is slow to mount after create** — `.q-select` elements are often still absent 5s later.
  If they are missing, re-navigate to `/subsequence/{id}/lead-condition` and wait; don't retry blindly.
- A fresh subsequence has **no schedule at all** (`scheduler_cron_value: null`, `max_leads_per_day: 100`,
  `follow_up_percentage: 100`, `track_settings: []`). Always POST `/schedule` and `/settings` afterwards
  or it will not match the source.
- **Near never tracks opens or clicks.** A fresh subsequence defaults to `track_settings: []` (tracking ON),
  so the `/settings` POST must include `"track_settings":["DONT_EMAIL_OPEN","DONT_LINK_CLICK"]`. On 2026-10-19,
  26 subs created without it were leaking opens into the dashboard. Audit: one `GET /campaigns` call, filter
  rows whose `track_settings` is missing `DONT_EMAIL_OPEN`.

### The public API CANNOT create a subsequence (verified 2026-09-21)

Probed exhaustively before attempting a 30-subsequence replication. Do not re-probe this:

- Every subsequence/trigger route 404s: `GET /campaigns/{id}/subsequence`, `/lead-condition`,
  `/lead-conditions`, `/trigger`, `/conditions`, `/sub-sequence`, and `GET /campaigns/{parent}/subsequences`.
- `POST /campaigns/create` rejects the fields that would be required — `parent_campaign_id`,
  `subsequence_of`, `lead_condition`, `trigger`, `parent_id`, `sub_sequence_id` all return
  `"<field>" is not allowed` (Joi whitelist). Probe safely by sending a **valid `name` plus an invalid
  TYPE** on the field under test: validation fails either way, so nothing is created.
- Consequence: a subsequence can only be created, and its trigger set, through the **Smartlead UI** or an
  undocumented internal app-API path. The 2026-09-03 bulk replication (subs 3902593–3902611) left no record
  of its method; its log line mentions "Smartlead UI trigger audits", implying the UI.
- What the public API *can* do to an existing subsequence: rename it, read its sequences/settings, and read
  its parent. That is all.

**The working method (verified 2026-09-21 over 30 subsequences) is hybrid UI + API:**

1. **UI — create the shell and set the trigger.** Go to
   `https://app.smartlead.ai/app/email-campaigns-v2/{parentId}/subsequences` (direct URL works).
   The add button is labelled **"Add Subsequence"** when the campaign already has subsequences and
   **"Create First SubSequence"** when it has none — match both. Type the name, click
   *Create SubSequence*; Smartlead creates the child and redirects to
   `/subsequence/{newId}/lead-condition`, so **the new subsequence ID comes from `location.href`**.
   On that page set *Choose condition* (already defaults to "Add leads based on the lead categories"),
   pick the category, set the delay, then *Save & Continue*.
2. **API — everything else**, against the new `{subsequence_id}` exactly like a normal campaign:
   `POST /sequences`, `POST /schedule`, `POST /settings`, then `POST /status {"status":"ACTIVE"}`.
   Do **not** post `/email-accounts` — a subsequence with 0 directly attached inboxes inherits the parent's.

**Browser-automation gotchas (cost real time; don't rediscover them):**
- Do **not** emulate a viewport (`resize_window` with width/height): click coordinates stop mapping to the
  page and clicks land on `body`. Use the pane's own size (preset `desktop`).
- Driving Quasar (`.q-*`) widgets by JS click works for buttons and `.q-item` options. Text inputs need a
  real keystroke: `input.focus()` via JS, then send a `type` action — setting `.value` from JS does not
  register with Vue.
- The category dropdown must be **opened first** (click the `.q-select` whose input value is empty) before
  its `.q-item` options exist in the DOM. Typing does not filter the list; find the option by exact text.
- Assert the name, category and delay in the page **before** clicking Save, and re-read the
  `/lead-condition` page afterwards — for a DRAFTED subsequence it renders the stored values directly,
  no Edit mode needed. That post-save read is the only trigger audit available.

**Trigger categories in this workspace** (exact strings): `Info Requested/Interested - Follow Up`,
`Meeting Request - Follow up`, `Candidate sent - Follow Up`, `Weekend Follow Up`, plus the Smartlead
built-ins (Interested, Meeting Request, Information Request, …).


### Updating an EXISTING subsequence's copy in place (verified 2026-09-23, 27 live subs)

Replicating a subsequence across campaigns that **already have one** is an update, not a create — so it
needs no UI at all. The whole job is two public-API calls per subsequence:

1. `POST /campaigns/{sub}/sequences` with the **existing `id` of every step you are rewriting** plus the
   new steps with no `id`. Bodies/subjects/delays on the id-carrying rows are overwritten in place and
   `email_campaign_seq_id` history survives. This is the same id trap as §2 of the campaign-creator
   api-reference, used deliberately: 3 old steps upserted, 3 new ones appended, 27/27 with zero id churn.
2. `POST /campaigns/{sub}/settings {"name": "..."}` to rename.

**Writes are eventually consistent — on `/sequences` AND `/settings`.** Both return `{"ok":true}`
immediately, but a `GET` seconds later can still serve the PRE-write state: on 2026-09-23 a verification
pass 4s after an 8-subsequence batch showed 5 of 8 still as the old 3-step version, and all 8 read clean
at ~30s. **Wait ~30s before the verification read, and on a mismatch re-read once before re-posting** —
re-posting on a stale read is how you'd double-append steps. Same applies to `name`.

**Matching the right subsequence is a copy problem, not a name problem.** Replicated subs keep the
source campaign's name, so on 2026-09-23 six of 27 CV-sent subs were named things like
`SUB | [EXP005] ... | Candidate-led Angle` and `SUB | [EXP010] Apollo Open Jobs No HM` with no
"Candidate sent" anywhere. Identify by **sequence body** instead (the CV-sent sub is the one whose
step 1 reads *"did you have a chance to review the profile I sent over"*), then confirm the campaign's
other subs are all accounted for (`info requested`, `Meeting request`, `Weekend Follow Up`,
`HMs Reactivation`) before writing.

**Cheap blast-radius proof after a bulk write:** snapshot `GET /campaigns` (all pages) before and
after and diff every field except `updated_at` — 298→298 rows, only the intended `name` changes. Then
grep a distinctive string from the new copy across every sibling subsequence and parent campaign to
prove nothing else received it.

### Subsequences are campaigns with `parent_campaign_id`

`GET /campaigns` returns subsequences inline with normal campaigns; a subsequence is any row with a non-null
**`parent_campaign_id`** pointing at its parent. So the cheap way to audit "which campaigns have subsequence X"
is one `/campaigns` call, group by `parent_campaign_id` — no per-campaign requests needed.

- A subsequence's **`status` tracks lead flow, not configuration**: `DRAFTED` just means no lead has been
  triaged into it yet (0 leads, sequence steps still fully built); it flips to `ACTIVE` when the first lead
  enters. A `DRAFTED` subsequence is *not* broken or unpublished — don't report it as missing.
- The **trigger category** (which lead category fires the subsequence) is **not exposed by the API** — it's
  UI-only config. You can only match subsequences by name; confirm triggers in the UI.
- Replicating a subsequence across parents does **not** rename it — copies keep the source campaign's name, so
  names go stale fast and are a poor guide to what a sub actually does. Check `parent_campaign_id`, not the name.

- Error responses come back as `{"message": "..."}` (e.g. `Invalid API Key` when a key rotates/expires — cf. [[tools/make]] key-expiry note).

### Counting uncontacted leads (verified 2026-09-18)

"Uncontacted" = lead added to a campaign whose sequence has not sent anything yet. Two routes, both cheap:

- **`GET /campaigns/{id}/analytics`** → `campaign_lead_stats: {total, notStarted, inprogress, completed, paused, stopped, blocked, interested}`. `notStarted` is the count. One request per campaign (~186 total, seconds at 8 workers). Counts here lag the live list slightly (683 vs 719 on one campaign) — good for a sweep, not for an exact number.
- **`GET /campaigns/{id}/leads?status=STARTED&offset=&limit=100`** → the authoritative list. **`status` is an accepted query param on this route** (`lead_status`, `campaign_lead_status`, `filter` all 400). `STARTED` == analytics' `notStarted`; spot-checked 12 of them against `message-history` → all 0 messages. Rows carry `created_at` (when the lead was added to the campaign) so you can age the backlog. Full account scan = ~270 requests, under a minute.

Watch the campaign status when reporting: the bulk of account-wide `notStarted` sits in **ARCHIVED** campaigns and will never send. On 2026-09-18: 8,114 uncontacted total, but 6,673 were in archived May–June campaigns; only 1,441 were in ACTIVE/PAUSED campaigns. Always split by `campaign.status` before quoting a number.

## Booked-call attribution (same-week vs prev-week pipeline) — verified 2026-09-01

Built to answer "of the calls booked this week, how many came from emails sent this week vs.
contacts from earlier weeks". Rule: bucket on the lead's **first** reply — first reply inside the
booking week = that week's pipeline; first reply before it = a prior week's pipeline. Later replies
in an ongoing thread are irrelevant.

- **`GET /leads/?email=` also returns `lead_campaign_data[]`** — per campaign it carries
  `campaign_id`, `campaign_name`, `lead_category_id`, `last_reply_at`, `last_sent_at`,
  `campaign_lead_map_id`. **This is the cheap way to get a lead's category** — one request instead
  of paging a campaign's `/statistics`. The category lives on the **campaign↔lead mapping, not the
  lead**: the same lead is `101822` in one campaign and `null` in another.
- **`last_reply_at` is the LAST reply, not the first.** For first-reply attribution you must pull
  `/campaigns/{cid}/leads/{lid}/message-history` and take the earliest `type: REPLY`. Leads are
  routinely in 2 campaigns, so take the min across **all** campaigns in `lead_campaign_data`.
- **Category IDs** (from `/leads/fetch-categories`): `1` Interested, `2` Meeting Request,
  `3` Not Interested, `4` Do Not Contact, `5` Information Request, `6` Out Of Office,
  `7` Wrong Person, `8` Uncategorizable by Ai, `9` Sender Originated Bounce,
  `31756` Asked to Circle Back Later, `101821` Candidate sent - Follow Up,
  **`101822` Meeting Booked**, `127523` CV Sent - Opp Lost,
  `133363` Send to Cold Call (Lead went cold), `167092` Not Qualified.

### Finding who booked at a given company — scan categories, don't guess domains

Two routes were tried. **The statistics scan is the better one:**

- `GET /campaigns/{id}/statistics` over all non-DRAFTED campaigns, filtering
  `lead_category == "Meeting Booked"` → **139 campaigns scanned, 481 rows, 318 unique booked leads
  account-wide, ~7 min** at 8 workers / 170 req-per-min. Small enough to then match companies by eye.
- The `/leads/all` crawl (214,668 leads, 5.5 min) works for company→leads but needs the company's
  domain guessed up front, which is exactly what fails on ambiguous names.

**Why the scan wins:** it resolved the cases the domain crawl could not.
`Purpose` matched **6 unrelated companies** by name (purpose.app, teampurpose.com,
purpose-unlimited.com, purposebrands.com, …); the booked-lead list identified it as `purpose.app`
with no guessing. Only fall back to the domain crawl to find a company's *colleagues*.

> [!warning] **Don't strip the last dot-segment as a "TLD" when normalising domains.**
> A matcher that did this turned `grade.capital` into the stem `grade` and silently missed the
> GRADE CAPITAL booking. New gTLDs (`.capital`, `.app`, `.io`, `.ai`) are common in this book —
> match on the **full** domain. Cf. `norm_domain()` in the `booked-call-pause` skill, which
> correctly keeps the whole domain.

### Automated now — see the `booked-call-attribution` skill (added 2026-09-01)

The manual "Gaston pastes a company list" step is gone. HubSpot supplies the roster directly:
meetings created in the week with `hs_activity_type` present, whose associated **contact** carries
`meeting_source__standardized_ == "Email Outreach"`. Validated against the 74-row hand-built
baseline over 8 weeks — 5 weeks match exactly, and the filter independently found **3 bookings the
manual roster had missed** (Krece 08-03, which was the open question in the handoff, and Cash Margin
Partners twice). Full comparison in `.claude/skills/booked-call-attribution/references/regression.md`.

Two consequences for anything reading this section:

- **Because HubSpot hands over the booker's exact email, most bookings resolve with a single
  `/leads/?email=` call** — 8 of 12 in the 2026-08-24 week. The ~7-minute statistics scan is now a
  *fallback*, triggered only when something is left unresolved, rather than the first move.
- **Booking addresses can be helpdesk hosts.** Artic Grey books from
  `anthony.spallone@arcticgreyltd.zendesk.com` while the lead we emailed is
  `anthony.spallone@arcticgrey.com`. `zendesk.com`, `freshdesk.com`, `helpscout.net`, `intercom.io`
  and friends now sit in `JUNK_DOMAINS` next to LinkedIn and the free mailboxes — keying on one
  would join every company routing support through the same vendor.

Resolved end-to-end for the 2026-08-24 week: 12 bookings, **0 unresolved**, 7 same-week / 5 prev-week,
and every one of the six hand-verified first-reply timestamps reproduced to the minute.

### Company matching gotchas seen in this run

- **`company_name` is often a shortened brand**: `Sana` for Sana Benefits, `Grade` for GRADE
  CAPITAL, `HypeProxies` for Hype Proxies. Match on domain + name, never name alone.
- **Email domain ≠ company domain, legitimately.** The Blackout Coffee Co. booking is
  `john@howloo.com` with `company_url: blackoutcoffee.com`; the LinkedIn company and job post both
  confirm Blackout Coffee. Verify via `custom_fields.company_linkedin_url` / `job_url` before
  rejecting a mismatch (and cf. the cross-company guard in `booked-call-pause`).
- **Short/common company names generate heavy false positives** on substring matching: `usad`
  matched 25 leads (USADA, USA Diving, `adusasc.com`, `atticusadvantage.com`, …), `cactus` matched
  23 (Cactus Life Sciences / Materials / Wellhead / Inc). Always eyeball the matched name list
  before spending per-lead requests.

### The booking company is NOT always the lead's company — match on the person

The single hardest case in this run. The **USAD** booking came from `Yasha@usadistributions.com`,
which returns `{}` from `/leads/?email=` — that address is not in Smartlead at all. The same human is
in Smartlead as **`yasha@mercatodibellina.com`** ("Mercato Di Bellina", Founder,
`linkedin.com/in/yashasack/`), cold-emailed about an Amazon account-manager role at that company.
He booked under a *different* company he's involved with.

So when a company name and every plausible domain come up empty, **fall back to matching the
booker's name** against `lead_name` in the Meeting-Booked set, then confirm via
`linkedin_profile`. Founders with several ventures book under whichever entity is hiring.
Never conclude "not in Smartlead" from a domain miss alone.

(Cf. the milder version of this: Blackout Coffee's booker mails from `howloo.com`.)

### Long-nurture bookings are real — do not window the first-reply search

USAD first replied **2026-07-15**, went quiet for a month, re-engaged 08-17, and booked in the
08-24 week — a 6-week gap between first reply and booking. Any attribution query that only looks
back one or two weeks for the first reply will mis-bucket these as same-week. Search the lead's
**entire** message history, unbounded.

### Results — 8 weeks, 2026-07-06 → 2026-08-30 (measured 2026-09-01)

74 booked calls across 8 weeks: **42 same-week (57%), 32 prev-week (43%)**.

| Week (Mon–Sun) | Calls | Same wk | Prev wk | Same % |
|---|---|---|---|---|
| 07-06 → 07-12 | 10 | 5 | 5 | 50% |
| 07-13 → 07-19 | 5 | 2 | 3 | 40% |
| 07-20 → 07-26 | 12 | 8 | 4 | 67% |
| 07-27 → 08-02 | 10 | 4 | 6 | 40% |
| 08-03 → 08-09 | 5 | 4 | 1 | 80% |
| 08-10 → 08-16 | 7 | 6 | 1 | 86% |
| 08-17 → 08-23 | 12 | 6 | 6 | 50% |
| 08-24 → 08-30 | 13 | 7 | 6 | 54% |
| **Total** | **74** | **42** | **32** | **57%** |

Per-company detail is re-derivable; a CSV was handed to Gaston in-session.

> [!warning] **Weekly volume is 5–13 calls, so the weekly percentage is mostly noise.**
> The two highest same-week rates (80%, 86%) are the two **lowest-volume** weeks (5 and 7 calls) —
> one booking moves them 14–20 points. Read the 8-week pooled 57% as the real number and treat the
> weekly series as directional only. Do not report a single week's swing as a trend.

**A Mon/Tue-reply hypothesis was tested and refuted.** In the 08-24 week every same-week booking
first replied Mon or Tue, which suggested Wed–Fri replies always slip. Across all 8 weeks that is
false — same-week bookings first replied on every weekday, including Fri (Aventiqo 08-14, WebForce
07-24, Lindsey Self Storage 07-24) and Sat (Safeguard 07-11). Same-week conversion is not gated on
an early-week reply.

**Watch the weekend boundary — it decides real calls.** TheMCTTeam first replied **Sun 08-16 10:30**,
~14 h before its week opened; jmfbuilders **Sat 08-15 01:05**; Rex Developments **Sat 07-04**. A
Sunday-start week would move these to same-week. The Mon-00:00 ET cutoff is load-bearing, so state
it on any chart.

**Also expect off-hours first replies.** Maxim Group 05:03, AstroZon 02:42, AfterShip 06:23 ET —
overseas leads reply outside US hours. Nothing to fix; just don't treat them as data errors.

### Two more identity cases (both cracked by person, not company)

- **RISE Research** books as `yash@riseresearch.com` (HubSpot) but is `yash@riseglobaleducation.com`
  in Smartlead — same human, Yash Mundada. A colleague (`shreyans@riseglobaleducation.com`) is also
  tagged Meeting Booked, so domain-only matching returns two candidates and picks wrong 50% of the time.
- **Rex Developments** books as `design@rexarch.com`; Smartlead has `mahmad@rexmediausa.com`
  (`company_name: Rex`, `company_url: rexarch.com`, Mohadib Ahmad). HubSpot spells the surname
  *Bakali*, Smartlead *Ahmad* — first name + company domain is what ties them.

**When two leads at one company both carry the Meeting Booked tag, go to HubSpot for the tiebreak** —
`hs_createdate` on the booking says which one booked in the week you're measuring. Krece had two
genuine bookings 5 days apart (Samuel Gedaly 08-05, Jonathan Bentata 08-10) landing in *different*
weeks. Four of 49 companies in this run were ambiguous this way, so budget for it.

**A false positive to know about:** loose substring keys are dangerous on short names. `rex` matched
`cognitrex.com`, `rise` matched 10 unrelated HubSpot companies, `sana` matched 50+.
Require the key to match the **registrable domain or the full company name**, not any substring.

### Not every booked company is in Smartlead

**jmfbuilders** has no Smartlead lead at all — `info@jmfbuilders.com` and `mauricio@jmfbuilders.com`
both return `{}`, no booked lead matches "Mauricio Giron", and its HubSpot booking says
*"How did you hear about Near?: Email"* with no matching Smartlead record. Gaston supplied the reply
date (Sat 08-15 01:05) from his own inbox. So `Email` in the Chili Piper form does **not** imply a
Smartlead lead — some replies arrive on channels this pipeline can't see. Cf. the `booked-call-pause`
finding that 15 of 22 bookings in one window were genuinely absent from Smartlead.

**Escalation order when a company won't resolve** (do not skip ahead):
1. Smartlead Meeting-Booked set by domain, then by company-name variant.
2. Smartlead by **person name** → confirm on `linkedin_profile` (this is what cracked USAD).
3. HubSpot: company search → `/crm/v4/objects/companies/{id}/associations/contacts` → contact
   `email` → back to Smartlead. The booking form's own fields live in `hs_meeting_body` (HTML —
   strip tags) and carry First/Last Name, Company Name, Email, employee count and the role.
   **`hs_createdate` (when the booking was made) is the field this metric keys on** — confirmed by
   Gaston 2026-09-01. `hs_meeting_start_time` (when the call happens) is *not* used and often falls
   in a different week (jmfbuilders: booked 08-20, held 08-25 → counts in the 08-17 week). Whether
   the call was actually held is irrelevant: no filtering on attendance, no-shows or cancellations.
4. Only then ask Gaston.

## Per-lead pause API — verified 2026-08-20

Discovered while designing the booked-call auto-pause routine. Base `https://server.smartlead.ai/api/v1`, auth `?api_key=`.

- `POST /campaigns/{campaign_id}/leads/{lead_id}/pause` → `{"ok":true,"data":"success"}`. Sets that
  lead's per-campaign status to `PAUSED`. **Pauses one lead in one campaign — not the whole campaign.**
- `POST /campaigns/{campaign_id}/leads/{lead_id}/resume` → same shape, status returns to `INPROGRESS`.
  Verified the full round-trip live (INPROGRESS → PAUSED → INPROGRESS).
- `GET /leads/{lead_id}/campaigns` → `[{id, status, name}, ...]` — **the key endpoint.** Tells you every
  campaign a lead sits in plus each campaign's status, so you never have to crawl 70 active campaigns
  to find where a lead is running. Undocumented; not in the public docs.
- `GET /leads/?email=` → global lookup, returns the lead incl. `id`. **`email` is the ONLY accepted
  query param** — `company_url`, `company_name`, and a `/leads/search` route all 400. There is
  **no company-level lead search in the Smartlead API**; company→leads must be resolved from our own index.
- `GET /campaigns/{id}/leads?offset=&limit=` → `{total_leads, data:[{campaign_lead_map_id, status, lead:{...}}]}`.
  Per-lead `status` values seen: `INPROGRESS`, `PAUSED`, `COMPLETED`, `STOPPED`, `BLOCKED`.
  The nested `lead` carries `company_url` (bare domain) and `custom_fields.company_linkedin_url` —
  the two company keys usable for matching. Campaign sizes are large (12.5k leads in one), so
  full crawls are a batch job, never an inline webhook step.
- Account has ~145 campaigns, **70 ACTIVE** (2026-08-20) — a per-webhook full crawl is not viable.
- Domain density: in a 500-lead sample, **76% of leads shared a company domain with ≥1 sibling**
  (up to 8 leads per domain). Pausing only the booked lead's own email leaves most of the company
  still being emailed — the domain index is essential, not an optimisation.

### `GET /leads/all` — global bulk lead fetch (verified 2026-08-20)

The only way to get leads across the whole account. Undocumented; doesn't follow the other
`/leads/*` route patterns (which all fall through to a `leadId` param validator).

```
GET /leads/all?api_key=…&limit=1000&lastSeenLeadId={cursor}
→ {"ok":true,"data":{leads:[…], lastSeenLeadId, totalCount}}
```

- **Cursor pagination** via `lastSeenLeadId` — **camelCase**. `last_seen_lead_id`, `after`, `cursor`,
  `offset_id` all 400. `offset`/`page`/`page_size` are rejected ("not allowed").
- **`limit` max = 1000** here. ⚠️ **`/campaigns/{id}/leads` caps `limit` at 100** and 400s above that —
  the two endpoints have *different* caps. Exceeding it yields no usable rows, which is easy to
  misread as "no data" if the response isn't checked.
- Throughput ~1.0–1.2s per 1000 leads. **75,000 leads crawled in 79s**; full account (~205k) ≈ 3.5 min
  / ~205 requests. Contends with the 200 req/min account-wide limit — don't run alongside the
  weekly KPI job, and implement retry/resume on the cursor (one transient non-JSON
  response hit at 75k depth during parallel probing).
- **Fields (100% fill across a 6k sample):** `company_url`, `email_domain`, `linkedin_profile`,
  `company_name`. Richer than the per-campaign lead object — also has `seg_type`, `source`,
  `category_ids`, `email_campaign_leads_mappings_count`, `is_unsubscribed`.
  So domain / LinkedIn / email matching is all doable client-side from this one feed.

**Ordering — strictly newest-first by lead `id` desc.** `created_at` tracks it near-perfectly:
16 inversions per 20,000 leads (0.08%), largest backwards jump <1h. Depth→date is ~10k leads
per 10 days: 10k→2026-08-11, 30k→2026-07-15, 50k→2026-06-26, 70k→2026-06-11.

**But do NOT truncate the crawl by depth to save time.** Sequences run for weeks, so old leads are
still sending: in campaign 3570999, leads added **2026-06-30 are 94% still `INPROGRESS`**
(5% COMPLETED, 1% BLOCKED). Active-campaign membership does not decay with depth — 36/36 leads
sampled down to 60k deep were in an ACTIVE campaign. An 8k/10-day cutoff would miss most leads
still receiving email. If bounding the crawl, bound it **by `created_at` vs. the oldest active
campaign's start date** (~90 days), not by lead count.

### Send windows (all active campaigns, verified 2026-08-20)

All **70 ACTIVE** campaigns: `America/New_York`, **09:00–18:00**, Mon–Fri (one outlier 09:00–19:00),
`min_time_btwn_emails: 20`, `max_leads_per_day` 1000 (54 campaigns) / 2000 (14) / 1250 / 400.

Implication for any auto-pause automation: **pausing is only useful before or during 09:00–18:00 ET.**
A run after 18:00 can't prevent anything that day — it only cleans up retroactively. Schedule
pause runs at **09:00** (before the first send) and **13:30** (mid-window), not in the evening.

> [!important] **Two different windows — don't conflate them.**
> The `09:00–18:00` above is when **campaigns send email**, a per-campaign Smartlead setting.
> It is unrelated to the **response team's working hours**, which the reply-time KPI uses to
> compute business-hours-to-reply. Those are **09:00–18:00 ET** as of 2026-09-11 (history:
> 09:00–19:00 → 10:00–19:00 on 2026-08-27 → reverted to 09:00–18:00) and live in
> `OFFICE_OPEN`/`OFFICE_CLOSE` in the `smartlead-weekly-response-kpi` skill.
> The two windows now happen to share the same hours — that is a coincidence, not a link.
> Changing a send window must never be propagated into the KPI window, or vice versa.
> See [[wiki/tasks/done/2026-08-27-fix-reply-time-tracking-window]] and
> [[wiki/tasks/done/2026-09-11-revert-reply-time-window-to-9-18]].

## Fresh uncontacted stock and capacity — verified 2026-09-17

- `GET /campaigns/{id}/leads?status=STARTED&limit=100&offset=0` filters the UI's not-started leads; `START` is rejected. Valid status query values: STARTED, INPROGRESS, COMPLETED, PAUSED, STOPPED. `total_leads` is the filtered count. Page every result; the endpoint orders oldest first.
- Mapping `created_at` is campaign enrollment time, not original lead creation. Join IDs against `/leads/all` and filter its `created_at` to exclude stale leads re-enrolled this week. For a fresh-only query, crawl newest-first through a complete page older than the cutoff, with a one-day margin for minor timestamp inversions.
- Exclude subsequences (`parent_campaign_id` present) from first-contact stock: STARTED there can mean a previously contacted lead waiting for a follow-up. Verified on three fresh leads whose parent mappings already had `last_sent_at`. Exclude unsubscribed leads and deduplicate lead IDs.
- `GET /campaigns/{id}/analytics-by-date?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` returns date-bounded sending metrics.
- Capacity: deduplicate inbox IDs attached to ACTIVE campaigns, join fresh `/email-accounts/` values, require `is_smtp_success`, and sum `max(0, message_per_day - daily_sent_count)`. Never sum repeated inbox limits across campaigns. Configured remaining capacity is an upper bound; follow-ups, schedules, pacing, routing, and shared inboxes affect actual delivery. A 70% first-contact estimate is a planning assumption, not an exact queued-send forecast.

### Why uncontacted leads can remain despite spare daily capacity — verified 2026-10-14

- Snapshot at 15:42 ART: 361 leads added since 2026-10-07 were still `STARTED` in ACTIVE parent
  campaigns; 287 were added that day and 74 were older. The 339 healthy inboxes attached across the
  affected campaigns had 1,725 configured sends remaining (4,530 limit, 2,805 sent), so daily
  capacity was not the binding constraint.
- The affected campaigns almost all shared the same 336 inboxes, `09:00–18:00 America/New_York`
  window, and 20-minute cadence. Smartlead's official low-volume troubleshooting guide says shared
  mailboxes on multiple campaigns with identical schedules create simultaneous trigger conflicts;
  triggers can be skipped even while aggregate daily capacity remains. Stagger campaign start times
  to avoid this: [Smartlead — campaign not sending or sending less volume](https://helpcenter.smartlead.ai/en/articles/228-my-campaign-is-not-sending-emails-or-sending-less-volume).
- Settings were otherwise healthy: all attached inboxes reported SMTP success; campaign new-lead
  limits were 400–2,000/day; 20 affected campaigns had `follow_up_percentage: 30` (70% new-lead
  priority) and the two LATAM campaigns had `20` (80% new). The affected campaigns sent 836 Email 1s
  that day, so this was partial queue starvation, not a stopped sender fleet.
- Public API `campaign_activity_logs` returned `{}` and could not prove the exact skipped trigger for
  each old lead. For lead-level confirmation, use Campaign → Performance → Audit Logs and look for
  `No email sent after processing all accounts and leads` or mailbox/trigger conflicts before changing
  schedules.

### Subsequences are campaigns — how to measure them (verified 2026-09-21)

Subsequences ("SUB | …") come back from `GET /campaigns` like any other campaign, distinguished by
a non-null **`parent_campaign_id`**. So `/campaigns/{sub_id}/analytics`, `/statistics` and `/leads`
all work per subsequence — no separate subsequence endpoint needed.

- Their `scheduler_cron_value` carries the sending window; the weekend follow-ups use
  `days: [0,6]` (Sun+Sat), `09:00–18:00`, tz `America/Argentina/Salta`. `sent_time` is UTC.
- **A subsequence with `campaign_lead_stats.total == 0` shows `status: COMPLETED`** — it completes
  vacuously with nothing enrolled. Never read COMPLETED as "it ran". Check `total` / `sent_count`.
- Seen on the 09-19/20 weekend: 28 `… | Sales/GTM - Weekend Follow Up` subsequences existed, 27 of
  them (created Sun 16:50–17:37 UTC, one per parent campaign) had **zero leads enrolled**. Only
  `3984257` (parent `3896110`, created 09-18) sent — 2 emails, 2 leads, Sun 09:01 Salta.
  If a weekend batch looks empty, the enrollment step upstream is the thing to check, not sending.

### Counting leads by category — `lead_category_id` filters `/campaigns/{id}/leads` (verified 2026-09-21)

`GET /campaigns/{id}/leads?lead_category_id={id}` **is an accepted query param** (alongside
`status`). One request per campaign → an account-wide "who carries category X" count in seconds,
instead of the ~7-minute `/statistics` scan. (`category_id`, `lead_category`, `categoryId` all 400.)

- New category **`182137` Weekend Follow Up** (positive), created 2026-09-18T20:29Z — 7 minutes
  before the first weekend subsequence.
- Snapshot 2026-09-21: **49 leads** carry it, across 15 ACTIVE campaigns, **all with map
  `status: COMPLETED`** (finished the parent sequence). 41 of the 49 are in a campaign that now has
  a Weekend Follow Up sub; 8 are in campaigns with no such sub (incl. 2 sitting inside `SUB |`
  campaigns, which can't have children). 20 of the 28 subs have 0 tagged leads in their parent.
- **Only 2 of the 49 were ever enrolled and emailed.** Likely mechanism (inference, one clean case):
  Smartlead enrols on the **categorization event**, not retroactively — `joana.fonseca@coverflex.com`
  carries `182137` today but sits in the *Info Request/Interested* sub she was enrolled into on
  09-17, and that sub emailed her 09-21. Re-tagging a lead after the fact does not move her.
  ⇒ Creating a subsequence does not sweep up already-tagged leads. To activate a backlog, the leads
  have to be re-triggered (re-categorized or bulk-added to the sub).

## Adding steps to a live campaign — who gets the new emails (verified 2026-09-21)

Case: campaign `3838665` ([EXP008 B] ... 7 Email Seq - B inboxes) went from 3 email steps to 7
mid-flight. Question was whether in-progress / completed leads pick up the new steps 4–7.

- **Lead status is derived, not stored.** `INPROGRESS` vs `COMPLETED` is recomputed from "is there a
  next step left for this lead". Adding steps 4–7 **auto-reactivated every sequence-exhausted lead**:
  627 of the 629 leads that had already received email 3 showed up under
  `GET /campaigns/{id}/leads?status=INPROGRESS` right after the edit (checked one that got email 3 on
  08-31 and had gone silent — back in progress). **No re-import, no resume call needed.**
- **`COMPLETED` in our campaigns means "replied", not "finished the sequence".** With
  `stop_lead_settings: REPLY_TO_AN_EMAIL`, a reply terminates the lead. On 3838665 all 28 `COMPLETED`
  leads had ≥1 `REPLY` in message-history and stopped at email 1, 2 or 3. So the completed bucket is
  exactly the people you must **not** re-enroll. Always check message-history before treating
  `completed` as "exhausted the sequence".
- Caveat: campaigns that end with the manual **"Send Lead to Justcall"** step (e.g. `3717116`) park
  leads at that step, so their `completed` count mixes repliers + manually-advanced leads. 3838665 has
  **no** Justcall step — worth knowing if cold leads from the 7-email variants should route to calling.

### `seq_delay_details.delayInDays` = the wait BEFORE that step

Verified against real send gaps (steps 1/2/3 = 1/2/4 → observed E1→E2 = 2 days, E2→E3 = 4 days).
Step 1's own delay is ignored (email 1 goes out same day the lead is added). So a new step set to
`delayInDays: 1` fires 1 day after the previous email — four steps at 1 day each = four emails on
four consecutive send days.

**Consequence when back-filling steps onto an old campaign:** every reactivated lead is already past
the new step's delay, so the whole backlog goes out at once. On 3838665 that's ~627 email-4s on day
one. Per-inbox load stayed safe (334 inboxes / 4,450-a-day capacity vs ~120/day actual), so the risk
is prospect experience, not deliverability — check the new steps' delays before the next send window.

### Also check: are the new steps' merge variables populated?

Bodies use per-lead custom fields (`{{email_one}}` … `{{email_seven}}`) fed by Clay. A step added for
copy the leads don't carry would send a blank body. Audit before the next send window:
`GET /campaigns/{id}/leads` (page all) → assert every lead's `custom_fields.email_four…seven` is
non-empty. On 3838665 all 1,115 leads already had 4–7 filled (min 182 chars).

### Appending a step to a live campaign — the id trap (verified 2026-09-21)

`POST /campaigns/{id}/sequences` replaces the whole step list. Pass every existing step's **`id`** and
those rows are updated in place; omit them and the rows are deleted and re-created with new ids.
Sent-email history points at the step row (`email_campaign_seq_id`), so a no-id re-save orphans all of
it and can re-send the entire sequence to leads who already received it. Full procedure + the
variant-vs-non-variant step shapes are in `smartlead-campaign-creator/references/api-reference.md` §2.

Done on 3838665 this way: appended step 8 = manual **"Send Lead to Justcall"** (`delay_in_days: 1`,
body `<div>Send to Clay - Add to JustCall</div>`, copied from 3717116), steps 1–7 verified
byte-identical afterwards. Snapshot the GET to disk first — it is the rollback payload.

## A/B inbox rotation audit (verified 2026-09-24)

Inboxes carry tag `A` or `B` (never both) for rest/active rotation; since ~Aug 2026 B is active, A resting.
Finding: **33 `A`+`Premium Inboxes` accounts (franco@ / franco.p@ / hayden@ on talentnearremote, remotenear-talent,
withneartalent, hirewnearremote … domains) are attached to every "B inboxes" campaign** (33/334 accounts each)
and to the B-style mix in `[EXP009] CEOs MultiRole Savings | Challenger - A inboxes` (still getting new leads).
They produced ~80–90% of A-group sends; A-parent subsequences (Reactivation, Candidate sent) the rest.
**Fixed 2026-09-24:** all A accounts removed from the 30 B parent campaigns (see `logs/smartlead-campaign-log.md`).
Removal = `DELETE /campaigns/{id}/email-accounts` body `{"email_account_ids":[…]}` → `{"ok":true,"result":N}`;
does not change any campaign field. No tagged account ever carries both A and B — check tags, not names.
**Rule (Gaston, 2026-09-24):** active-group campaigns get *every* account except the resting group's tag and
`[Don't use] Sales Inbox AEs` (336 accounts while B is active). `POST /campaigns/{id}/email-accounts` adds;
`GET …/email-accounts` can lag ~20 s after a write — re-read before retrying.

How to audit cheaply:
- `GET /email-accounts` → `tags[]` + `daily_sent_count` (today's campaign sends). `campaign_count` is always 0 — useless.
- `GET /campaigns/{id}/email-accounts` per live campaign → which A accounts sit on which campaign.
- `GET /campaigns/{id}/statistics?sent_time_start_date=…&sent_time_end_date=…&limit=500` → sends by day + `sequence_number`
  (seq 1 = new leads entering). Rows have **no sender field**.
- Sender per send: `/leads/?email=` (URL-encode `+`) → `/campaigns/{cid}/leads/{lid}/message-history`, `from` on `type: SENT`.
- Estimating A share as `sends × nA/n` per campaign matched `daily_sent_count` within ~10%.

## HM Reactivation subsequences — send audit (verified 2026-10-02)

21 subs named `SUB | US OJ | HMs Reactivation` (ids 3902454, 3902496, 3902593–3902611), trigger category
177715 `HM Reactivation | New Job Post`. Find them via `GET /campaigns` → `parent_campaign_id`.
As of 2026-10-02: 11 ACTIVE / 10 COMPLETED; ~873 sends lifetime, ~350 in the last 14 days, 3 replies.
COMPLETED ones had 0–1 leads (Smartlead marks an empty/finished sub COMPLETED).

**Stuck-lead finding:** leads sit at `status: STARTED` with empty message-history for weeks when the inbox
that sent them the *parent* sequence is no longer attached to the parent campaign. Subsequences send from
the lead's original sender. 3902609: 79/81 STARTED leads had a detached sender, while all 74 sent leads had
an attached one. 3902608: 13/16. Check: parent `message-history` → last `SENT.from` ∈ `GET /campaigns/{parent}/email-accounts`.
Note: these subs have their OWN inbox list (3902609: 48, parent: 115), contradicting "0 attached → inherits"
above. Check the sender against both lists.
Possible fix (1-lead test running since 2026-10-02 — see logs/smartlead-campaign-log.md): `POST /campaigns/update-lead-email-account`
`{"email_account_id", "email_campaign_id", "email_lead_id", "override_lead_email_account": true}` changes
which inbox sends to a lead. The docs don't say whether it works on a subsequence id or whether the new inbox
must be attached to the parent. The UI "Reassociate" button (Performance → Sender Accounts → Action) only
re-links leads to their *original* mailbox after it's re-added. It doesn't switch them to a different one.

## Experiment → campaign map + how to read the "Email experiments" slide (verified 2026-10-06)

Parent campaigns (ignore `SUB |` children for reach/positives):
- 008A `3838661` (NO HMs Personalized E2-3) · 008B `3838665` (NO HMs 7 Email Seq)
- 009 `3795112` Baseline + `3796733` Challenger (both A inboxes; Baseline stopped adding leads 08-20)
- 011 `3872715` · 012 Eng `3889858` / Sales-GTM `3896110` / Marketing `3895951` (3,600 target **per segment**)

Method: page `/campaigns/{id}/statistics` (500/page). "Reached Email N" = unique `lead_email` with a sent row at
`sequence_number` N. Positive = lead's current `lead_category` has `sentiment_type: positive`; attribute it to the
step of the lead's first `reply_time`. Booked = category `Meeting Booked`. Category is *current*, so counts can drop
when a lead is re-categorized — the 2026-10-06 rerun had fewer positives than the slide on 008A, 009, 012 Eng/Sales.
`/campaigns/{id}/leads` bodies can contain raw control chars — parse with `json.loads(..., strict=False)`.

### Experiment readout notes (2026-10-06 run)
- **Two "EXP008" families exist.** HM-side `[EXP008]` 3717116 Baseline / 3717123 Personalized E2-3 / 3717593
  Personalized 7 emails (A inboxes, since 07-24, ~250–400 leads each) vs No-HM `[EXP008 A/B]` 3838661 / 3838665.
  Readouts use the No-HM pair (map above). Confirm with the team if a readout asks for "EXP-008" without a side.
- **No-HM benchmark = `3804786` (Routing CTA, B).** Its population changed on 2026-09-04 (CEO/founder <50 emp
  routes to baseline, everyone else to Exp 12), so: compare Exp 12 to the **pre-split cohort** (first E1 sent
  08-14 → 09-01: 26 pos / 5,860 = 0.44%, 6 booked) and treat post-split baseline (0.74%) as a different population.
- Every positive lead had exactly one reply row, so "first reply step" attribution is unambiguous.
- EXP009 (3795112/3796733) still has the 33 resting `A`+Premium inboxes and 1 `[Don't use] Sales Inbox AEs` attached.
- Script: pull every parent + non-DRAFTED `SUB |` child via `/statistics`; union categories across parent+subs.
- (2026-10-23) `Not Qualified` (167092) has `sentiment_type: positive` and **is a real positive** (per Gaston: an interested reply
  we decide not to book). Count it as positive. Separately, check whether a spike is several people at one company (008B, week
  of Oct 19: 3 of 6 positives were at us-ignite.org).

### Experiment readout notes (2026-10-13 run)
- `/campaigns/{id}/leads` has `custom_fields.prospect_title` (lead's title) and `open_role_title` (the job). Use
  `prospect_title` for persona checks (e.g. HR leaking into Exp 12); `open_role_title` gives false HR hits.
- Feed-health check: max `created_at` per campaign from `/campaigns/{id}/leads`. A segment whose leads all have an
  Email 1 sent row has an empty queue, so a stalled Clay feed shows up as 0 new E1 the next day.
- EXP-013 = `4114413` (DRAFTED, 0 leads as of 2026-10-13). EXP-011 HM-overlap check against `3804823` alone is
  partial: most 011 CEOs' HMs sit in other HM campaigns.
- "Did every active campaign get fresh leads today?" (2026-10-16): `/campaigns/{id}/leads` returns
  oldest-first, so read the last page (`offset=total-100`) and walk back until a page predates midnight ET;
  join lead IDs to `/leads/all` rows created today to separate fresh leads from re-enrollments. 63 ACTIVE
  parents, ~1 min. "ACTIVE" includes ~35 A-inbox campaigns that are resting by design — split by inbox
  group before calling a campaign starved.
- ⚠️ 2026-10-20: the API slowed to ~56s/call; `curl -m 60` timeouts parsed as empty pages and produced
  false zeros (EXP011 "0 added" vs 22 real). Retry until the response has `data`, and fail loudly
  instead of treating an empty page as "no leads". Feed timing also drifts: the ~11:10 ET batch
  (Routing CTA, EXP012, Asia No HM) landed ~15:00 ET that day, so a midday zero isn't proof of a stall.
- 2026-11-03: the `created_at_gt` + `limit=1` count (64 parents × today + 7-day, ~3 min) is the quick version.
  Pair today with a 7-day count to tell "starved" from "never fed". HubSpot Cold Accounts / current-clients
  campaigns are one-off batches (all of last week's arrived Oct 30), not daily feeds. HireBase `4217467` fills
  daily ~16:xx UTC from the Hirebase routine, so a zero there means checking the routine's run log first.
  The responses can contain raw control characters, so parse with `json.loads(..., strict=False)`.

## Hard follow-up audit — enrollment + five-send verification (verified 2026-10-14)

Full artifact: `exports/smartlead-followup-audit-2026-10-14/summary.md`.

Trigger categories are `181810` Info Requested/Interested - Follow Up, `181675` Meeting Request - Follow up,
and `101821` Candidate sent - Follow Up. The first trigger covers both original Interested and Information
Request replies. Audit every non-drafted parent plus drafted parents that already have a matching child.

Method:
1. Find matching child campaigns through non-null `parent_campaign_id` and normalized name fragments.
2. Page `GET /campaigns/{parent}/leads?lead_category_id={trigger}&limit=100&offset=…` for current tagged leads.
3. Page each matching child's `/leads`; compare lead ids under the same parent. A tag alone does not prove
   enrollment, and creating a child does not backfill already-tagged leads.
4. Use child mapping `created_at` as the precise enrollment time. Smartlead does **not** expose category-assignment
   timestamps, so current missing enrollments are all-time/current-state; use parent message history reply timestamps
   only as a conservative recent lower bound.
5. Page child `/statistics` with `sent_time_start_date` / `sent_time_end_date`; group by `lead_email` and distinct
   `sequence_number` 1–5. Treat replies, bounces, unsubscribes and manual STOPPED/PAUSED states as valid early exits.
6. `STARTED` + zero child history after several send days is the reliable stuck signal. Check original parent sender,
   attachment to both campaigns, SMTP/IMAP state, and the sender's daily cap before blaming child status.

2026-10-14 snapshot (14:52 ET, Oct 1–14 window): 336 campaigns / 119 parents / 164 matching children. Across
815 current tagged campaign-lead records, 763 were in the correct child and **52 were missing** across 20 parents.
Four misses had a parent reply in the window (a conservative recent floor). Of 138 child enrollments in the window,
20 completed all five, 64 exited legitimately, 51 were progressing, and **3 were STARTED with zero sends after
5–9 business days**. Their original senders were attached and healthy, but each was capped at 1 email/day and had
already used the day's capacity — sender contention is the likely cause, not detached mailboxes.

Configuration was also incomplete: 63/164 matching children were DRAFTED; among parents carrying target tags,
three had only a drafted correct child and eight had no correct child. Ten Candidate Sent children still used the
old 3-email day 1/3/5 setup; `3281583` (Coworkers | US OJ HMs - A Inboxes) was still ACTIVE.

## EXP014 Engineering campaigns + clone gotchas (verified 2026-11-06)

- **Baseline `4341415`** `[EXP014] - Baseline | US OJ No HM Priority Segments | Engineering dept | B Inboxes`
- **Challenger1 `4341416`** `[EXP014] - Challenger1 | US OJ No HM Priority Segments | Engineering dept | B Inboxes`
- Cloned 1:1 from EXP012 Sales/GTM `3896110` (identical to EXP012 Eng `3889858`): 4 non-variant steps (`​{{subject_line}}`/`{{email_one}}`, +2 `{{email_two}}`, +4 `{{email_three}}`, +1 manual Justcall), NY Mon–Fri 9–18, 20 min, 1,000/day, plain text, 30% follow-ups, 336 B-group inboxes. Both DRAFTED, 0 leads. Clay: Baseline leads `t_0to30ofXUvuvCmfFXx5` → 4341415, Challenger leads `t_0to32hk9NUSCytAykwK` → 4341416.
- **Launched 2026-11-06: both ACTIVE** (80 / 77 leads at launch). OOO set by Gaston in the UI. **Still to do:** the 4 follow-up subsequences (copy from EXP012 subs 3896111, 3978389, 3979091, 3984257; each has its own tz/days/inboxes).
- Clay's add-lead SUCCESS ≠ added: Smartlead skips leads already in another campaign (`lead_actually_added: false`, `skipped_in_other_campaign_count`). About 70% of the first EXP014 run was skipped that way, so count reach from Smartlead.
- Gotchas found while cloning:
  - EXP012 campaign names contain a **non-breaking space** (U+00A0) after "Segments |"; match by ID.
  - New API campaigns default to `add_unsubscribe_tag: true`, empty `ai_categorisation_options`, OOO handling off. The first two are settable via `POST /settings` (`ai_categorisation_options` = array of category ids). OOO is settable but rejects `autoCategorizeOOO` + `autoReactivateOOO` both true, even though live campaigns have that combo (set in the UI).
  - `create_campaign.py` builds variant-shaped steps and forces Day 1 delay 0, so it's not a 1:1 cloner. Clone from the source GETs instead (build log 2026-11-06, step 24).
  - Saving sequences by API auto-fills `follow_up_subject` on in-thread steps.
  - Full build log: [[logs/2026-11-06-eng-email1-experiment-build]].


## EXP014 Sales/GTM + Marketing campaigns (created 2026-11-06)

| Segment | Arm | ID | Cloned from | Clay leads table |
|---|---|---|---|---|
| Sales/GTM | Baseline | `4344071` | 4341415 | `t_0to3a8tTHdQweSNHbk6` |
| Sales/GTM | Challenger1 | `4344081` | 4341416 | `t_0to3a8tbWEA8JDyvgAg` |
| Marketing | Baseline | `4344087` | 4341415 | `t_0to3a8lkgN4KaHiB8Xh` |
| Marketing | Challenger1 | `4344090` | 4341416 | `t_0to3a8ldXt8NPsGZjA5` |

- Names: `[EXP014] - <Baseline|Challenger1> | US OJ No HM Priority Segments | <Sales/GTM|Marketing> dept | B Inboxes`.
- **Launched 2026-11-06: all 4 ACTIVE** (1 / 1 / 46 / 57 leads at launch; every lead checked against Clay). OOO set in the UI.
- Identical to the Engineering arms except the name: 4 non-variant steps (1/+2/+4 + manual Justcall +1), NY Mon–Fri 9–18, 20 min, 1,000/day, plain text, 30% FU, 10 AI categories, same 336 inboxes. DRAFTED, 0 leads.
- No subsequences yet (Gaston to build). ~78% of Clay adds skipped as already in another campaign at launch; Sales/GTM ~93%.
- **B-inbox pool (336 accounts, 4,448 emails/day)** is shared by 32 parent campaigns using all of it, plus partial overlap with the A-inbox campaigns. The 6 EXP014 campaigns' caps (6 × 1,000) exceed capacity on paper; real volume is bounded by inbox limits and lead supply.
- Clone scripts: build log [[logs/2026-11-06-exp014-sales-marketing-build]] steps 20–21.
