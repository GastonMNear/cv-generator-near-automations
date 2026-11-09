#!/usr/bin/env python3
"""Scan every non-DRAFTED campaign's /statistics for leads currently tagged 'Meeting Booked'.

Authoritative discovery of who booked — no need to guess company domains.
"""
import json, os, subprocess, sys, threading, time
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed

API = os.environ["SMARTLEAD_API_KEY"]
BASE = "https://server.smartlead.ai/api/v1"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "booked_rows.json")
MAX_PER_MIN = 170

_lock, _stamps = threading.Lock(), deque()
def _throttle():
    while True:
        with _lock:
            now = time.monotonic()
            while _stamps and now - _stamps[0] > 60: _stamps.popleft()
            if len(_stamps) < MAX_PER_MIN:
                _stamps.append(now); return
            wait = 60 - (now - _stamps[0]) + 0.05
        time.sleep(wait)

def curl_json(path, tries=6):
    sep = "&" if "?" in path else "?"
    url = f"{BASE}{path}{sep}api_key={API}"
    for a in range(tries):
        _throttle()
        out = subprocess.run(["curl", "-s", "--max-time", "60", url],
                             capture_output=True, text=True).stdout
        if "rate limit" in out.lower():
            time.sleep(15); continue
        try: r = json.loads(out)
        except Exception:
            time.sleep(3 * (a + 1)); continue
        if isinstance(r, str):
            time.sleep(3); continue
        return r
    return None

camps = curl_json("/campaigns/")
if not isinstance(camps, list): sys.exit(f"campaigns failed: {str(camps)[:200]}")
scan = [c for c in camps if c.get("status") != "DRAFTED"]
print(f"campaigns={len(camps)} scanning={len(scan)}", flush=True)

done_n = [0]
def scan_campaign(c):
    cid, found, offset = c["id"], [], 0
    while True:
        d = curl_json(f"/campaigns/{cid}/statistics?offset={offset}&limit=1000")
        if not d or "data" not in d: break
        rows = d["data"]
        total = int(d.get("total_stats", 0) or 0)
        for r in rows:
            if r.get("lead_category") == "Meeting Booked":
                found.append({
                    "campaign_id": cid, "campaign_name": c.get("name"),
                    "lead_email": r.get("lead_email"), "lead_name": r.get("lead_name"),
                    "reply_time": r.get("reply_time"), "sent_time": r.get("sent_time"),
                })
        offset += len(rows)
        if not rows or offset >= total: break
    done_n[0] += 1
    if done_n[0] % 20 == 0: print(f"  {done_n[0]}/{len(scan)} campaigns", flush=True)
    return found

allrows = []
with ThreadPoolExecutor(max_workers=8) as ex:
    for fut in as_completed([ex.submit(scan_campaign, c) for c in scan]):
        allrows.extend(fut.result())

json.dump(allrows, open(OUT, "w"), indent=1)
emails = {r["lead_email"] for r in allrows}
print(f"DONE: {len(allrows)} Meeting-Booked rows, {len(emails)} unique leads -> {OUT}")
