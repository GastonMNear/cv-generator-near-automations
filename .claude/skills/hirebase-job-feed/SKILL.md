---
name: hirebase-job-feed
description: >
  Daily feed of hiring-intent leads: pulls yesterday's US remote, full-time jobs at 1-500 employee
  companies in Near's qualified sub-industries from the Hirebase API and posts each job to a Clay
  webhook table as its own row, smallest companies first. Runs once a day as a Claude routine. Use this whenever asked about
  the Hirebase feed, the open-jobs / hiring-intent lead source, "new jobs in Clay", backfilling a
  missed day, changing the job-search filters or sub-industry list, or Hirebase spend.
---

# Hirebase → Clay job feed

Companies posting jobs = hiring intent = outbound targets for the US open-jobs campaign
(HM and no-HM variants are routed later in Clay, depending on whether an HM is found).

## Pipeline

```
1. POST /v2/jobs/estimate   free, 9 calls: per band for day and day+1 (exact count = difference),
                            plus a 7-day window to confirm date_posted is on-or-after → abort if > --max-jobs
2. POST /v2/jobs/search     one band at a time, smallest first (1-10, 11-50, 51-200, 201-500);
                            oldest first; pages sized to the band's exact count, stop at that count
                            or at the first job dated after the target day
3. save the fetched jobs to a run file (before posting)
4. POST <Clay webhook>      one flat JSON object per job = one Clay row
```

**Size priority (Gaston, 2026-11-03):** 1-10 and 11-50 reply best (historic No-HM positive rate 3.2% /
0.9% vs 0.26% at 51-200 and 0.13% at 201-500), so they are always fetched. Larger companies only fill
spare credits. Before 51-200 and 201-500, `feed.py` checks `Hirebase-Usage-Included-Remaining` (from
the last search response) and skips the band if its estimate would cut into the reserve:
`PRIORITY_DAILY` (200 units) × days left until `Hirebase-Usage-Period-End`. The skip is logged
(`skip 201-500: ...`) and the run still exits 0. Tune `PRIORITY_BANDS` / `PRIORITY_DAILY` in `feed.py`.

**A failed search page never wastes units:** jobs already fetched are saved and posted, the run exits 1
and prints `run.sh --live --date D --resume BAND:PAGE:LIMIT`. That command skips the bands and pages already
paid for (LIMIT keeps the page offsets identical). On 2026-11-03 a plan-cap 429 at page 6 threw away 500
billed units and the rerun paid for them again; this is the fix. After a `limit_exceeded` 429, resume only
once the quota is back.

**No next-day jobs on the last page:** `date_posted` is "on or after", so a full last page of 100 also
returns jobs from the next day. They can't be kept and skipped tomorrow: tomorrow's search returns and
bills them again, and late indexing shifts offsets within a day. So each band uses equal pages that end on
the day's last job (201 jobs → 3 × 67) and stops at the count. On 2026-11-04 the four bands paid for 121
next-day jobs (1,143 units for 1,022 jobs); now the waste is only rounding, a few units per band. If the
7-day check fails (date_posted flipped back to exact-day), it logs a WARNING and uses full pages +
stop-at-next-day, which is correct under both semantics.

```bash
./scripts/run.sh                    # DRY RUN: free estimate only
./scripts/run.sh --live             # fetch yesterday (UTC) + post to Clay
./scripts/run.sh --live --sample 3  # cheap end-to-end test (3 job units)
./scripts/run.sh --live --date 2026-10-19   # backfill one missed day
./scripts/run.sh --live --resend FILE       # re-post saved jobs to Clay, no Hirebase cost
./scripts/run.sh --live --date D --resume 51-200:3:84   # finish a run whose search page failed
```

**A Hirebase outage before any search costs nothing and is retried.** On 2026-11-08 (HTTP 500) and
2026-11-09 (read timeouts) the estimate step failed, both runs stopped, and Nov 7 and Nov 8 were
never fetched until a manual backfill. Now the free estimate phase retries for `ESTIMATE_PATIENCE`
(180 s) in total. If the day's estimates still fail, the run exits **3** and prints `NOTHING BILLED`,
which means no search ran and rerunning the same command is free. The routine waits about 9 minutes
and reruns, at most twice. The 7-day and day+1 estimates are optional: if they fail, the run logs a
WARNING and uses full pages + stop-at-next-day. Exit 1 still means something may have been billed,
so never blind-rerun it. A day that's still missed after the reruns is **not** caught up
automatically, because the cloud run keeps no state between days. Backfill it with
`run.sh --live --date D`. Spot a missed day by HireBase `4217467` adds collapsing in Smartlead or the
Clay webhook source going quiet for more than 26h.

Network errors are retried with backoff (incl. SSL "bad record mac", which killed the first full
run on 2026-10-21 at job 567 of 1,249). A job that still fails never stops the run: it goes to an
`hirebase-unposted-*.json` file, the run exits 1 and prints the exact `--resend` command. **In a
routine, run that command once when the exit code is 1** — the file lives in the run's temp dir
and is gone after the routine ends.

## Filters

`references/search_filters.json`: Full Time, Remote, country United States (`strict`),
company size 1-10 / 11-50 / 51-200 / 201-500, `hide_recruiting_agencies`, and **276
sub-industries**. The run adds `date_posted` itself and splits `company_types` into one search per band.
`company_types` order is the fetch priority, so keep it smallest first.

Exclusions (Gaston, 2026-11-03; analysis in `output/hirebase/optimization/report.md`), about −10% units, −0.2% leads:
- `job_titles`: 31 `-word` negations (nurse, RN, therapist, physician, attorney, licensed, participants,
  field trades…). Clay's role check rejects 96% of these jobs, and they gave 4 of 2,305 leads.
  Deliberately not excluded, because Near places some of them: technician, driver, paralegal, construction.
- `company_keywords: ["-blackbox"]`: Clients Blackbox, a Monday-burst mass poster (654 jobs since Oct 20),
  all HubSpot do-not-contact, 0 leads. This replaces the 2026-10-21 "no company exclusions" rule.

Before changing filters, price the new body with the free estimate (`./scripts/run.sh --date D`) and
compare it with the old one. The expansion candidate (Hybrid, 1-50 employees, ~4.8k units/month) is
priced in `output/hirebase/optimization/expansion_search_filters.json` and not live.

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
  table's `Dedupe` column (`title - company`) collapses them; that's intended. That one company was
  Clients Blackbox, now excluded (Gaston 2026-11-03; it was "no company exclusions" on 2026-10-21).
- `days_ago` is unreliable (`days_ago: 0` returned 1 job when today had 96). Don't use it.
- `sub_industry` works without `industry`. It matches on the **company's** tags, any-of. Companies
  carry several tags, so cutting a sub only removes companies whose tags are *all* cut.
- `hide_recruiting_agencies: "true"` removes ~13% (staffing reposts).
- `/v2/jobs/estimate` is free and accepts the same body (`limit: 0` → total count).
- Billing: 1 unit per job returned by search. A plan-quota 429 has `X-Billing-Code: limit_exceeded`
  and is not retried.
- Checking usage: only `/search` returns the `Hirebase-Usage-*` headers (`Included-Limit/-Used/-Remaining`,
  `Period-Start/-End`); `/estimate` doesn't and there is no usage endpoint. A `limit: 1` search with
  `search_filters.json` reads them for 1 unit. As of 2026-10-28: 2,000,000 included per period,
  period 2026-10-20 → 2026-11-03, overage mode `meter` (the trial; moving to a 25k units/month plan in
  Nov 2026). `feed.py`'s size-band guard reads `-Included-Remaining` and `-Period-End` from these headers.
- Rate limit 100 req/min (search). The `/data/*` taxonomy endpoints observed at ~25/min.
- `Other` and `Retail` are listed as industries but `/subindustries` 404s on both.
- Filter fields (tested 2026-11-03 via estimate). **Unknown fields return 422 `extra_forbidden`**:
  - Work: `job_titles` (`-word` negation, works on its own), `company_keywords` (`-word` negation),
    `keywords` (`-word`), `experience` (Entry/Junior/Mid/Senior/Executive), `job_category` (exact names
    from `/data/categories`), `salary {min,max}`, `yoe`, `signals: ["reposted"]`, `ingested_after`.
  - Include-only: `company_name` (`-X` returns 0 jobs, not an exclusion).
  - 422: `job_categories`, `experience_level`, `job_boards`, `exclude_company_names`, `min_salary`.
    `experience_levels` returns 200 but is ignored.
  - `job_category` and `experience` include-lists drop untagged jobs (12% / 16%).
  - `-` exclusions are word-level: `-"clients blackbox"` removed every job whose company says "clients" (2,017).
- `sub_industry` is a weak lever: dropping it entirely adds only +1.7% (multi-tagged companies).

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

## Cloud routine (live)

`trig_01YKNX5PsqwEh6s6N5LVo2sk`, "Hirebase Job Feed (daily 16:03 UTC)": cron `3 16 * * *`
(12:03 ET in summer time, 11:03 ET from Nov 1), model claude-sonnet-5-5, no connectors. It clones
`GastonMNear/cv-generator-near-automations` (main) into its own environment `env_01P5pofgfYkKGgiroxZxoWWC` (".env | HireBase")
and runs `run.sh --live` for yesterday (UTC), plus one `--resend` if posts failed. On exit 3 (nothing
billed) it sleeps 540 s and reruns, at most twice. It never refetches after exit 1. The session
status reads "succeeded" even when the feed failed, so read the run log (`RemoteTrigger get_run_log`)
to see the real outcome.
Noon is chosen so yesterday is mostly indexed (see Late indexing). The environment needs
`HIREBASE_API_KEY` and `CLAY_HIREBASE_WEBHOOK_URL`, and allowed domains `api.hirebase.org` and
`api.clay.com`. First run: 2026-10-22, for 2026-10-21.
