---
name: hirebase-job-feed
description: >
  Daily feed of hiring-intent leads: pulls yesterday's US remote, full-time jobs at 1-500 employee
  companies in Near's qualified sub-industries from the Hirebase API and posts each job to a Clay
  webhook table as its own row. Runs once a day as a Claude routine. Use this whenever asked about
  the Hirebase feed, the open-jobs / hiring-intent lead source, "new jobs in Clay", backfilling a
  missed day, changing the job-search filters or sub-industry list, or Hirebase spend.
---

# Hirebase → Clay job feed

Companies posting jobs = hiring intent = outbound targets for the US open-jobs campaign
(HM and no-HM variants are routed later in Clay, depending on whether an HM is found).

## Pipeline

```
1. POST /v2/jobs/estimate   free: upper bound for the run → abort if > --max-jobs
2. POST /v2/jobs/search     oldest first, limit=100; stop at the first job dated after the target day
3. save the fetched jobs to a run file (before posting)
4. POST <Clay webhook>      one flat JSON object per job = one Clay row
```

```bash
./scripts/run.sh                    # DRY RUN: free estimate only
./scripts/run.sh --live             # fetch yesterday (UTC) + post to Clay
./scripts/run.sh --live --sample 3  # cheap end-to-end test (3 job units)
./scripts/run.sh --live --date 2026-10-19   # backfill one missed day
./scripts/run.sh --live --resend FILE       # re-post saved jobs to Clay, no Hirebase cost
```

Network errors are retried with backoff (incl. SSL "bad record mac", which killed the first full
run on 2026-10-21 at job 567 of 1,249). A job that still fails never stops the run: it goes to an
`hirebase-unposted-*.json` file, the run exits 1 and prints the exact `--resend` command. **In a
routine, run that command once when the exit code is 1** — the file lives in the run's temp dir
and is gone after the routine ends.

## Filters

`references/search_filters.json`: Full Time, Remote, country United States (`strict`),
company size 1-10 / 11-50 / 51-200 / 201-500, `hide_recruiting_agencies`, and **276
sub-industries**. The run adds `date_posted` itself.

The sub-industry list comes from mapping Near's 89 placement industries (HubSpot/LinkedIn labels)
to Hirebase's taxonomy. The mapping, exclusion reasons and generator live in
`output/hirebase/` (`build_mapping.py`, `industry_mapping.csv`, `excluded_subindustries.csv`,
`README.md`). To change the list, edit `build_mapping.py`, rerun it, and copy the new
`sub_industry_filter.json` into `search_filters.json`. Values must be exact API strings or
search returns 422.

## Hirebase behaviour

- **`date_posted` changed meaning overnight, undocumented.** On 2026-10-20 it matched one exact day
  (≥10-18 → 22 jobs, ≥10-19 → 1,316). On 2026-10-21 it matched "on or after", as the docs say
  (≥10-12 → 5,947 … ≥10-20 → 1,289). The oldest-first sort + stop-at-next-day makes the script
  correct under both; overspend is at most the rest of the last page (40 units on 2026-10-21).
- **Late indexing:** most of a day's jobs are indexed the *following* day (10-21 had 40 jobs at
  18:18 UTC that day; 10-20 had 1,249 by then). 10-19: 1,316 → 1,438 → 1,357 over two days, so
  after ~1 day a date only drifts a few % (late adds vs expiry).
- Volume: ~600-700 jobs on weekdays, ~20-90 on weekends, Monday spike (~1,350).
- **Same role, many postings:** Hirebase lists each location/requisition separately (unique `_id`
  and URL). 10-20: 1,249 jobs = 570 unique `title - company` (one company posted 630). The Clay
  table's `Dedupe` column (`title - company`) collapses them; that's intended. No company exclusions
  (Gaston, 2026-10-21).
- `days_ago` is unreliable (`days_ago: 0` returned 1 job when today had 96). Don't use it.
- `sub_industry` works without `industry`. It matches on the **company's** tags, any-of. Companies
  carry several tags, so cutting a sub only removes companies whose tags are *all* cut.
- `hide_recruiting_agencies: "true"` removes ~13% (staffing reposts).
- `/v2/jobs/estimate` is free and accepts the same body (`limit: 0` → total count).
- Billing: 1 unit per job returned by search. A plan-quota 429 has `X-Billing-Code: limit_exceeded`
  and is not retried.
- Rate limit 100 req/min (search). The `/data/*` taxonomy endpoints observed at ~25/min.
- `Other` and `Retail` are listed as industries but `/subindustries` 404s on both.

## Secrets

| Var | Purpose |
|---|---|
| `HIREBASE_API_KEY` | Hirebase API key (`hb_…`) |
| `CLAY_HIREBASE_WEBHOOK_URL` | Webhook URL of the Clay jobs table (live runs only) |

Both must be in the repo `.env` (local) and in the routine's cloud environment.

## Clay side

- Webhook-source table; dedupe is on its `Dedupe` column (`title - company`).
- Clay answers `202 {"accepted":true}` even when it drops the row: on 2026-10-20 nothing landed
  for hours (Clay-side, fixed by support), and on 2026-10-21 37 of the first 567 accepted jobs
  never appeared until re-sent. A 202 is not proof of a row; reconcile against an export if counts
  look low (match on `Job Url` = `application_link`).
- Rows arriving by webhook cost no Clay credits. Credits go on enrichment, so gate paid columns
  behind filters, and find the HM **once per company** (many companies post several jobs).
- At ~18k rows/month, watch the table's row cap and roll to a new table periodically.
