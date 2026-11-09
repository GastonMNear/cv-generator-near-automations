#!/usr/bin/env python3
"""First reply per booked lead across ALL its campaigns -> same-week vs prev-week,
for the 6 weeks 2026-07-06 .. 2026-08-16."""
import json, os, subprocess, sys, threading, time
from collections import deque
from datetime import datetime
from zoneinfo import ZoneInfo
from concurrent.futures import ThreadPoolExecutor, as_completed

API = os.environ["SMARTLEAD_API_KEY"]
BASE = "https://server.smartlead.ai/api/v1"
ET = ZoneInfo("America/New_York")
BOOKED = 101822
MAX_PER_MIN = 170

ROSTER = [
 ("2026-08-10", [
   ("Aventiqo", "anuragp@aventiqo.com"), ("Produck", "yuv.bindal@tryproduck.com"),
   ("Batera", "carnolds@batera.ai"), ("Heatso", "as@heatso.com"),
   ("PAS Agency", "ruben@pasagency.com"), ("Zynq", "hemanth@zynq.io"),
   ("Krece", "jonathan@krece.app")]),
 ("2026-08-03", [
   ("Scale Club", "jake@scaleclub.com"), ("LotusGroup Advisors", "amanda@lgadvisors.com"),
   ("Live Forever Golf", "sriley@liveforevergolf.com"),
   ("Keresech Holdings", "gideon@keresech.com"), ("CareComply", "shen@carecomply.ai")]),
 ("2026-07-27", [
   ("Canela Media", "ileana.cordova@canelamedia.com"), ("Dwell", "viviana@dwell-escape.com"),
   ("onors", "patrick@onors.shop"), ("Kaged", "connor@kaged.com"),
   ("GSC Outsourcing", "gautam@gscoutsourcing.com"), ("iSourcify", "frank.vassaux@isourcify.com"),
   ("Raven Performance", "sophie@ravenperformance.co"), ("Clover Labs", "saad.mehdaoui@cloverlabs.ai"),
   ("City of Yellowknife", "bsleem@yellowknife.ca"), ("Windsor Drake", "jeff.barrington@windsordrake.com")]),
 ("2026-07-20", [
   ("Lindsey Self Storage Group", "john@lindseyselfstoragegroup.com"),
   ("WebForce / Phone Sales Team", "jrodriguez@webforcehq.com"),
   ("SERVPRO", "cdoyle@servprowesternlehighcounty.com"),
   ("Field Engine Wildlife", "vickie.denicola@fieldengine.com"), ("Mubite", "gertil@mubite.com"),
   ("Vimerson", "pablo@vimerson.com"), ("AstroZon", "sajid@astrozon.us"),
   ("Voicing AI", "stamayo@voicing.ai"), ("RISE Research", "yash@riseglobaleducation.com"),
   ("Maxim Group", "jsardo@maximgrp.com"), ("AfterShip", "chris.schmicker@aftership.com"),
   ("Innovative Seed Solutions", "djoy.eysink@innovativeseedsolutions.com")]),
 ("2026-07-13", [
   ("Revryze", "cwarner@revryze.com"), ("Intrinsic Firm", "spowers@intrinsicfirm.com"),
   ("The Sales Process Co", "brian.hayes@thesalesprocessco.com"),
   ("PGS Gold And Coin", "aaron.r@pgsgoldandcoin.com"), ("Autopublicacion", "john@autopublicacion.com")]),
 ("2026-07-06", [
   ("Safeguard", "hritik@safeguard.sh"), ("Lime Technology", "candice@unraid.net"),
   ("Levers", "johnmark@levers.health"), ("Telemedic", "cponce@tele-medic.net"),
   ("BDC United", "joseph@bdcunited.com"), ("Shram Logistics", "mathena@shramlogistics.com"),
   ("Rex Developments", "mahmad@rexmediausa.com"), ("BDigital", "ben@bdigitalco.com"),
   ("Rosy Finch", "jessica@rosyfinchmc.com"), ("Panelized Cladding Systems", "uciel@panelclad.us")]),
]

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
        if "rate limit" in out.lower(): time.sleep(15); continue
        try: r = json.loads(out)
        except Exception: time.sleep(2 * (a + 1)); continue
        if isinstance(r, str): time.sleep(3); continue
        return r
    return None

def parse_ts(s):
    if not s: return None
    s = s.replace("Z", "+0000")
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z"):
        try: return datetime.strptime(s, fmt)
        except Exception: pass
    return None

def measure(week_start, company, email):
    wk = datetime.strptime(week_start, "%Y-%m-%d").replace(tzinfo=ET)
    lead = curl_json(f"/leads/?email={email}")
    if not isinstance(lead, dict) or "id" not in lead:
        return {"week_start": week_start, "company": company, "email": email, "error": "lead not found"}
    lid = lead["id"]
    replies, camps, booked_anywhere = [], [], False
    for c in lead.get("lead_campaign_data") or []:
        cid = c.get("campaign_id")
        if c.get("lead_category_id") == BOOKED: booked_anywhere = True
        d = curl_json(f"/campaigns/{cid}/leads/{lid}/message-history")
        hist = d.get("history") if isinstance(d, dict) else d
        cr = [t for t in (parse_ts(m.get("time")) for m in (hist or [])
              if (m.get("type") or "").upper() == "REPLY") if t]
        replies += cr
        camps.append({"campaign_id": cid, "category_id": c.get("lead_category_id"),
                      "n_replies": len(cr),
                      "first_reply": min(cr).isoformat() if cr else None})
    first = min(replies) if replies else None
    fet = first.astimezone(ET) if first else None
    return {"week_start": week_start, "company": company, "email": email, "lead_id": lid,
            "lead_name": f"{lead.get('first_name') or ''} {lead.get('last_name') or ''}".strip(),
            "sl_company_name": lead.get("company_name"), "company_url": lead.get("company_url"),
            "booked_tag": booked_anywhere, "n_campaigns": len(camps), "total_replies": len(replies),
            "first_reply_et": fet.strftime("%a %Y-%m-%d %H:%M") if fet else None,
            "first_reply_iso": first.isoformat() if first else None,
            "bucket": (None if not fet else "SAME" if fet >= wk else "PREV"),
            "campaigns": camps}

jobs = [(ws, c, e) for ws, comps in ROSTER for c, e in comps]
results = []
with ThreadPoolExecutor(max_workers=6) as ex:
    futs = {ex.submit(measure, *j): j for j in jobs}
    for f in as_completed(futs):
        results.append(f.result())

results.sort(key=lambda r: (r["week_start"], r["first_reply_iso"] or ""), reverse=True)
json.dump(results, open("results8.json", "w"), indent=1)

errs = [r for r in results if r.get("error") or not r.get("first_reply_et")]
print(f"measured={len(results)}  problems={len(errs)}")
for ws, comps in ROSTER:
    grp = [r for r in results if r["week_start"] == ws]
    same = [r for r in grp if r.get("bucket") == "SAME"]
    prev = [r for r in grp if r.get("bucket") == "PREV"]
    print(f"\n===== week starting {ws} =====  SAME={len(same)} PREV={len(prev)} of {len(grp)}")
    for r in sorted(grp, key=lambda r: r.get("first_reply_iso") or ""):
        tag = "" if r.get("booked_tag") else "  [no MB tag]"
        print(f"  {r.get('bucket') or '??':5} | {r['company']:28} | {r.get('first_reply_et') or 'NO REPLY':22}"
              f" | {r.get('lead_name','')[:22]:22} | SL={str(r.get('sl_company_name'))[:22]:22}{tag}")
if errs:
    print("\nPROBLEMS:", [(r['company'], r.get('error')) for r in errs])
