#!/usr/bin/env python3
"""Smartlead weekly response-time KPI.

Measures how long it takes us to reply to positive replies, in BUSINESS HOURS
(Mon-Fri 09:00-18:00 America/New_York), over a Mon-Sun week.

Pipeline (efficient by design — never pulls conversations we don't need):
  1. Cheap scan: one `statistics` call per campaign gives reply_time + lead_category
     + email. Filter in memory to replies that landed in the week AND whose category
     has positive sentiment. Nothing else is downloaded in this step.
  2. Only for those leads: resolve lead_id and pull message-history, then find the
     positive reply and OUR next outbound (type SENT) after it -> response time.

Transport is `curl` (Smartlead blocks python-requests with a Cloudflare 403).
All requests go through a global rate limiter (Smartlead caps at 200 req/min).

Usage:
  python run_weekly_kpi.py                 # previous full week (Mon-Sun), auto from today ET
  python run_weekly_kpi.py 2026-07-13      # the week starting this Monday (Mon-Sun)
  python run_weekly_kpi.py 2026-07-13 2026-07-19

Env: SMARTLEAD_API_KEY (required)
Output: writes kpi_output.json next to this script and prints a short summary.
"""
import subprocess, json, os, sys, time, threading
from collections import deque
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from concurrent.futures import ThreadPoolExecutor, as_completed

API = os.environ.get("SMARTLEAD_API_KEY")
if not API:
    sys.exit("ERROR: SMARTLEAD_API_KEY not set")

BASE = "https://server.smartlead.ai/api/v1"
ET = ZoneInfo("America/New_York")
OFFICE_OPEN, OFFICE_CLOSE = 9, 18          # business hours, ET, Mon-Fri (09:00-18:00)
POSITIVE_ONLY = True                         # keep only sentiment_type == "positive"
MAX_PER_MIN = 175                            # stay safely under the 200/min hard cap
HERE = os.path.dirname(os.path.abspath(__file__))

# ---- global rate limiter (thread-safe) -------------------------------------
_lock = threading.Lock()
_stamps = deque()
def _throttle():
    while True:
        with _lock:
            now = time.monotonic()
            while _stamps and now - _stamps[0] > 60:
                _stamps.popleft()
            if len(_stamps) < MAX_PER_MIN:
                _stamps.append(now)
                return
            wait = 60 - (now - _stamps[0]) + 0.05
        time.sleep(wait)

def curl_json(path, tries=6):
    sep = "&" if "?" in path else "?"
    url = f"{BASE}{path}{sep}api_key={API}"
    for _ in range(tries):
        _throttle()
        out = subprocess.run(["curl", "-s", "--max-time", "45", url],
                             capture_output=True, text=True).stdout
        if "rate limit" in out.lower():
            time.sleep(15)
            continue
        try:
            r = json.loads(out)
            if isinstance(r, str):   # bare-string response = transient API error, retry
                time.sleep(3)
                continue
            return r
        except Exception:
            time.sleep(3)
    return None

# ---- time helpers -----------------------------------------------------------
def parse_ts(s):
    if not s:
        return None
    s = s.replace("Z", "+0000")
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            pass
    return None

def to_et(dt):
    return dt.astimezone(ET)

def business_hours(start_et, end_et):
    """Elapsed business hours (Mon-Fri OFFICE_OPEN-OFFICE_CLOSE ET) between two ET datetimes.
    A reply that lands outside office hours effectively starts counting at the next open."""
    if not start_et or not end_et or end_et <= start_et:
        return 0.0
    total = 0.0
    cur = start_et
    while cur < end_et:
        if cur.weekday() < 5:  # Mon-Fri
            day_open = cur.replace(hour=OFFICE_OPEN, minute=0, second=0, microsecond=0)
            day_close = cur.replace(hour=OFFICE_CLOSE, minute=0, second=0, microsecond=0)
            s = max(cur, day_open)
            e = min(end_et, day_close)
            if e > s:
                total += (e - s).total_seconds()
        cur = (cur + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return round(total / 3600, 2)

def resolve_period(argv):
    """Return (start_et, end_et_exclusive, label).
    --daily      = the previous day. Run Mon-Fri, so on Monday it covers the whole prior
                   weekend (Fri+Sat+Sun) — that way no business day slips past the daily report.
    two dates    = explicit inclusive range (YYYY-MM-DD YYYY-MM-DD), for backfills/testing.
    one date     = the Mon-Sun week starting that Monday.
    no args      = the previous full Mon-Sun week (the weekly default)."""
    args = argv[1:]
    dates = [a for a in args if not a.startswith("-")]
    if "--daily" in args:
        today = datetime.now(ET).replace(hour=0, minute=0, second=0, microsecond=0)
        back = 3 if today.weekday() == 0 else 1   # Monday reaches back to Friday
        start, end = today - timedelta(days=back), today
    elif len(dates) >= 2:
        start = datetime.strptime(dates[0], "%Y-%m-%d").replace(tzinfo=ET)
        end = datetime.strptime(dates[1], "%Y-%m-%d").replace(tzinfo=ET) + timedelta(days=1)
    elif len(dates) == 1:
        start = datetime.strptime(dates[0], "%Y-%m-%d").replace(tzinfo=ET)
        end = start + timedelta(days=7)
    else:
        now = datetime.now(ET)
        this_mon = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        start, end = this_mon - timedelta(days=7), this_mon
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    last = end - timedelta(days=1)
    if start.date() == last.date():
        label = start.strftime("%a %b %d, %Y")                       # single day
    else:
        label = f"{start.strftime('%b %d')} – {last.strftime('%b %d, %Y')}"
    return start, end, label

# ---- pipeline ---------------------------------------------------------------
def main():
    start_et, end_et, label = resolve_period(sys.argv)
    print(f"Period (ET): {label}")

    cats = curl_json("/leads/fetch-categories")
    if not isinstance(cats, list):
        sys.exit(f"ERROR: fetch-categories did not return a list — check SMARTLEAD_API_KEY. API said: {cats}")
    positive = {c["name"] for c in cats if isinstance(c, dict) and c.get("sentiment_type") == "positive"}
    print("positive categories:", sorted(positive))

    camps = curl_json("/campaigns/")
    if not isinstance(camps, list):
        sys.exit(f"ERROR: campaigns did not return a list — check SMARTLEAD_API_KEY. API said: {camps}")
    scan = [c for c in camps if c.get("status") != "DRAFTED"]  # DRAFTED never sent
    print(f"campaigns={len(camps)} | scanning={len(scan)}")

    def scan_campaign(c):
        cid, found, offset = c["id"], [], 0
        while True:
            d = curl_json(f"/campaigns/{cid}/statistics?offset={offset}&limit=1000")
            if not d or "data" not in d:
                break
            rows = d["data"]
            total = int(d.get("total_stats", 0) or 0)
            for r in rows:
                rt = parse_ts(r.get("reply_time"))
                if not rt:
                    continue
                rt_et = to_et(rt)
                if not (start_et <= rt_et < end_et):
                    continue
                if POSITIVE_ONLY and r.get("lead_category") not in positive:
                    continue
                found.append({
                    "campaign_id": cid, "campaign_name": c.get("name"),
                    "lead_email": r.get("lead_email"), "lead_name": r.get("lead_name"),
                    "lead_category": r.get("lead_category"),
                    "reply_time_utc": r.get("reply_time"),
                })
            offset += len(rows)
            if offset >= total or not rows:
                break
        return found

    matches = []
    with ThreadPoolExecutor(max_workers=10) as ex:
        for fut in as_completed([ex.submit(scan_campaign, c) for c in scan]):
            matches.extend(fut.result())

    # dedupe by (campaign, lead): keep earliest positive reply in the window
    best = {}
    for m in matches:
        k = (m["campaign_id"], m["lead_email"])
        if k not in best or m["reply_time_utc"] < best[k]["reply_time_utc"]:
            best[k] = m
    leads = list(best.values())
    print(f"positive replies in window: {len(leads)} unique leads")

    def measure(m):
        lead = curl_json(f"/leads/?email={m['lead_email']}")
        if not isinstance(lead, dict) or "id" not in lead:
            return {**m, "error": "lead_id not found"}
        lid = lead["id"]
        d = curl_json(f"/campaigns/{m['campaign_id']}/leads/{lid}/message-history")
        hist = d.get("history") if isinstance(d, dict) else d
        if not hist:
            return {**m, "lead_id": lid, "error": "no history"}
        msgs = []
        for x in hist:
            t = parse_ts(x.get("time"))
            if t:
                msgs.append((t, (x.get("type") or "").upper()))
        msgs.sort(key=lambda z: z[0])
        reply_dt = parse_ts(m["reply_time_utc"])
        inbound = [mm for mm in msgs if mm[1] == "REPLY"]
        pos = min(inbound, key=lambda z: abs((z[0] - reply_dt).total_seconds()), default=None)
        if not pos:
            return {**m, "lead_id": lid, "error": "reply not in history"}
        after = [mm for mm in msgs if mm[1] == "SENT" and mm[0] > pos[0]]
        our = min(after, key=lambda z: z[0], default=None)
        rec = {
            "campaign_id": m["campaign_id"], "campaign_name": m["campaign_name"],
            "lead_email": m["lead_email"], "lead_name": m["lead_name"],
            "lead_category": m["lead_category"], "lead_id": lid,
            "positive_reply_at_et": to_et(pos[0]).strftime("%a %m-%d %H:%M"),
            "our_reply_at_et": to_et(our[0]).strftime("%a %m-%d %H:%M") if our else None,
            "response_business_hours": business_hours(to_et(pos[0]), to_et(our[0])) if our else None,
            "response_raw_hours": round((our[0] - pos[0]).total_seconds() / 3600, 2) if our else None,
            # real wall-clock speed flags (how often we jumped on it in N real minutes)
            "under_5min": ((our[0] - pos[0]).total_seconds() < 300) if our else None,
            "under_10min": ((our[0] - pos[0]).total_seconds() < 600) if our else None,
        }
        return rec

    results = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        for fut in as_completed([ex.submit(measure, m) for m in leads]):
            results.append(fut.result())

    done = [r for r in results if "error" not in r]
    answered = [r for r in done if r["response_business_hours"] is not None]
    pending = [r for r in done if r["response_business_hours"] is None]
    errors = [r for r in results if "error" in r]

    def med(v):
        v = sorted(v)
        n = len(v)
        return None if n == 0 else (v[n // 2] if n % 2 else round((v[n // 2 - 1] + v[n // 2]) / 2, 2))

    biz = [r["response_business_hours"] for r in answered]
    raw = [r["response_raw_hours"] for r in answered]
    under5 = [r for r in answered if r.get("under_5min")]
    under10 = [r for r in answered if r.get("under_10min")]
    summary = {
        "period_label": label,
        "period_start": start_et.date().isoformat(),
        "period_end": (end_et - timedelta(days=1)).date().isoformat(),
        "positive_replies": len(done),
        "answered": len(answered),
        "pending": len(pending),
        "errors": len(errors),
        "biz_avg_h": round(sum(biz) / len(biz), 2) if biz else None,
        "biz_median_h": med(biz),
        "biz_min_h": min(biz) if biz else None,
        "biz_max_h": max(biz) if biz else None,
        "raw_avg_h": round(sum(raw) / len(raw), 2) if raw else None,
        "raw_median_h": med(raw),
        "under_5min_count": len(under5),
        "pct_under_5min": round(len(under5) / len(answered) * 100, 1) if answered else None,
        "under_10min_count": len(under10),
        "pct_under_10min": round(len(under10) / len(answered) * 100, 1) if answered else None,
    }

    # per-category breakdown (business hours)
    cat_break = {}
    for cat in sorted({r["lead_category"] for r in done}):
        grp = [r["response_business_hours"] for r in answered if r["lead_category"] == cat]
        cat_break[cat] = {
            "count": sum(1 for r in done if r["lead_category"] == cat),
            "answered": len(grp),
            "avg_h": round(sum(grp) / len(grp), 2) if grp else None,
            "median_h": med(grp),
        }

    out = {
        "generated_at_utc": subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
                                            capture_output=True, text=True).stdout.strip(),
        "summary": summary,
        "category_breakdown": cat_break,
        "leads": sorted(done, key=lambda r: (r["response_business_hours"] is None,
                                             r["response_business_hours"] or 0)),
        "errors": errors,
    }
    with open(os.path.join(HERE, "kpi_output.json"), "w") as f:
        json.dump(out, f, indent=2)

    print(json.dumps(summary, indent=2))
    print(f"\nwrote {os.path.join(HERE, 'kpi_output.json')}")

if __name__ == "__main__":
    main()
