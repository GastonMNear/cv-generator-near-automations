---
name: smartlead-weekly-response-kpi
description: >
  Computes the weekly KPI of how fast we respond to positive replies in Smartlead —
  the business-hours gap between when a positive reply lands and when we reply to it —
  and posts it to Slack as a threaded message. Use this whenever asked for the weekly
  response-time report, "how fast are we replying to positive replies", Smartlead
  reply-time / response-time metrics, or when run as a scheduled Claude routine. Runs
  over a Mon–Sun week (defaults to the previous full week) across all Smartlead campaigns.
---

# Smartlead Weekly Response-Time KPI

Measures our **speed of response to positive replies** and reports it to Slack every week.
Built to run unattended as a **Claude routine** (cron), so it must be deterministic and
never depend on choices made at runtime — all the logic lives in the bundled scripts.

## What it measures

- **A positive reply** = a lead reply whose Smartlead category has `sentiment_type: "positive"`
  (Interested, Meeting Request, Information Request, Meeting Booked, Candidate sent - Follow Up,
  Send to Cold Call). The list is fetched live, so new positive categories are picked up automatically.
- **Response time** = time from the positive reply landing to **our next outbound message**
  (`type: SENT` in the message history, including manual replies sent from the Master Inbox).
- **Primary metric = business hours** (Mon–Fri, 09:00–18:00 America/New_York). Off-hours don't
  count: a reply at 20:00 answered at 09:30 next morning is ~0.5 h, not ~13.5 h. This keeps the
  average and median honest — the team isn't penalized for not working overnight/weekends.
- **Raw wall-clock** is reported alongside, for reference only.
- **% responded in <5 min and <10 min** = share of answered positive replies where the *real*
  (wall-clock) gap was under 5 / under 10 minutes — the "we jumped on it" responsiveness metric.
  Uses wall-clock on purpose (a reply caught N real minutes later, even at night, is a genuine
  fast response; after-hours replies we couldn't catch in N min simply don't count toward it).

## Prerequisites (secrets)

These must exist in the environment where the skill runs (locally: the repo `.env`; in a
routine: the routine's configured secrets):

| Var | What | Notes |
|---|---|---|
| `SMARTLEAD_API_KEY` | Smartlead API key | already in repo `.env` |
| `SLACK_BOT_TOKEN` | `xoxb-…` bot token | Slack app with scopes `chat:write` + `files:write`, **added to the target channel** |
| `SLACK_CHANNEL_ID` | e.g. `C0123456789` | the channel **ID**, not the `#name` |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` / `GOOGLE_REFRESH_TOKEN` | Google OAuth creds | **weekly only** — for the Sheets write. The `drive` scope on this token covers Sheets. |

**Why a bot token and not an Incoming Webhook:** threading (a first message + a reply in its
thread) requires the parent message's `ts`, which `chat.postMessage` returns and webhooks don't.
A bot token is a static secret, so it works fine in headless cron — it's just more capable.

## How to run

Curl-based (Smartlead blocks python-requests with a Cloudflare 403).

```bash
# 1. Compute the KPI → writes scripts/kpi_output.json
python3 scripts/run_weekly_kpi.py                     # WEEKLY: previous full Mon–Sun week (auto)
python3 scripts/run_weekly_kpi.py --daily             # DAILY: the previous day (Mon covers Fri+Sat+Sun)
python3 scripts/run_weekly_kpi.py 2026-07-13          # the week starting that Monday
python3 scripts/run_weekly_kpi.py 2026-07-13 2026-07-19  # explicit start/end (inclusive, ET)

# 2. Post to Slack (reads scripts/kpi_output.json)
python3 scripts/post_to_slack.py

# 3. WEEKLY ONLY — append the week as a new column in the tracking Google Sheet
python3 scripts/write_to_sheet.py
```

Times in the Slack message are shown as **HH:MM** (e.g. `1h 36m`, or `36m` under an hour), not
decimal hours — more intuitive to read.

The same script drives both cadences — only the date window differs (that's why there's no
separate "daily" skill). Defaults: no args = the **previous full Mon–Sun week** (what a
Monday-morning weekly routine wants); `--daily` = the **previous day**, but because the daily
routine only runs Mon–Fri, a Monday run reaches back over the weekend (Fri+Sat+Sun) so no
business day is ever missed between the daily and weekly reports. The Slack header adapts:
a single day shows the date ("Mon Jul 13, 2026"), a range shows the span.

(The script file is still named `run_weekly_kpi.py` for historical reasons — it handles both
periods. Renaming would mean re-pointing the live weekly routine's prompt, so it's left as-is.)

## Slack output shape

- **Message 1 (channel):** headline — period label, # positive replies, answered/pending,
  business-hours **avg / median / min / max**, **% responded in <5 min and <10 min** (wall-clock),
  and the raw avg/median underneath for reference — plus a compact **per-category** table.
- **Reply in thread:** the full **lead-by-lead** breakdown as a **CSV file attachment** (Slack
  renders it in a scrollable viewer that opens as a spreadsheet — cleaner than a wide code block).

## Setting it up as a Claude routine

Create routines (cron) with a minimal prompt that just invokes this skill — keep the logic in the
skill, not the prompt, so it stays consistent. Two routines share this one skill/repo:

- **Weekly** — Monday ~08:00 ET. Prompt: previous full week (`run_weekly_kpi.py` no args) → post to
  Slack (`post_to_slack.py`) → append to the Google Sheet (`write_to_sheet.py`).
- **Daily** — Mon–Fri ~08:00 ET. Prompt: daily mode (`run_weekly_kpi.py --daily`) → post to Slack.
  **Daily does NOT write to the sheet** — only the weekly does.
- **Environment:** confirm the secrets above are present in the routine's environment (weekly also
  needs the three Google vars). Because each routine run is a fresh checkout, this skill and its
  scripts must be committed to the repo.

## Google Sheet (weekly only)

`write_to_sheet.py` appends each week as a **new column** (metric-per-row layout) in tab
`Email Time-to-reply tracker` of the tracking spreadsheet (ID hard-coded in the script), so the
numbers accumulate for WoW comparisons and trend charts. It finds the next empty column via the
"Avg" row and writes Start/End/run-Date plus the metrics. All values go in with
`valueInputOption=USER_ENTERED`, so Sheets stores **real typed values — dates, percentages, and
durations (numeric under the hood), never strings** — which is what keeps the sheet chartable and
formula-friendly. "Interested Replies" = total positive replies; durations are written as `H:MM`.

Each routine should: run step 1 (with the right args), confirm `kpi_output.json` was written with
`errors: 0` (or note any errors), then run step 2. If Slack posting fails, report the KPI summary
in the run output so the number is never lost.

## Methodology details (so the number is trustworthy)

- **Efficiency:** the scan uses one `statistics` call per campaign (returns `reply_time` +
  `lead_category` + email — no conversation bodies). Only leads that pass the week+positive filter
  get a `message-history` fetch. We never pull conversations we don't need.
- **Dedupe:** one row per (campaign, lead), keeping the earliest positive reply in the window.
- **Timezone:** the week boundary and the office-hours clock are both America/New_York. Change
  `OFFICE_OPEN`/`OFFICE_CLOSE`/`ET` in `run_weekly_kpi.py` if the response team's hours change.
- **`biz = 0.00h`** is legitimate (rare with the 9–18 window): the reply landed outside office
  hours and we answered before the next office-open — we replied before the business clock started.
- **Pending** = a positive reply with no outbound from us yet at run time. Counted, but excluded
  from avg/median. A persistent pending may mean we replied from outside Smartlead (Gmail/Outlook),
  which won't appear in the thread — worth a manual check.

## Known API facts (verified live 2026-07-20)

- Base URL `https://server.smartlead.ai/api/v1`, auth `?api_key=`. **curl only** (python 403).
- **Rate limit: 200 requests/min.** A full weekly run is ~106 (scan) + 2×(positive leads) requests.
  `run_weekly_kpi.py` has a global throttle capped at 175/min plus backoff, so it self-paces.
- `GET /leads/fetch-categories` → categories with `sentiment_type`.
- `GET /campaigns/{id}/statistics?offset=&limit=` → rows with `reply_time`, `lead_category`,
  `lead_email`. `total_stats` may come back as a **string** — cast to int when paging.
- `GET /leads/?email=` → lead object with `id` (needed for message-history).
- `GET /campaigns/{id}/leads/{lead_id}/message-history` → `{history: [...]}`, each message has
  `type` (`SENT`/`REPLY`), `time`, `email_seq_number`. **Manual Master-Inbox replies appear as
  `type: SENT` with `email_seq_number: null`** — this is what confirms we can measure our replies.

## Self-annealing

If a run fails or a field shifts, fix the script, test against the regression anchor below, and
update the "Known API facts" above with whatever changed.

Regression anchor (week Jul 13–19, 2026, measured under the **old 9–19 ET window**): ~79 positive
replies, biz avg ~5.9 h, biz median ~4.3 h, raw avg ~21 h, <10 min ~1–2%. Exact counts
(answered/pending) drift over time as the team keeps replying to still-pending leads, so treat them
as approximate.

> [!warning] **Window history — this anchor is not directly comparable to current runs.** The
> office-hours window has moved twice: it was **9–19 ET** when this anchor was measured, changed to
> **10–19 ET** on 2026-08-27, and was reverted to **9–18 ET** on 2026-09-11 (the intended window —
> 9 am to 6 pm ET). The current window is one hour shorter per day than the anchor's (same 09:00
> open, earlier 18:00 close), so replies answered between 18:00 and 19:00 now roll to the next
> morning instead of counting the same day. Business-hours averages will read **higher** than this
> anchor for identical behaviour. Do not read a week-over-week change across either boundary as a
> performance shift — re-baseline before comparing, and note the window on any chart spanning
> 2026-08-27 or 2026-09-11.
