#!/usr/bin/env python3
"""Step 3 — the set of everyone in Smartlead currently tagged 'Meeting Booked'.

Why this exists at all: Smartlead has no company-level lead search. `/leads/?email=`
takes an exact address and nothing else, so when the address HubSpot recorded is not
the address we emailed, the only way back to the lead is to search a population.

The population to search is NOT all ~215k leads. That was tried and it failed on
exactly the cases it was needed for — 'Purpose' matched six unrelated companies,
'cactus' 23, 'usad' 25, with nothing to choose between them. The set of people who
actually booked is ~318 account-wide, so ambiguity mostly evaporates: there is
exactly one booked lead at purpose.app.

Cost is ~1,400 requests / ~7 minutes and is FLAT — it costs the same for 5 bookings
as for 50. That's why attribute.py only triggers it when direct lookups leave
something unresolved.

Usage:
    python3 scan_booked_leads.py --out booked_leads.json
Env: SMARTLEAD_API_KEY
"""
import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

from common import dump_json, smartlead

BOOKED_CATEGORY = "Meeting Booked"


def booked_category_id():
    """Resolve the tag id live. It was 101822 on 2026-09-01, but the account adds
    custom categories over time and a hardcoded id fails silently — it just returns
    an empty set, which reads as 'nobody booked' rather than as an error."""
    cats = smartlead("/leads/fetch-categories") or []
    for c in cats if isinstance(cats, list) else []:
        if (c.get("name") or "").strip().lower() == BOOKED_CATEGORY.lower():
            return c.get("id")
    return None


def live_campaigns():
    """DRAFTED campaigns never sent, so they hold no replies and no tags."""
    camps = smartlead("/campaigns/") or []
    if not isinstance(camps, list):
        sys.exit(f"ERROR: unexpected /campaigns/ response: {str(camps)[:200]}")
    return [c for c in camps if (c.get("status") or "").upper() != "DRAFTED"]


def scan_campaign(cid):
    """Every 'Meeting Booked' row in one campaign's statistics."""
    found, offset = [], 0
    while True:
        page = smartlead(f"/campaigns/{cid}/statistics?offset={offset}&limit=1000")
        if not isinstance(page, dict):
            break
        rows = page.get("data") or []
        for r in rows:
            if (r.get("lead_category") or "").strip() == BOOKED_CATEGORY:
                found.append({
                    "campaign_id": cid,
                    "email": (r.get("lead_email") or "").strip().lower(),
                    "name": (r.get("lead_name") or "").strip(),
                    "reply_time": r.get("reply_time"),
                })
        offset += len(rows)
        # total_stats comes back as a STRING on some campaigns — cast before compare.
        try:
            total = int(page.get("total_stats") or 0)
        except (TypeError, ValueError):
            total = 0
        if not rows or offset >= total:
            break
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="booked_leads.json")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()

    cat_id = booked_category_id()
    camps = live_campaigns()
    print(f"[smartlead] '{BOOKED_CATEGORY}' = id {cat_id}; "
          f"scanning {len(camps)} non-DRAFTED campaign(s)…", file=sys.stderr)

    rows, done = [], 0
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        futs = {pool.submit(scan_campaign, c["id"]): c["id"] for c in camps}
        for f in as_completed(futs):
            try:
                rows += f.result()
            except Exception as e:                       # one bad campaign != a dead run
                print(f"[smartlead] campaign {futs[f]} failed: {e}", file=sys.stderr)
            done += 1
            if done % 25 == 0:
                print(f"[smartlead]   {done}/{len(camps)} campaigns, "
                      f"{len(rows)} booked rows", file=sys.stderr)

    # One record per person, remembering every campaign they're booked in.
    leads = {}
    for r in rows:
        if not r["email"]:
            continue
        rec = leads.setdefault(r["email"], {"email": r["email"], "name": r["name"],
                                            "campaign_ids": [], "reply_time": None})
        rec["campaign_ids"].append(r["campaign_id"])
        if r["name"] and not rec["name"]:
            rec["name"] = r["name"]
        # earliest reply_time is only a sort key — it is A reply, not the FIRST one
        if r["reply_time"] and (not rec["reply_time"]
                                or r["reply_time"] < rec["reply_time"]):
            rec["reply_time"] = r["reply_time"]

    dump_json(a.out, {"category_id": cat_id, "campaigns_scanned": len(camps),
                      "rows": len(rows), "leads": sorted(leads.values(),
                                                         key=lambda x: x["email"])})
    print(f"[smartlead] {len(rows)} booked rows / {len(leads)} unique leads "
          f"-> {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
