#!/usr/bin/env python3
"""Pull yesterday's matching jobs from Hirebase and push each one to a Clay webhook as a row.

Hirebase bills one unit per job RETURNED by /v2/jobs/search, so this script:
  1. sizes the run with /v2/jobs/estimate first (free),
  2. aborts if the run would exceed --max-jobs (protects the allowance),
  3. fetches only the target day: `date_posted` has behaved both as an exact-day match
     (2026-10-20) and as "on or after" (2026-10-21), so results are sorted OLDEST first and
     paging stops at the first job dated after the target day. Under either behaviour each
     job is fetched once; the overspend is at most the rest of the last page (<100 jobs).
  4. saves the fetched jobs to a file BEFORE posting, so a Clay failure is fixed with
     --resend <file> instead of paying Hirebase again.
  5. fetches one company-size band at a time, in the order `company_types` lists them in
     search_filters.json (smallest first). PRIORITY_BANDS are always fetched; a larger band is
     skipped when it would eat into the quota the priority bands need for the rest of the
     billing period (Gaston 2026-11-03: small companies always, larger ones with spare credits).
  6. if a search page fails (e.g. the plan-quota 429), keeps and posts what was already paid
     for and prints a --resume command that starts at the failed band/page.
  7. sizes each band's pages to the day's exact count (estimate(day) - estimate(day+1), both free)
     and stops at that count, so the last page doesn't pay for next-day jobs (2026-11-04: 121 of
     1,143 units were next-day jobs). Only when date_posted is confirmed on-or-after (a 7-day
     window must be >2x the day); otherwise it falls back to full pages + stop-at-next-day.

DRY RUN by default: only the free estimates run. --live fetches and posts.

Usage:
    python3 feed.py                         # dry run, yesterday (UTC)
    python3 feed.py --live                  # fetch + push to Clay
    python3 feed.py --live --sample 3       # fetch only 3 jobs (cheap end-to-end test)
    python3 feed.py --date 2026-10-19       # a specific day (backfill after a missed run)
    python3 feed.py --live --resend FILE    # re-post a saved run to Clay (no Hirebase cost)
    python3 feed.py --live --date D --resume 51-200:3:67   # after a failed page: skip what was paid for
Env: HIREBASE_API_KEY, CLAY_HIREBASE_WEBHOOK_URL (live only)
"""
import argparse
import html
import http.client
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

API = "https://api.hirebase.org/v2/jobs"
FILTERS = Path(__file__).resolve().parent.parent / "references" / "search_filters.json"
PAGE_SIZE = 100          # Hirebase max per page
HIREBASE_PAUSE = 0.7     # s between Hirebase calls (limit: 100 req/min)
CLAY_PAUSE = 0.1         # s between Clay webhook posts
DESC_MAX = 8000          # chars of plain-text description kept per row
PRIORITY_BANDS = {"1-10", "11-50"}   # always fetched (best reply rates, see output/hirebase/optimization)
PRIORITY_DAILY = 200     # units/day the priority bands need (≈2,660 over Oct 20-Nov 2), kept in reserve


ESTIMATE_PATIENCE = 180  # s the whole free-estimate phase keeps retrying a down/slow Hirebase
NOTHING_BILLED_EXIT = 3  # estimate phase failed transiently: nothing was billed, rerunning is free


def request(url, body=None, headers=None, retries=4, timeout=60):
    """POST/GET with backoff on 429/5xx. Returns (status, parsed_json_or_text, headers)."""
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, data=data, method="POST" if data else "GET",
                                     headers={"Content-Type": "application/json", **(headers or {})})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read().decode()
                try:
                    return r.status, json.loads(raw), r.headers
                except json.JSONDecodeError:
                    return r.status, raw, r.headers
        except urllib.error.HTTPError as e:
            raw = e.read().decode(errors="replace")
            # A plan-quota 429 is not transient: retrying can't help.
            if e.code == 429 and e.headers.get("X-Billing-Code") == "limit_exceeded":
                return e.code, raw, e.headers
            if (e.code == 429 or e.code >= 500) and attempt < retries:
                time.sleep(float(e.headers.get("Retry-After") or 2 ** (attempt + 1)))
                continue
            return e.code, raw, e.headers
        except (urllib.error.URLError, OSError, http.client.HTTPException):
            # Network-level failures (DNS, reset, SSL "bad record mac" seen 2026-10-21) are
            # transient. A retried Clay post can duplicate a row; dedupe on job_id covers it.
            if attempt < retries:
                time.sleep(2 ** (attempt + 1))
                continue
            raise


def strip_html(s):
    if not s:
        return ""
    s = re.sub(r"<(br|/p|/li|/h\d)[^>]*>", "\n", s, flags=re.I)
    s = re.sub(r"<li[^>]*>", "- ", s, flags=re.I)
    s = html.unescape(re.sub(r"<[^>]+>", "", s))
    return re.sub(r"\n{3,}", "\n\n", s).strip()[:DESC_MAX]


def flatten(job, fetched_at):
    """One flat dict per job = one Clay row. job_id is the dedupe key."""
    c = job.get("company_data") or {}
    size = c.get("size_range") or {}
    yoe = job.get("yoe_range") or {}
    sal = job.get("salary_range") or {}
    return {
        "job_id": job.get("_id"),
        "job_title": job.get("job_title"),
        "application_link": job.get("application_link"),
        "date_posted": job.get("date_posted"),
        "location_raw": (job.get("location_raw") or "").strip(),
        "location_type": job.get("location_type"),
        "job_type": job.get("job_type"),
        "experience_level": job.get("experience_level"),
        "yoe_min": yoe.get("min"),
        "yoe_max": yoe.get("max"),
        "salary_min": sal.get("min"),
        "salary_max": sal.get("max"),
        "salary_currency": sal.get("currency"),
        "job_categories": ", ".join(job.get("job_categories") or []),
        "requirements_summary": job.get("requirements_summary"),
        "description": strip_html(job.get("description")),
        "job_board": job.get("job_board"),
        "company_name": job.get("company_name"),
        "company_domain": job.get("company_link"),
        "company_linkedin": c.get("linkedin_link"),
        "company_size_min": size.get("min"),
        "company_size_max": size.get("max"),
        "company_type": c.get("type"),
        "company_industries": ", ".join(c.get("industries") or []),
        "company_subindustries": ", ".join(c.get("subindustries") or []),
        "company_description": c.get("description_summary"),
        "company_slug": job.get("company_slug"),
        "source": "hirebase",
        "fetched_at": fetched_at,
    }


def days_left(period_end, day):
    """Whole days from the run's target day to the end of the billing period (0 if unknown)."""
    try:
        end = datetime.fromisoformat(str(period_end).replace("Z", "+00:00")).date()
    except ValueError:
        return 0
    return max(0, (end - datetime.strptime(day, "%Y-%m-%d").date()).days)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="day to fetch, YYYY-MM-DD (default: yesterday UTC)")
    ap.add_argument("--live", action="store_true", help="fetch from Hirebase and post to Clay")
    ap.add_argument("--max-jobs", type=int, default=3000,
                    help="abort if the estimate exceeds this (default 3000; a Monday is ~1,400, and the "
                         "estimate can include later days when date_posted acts as on-or-after)")
    ap.add_argument("--sample", type=int, help="live: fetch only this many jobs (end-to-end test)")
    ap.add_argument("--resend", help="live: post jobs from a saved run file to Clay; skips Hirebase")
    ap.add_argument("--resume", help="live: BAND:PAGE:LIMIT printed by a failed run; skips bands/pages already paid for")
    ap.add_argument("--out-dir", default=os.environ.get("TMPDIR", "/tmp"), help="where the run file is saved")
    args = ap.parse_args()

    if args.resend:
        if not args.live:
            sys.exit("--resend needs --live")
        jobs = json.load(open(args.resend))
        print(f"== hirebase-job-feed RESEND {len(jobs)} jobs from {args.resend} ==")
        post_to_clay(jobs, datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), None)
        return

    key = os.environ.get("HIREBASE_API_KEY")
    if not key:
        sys.exit("HIREBASE_API_KEY not set")
    auth = {"x-api-key": key}
    day = args.date or (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    body = json.load(open(FILTERS))
    body["date_posted"] = day  # exact-day or on-or-after: see docstring, step 3
    body["sort_by"], body["sort_order"] = "date_posted", "asc"
    bands = body["company_types"]  # fetch order = priority order (step 5)
    resume_band, resume_page, resume_limit = (args.resume.split(":") + ["1", ""])[:3] if args.resume \
        else (bands[0], "1", "")
    if resume_band not in bands:
        sys.exit(f"--resume band {resume_band!r} is not in company_types {bands}")
    bands = bands[bands.index(resume_band):]

    print(f"== hirebase-job-feed date_posted={day} {'LIVE' if args.live else '(dry run)'} ==")

    # Estimates are free, so a Hirebase outage (HTTP 500 on 2026-11-08, read timeouts on 2026-11-09) is
    # retried for ESTIMATE_PATIENCE in total. If the day's estimates still fail, exit NOTHING_BILLED_EXIT:
    # no search ran, so the routine can wait and rerun the same command at no cost.
    deadline = time.monotonic() + ESTIMATE_PATIENCE

    def estimate(d, types, required=True):
        wait = 15
        while True:
            try:
                st, res, _ = request(f"{API}/estimate", {**body, "date_posted": d, "company_types": types,
                                                         "limit": 0}, auth, retries=1, timeout=30)
            except Exception as e:  # network failure that outlived request()'s own retry
                st, res = None, repr(e)
            if st == 200:
                time.sleep(HIREBASE_PAUSE)
                return int(res["cost"])
            transient = st is None or st == 429 or st >= 500
            if not transient or time.monotonic() + wait > deadline:
                break
            print(f"  estimate {d} {types}: HTTP {st} {str(res)[:120]}; retrying in {wait}s", flush=True)
            time.sleep(wait)
            wait = min(wait * 2, 60)
        msg = f"estimate failed for {types} {d}: HTTP {st} {str(res)[:300]}"
        if not required:
            print(f"WARNING: {msg}")
            return None
        if transient:
            print(msg, file=sys.stderr)
            print("NOTHING BILLED: failed before any search; rerunning the same command is free",
                  file=sys.stderr)
            sys.exit(NOTHING_BILLED_EXIT)
        sys.exit(msg)

    nxt = (datetime.strptime(day, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    est = {b: estimate(day, [b]) for b in bands}
    total = sum(est.values())
    # Step 7: exact per-day counts are only valid if date_posted means "on or after". Optional: if these
    # estimates fail, fall back to full pages + stop-at-next-day (correct, a few units of overspend).
    week = estimate((datetime.strptime(day, "%Y-%m-%d") - timedelta(days=6)).strftime("%Y-%m-%d"), bands,
                    required=False)
    exact = {}
    if week is not None and week > 2 * total:
        nxt_est = {b: estimate(nxt, [b], required=False) for b in bands}
        if None not in nxt_est.values():
            exact = {b: est[b] - nxt_est[b] for b in bands}
    print(f"estimate: {total} jobs dated {day} or later (free; upper bound) by band: "
          + ", ".join(f"{b} {n}" for b, n in est.items()))
    if exact:
        print(f"dated exactly {day}: {sum(exact.values())} by band: "
              + ", ".join(f"{b} {n}" for b, n in exact.items()))
    elif week is None or week > 2 * total:
        print("WARNING: exact-day count unavailable (estimate failed); using full pages + stop-at-next-day")
    else:
        print(f"WARNING: date_posted no longer looks on-or-after (7-day window {week} vs day {total}); "
              "using full pages + stop-at-next-day")
    if total > args.max_jobs and not args.sample:
        sys.exit(f"ABORT: {total} > --max-jobs {args.max_jobs}. Check the filters, or rerun with a higher cap.")
    if not args.live:
        print(f"dry run: a live run would consume about {sum(exact.values()) if exact else total} Hirebase "
              "job units. Nothing fetched or posted.")
        return
    if total == 0:
        print("nothing to fetch")
        return

    if not os.environ.get("CLAY_HIREBASE_WEBHOOK_URL"):
        sys.exit("CLAY_HIREBASE_WEBHOOK_URL not set (checked before spending anything)")

    want = min(total, args.sample) if args.sample else total
    fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    jobs, seen, remaining, period_end, units = [], set(), None, None, 0
    skipped, failed = [], None
    for band in bands:
        if len(jobs) >= want:
            break
        if band not in PRIORITY_BANDS and remaining is not None:
            reserve = PRIORITY_DAILY * days_left(period_end, day)
            need = exact.get(band, est[band])
            if need > remaining - reserve:
                print(f"  skip {band}: needs ~{need}, {remaining} left, {reserve} reserved for 1-50 "
                      f"until the period ends")
                skipped.append(band)
                continue
        n = exact.get(band)  # jobs dated exactly `day` in this band, or None (unknown)
        if n == 0:
            print(f"  {band}: no jobs dated {day}")
            continue
        # Constant per band (page N is offset (N-1)*limit): equal pages that end on the day's last job.
        limit = PAGE_SIZE if n is None else math.ceil(n / math.ceil(n / PAGE_SIZE))
        page = 1
        if band == resume_band and args.resume:
            page, limit = int(resume_page), int(resume_limit or limit)
        limit = min(limit, want - len(jobs))
        band_kept = (page - 1) * limit  # jobs of this band already fetched by an earlier run
        while len(jobs) < want:
            st, res, hdr = request(f"{API}/search", {**body, "company_types": [band], "page": page,
                                                     "limit": limit}, auth)
            if st != 200:
                failed = (band, page, limit, st, str(res)[:300])
                break
            if hdr.get("Hirebase-Usage-Included-Remaining") is not None:
                remaining = int(float(hdr["Hirebase-Usage-Included-Remaining"]))
            period_end = hdr.get("Hirebase-Usage-Period-End", period_end)
            batch = res.get("jobs", [])
            units += len(batch)
            later = False
            for j in batch:
                if (j.get("date_posted") or "") > day:
                    later = True   # sorted oldest first: everything after this is a later day
                    break
                band_kept += 1
                if j.get("_id") not in seen:
                    seen.add(j.get("_id"))
                    jobs.append(j)
            print(f"  {band} page {page}: {len(batch)} returned, {len(jobs)} kept so far", flush=True)
            time.sleep(HIREBASE_PAUSE)
            if later or page >= (res.get("total_pages") or 0) or not batch or (n and band_kept >= n):
                break
            page += 1
        if failed:
            break
    jobs = jobs[:want]
    print(f"fetched {len(jobs)} jobs dated {day} ({units} Hirebase units used)"
          + (f"; skipped for quota: {', '.join(skipped)}" if skipped else ""))

    os.makedirs(args.out_dir, exist_ok=True)
    saved = os.path.join(args.out_dir, f"hirebase-{day}-{fetched_at.replace(':', '')}.json")
    json.dump(jobs, open(saved, "w"))
    print(f"saved run file: {saved}")

    if failed:
        # Jobs already fetched were paid for: post them, then resume from the failed page only.
        band, page, limit, st, res = failed
        print(f"search failed at {band} page {page}: HTTP {st} {res}", file=sys.stderr)
        print(f"after fixing the cause, finish with: run.sh --live --date {day} --resume {band}:{page}:{limit}",
              file=sys.stderr)
    post_to_clay(jobs, fetched_at, remaining)
    if failed:
        sys.exit(1)


def post_to_clay(jobs, fetched_at, remaining):
    hook = os.environ.get("CLAY_HIREBASE_WEBHOOK_URL")
    if not hook:
        sys.exit("CLAY_HIREBASE_WEBHOOK_URL not set")
    ok, failed, unposted = 0, [], []
    for i, j in enumerate(jobs, 1):
        try:
            st, res, _ = request(hook, flatten(j, fetched_at))
        except Exception as e:  # never let one job stop the run
            st, res = None, repr(e)
        if st and 200 <= st < 300:
            ok += 1
        else:
            failed.append((j.get("_id"), st, str(res)[:200]))
            unposted.append(j)
        if i % 100 == 0:
            print(f"  posted {i}/{len(jobs)}", flush=True)
        time.sleep(CLAY_PAUSE)

    print(f"posted to Clay: {ok}/{len(jobs)}")
    if remaining is not None:
        print(f"Hirebase allowance remaining: {remaining}")
    for f in failed[:20]:
        print(f"  FAILED {f}", file=sys.stderr)
    if failed:
        out = os.path.join(os.environ.get("TMPDIR", "/tmp"), f"hirebase-unposted-{fetched_at.replace(':', '')}.json")
        json.dump(unposted, open(out, "w"))
        print(f"{len(unposted)} job(s) not posted; retry with: run.sh --live --resend {out}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
