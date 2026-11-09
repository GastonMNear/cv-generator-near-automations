"""Gate D: start campaigns created in THIS run, only on Gaston's explicit request.

  python3 start_campaigns.py --ids 111,222 --created-this-run 111,222 --approved-by "<Gaston's exact words>"

Refuses unless every ID: was created in this run (listed in --created-this-run, from the build log),
is DRAFTED or PAUSED, has > 0 leads, and has OOO handling set (ignore-as-reply on). Then POSTs START
and re-reads until ACTIVE. Run lead_check.py first; this script doesn't repeat it.
"""
import argparse, sys, time
from sl import call, get

ap = argparse.ArgumentParser()
ap.add_argument("--ids", required=True)
ap.add_argument("--created-this-run", required=True)
ap.add_argument("--approved-by", required=True)
a = ap.parse_args()
ids = [int(x) for x in a.ids.split(",")]
created = {int(x) for x in a.created_this_run.split(",")}
if not a.approved_by.strip():
    sys.exit("--approved-by must quote Gaston's request")

bad = []
for cid in ids:
    c = get(f"/campaigns/{cid}")
    an = get(f"/campaigns/{cid}/analytics")
    leads = (an.get("campaign_lead_stats") or {}).get("total") or 0
    ooo = (c.get("out_of_office_detection_settings") or {}).get("ignoreOOOasReply")
    why = [w for w, cond in [("not created this run", cid not in created), (f"status {c['status']}", c["status"] not in ("DRAFTED", "PAUSED")),
                              ("0 leads", leads == 0), ("OOO not set in the UI", not ooo)] if cond]
    print(cid, c["name"][:70], c["status"], "leads", leads, "OOO", ooo, "→", "BLOCKED: " + ", ".join(why) if why else "ok")
    if why:
        bad.append(cid)
if bad:
    sys.exit("nothing started")
for cid in ids:
    print(cid, "start:", call("POST", f"/campaigns/{cid}/status", {"status": "START"}))
time.sleep(10)
for cid in ids:
    print(cid, "now", get(f"/campaigns/{cid}")["status"])
