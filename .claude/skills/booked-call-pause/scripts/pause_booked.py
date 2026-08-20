#!/usr/bin/env python3
"""Pause Smartlead sequences for every lead at a company that just booked a call.

Runs twice a day (09:00 + 13:30 ET). ONE crawl per run serves the whole batch of
bookings in the window — N bookings cost the same crawl as one. Stateless: the lead
index is built in memory and discarded, so a fresh cloud checkout needs no setup and
no lead PII is written to disk.

Per booking: resolve company keys -> look up leads in the local index
(domain -> company LinkedIn -> email) -> for each matched lead ask
`/leads/{id}/campaigns` which campaigns it's in -> pause it in the ACTIVE ones.

Only campaigns with status ACTIVE are touched: pausing a lead inside a DRAFTED or
COMPLETED campaign changes nothing and just burns requests.

Usage:
    python3 pause_booked.py --bookings bookings.json            # DRY RUN (default)
    python3 pause_booked.py --bookings bookings.json --live     # actually pause
    python3 pause_booked.py --domain acme.com                   # ad-hoc single company

bookings.json: [{"company_domain": "...", "company_linkedin": "...",
                 "email": "...", "company_name": "...", "booked_at": "..."}]
Env: SMARTLEAD_API_KEY
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lead_index as idx   # noqa: E402  (shares throttle, curl, schema, lookup)

def active_campaigns_for(lead_id):
    """GET /leads/{id}/campaigns -> the campaigns this lead sits in, with status.

    This is what makes the whole thing cheap: without it we'd have to scan all 70
    active campaigns (12.5k leads each) to find where a lead is running.
    """
    r = idx.curl_json(f"/leads/{lead_id}/campaigns")
    if isinstance(r, dict):
        r = r.get("data") or []
    if not isinstance(r, list):
        return []
    return [c for c in r if str(c.get("status", "")).upper() == "ACTIVE"]


def pause(campaign_id, lead_id):
    """POST .../pause -> {"ok":true,"data":"success"}. Reversible via .../resume."""
    url = (f"{idx.BASE}/campaigns/{campaign_id}/leads/{lead_id}/pause"
           f"?api_key={idx.API}")
    import subprocess
    for attempt in range(4):
        idx._throttle()
        out = subprocess.run(
            ["curl", "-s", "-X", "POST", "--max-time", "45", url],
            capture_output=True, text=True,
        ).stdout
        try:
            r = json.loads(out)
            if r.get("ok"):
                return True, "paused"
            return False, str(r)[:160]
        except Exception:
            time.sleep(2 * (attempt + 1))
    return False, "no valid response after retries"


def process_booking(booking, index, live, budget):
    domain = booking.get("company_domain")
    linkedin = booking.get("company_linkedin")
    email = booking.get("email")

    matched_by, rows = index.lookup(
        domain=domain, linkedin=linkedin, email=email
    )

    result = {
        "company": booking.get("company_name") or domain or email,
        "company_domain": idx.norm_domain(domain),
        "booked_email": idx.norm_email(email),
        "booked_at": booking.get("booked_at"),
        "matched_by": matched_by,
        "leads_matched": len(rows),
        "paused": [],
        "not_in_active_campaign": [],
        "errors": [],
    }
    if not rows:
        return result

    for rec in rows:
        lead_id, lead_email = rec["lead_id"], rec["email"]
        if budget["left"] <= 0:
            result["errors"].append(
                {"email": lead_email,
                 "error": "per-run pause cap reached — rerun to continue"})
            break
        camps = active_campaigns_for(lead_id)
        if not camps:
            result["not_in_active_campaign"].append(lead_email or lead_id)
            continue
        for c in camps:
            entry = {
                "lead_id": lead_id,
                "email": lead_email,
                "campaign_id": c.get("id"),
                "campaign": c.get("name"),
            }
            if live:
                ok, detail = pause(c["id"], lead_id)
                if ok:
                    budget["left"] -= 1
                    result["paused"].append(entry)
                else:
                    result["errors"].append({**entry, "error": detail})
            else:
                budget["left"] -= 1
                result["paused"].append({**entry, "dry_run": True})
    return result


def render(results, live, sync_info):
    live_tag = "LIVE" if live else "DRY RUN — nothing was changed"
    lines = [f"*Booked-call auto-pause* — {live_tag}"]
    if sync_info:
        lines.append(
            f"_crawled {sync_info['stored']} leads in "
            f"{sync_info['requests']} requests_"
        )
    tot_p = tot_m = 0
    for r in results:
        tot_m += r["leads_matched"]
        tot_p += len(r["paused"])
        if not r["leads_matched"]:
            lines.append(
                f"\n• *{r['company']}* — no Smartlead leads found "
                f"(domain `{r['company_domain'] or '?'}`)"
            )
            continue
        lines.append(
            f"\n• *{r['company']}* — {r['leads_matched']} lead(s) "
            f"via `{r['matched_by']}`"
        )
        for p in r["paused"]:
            verb = "would pause" if p.get("dry_run") else "paused"
            lines.append(f"    ✅ {verb} {p['email']} — {p['campaign']}")
        for e in r["not_in_active_campaign"]:
            lines.append(f"    ➖ not in an active campaign: {e}")
        for e in r["errors"]:
            lines.append(f"    ⚠️ FAILED {e['email']} — {e['error']}")
    verb = "Paused" if live else "Would pause"
    lines.append(
        f"\n*{verb} {tot_p} lead(s)* across {len(results)} booking(s) "
        f"({tot_m} matched)."
    )
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bookings", help="JSON file: list of booking dicts")
    ap.add_argument("--domain", help="ad-hoc: single company domain")
    ap.add_argument("--email", help="ad-hoc: booked lead email")
    ap.add_argument("--linkedin", help="ad-hoc: company LinkedIn URL")
    ap.add_argument("--live", action="store_true",
                    help="actually pause (default is dry run)")
    ap.add_argument("--max-pauses", type=int, default=250,
                    help="safety cap on pauses per run (default 250)")
    ap.add_argument("--json-out", help="write the full result JSON here")
    a = ap.parse_args()

    if a.bookings:
        with open(a.bookings) as f:
            bookings = json.load(f)
    elif a.domain or a.email or a.linkedin:
        bookings = [{
            "company_domain": a.domain,
            "email": a.email,
            "company_linkedin": a.linkedin,
            "company_name": a.domain or a.email,
        }]
    else:
        sys.exit("ERROR: pass --bookings FILE or --domain/--email/--linkedin")

    # One crawl per run, shared by every booking in the batch.
    index = idx.build()
    if not index.complete:
        print("[pause] refusing to run LIVE on an incomplete crawl — "
              "a partial index would miss leads that should be paused",
              file=sys.stderr)
        if a.live:
            sys.exit(2)

    results = []
    budget = {"left": a.max_pauses}
    for b in bookings:
        results.append(process_booking(b, index, a.live, budget))

    sync_info = {"stored": index.count, "requests": index.requests}
    report = render(results, a.live, sync_info)
    print("\n" + report)

    if a.json_out:
        with open(a.json_out, "w") as f:
            json.dump({"live": a.live, "sync": sync_info, "results": results},
                      f, indent=2)
    return report


if __name__ == "__main__":
    main()
