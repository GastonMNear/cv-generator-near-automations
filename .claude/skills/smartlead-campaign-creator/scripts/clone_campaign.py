#!/usr/bin/env python3
"""Clone an existing Smartlead campaign 1:1 into a NEW DRAFTED campaign (create-only).

Usage:
  python3 clone_campaign.py --source-id 3896110 --name "[EXP015] - Baseline | ..." [--start-date YYYY-MM-DD]
  python3 clone_campaign.py --source-id 3896110 --name "..." --campaign-id <id created earlier THIS run>  # repair

Reads the source (GET only) and copies: non-variant sequence steps (same delays, subjects,
bodies; the "Send Lead to Justcall" step as MANUAL), schedule (start = --start-date, default
today), settings (incl. add_unsubscribe_tag + ai_categorisation_options, which new campaigns
otherwise default differently), and the exact inbox list. Never writes to the source, never
calls /status. OOO detection and subsequences are NOT cloned (API limits). Report them.
Verified 2026-11-06 (EXP014: 4341415, 4341416 cloned from 3896110).
"""
import argparse, datetime, json, os, subprocess, sys, tempfile

BASE = "https://server.smartlead.ai/api/v1"
MANUAL_TITLES = {"Send Lead to Justcall", "Send lead to Clay"}
TRACK_MAP = {"DONT_EMAIL_OPEN": "DONT_TRACK_EMAIL_OPEN", "DONT_LINK_CLICK": "DONT_TRACK_LINK_CLICK"}


def load_key():
    if os.environ.get("SMARTLEAD_API_KEY"):
        return os.environ["SMARTLEAD_API_KEY"]
    d = os.path.dirname(os.path.abspath(__file__))
    while d != "/":
        p = os.path.join(d, ".env")
        if os.path.exists(p):
            for line in open(p):
                if line.startswith("SMARTLEAD_API_KEY="):
                    return line.split("=", 1)[1].strip().strip("'\"")
        d = os.path.dirname(d)
    sys.exit("SMARTLEAD_API_KEY not found")


KEY = load_key()


def call(method, path, body=None):
    cmd = ["curl", "-s", "-X", method, f"{BASE}{path}{'&' if '?' in path else '?'}api_key={KEY}", "-H", "Content-Type: application/json"]
    tmp = None
    if body is not None:
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        json.dump(body, tmp, ensure_ascii=False); tmp.close()
        cmd += ["--data-binary", f"@{tmp.name}"]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if tmp:
        os.unlink(tmp.name)
    try:
        return json.loads(out.stdout, strict=False)
    except Exception:
        sys.exit(f"non-JSON from {method} {path}: {out.stdout[:300]}")


def ok(r, step):
    if isinstance(r, dict) and (r.get("ok") is True or "id" in r):
        return r
    sys.exit(f"FAILED {step}: {json.dumps(r)[:400]}")


ap = argparse.ArgumentParser()
ap.add_argument("--source-id", type=int, required=True)
ap.add_argument("--name", required=True)
ap.add_argument("--start-date", default=datetime.date.today().isoformat())
ap.add_argument("--campaign-id", type=int, default=None)
a = ap.parse_args()
if a.campaign_id == a.source_id:
    sys.exit("refusing to write to the source campaign")

src = call("GET", f"/campaigns/{a.source_id}")
seqs = call("GET", f"/campaigns/{a.source_id}/sequences")
accts = call("GET", f"/campaigns/{a.source_id}/email-accounts")
if src.get("parent_campaign_id"):
    sys.exit("source is a subsequence; clone its parent")

steps = []
for s in sorted(seqs, key=lambda x: x["seq_number"]):
    if s.get("sequence_variants"):
        sys.exit("source has A/B variant steps; this cloner handles non-variant steps only (extend it, then propose the change)")
    st = {"seq_number": s["seq_number"], "seq_delay_details": {"delay_in_days": s["seq_delay_details"]["delayInDays"]},
          "subject": s.get("subject") or "", "email_body": s.get("email_body") or ""}
    st["seq_type"] = "MANUAL" if st["subject"] in MANUAL_TITLES else "EMAIL"
    steps.append(st)

sc = src["scheduler_cron_value"]
schedule = {"timezone": sc["tz"], "days_of_the_week": sc["days"], "start_hour": sc["startHour"], "end_hour": sc["endHour"],
            "min_time_btw_emails": src["min_time_btwn_emails"], "max_new_leads_per_day": src["max_leads_per_day"],
            "schedule_start_time": f"{a.start_date}T13:00:00.000Z"}
settings = {"track_settings": [TRACK_MAP.get(t, t) for t in src["track_settings"]], "stop_lead_settings": src["stop_lead_settings"],
            "send_as_plain_text": src["send_as_plain_text"], "follow_up_percentage": src["follow_up_percentage"],
            "enable_ai_esp_matching": src["enable_ai_esp_matching"], "unsubscribe_text": src["unsubscribe_text"] or ""}
extra = [{"add_unsubscribe_tag": bool(src.get("add_unsubscribe_tag"))},
         {"ai_categorisation_options": [c["id"] for c in (src.get("ai_categorisation_options") or [])]}]
ids = [x["id"] for x in accts]

if a.campaign_id:
    cid = a.campaign_id; print("RESUMING", cid)
else:
    cid = ok(call("POST", "/campaigns/create", {"name": a.name}), "create")["id"]; print("CREATED", cid, a.name)
ok(call("POST", f"/campaigns/{cid}/sequences", {"sequences": steps}), "sequences")
ok(call("POST", f"/campaigns/{cid}/schedule", schedule), "schedule")
ok(call("POST", f"/campaigns/{cid}/settings", settings), "settings")
for e in extra:
    ok(call("POST", f"/campaigns/{cid}/settings", e), f"settings {list(e)[0]}")
for i in range(0, len(ids), 100):
    ok(call("POST", f"/campaigns/{cid}/email-accounts", {"email_account_ids": ids[i:i + 100]}), f"accounts {i}")
subs = [c["id"] for c in call("GET", "/campaigns/") if c.get("parent_campaign_id") == a.source_id]
print(json.dumps({"campaign_id": cid, "steps": len(steps), "inboxes": len(ids), "not_cloned": {
    "ooo_detection": src.get("out_of_office_detection_settings"), "source_subsequences": subs}}))
print("Next: python3 verify_clone.py", a.source_id, cid)
