# Booked-Call Pipeline Attribution — Build Handoff

**Written:** 2026-09-01 · **Author:** prior Claude Code session · **For:** the agent that will turn
this into a skill + a Claude routine.

> **Your scope:** build the skill and the routine. This document is the *domain* handoff — what the
> metric is, which endpoints answer it, what the data actually looks like, and every trap that cost
> the first run time. It deliberately does **not** design the skill layout, the script decomposition,
> the CLI surface, the schedule, or the output destination. Those are your calls.

Supporting material in `docs/booked-call-attribution/`:

| Path | What it is |
|---|---|
| `reference-scripts/scan_booked.py` | Step 2 — scans all campaigns for the Meeting Booked tag. Ran clean. |
| `reference-scripts/run8.py` | Step 4 — first-reply measurement + bucketing. Ran clean over 49 leads. |
| `reference-scripts/hs_by_domain.py` | Step 3c — HubSpot contacts-at-a-domain → their bookings. |
| `reference-scripts/hs_resolve.py` | Step 3c — HubSpot company-name search → associated bookings. |
| `reference-scripts/weeks.py` | Shape of the week/company input roster. |
| `reference-scripts/crawl.py` | `/leads/all` full crawl. **The route that did NOT work well** — see §7. |
| `results-2026-07-06_2026-08-30.csv` | The 74-row verified output. Use as your regression fixture. |

These are **throwaway exploration scripts**, not a codebase. They are here so you can read working
request/response handling and copy the throttle, not so you can wrap them. Expect to rewrite.

---

## 1. What the metric answers

> *Of the calls booked this week, how many came from emails we sent this week, versus contacts who
> replied in an earlier week and only booked now?*

The business question is whether new sending drives bookings or whether we are harvesting an ageing
backlog of warm replies. Gaston reports this weekly.

### The rule, exactly

For each company that booked a call in the target week, find the person who booked, then find **the
first time that person ever replied to us**:

- First reply **inside** the target week (Mon 00:00:00 ET → Sun 23:59:59 ET) → **same-week pipeline**
- First reply **before** the target week → **prev-week pipeline** (regardless of how much earlier)

**Only the first reply matters.** Later replies are irrelevant — long ongoing threads are normal and
must not pull a lead into the current week. There is no "two weeks ago" bucket; anything before the
week start is one bucket.

Unit of counting is **one company = one call**. Gaston supplies the company list per week (it comes
out of HubSpot); your job is company → booker → first reply → bucket.

### Boundary specifics that decided real rows

- Week starts **Monday 00:00 America/New_York**. This is load-bearing, not cosmetic. Three of 74
  calls hinged on it: TheMCTTeam first replied Sun 08-16 10:30 (14 h before its week opened),
  jmfbuilders Sat 08-15 01:05, Rex Developments Sat 07-04. A Sunday-start week moves all three.
- Timestamps from the API are UTC. Convert to ET **before** comparing to the boundary. GRADE CAPITAL
  first replied 2026-08-24 13:05 UTC = 09:05 ET — same day either way, but Artic Grey at
  2026-08-25 00:09 UTC is **Aug 24 20:09 ET**, i.e. a different calendar day. Getting this wrong
  flips rows.
- Off-hours first replies are normal (Maxim Group 05:03, AstroZon 02:42, AfterShip 06:23 ET —
  overseas leads). Do not filter or "correct" them.

### Which date puts a call in a week — settled

**The booking date.** A call belongs to the week the meeting was *booked* in, i.e. HubSpot
`hs_createdate` on the MEETING_EVENT. Confirmed by Gaston 2026-09-01.

- **`hs_meeting_start_time` is not used.** jmfbuilders was booked 08-20 and held 08-25 — it counts in
  the 08-17 week, the week it was booked.
- **Whether the call was actually held is irrelevant** to this metric. Do not filter on outcome,
  attendance, no-shows, cancellations, or reschedules. A booking that never happened still counts.
- So the denominator is "meetings booked in week W", and the split is on the booker's first reply.
  Both halves of the metric are reply/booking events; nothing downstream of the booking matters.

---

## 2. Credentials and transport

All in the repo `.env`, all already present:

| Var | Used for |
|---|---|
| `SMARTLEAD_API_KEY` | everything in Smartlead |
| `HUBSPOT_ACCESS_TOKEN` | fallback identity resolution (private-app token, `pat-na1-…`) |

- Smartlead base: `https://server.smartlead.ai/api/v1`, auth as `?api_key=…` query param.
- HubSpot base: `https://api.hubapi.com`, auth as `Authorization: Bearer …`.
- **Smartlead must be called with `curl`.** python-`requests` gets a Cloudflare 403. Every script
  here shells out via `subprocess.run(["curl", "-s", "--max-time", "60", url])`.
- **Smartlead rate limit is 200 req/min account-wide.** Throttle to ~170/min. Copy the deque-based
  `_throttle()` in `scan_booked.py` — it is thread-safe and was used at 8 workers with no 429s.
- `.env` contains a value with an unescaped `$3`. Any shell wrapper must **not** use `set -u` when
  sourcing it, or it aborts. (Pre-existing repo gotcha, documented in the `booked-call-pause` skill.)
- Retry rules that mattered in practice: a response body containing `rate limit` → sleep 15 s and
  retry; a bare JSON **string** response (not an object) is a transient API error → sleep 3 s and
  retry; unparseable JSON → backoff `3 × attempt`. All three were observed live.

---

## 3. Smartlead endpoints — verified shapes

Everything below was confirmed live on 2026-09-01. There is a maintained copy of the API facts in
`Near Work Partner/wiki/tools/smartlead.md` (§ "Booked-call attribution"); keep the two in sync.

### `GET /leads/fetch-categories`
Returns the tag vocabulary. **`Meeting Booked` is `id: 101822`.** Full list as of 2026-09-01:

```
1 Interested (positive)              9 Sender Originated Bounce
2 Meeting Request (positive)     31756 Asked to Circle Back Later
3 Not Interested (negative)     101821 Candidate sent - Follow Up (positive)
4 Do Not Contact (negative)     101822 Meeting Booked (positive)   <-- the one we filter on
5 Information Request (positive) 127523 CV Sent - Opp Lost
6 Out Of Office                 133363 Send to Cold Call (Lead went cold) (positive)
7 Wrong Person                  167092 Not Qualified (negative)
8 Uncategorizable by Ai
```

Fetch it live rather than hardcoding `101822` — the account adds custom categories over time.

### `GET /campaigns/`
Returns an array of campaigns. Account had **153 campaigns, 139 non-`DRAFTED`** on 2026-09-01.
Skip `DRAFTED` — they never sent, so they hold no replies.

### `GET /campaigns/{id}/statistics?offset=&limit=1000`
The **discovery** endpoint. Per-email rows carrying `lead_email`, `lead_name`, `lead_category`
(a category **name** string, e.g. `"Meeting Booked"`), `reply_time`, `sent_time`.

- Paginate on `offset`; `total_stats` may come back as a **string**, so cast to `int`.
- `reply_time` here is *a* reply, not necessarily the first — do not use it for the metric. It is
  fine as a rough sort key during discovery.
- Filtering these rows to `lead_category == "Meeting Booked"` across all 139 campaigns produced
  **481 rows / 318 unique booked leads** account-wide. That whole scan took **~7 minutes** at 8
  workers. This is the dominant cost of a run, and it is **flat** — it costs the same whether you
  are attributing 5 companies or 50.

### `GET /leads/?email={email}`
Single-lead lookup. `email` is the **only** accepted query param — `company_url`, `company_name`,
`domain`, and a `/leads/search` route all return 400. Returns `{}` (empty object, HTTP 200) when the
address is unknown, which is your "not in Smartlead" signal.

Returns, among other fields:

```json
{
  "id": "4408016970",
  "first_name": "Egan", "last_name": "Frawley",
  "email": "egan@sanabenefits.com",
  "company_name": "Sana",                      // often a SHORTENED brand, see §6
  "company_url": "sanabenefits.com",
  "linkedin_profile": "https://www.linkedin.com/in/eganfrawley",
  "custom_fields": { "company_linkedin_url": "...", "job_url": "...",
                     "normalized_company_name": "Sana", "prospect_title": "..." },
  "lead_campaign_data": [
    { "campaign_id": 3804786, "campaign_name": "...",
      "lead_category_id": 101822,              // <-- the tag, PER CAMPAIGN
      "last_reply_at": "2026-08-26T16:36:53+00:00",
      "last_sent_at": "...", "campaign_lead_map_id": 3577569301 }
  ]
}
```

Two things worth internalising:

1. **`lead_campaign_data` gives you the category in one request** — you do not need a campaign
   statistics page to read a known lead's tag. The category lives on the **campaign↔lead mapping,
   not on the lead**: the same person is `101822` in one campaign and `null` in another.
2. **`last_reply_at` is the LAST reply, not the first.** It is the single most tempting wrong field
   in this whole job. Using it would have mis-bucketed Hype Proxies (last reply 08-27, first reply
   08-21) and USAD (last 08-26, first 07-15).

### `GET /campaigns/{campaign_id}/leads/{lead_id}/message-history`
The **measurement** endpoint. Returns `{"history": [...]}`; each message has `type`
(`SENT` / `REPLY`), `time`, `email_seq_number`.

```
SENT   | 2026-08-25T14:05:49.066Z   | seq 1
REPLY  | 2026-08-25T14:09:59.000Z   | seq 1      <-- first reply
SENT   | 2026-08-25T14:38:30.57+00:00 | seq None  <-- manual Master-Inbox reply
```

- **First reply = earliest `type: REPLY`.** That is the metric's input.
- Manual replies sent from the Master Inbox appear as `type: SENT` with `email_seq_number: null`.
- **Timestamp formats are inconsistent within one response** — `…Z`, `…+00:00`, with and without
  microseconds. Parse defensively; every script here tries `%Y-%m-%dT%H:%M:%S.%f%z` then
  `%Y-%m-%dT%H:%M:%S%z` after replacing `Z` with `+0000`.
- **Iterate every campaign in `lead_campaign_data` and take the global minimum.** Leads are routinely
  in 2 campaigns; 20 of 49 in the last batch were. A lead's first reply can sit in a campaign that
  does *not* hold the Meeting Booked tag. In the data measured so far the global-min and
  booked-campaign-only readings never produced a different bucket, but they are not guaranteed to
  agree and the rule as Gaston stated it ("when they FIRST replied") is unambiguously global.
- **The search must be unbounded.** USAD first replied 2026-07-15 and booked in the 08-24 week — a
  6-week gap. Any "look back 2 weeks" optimisation silently mis-buckets long nurtures as same-week.

### `GET /leads/all?limit=1000&lastSeenLeadId={cursor}`
Global bulk lead feed. `{"ok":true,"data":{leads:[…], lastSeenLeadId, totalCount}}`. Cursor
pagination, **camelCase** `lastSeenLeadId` (snake_case 400s). `limit` max 1000 here — note
`/campaigns/{id}/leads` caps at 100, a different limit on a similar-looking route.

Crawled **214,668 leads in 332 s / ~215 requests**. `company_url`, `email_domain`,
`linkedin_profile`, `company_name` are ~100% populated. **See §7 — this is not the route to build on.**

---

## 4. HubSpot endpoints — the identity fallback

Only needed when Smartlead can't resolve a company, or when it resolves to *more than one* candidate.

### `POST /crm/v3/objects/companies/search`
```json
{"filterGroups":[{"filters":[{"propertyName":"name","operator":"CONTAINS_TOKEN","value":"jmf*"}]}],
 "properties":["name","domain","website"],"limit":20}
```
`CONTAINS_TOKEN` with a trailing `*` is what worked. Caveat: token search on a short/common word is
useless — `"research"` returned 40 unrelated companies and RISE Research was the *last* row.
Prefer searching by domain when you have one.

### `POST /crm/v3/objects/contacts/search`
Find everyone at a domain — this is the higher-yield query:
```json
{"filterGroups":[{"filters":[{"propertyName":"email","operator":"CONTAINS_TOKEN","value":"*@krece.app"}]}],
 "properties":["email","firstname","lastname","company","createdate"],"limit":20}
```

### `GET /crm/v4/objects/{companies|contacts}/{id}/associations/meetings`
Returns `{results:[{toObjectId, associationTypes}]}`. **Go via the contact, not the company** —
Krece's company record had *zero* associated meetings while both of its contacts had one each.

### `GET /crm/v3/objects/meetings/{id}?properties=hs_meeting_body,hs_createdate,hs_meeting_start_time,hs_activity_type`
The booking record. Critical parsing notes:

- **Filter on `hs_activity_type` being present.** Fathom also writes MEETING_EVENTs ("Fathom summary
  for …") for calls that already happened; those have no `hs_activity_type`. Without this filter you
  get phantom bookings.
- **The booker's email is not a property.** It is inside `hs_meeting_body`, which is HTML. Unescape
  entities, strip tags, then regex the Chili Piper form fields:
  ```
  First Name: Mauricio
  Last Name: Giron
  Company Name: jmfbuilders
  Email: info@jmfbuilders.com
  Number of Employees: 1-10
  How did you hear about Near?: Email
  Roles you're hiring for: Administrative Assistant with advanced English skills
  ```
- **`hs_createdate` = when they booked. This is the field the metric keys on** (see §1) and the
  tiebreak for multi-booking companies. `hs_meeting_start_time` = when the call happens; it lands in
  a different week frequently and is **not** used here.
- `hs_object_source_detail_1` is `"Chili Piper"` on roughly half the records and `null` on the rest —
  **do not filter on it.**
- `"How did you hear about Near?: Email"` does **not** imply a Smartlead lead exists. jmfbuilders
  answered Email and has no Smartlead record at all.

---

## 5. The pipeline, step by step

This is what actually ran, in order.

### Step 1 — Inputs
A list of `(week_start, week_end, [company names])`. Gaston pastes company names as they appear in
**HubSpot**, which do not always match Smartlead's `company_name`. Names arrive dirty:
`"Enabledoc LLC;Enabledoc"`, `"SERVPRO;SERVPRO"`, `"WebForce;The Phone Sales Team"` — semicolon-joined
duplicates/aliases. Split on `;` and treat each part as an alias of one company.

### Step 2 — Discover who booked (the expensive, flat-cost step)
Scan all non-`DRAFTED` campaigns' `/statistics`, keep rows where `lead_category == "Meeting Booked"`,
dedupe by `lead_email` keeping the earliest `reply_time`. Yields ~318 leads / ~7 min.

Result is a small in-memory set you then match company names against. **Do this once per run and
share it across every week and company being attributed.**

### Step 3 — Resolve company → booker (the hard part)
Escalation ladder. **Do not skip ahead** — Gaston was explicit that Smartlead comes first and HubSpot
is only a fallback.

**3a. Match against the booked set by domain.** Normalise and compare the company's domain against
the lead's email domain. Resolved 45 of 49 companies in the last batch, instantly and for free.

**3b. Match by company name, then by person name.** For a company whose domain you don't know, match
`company_name` variants. If that fails, match the **booker's name** against `lead_name` in the booked
set and confirm via `linkedin_profile`. This is what cracked USAD.

**3c. HubSpot.** Company search (or contact-search by domain) → contact → associated meetings →
parse `hs_meeting_body` for the real booker name/email → take that identity back to Smartlead
(`/leads/?email=`, then person-name matching).

**3d. Ask Gaston.** He has inbox access and will simply supply the reply date. He did this for
jmfbuilders (Sat 08-15 01:05) and confirmed Cactus Audio as an older lead. Two of 74 rows came from
him — budget for a small number of unresolvables per run rather than treating them as failures.

### Step 4 — Measure and bucket
For each resolved `(company, booker email, week_start)`: `/leads/?email=` → for every campaign in
`lead_campaign_data` pull `message-history` → global earliest `REPLY` → convert to ET → compare to
`week_start` 00:00 ET → `SAME` or `PREV`. Cost is ~3 requests per lead; 49 leads ran in well under a
minute at 6 workers.

`run8.py` also records `booked_tag` (whether any campaign still shows `101822`) as a self-check. All
49 passed. A lead that resolves but has *lost* the tag is a signal your identity match is wrong.

### Step 5 — Aggregate
Per week: count, same, prev, same%. Pool across weeks for the headline.

---

## 6. Traps — every one of these cost real time

**Do not strip the last dot-segment as a "TLD".** A domain normaliser that did this turned
`grade.capital` into the stem `grade` and silently lost the GRADE CAPITAL booking. New gTLDs are
common in this book: `.capital`, `.app`, `.io`, `.ai`, `.shop`, `.health`, `.sh`, `.co`, `.us`, `.ca`.
Match on the full domain.

**Loose substring matching on short names is actively dangerous.** Measured false-positive counts:
`usad` → 25 leads (USADA the anti-doping agency, USA Diving, `adusasc.com`, `atticusadvantage.com`),
`cactus` → 23 (Cactus Life Sciences / Materials / Wellhead / Inc), `sana` → 93, `purpose` → 61,
`rise` → 10 unrelated HubSpot companies, `rex` → matched `cognitrex.com`. Require the key to match a
**registrable domain or a full company name**, and always surface the candidate list for review
before spending per-lead requests.

**`company_name` is often a shortened brand, and sometimes just wrong.**
Shortened: `Sana` for Sana Benefits, `Grade` for GRADE CAPITAL, `HypeProxies` for Hype Proxies,
`Rex` for Rex Developments, `MCT` for TheMCTTeam, `Clad` for Panelized Cladding Systems.
Simply wrong (bad enrichment): City of Yellowknife (`bsleem@yellowknife.ca`) is filed as
**"Western Arctic Moving"**; Mubite (`gertil@mubite.com`) is filed as **"Pionex"**. The domain was
right in both cases. Trust the domain over `company_name`.

**The booking email is often not the Smartlead email.** Four confirmed cases:

| Company | Books as (HubSpot) | Is in Smartlead as | Tied together by |
|---|---|---|---|
| USAD | `Yasha@usadistributions.com` | `yasha@mercatodibellina.com` | name + LinkedIn `/in/yashasack/` |
| RISE Research | `yash@riseresearch.com` | `yash@riseglobaleducation.com` | name (Yash Mundada) |
| Rex Developments | `design@rexarch.com` | `mahmad@rexmediausa.com` | first name + `company_url: rexarch.com` |
| Blackout Coffee Co. | `john@howloo.com` | same | `company_url: blackoutcoffee.com` + job post |

Founders with several ventures book under whichever entity is hiring. HubSpot and Smartlead also
disagree on surnames (Rex: *Bakali* vs *Ahmad*). **Never conclude "not in Smartlead" from a domain
miss alone** — check the person.

**Multiple booked leads at one company.** 4 of 49 companies returned two Meeting-Booked leads:
Krece, Voicing AI, RISE Research, Rex Developments. Two are genuine colleagues, two were false
positives from loose keys. **Krece booked twice for real, five days apart, landing in two different
weeks** (Samuel Gedaly 08-05, Jonathan Bentata 08-10). Resolve with HubSpot `hs_createdate`.
This is ~8% of companies — handle it as a normal path, not an exception.

**Category tags are live and mutate.** Querying an old window later gives different counts as leads
get re-categorized (`Meeting Booked` → `CV Sent - Opp Lost`, etc.). All 49 leads from 8 weeks back
still carried the tag on 2026-09-01, so decay is slow — but for a historical rerun, discovery by tag
is not guaranteed reproducible. Freeze each week's result once computed; do not silently recompute
history.

**One open discrepancy to hand to Gaston, not resolve yourself.** Samuel Gedaly's Krece booking
(created 08-05) falls in the Aug 3–9 week, which Gaston supplied as 5 companies *without* Krece. That
week may actually be 6 calls. Flagged to him; unanswered as of this writing.

---

## 7. The route that did not work — read before optimising

The first attempt resolved companies by crawling `/leads/all` (214,668 leads, 332 s) and matching
company names/domains client-side. `reference-scripts/crawl.py` is that attempt.

**It failed on the cases that mattered.** `Purpose` matched six unrelated companies in the account
(`purpose.app`, `teampurpose.com`, `purpose-unlimited.com`, `purposebrands.com`,
`realestateonpurpose.com`, `purposecapitalgroup.com`) with nothing to choose between them.
`grade.capital` was lost to the TLD bug. Cactus Audio and USAD produced 23 and 25 false positives
respectively and zero true ones.

**The statistics scan (Step 2) fixed all of it** — because the set of people who *actually booked* is
only ~318 leads, so ambiguity mostly evaporates: there is exactly one booked lead at `purpose.app`.

Keep `/leads/all` in the toolbox for one narrow job: finding a booker's **colleagues** at a known
company (which the `booked-call-pause` skill needs, and which the booked set can't give you). Do not
make it the primary resolution path.

Also note the prior art at `scripts/smartlead_company_lead_extract.mjs` — a Node script that resolves
companies→leads by crawling `/campaigns/{id}/leads` at `limit=100`. That is the slowest available
route. Don't build on it either.

---

## 8. Cost profile — for whoever sizes the routine

| Step | Requests | Wall clock |
|---|---|---|
| 2 — category scan, all 139 campaigns | ~1,400 | **~7 min** (8 workers, 170/min throttle) |
| 3 — HubSpot fallback, per unresolved company | ~5–15 | seconds |
| 4 — measurement, per lead | ~3 | seconds |
| **Total, 13 companies (1 week)** | ~1,450 | **~8 min** |
| **Total, 49 companies (6 weeks)** | ~1,600 | **~9 min** |

The scan dominates and is flat in the number of companies. A backfill of many weeks costs
approximately the same as one week — worth knowing when deciding cadence and whether to batch.

Smartlead's 200/min ceiling is **account-wide and shared** with the two `booked-call-pause` routines
(09:03 and 13:27 ET, ~207 requests each) and the reply-time KPI routines (~08:00 ET). Don't collide.

---

## 9. Regression fixture — verified output

`docs/booked-call-attribution/results-2026-07-06_2026-08-30.csv`, 74 rows. Pooled result:
**42 same-week (57%) / 32 prev-week (43%)**.

| Week (Mon–Sun) | Calls | Same | Prev | Same % |
|---|---|---|---|---|
| 2026-07-06 → 07-12 | 10 | 5 | 5 | 50% |
| 2026-07-13 → 07-19 | 5 | 2 | 3 | 40% |
| 2026-07-20 → 07-26 | 12 | 8 | 4 | 67% |
| 2026-07-27 → 08-02 | 10 | 4 | 6 | 40% |
| 2026-08-03 → 08-09 | 5 | 4 | 1 | 80% |
| 2026-08-10 → 08-16 | 7 | 6 | 1 | 86% |
| 2026-08-17 → 08-23 | 12 | 6 | 6 | 50% |
| 2026-08-24 → 08-30 | 13 | 7 | 6 | 54% |
| **Total** | **74** | **42** | **32** | **57%** |

Good single-lead assertions to pin in a test:

| Lead | First reply (ET) | Why it's a useful test |
|---|---|---|
| `egan@sanabenefits.com` | Tue 2026-08-25 10:09 | plain happy path; Gaston verified this one by hand |
| `yasha@mercatodibellina.com` | Wed 2026-07-15 16:27 | 6-week nurture + email/company mismatch |
| `gunnar@hypeproxies.io` | Fri 2026-08-21 11:19 | 2 campaigns; `last_reply_at` (08-27) would be wrong |
| `harshita@grade.capital` | Mon 2026-08-24 09:05 | new-gTLD domain; near the week boundary |
| `anthony.spallone@arcticgrey.com` | Mon 2026-08-24 20:09 | UTC date ≠ ET date |
| `ngideon@themctteam.com` | Sun 2026-08-16 10:30 | weekend, 14 h before week open |

Two rows in the CSV are **not** API-derived and must not be asserted against Smartlead: jmfbuilders
(no Smartlead record; date from Gaston) and Cactus Audio (no record; bucket from Gaston).

---

## 10. Reporting guidance to carry into the skill

**Weekly volume is 5–13 calls, so the weekly percentage is mostly noise.** The two best-looking weeks
(80%, 86%) are the two smallest (5 and 7 calls) — one booking moves them 14–20 points. Any output
should lead with the pooled multi-week figure and present the weekly series as directional. In the
report built for Gaston, bar length encodes call volume specifically so a thin bar cannot be misread
as a strong week.

**A hypothesis that was tested and refuted** — don't let it reappear. After the first week it looked
like every same-week booking first replied Mon or Tue. Across all 8 weeks that is false: same-week
bookings first replied on every weekday including Friday (Aventiqo 08-14, WebForce 07-24, Lindsey
Self Storage 07-24) and Saturday (Safeguard 07-11).

**Always state the Mon-00:00-ET boundary on any chart**, given three of 74 rows turn on it.

Existing artifact of the 8-week run (update rather than republish if you keep it):
`https://claude.ai/code/artifact/b9b59e19-3fa2-4206-a5ea-3969c4837f50`

---

## 11. Related existing work — read these before designing

| Thing | Why it's relevant |
|---|---|
| `Near Work Partner/wiki/tools/smartlead.md` | Maintained API reference. Its "Booked-call attribution" section is the canonical version of §3–§6 here. Update it, don't fork it. |
| `.claude/skills/booked-call-pause/` | Same two APIs, same account. Source for: the throttle, `norm_domain()` (correct, keeps the full domain), `JUNK_DOMAINS`, `same_company()` cross-company guard, and the HubSpot booking-feed quirks. Its `lead_index.py` is the `/leads/all` crawler done properly. |
| `.claude/skills/smartlead-weekly-response-kpi/` | Closest structural precedent: a weekly Smartlead metric that posts to Slack and appends a column to a Google Sheet, already running as two routines. Its `run_weekly_kpi.py` has the campaign-statistics scan and the Mon–Sun ET period resolver you will want. |
| `scripts/smartlead_company_lead_extract.mjs` | Prior attempt at company→lead resolution. Slowest route; noted so you don't rediscover it. |

Two conventions from those skills that apply here: cloud routine runs get a **fresh checkout**, so
everything the run needs must be committed and nothing may depend on local state; and the routine's
environment needs `server.smartlead.ai` plus `api.hubapi.com` on its network allowlist (a missing
host fails as a blocked-domain error, which reads nothing like an auth error).
