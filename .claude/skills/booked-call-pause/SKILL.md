---
name: booked-call-pause
description: >
  Pauses Smartlead email sequences for every lead at a company that just booked a call in
  HubSpot, so we stop cold-emailing an account that already converted. Runs twice a day
  (09:00 + 13:30 ET) as a Claude routine, batching all bookings in the window into a single
  Smartlead lead crawl. Use this whenever asked about auto-pausing sequences on booked calls,
  stopping outreach to companies that booked, the HubSpot→Smartlead pause automation, or
  "why is a lead still getting emails after they booked". Also use it to pause a single
  company ad-hoc by domain.
---

# Booked-Call Auto-Pause

When a company books a call, every lead at that company should stop receiving cold email —
not just the person who booked. Sequences run for weeks, and most leads have colleagues in
the same campaign, so a booked account keeps getting emailed unless we intervene.

## Why it's built this way

Three findings from the Smartlead API drove the design (all verified live — see
`[[wiki/tools/smartlead]]` for the raw endpoint notes):

1. **There is no company-level lead search.** `/leads/?email=` accepts only an exact email,
   and `/leads/all` rejects every filter param (`email_domain`, `company_url`, `domain`,
   `company_name`, `search`, `query` → HTTP 400). So company→leads must be resolved
   client-side, over the full lead list.
2. **`GET /leads/{id}/campaigns`** returns every campaign a lead is in, with status. Without
   it we'd have to scan all 70 active campaigns (12.5k leads each) to find where a lead runs.
3. **`GET /leads/all`** returns every lead (~205k) at 1000/page, ~207 requests, ~5 minutes.
   `company_url`, `email_domain`, `linkedin_profile` and `company_name` are 100% populated,
   so all matching is doable from this one feed.

**Stateless by design.** Cloud routine runs get a **fresh checkout** — nothing persists between
runs except what's committed. An incremental on-disk index would therefore be rebuilt from
scratch every run anyway, and would mean writing 60MB of lead PII to disk. So the index is
built **in memory each run and discarded**. At two runs a day that's ~414 requests total —
a couple of minutes of a 200/min budget — with no staleness and nothing to persist.

Never commit the index: `*.sqlite3` is gitignored. (An earlier build wrote a 60MB SQLite file;
it was deleted and the approach dropped.)

## Schedule — and why not the evening

All 70 active campaigns send **09:00–18:00 ET, Mon–Fri**. A pause run after 18:00 can't
prevent anything that day, it only cleans up retroactively. So:

- **09:00 ET** — before the first send of the day; catches the prior afternoon + overnight.
- **13:30 ET** — mid-window; catches the morning's bookings with half the window left.

## Pipeline

```
1. fetch_bookings.py   HubSpot: meetings created since last run   (1 request)
2. lead_index.py       ONE in-memory crawl for the whole batch    (~207 requests, ~5 min)
3. pause_booked.py     per booking: domain → LinkedIn → email lookup
                       per matched lead: /leads/{id}/campaigns → pause if ACTIVE
4.                     one Slack summary for the whole run
```

The crawl is shared across every booking in the window — 10 bookings cost the same crawl as 1.
If the crawl ends early (transient API failure), `--live` **aborts**: a partial index would
silently miss leads that should have been paused.

## Usage

`run.sh` chains all four steps and is what a routine should call:

```bash
./scripts/run.sh              # DRY RUN, last 12h
./scripts/run.sh --live       # actually pause
./scripts/run.sh --hours 24   # wider window, e.g. after a missed run
```

It exits early (no Smartlead crawl) when HubSpot returns no bookings for the window.

Individual steps:

```bash
# normal run — DRY RUN by default, prints what it would pause
python3 scripts/fetch_bookings.py --hours 12 --out /tmp/bookings.json
python3 scripts/pause_booked.py --bookings /tmp/bookings.json

# go live
python3 scripts/pause_booked.py --bookings /tmp/bookings.json --live

# ad-hoc single company
python3 scripts/pause_booked.py --domain acme.com --live

# sanity-check the crawl / a single lookup
python3 scripts/lead_index.py --stats
python3 scripts/lead_index.py --lookup acme.com
```

`--max-pauses` (default 250) caps how many leads one run may pause, so a matching bug can't
stop hundreds of sequences before anyone notices.

**Dry run is the default.** `--live` is required to actually pause anything.

## Matching — the fallback chain

`domain → company LinkedIn → exact email`, stopping at the first key that hits.

Domain is primary on purpose: booking emails are very often generic mailboxes
(`info@`, `hello@`) that match no Smartlead lead by address, but their domain matches fine.

### Two data-quality guards (both earned from real bugs)

**Junk domains.** `company_url` is enrichment output and sometimes holds an aggregator URL.
In this account `linkedin.com` carried **1,870 leads across 1,532 unrelated email domains** —
keying on it would have paused an entire unrelated book of business. Real companies top out
around 60 leads, so `JUNK_DOMAINS` (LinkedIn, Facebook, job boards, site builders, free
mailboxes) is never usable as a company key.

**Cross-company coherence.** ~15% of leads have an email domain that differs from their
indexed `company_url`. Two very different causes:

- *benign* — brand variant (`getforwardly.com` / `liveforwardly.com`)
- *harmful* — the lead actually works elsewhere (`patrick.mcgee@jpmorgan.com` filed under
  `huntington.com`)

`same_company()` accepts exact matches, shared brand stems, long common substrings, and free
mailboxes; it rejects clear cross-company cases. Found because a Huntington test run matched
JPMorgan and Veritex leads.

## Reversing a mistake

Pausing is fully reversible — same path with `resume`:

```bash
curl -s -X POST "https://server.smartlead.ai/api/v1/campaigns/{cid}/leads/{lid}/resume?api_key=$SMARTLEAD_API_KEY"
```

The run's `--json-out` file records every `(campaign_id, lead_id)` paused, so a bad run can be
undone exactly.

## Secrets

| Var | Purpose |
|---|---|
| `SMARTLEAD_API_KEY` | already in repo `.env` |
| `HUBSPOT_ACCESS_TOKEN` | already in repo `.env` — private-app token (`pat-na1-…`). **Verified 2026-08-20:** meetings/contacts/companies reads, the booking search, and v4 associations all return 200. (`HUBSPOT_PRIVATE_APP_TOKEN` also accepted as a fallback name.) |
| `SLACK_BOT_TOKEN` | already in `.env` — bot `email_kpi_bot`. Has `chat:write` but **not** `channels:read`, so it cannot list channels; test by posting. |
| `PAUSE_SLACK_CHANNEL_ID` | *optional* — defaults to `C0BRJAFNUG5` in `post_to_slack.py` (a channel ID isn't a secret, so cloud routines need no extra config). **Not** `SLACK_CHANNEL_ID`, which is the reply-time KPI channel. The bot must be invited to the channel or `chat.postMessage` returns `not_in_channel`. |

## HubSpot quirks

- Bookings are `MEETING_EVENT` objects created by **Chili Piper**
  (`hs_object_source_detail_1: "Chili Piper"`).
- **Fathom also writes MEETING_EVENTs** ("Fathom summary for …") for calls that already
  happened. They have no `hs_activity_type`, so the search filters on
  `hs_activity_type HAS_PROPERTY` to exclude them.
- The booker's email is **not a clean property** — it's inside the `hs_meeting_body` text as
  `Email: someone@co.com`. Parsed from there, cross-checked against the associated contact.
- `hs_createdate` sorts descending — that's the poll watermark.
- Volume: ~186 meetings/week (~27/day); 23 in a 30h window when tested.
- `GET /oauth/v1/access-tokens/{token}` returns **empty fields** for private-app tokens — it is
  not a valid way to check them. Test against a real endpoint instead.
- Contact `website` is often `null`, so the company domain usually comes from the **email
  domain** fallback, not the contact record.
- **Internal bookings share this feed** — e.g. an "Intro Call" for `pedro@hirewithnear.com`.
  `OWN_DOMAINS` drops them; without that guard an internal booking could pause our own domain
  if a Near address were ever sitting in a campaign as a test lead.
- `hs_activity_type` values seen: "Complimentary Remote Recruiting Consultation" (+ `- GM`,
  `- IV` variants) and "Intro Call". `hs_object_source_detail_1` is `"Chili Piper"` on about
  half the records and `null` on the rest, so **don't filter on source**.

## Verified end-to-end (2026-08-20)

Full chained dry run over 22 real bookings from a 30h window:

- crawled 205,800 leads in 207 requests, ~5 min
- **15 leads matched at 7 companies**, 18 pause actions (some leads sit in 2 campaigns)
- **11 of the 15 were colleagues, not the person who booked** — the whole reason the domain
  key exists. At Patch Media (4 leads) and Scalix AI (3 leads) the booker wasn't in a campaign
  at all; only their colleagues were. Email-only matching would have paused nothing there.
- The 15 no-match bookings were spot-checked against `/leads/?email=` and are genuinely absent
  from Smartlead (inbound bookings, never cold-emailed) — not matching failures.

## Operational notes

- `.env` contains a value with an unescaped `$3`, so `run.sh` must not use `set -u` — sourcing
  would abort. (Cf. the CLAUDE.md note about `$` in passwords/cookies.)
- Because each routine run is a **fresh checkout**, this skill and its scripts must stay
  **committed** to the repo, and no run may depend on local state.

## Cloud routines (live)

Two routines, both cloning `GastonMNear/cv-generator-near-automations` (main) into
environment `env_01DVzad9AipkSb49SRKPteVL` ("Slack Bot + SL + Drive"):

| Routine | Cron (UTC) | Local | Window | ID |
|---|---|---|---|---|
| morning | `3 13 * * 1-5` | 09:03 ET | `--hours 20` | `trig_013MdhuD9nA5PrF7hJP5T11q` |
| afternoon | `27 17 * * 1-5` | 13:27 ET | `--hours 6` | `trig_01UXrVZNP9GcChnc8sPM8kVh` |

Both run `--live`. Windows overlap deliberately so a booking can't fall between runs.
Off-the-hour minutes avoid the :00/:30 scheduling crush.

**`HUBSPOT_ACCESS_TOKEN` must be present in that environment** — it is the one secret the
environment did not already have. Until it is added the routines fail at step 1 with
"HUBSPOT_ACCESS_TOKEN not set"; they were therefore created **disabled**. Enable both at
https://claude.ai/code/routines once the secret is in place.

`PAUSE_SLACK_CHANNEL_ID` is not needed — the channel is defaulted in `post_to_slack.py`.

**Environment network allowlist** must include all three hosts this skill calls:

```
server.smartlead.ai     # lead crawl, /leads/{id}/campaigns, pause
api.hubapi.com          # meetings search + contact associations  <- added for this skill
slack.com               # chat.postMessage
```

The environment already had the Smartlead and Slack hosts from the KPI routines;
`api.hubapi.com` had to be added. A missing host fails as a blocked-domain error, which reads
differently from an auth error — check the allowlist before suspecting the token. (The token is
`pat-na1-…` = NA1 region, served by plain `api.hubapi.com`; use `*.hubapi.com` if a regional
host ever appears.)

## Overlapping windows and re-pausing (by design)

The two runs use **fixed lookback windows** (20h and 6h), not a "since last run" watermark, so
they deliberately re-process the same bookings. There is no persisted cursor — routine runs get
a fresh checkout, so any watermark would silently reset, and the failure mode of a reset
watermark is *missing* a booking, which is the thing this skill exists to prevent. Redundant
coverage is the safer way to be wrong.

**Re-pausing is a no-op — verified live 2026-08-20.** Calling pause on an already-`PAUSED` lead
returns `{"ok":true,"data":"success"}` and leaves the status `PAUSED`. Three consecutive pauses
produced the same state as one. Nothing is duplicated in Smartlead; the only cost is that the
Slack report lists the same lead again.

**The one case where the overlap does something unwanted:** if a lead is deliberately *resumed*
between the two runs (e.g. a colleague at a booked company should keep receiving a different
sequence), the next run will pause them again — the script cannot distinguish "never paused"
from "paused, then intentionally resumed". Rare, and not fixable without durable state, so it
is accepted. If it ever becomes a problem, the fix is an exclusion list, not a watermark.

## Never do

- Never call `POST /campaigns/{id}/status` — that pauses an **entire campaign**. This skill
  only ever pauses individual leads.
- Never pause without a dry run first when the matching logic has changed.
