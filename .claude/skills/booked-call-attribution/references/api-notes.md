# Verified endpoint shapes

Confirmed live 2026-09-01. The maintained copy of the Smartlead facts lives in
`Near Work Partner/wiki/tools/smartlead.md` (§ "Booked-call attribution") — update
that, don't fork it.

## Transport

| | Smartlead | HubSpot |
|---|---|---|
| Base | `https://server.smartlead.ai/api/v1` | `https://api.hubapi.com` |
| Auth | `?api_key=…` query param | `Authorization: Bearer pat-na1-…` |
| Client | **curl only** — python-`requests` gets a Cloudflare 403 | curl (consistency) |
| Limit | **200 req/min, account-wide** — throttle to ~170 | generous; batch anyway |

Smartlead's three retry cases, all observed live and all handled in `common.py`:
a body containing `rate limit` → sleep 15 s; a bare JSON **string** response (not an
object) → transient error, sleep 3 s; unparseable JSON → backoff `3 × attempt`.

## HubSpot

### `POST /crm/v3/objects/meetings/search`
Bookings are `MEETING_EVENT` objects. Filter `hs_activity_type HAS_PROPERTY` — it is
what separates the three populations sharing this object type:

| Population | Signature | Count in the 08-24 week |
|---|---|---|
| Chili Piper bookings | has `hs_activity_type` | 65 ← the real bookings |
| Fathom summaries | titled `Fathom summary for …`, no activity type | 47 |
| calendar copies, kickoffs, candidate interviews, re-engagement syncs | no activity type | 42 |

Without the filter that week goes 65 → 154 rows and Purpose, Zaelab, Nerife and
HypeProxies are each counted twice, because the calendar copy is a separate object.

`hs_object_source_detail_1` is `"Chili Piper"` on roughly half the records and `null`
on the rest — **never filter on it.** Paginate on `paging.next.after`; limit 100.
Volume is ~150 meetings/week of which ~65 are bookings.

### `POST /crm/v4/associations/meetings/contacts/batch/read`
### `POST /crm/v3/objects/contacts/batch/read`
Both take 100 ids per call. These two turn ~130 requests per week into 2. Every
booking needs the hop because the **source lives on the contact, not the meeting.**

### `meeting_source__standardized_` (contact property)
The Email Outreach filter. Live values seen: `Email Outreach`, `LinkedIn Outreach`,
`Google Search`, `Google Ad`, `LLM`, `Friend`, `Girdley`, `Atlas`, `Deel` — a wider
vocabulary than the property's declared enum options, so **match the target exactly**
rather than enumerating the rest. The same property exists on deals.

Do **not** substitute the meeting body's `How did you hear about Near?`. It is free
text the prospect typed; real Email Outreach bookings answered it with "They
outreached", "Cold reach out!", "cold email from Franco Pereyra", and "Email".

### `hs_meeting_body`
HTML. Unescape entities, strip tags, then read the Chili Piper form fields
(`First Name`, `Last Name`, `Company Name`, `Email`, `Number of Employees`,
`How did you hear about Near?`, `Roles you're hiring for`). Used only as a fallback —
the associated contact is more reliable.

### `GET /crm/v4/objects/{contacts|companies}/{id}/associations/meetings`
Go via the **contact, not the company** — Krece's company record had zero associated
meetings while both of its contacts had one each.

## Smartlead

### `GET /leads/fetch-categories`
`Meeting Booked` was `id 101822` on 2026-09-01. **Fetch it live** — the account adds
custom categories, and a hardcoded id fails silently as "nobody booked".

### `GET /campaigns/`
153 campaigns, **139 non-`DRAFTED`**. Skip `DRAFTED` — they never sent.

### `GET /campaigns/{id}/statistics?offset=&limit=1000`
The discovery endpoint. Rows carry `lead_email`, `lead_name`, `lead_category` (a
category **name** string), `reply_time`, `sent_time`. `total_stats` may come back as
a **string** — cast to int when paging. Filtering all 139 campaigns to
`lead_category == "Meeting Booked"` gives ~481 rows / ~318 unique leads in ~7 min at
8 workers. `reply_time` here is *a* reply, not the first — fine as a sort key, never
as the metric.

### `GET /leads/?email={email}`
`email` is the **only** accepted param — `company_url`, `company_name`, `domain` and
a `/leads/search` route all 400. Returns `{}` with HTTP 200 for an unknown address,
which is the "not in Smartlead" signal.

Returns `company_name`, `company_url`, `linkedin_profile`, `custom_fields`, and:

```json
"lead_campaign_data": [
  {"campaign_id": 3804786, "lead_category_id": 101822,
   "last_reply_at": "2026-08-26T16:36:53+00:00", "campaign_lead_map_id": 3577569301}
]
```

Two things to internalise: the category lives on the **campaign↔lead mapping**, so
the same person is `101822` in one campaign and `null` in another — and
**`last_reply_at` is the LAST reply**, the most tempting wrong field in this job.

### `GET /campaigns/{campaign_id}/leads/{lead_id}/message-history`
The measurement endpoint. `{"history": [...]}`, each message with `type`
(`SENT`/`REPLY`), `time`, `email_seq_number`. First reply = earliest `type: REPLY`.
Manual Master-Inbox replies appear as `type: SENT` with a null `email_seq_number`.

**Timestamp formats are inconsistent within one response** — `…Z`, `…+00:00`, with
and without microseconds. `common.parse_ts` tries four formats and returns `None`
rather than raising, so one odd row cannot abort a run.

### `GET /leads/all?limit=1000&lastSeenLeadId={cursor}`
214,668 leads in ~215 requests / 332 s. Cursor is **camelCase** (`lastSeenLeadId`;
snake_case 400s). `limit` maxes at 1000 here — note `/campaigns/{id}/leads` caps at
100, a different limit on a similar-looking route.

**Not the route to build on for this skill.** Resolving companies by crawling it
failed on exactly the cases that mattered: `Purpose` matched six unrelated companies
with nothing to choose between them, `cactus` 23, `usad` 25. The booked-set scan
fixed all of it because ~318 leads is a far less ambiguous population. Keep
`/leads/all` for finding a booker's *colleagues* (what `booked-call-pause` needs).

## Cost profile

| Step | Requests | Wall clock |
|---|---|---|
| HubSpot week fetch + review sweep | ~8 | ~4 s |
| direct email probe | 1 per booking | ~10 s |
| booked-lead scan (139 campaigns) | ~1,400 | **~7 min** |
| measurement | ~3 per lead | seconds |
| **Typical week (12 bookings)** | **~1,450** | **~8 min** |

The scan dominates and is **flat** in the number of bookings — a multi-week backfill
costs about the same as one week.
