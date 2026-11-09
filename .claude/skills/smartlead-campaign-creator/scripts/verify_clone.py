#!/usr/bin/env python3
"""Read-only diff of cloned campaigns vs their source and vs each other.

Usage: python3 verify_clone.py <source_id> <clone_id> [<clone_id> ...]
Waits WAIT seconds first (default 30) because Smartlead writes are eventually consistent.
Expected residual differences after clone_campaign.py: out_of_office_detection_settings
(UI-only combo), follow_up_subject auto-filled on in-thread steps, ignore_ss_mailbox_sending_limit
null vs false. Anything else is a problem.
"""
import json, os, subprocess, sys, time

BASE = "https://server.smartlead.ai/api/v1"
KEY = os.environ.get("SMARTLEAD_API_KEY")
if not KEY:
    d = os.path.dirname(os.path.abspath(__file__))
    while d != "/" and not KEY:
        p = os.path.join(d, ".env")
        if os.path.exists(p):
            for line in open(p):
                if line.startswith("SMARTLEAD_API_KEY="):
                    KEY = line.split("=", 1)[1].strip().strip("'\"")
        d = os.path.dirname(d)
time.sleep(int(os.environ.get("WAIT", "30")))


def get(path):
    out = subprocess.run(["curl", "-s", f"{BASE}{path}?api_key={KEY}"], capture_output=True, text=True, timeout=120)
    return json.loads(out.stdout, strict=False)


def snap(cid):
    c = get(f"/campaigns/{cid}")
    s = sorted(get(f"/campaigns/{cid}/sequences"), key=lambda x: x["seq_number"])
    a = sorted(x["id"] for x in get(f"/campaigns/{cid}/email-accounts"))
    leads = get(f"/campaigns/{cid}/analytics").get("campaign_lead_stats", {}).get("total")
    return c, s, a, leads


SKIP = {"id", "name", "created_at", "updated_at", "status", "schedule_start_time", "parent_campaign_id"}
ids = sys.argv[1:]
snaps = {i: snap(i) for i in ids}
steps = lambda q: [(x["seq_number"], x["seq_delay_details"].get("delayInDays"), x.get("subject"), x.get("email_body"), x.get("sequence_variants")) for x in q]
for i in ids:
    c, s, a, leads = snaps[i]
    print(f"\n== {i} | {c['name']!r} | {c['status']} | start {c.get('schedule_start_time')} | leads {leads} | inboxes {len(a)} | steps {len(s)}")
    for j in ids[:ids.index(i)]:
        cj, sj, aj, _ = snaps[j]
        d = [k for k in sorted(set(c) | set(cj)) if k not in SKIP and c.get(k) != cj.get(k)]
        fu = [x["seq_number"] for x in s if x.get("follow_up_subject") != next((y.get("follow_up_subject") for y in sj if y["seq_number"] == x["seq_number"]), None)]
        print(f"   vs {j}: settings diffs {d or 'none'} | steps identical {steps(s) == steps(sj)} | follow_up_subject differs on {fu or 'none'} | inboxes identical {a == aj}")
