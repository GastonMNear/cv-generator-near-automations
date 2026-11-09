#!/usr/bin/env python3
"""Create ONE Smartlead campaign from a spec JSON. Create-only, never edits existing campaigns.

Usage:
  python3 create_campaign.py spec.json
  python3 create_campaign.py spec.json --campaign-id 123456   # repair a campaign created earlier THIS run

Spec schema: see references/api-reference.md in this skill.

Flow: create campaign -> save sequences (emails + manual step) -> schedule -> settings
      -> attach inboxes -> re-fetch and print verification summary.

All HTTP goes through curl (Cloudflare blocks Python HTTP clients with 403/1010).
Exits non-zero on the first failure; re-run with --campaign-id to resume without duplicating.
"""
import argparse
import datetime
import json
import os
import subprocess
import sys
import tempfile

BASE = "https://server.smartlead.ai/api/v1"

STANDARD_SCHEDULE = {
    "timezone": "America/New_York",
    "days_of_the_week": [1, 2, 3, 4, 5],
    "start_hour": "09:00",
    "end_hour": "18:00",
    "min_time_btw_emails": 20,
    "max_new_leads_per_day": 2000,
}

STANDARD_SETTINGS = {
    "track_settings": ["DONT_TRACK_EMAIL_OPEN", "DONT_TRACK_LINK_CLICK"],
    "stop_lead_settings": "REPLY_TO_AN_EMAIL",
    "send_as_plain_text": False,
    "follow_up_percentage": 30,
    "enable_ai_esp_matching": False,
    "unsubscribe_text": "",
}

STANDARD_MANUAL_STEP = {
    "title": "Send Lead to Justcall",
    "description": "Send to Clay - Add to JustCall",
    "delay_after_last_email_days": 1,
}


def load_api_key():
    key = os.environ.get("SMARTLEAD_API_KEY")
    if key:
        return key
    d = os.path.dirname(os.path.abspath(__file__))
    while d != "/":
        env_path = os.path.join(d, ".env")
        if os.path.exists(env_path):
            for line in open(env_path):
                line = line.strip()
                if line.startswith("SMARTLEAD_API_KEY="):
                    return line.split("=", 1)[1].strip().strip("'\"")
        d = os.path.dirname(d)
    sys.exit("SMARTLEAD_API_KEY not found in environment or any parent .env")


def curl(method, url, body=None):
    cmd = ["curl", "-s", "-X", method, url, "-H", "Content-Type: application/json"]
    tmp = None
    if body is not None:
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        json.dump(body, tmp)
        tmp.close()
        cmd += ["--data-binary", f"@{tmp.name}"]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    finally:
        if tmp:
            os.unlink(tmp.name)
    if out.returncode != 0:
        sys.exit(f"curl failed for {method} {url.split('?')[0]}: {out.stderr}")
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError:
        sys.exit(f"Non-JSON response from {method} {url.split('?')[0]}: {out.stdout[:300]}")


def require_ok(resp, step):
    if isinstance(resp, dict) and (resp.get("ok") is True or "id" in resp):
        return resp
    sys.exit(f"FAILED at {step}: {json.dumps(resp)[:500]}")


def build_sequences(spec):
    emails = spec["emails"]
    if not emails:
        sys.exit("Spec has no emails")
    seqs, prev_day = [], None
    for i, e in enumerate(emails):
        day = e["day"]
        if prev_day is None:
            delay = max(0, day - 1)  # Day 1 sends immediately
        else:
            delay = day - prev_day
            if delay < 1:
                sys.exit(f"Email {i + 1} day {day} is not after previous day {prev_day}")
        prev_day = day
        variants = [{"subject": e.get("subject", ""), "email_body": e["body_html"], "variant_label": "A"}]
        for j, v in enumerate(e.get("variants", [])):
            variants.append({
                "subject": v.get("subject", ""),
                "email_body": v["body_html"],
                "variant_label": chr(ord("B") + j),
            })
        seqs.append({
            "seq_number": i + 1,
            "seq_delay_details": {"delay_in_days": delay},
            "seq_type": "EMAIL",
            "variant_distribution_type": "MANUAL_EQUAL",
            "seq_variants": variants,
        })

    manual = spec.get("manual_step", STANDARD_MANUAL_STEP)
    if manual is not None:
        seqs.append({
            "seq_number": len(seqs) + 1,
            "seq_delay_details": {"delay_in_days": manual.get("delay_after_last_email_days", 1)},
            "seq_type": "MANUAL",
            "subject": manual.get("title", STANDARD_MANUAL_STEP["title"]),
            "email_body": f"<div>{manual.get('description', STANDARD_MANUAL_STEP['description'])}</div>",
        })
    return seqs


def main():
    p = argparse.ArgumentParser()
    p.add_argument("spec", help="path to spec JSON")
    p.add_argument("--campaign-id", type=int, default=None,
                   help="resume/repair a campaign created earlier in this run instead of creating a new one")
    args = p.parse_args()

    spec = json.load(open(args.spec))
    key = load_api_key()

    for field in ("name", "emails", "email_account_ids"):
        if not spec.get(field):
            sys.exit(f"Spec is missing required field: {field}")

    sequences = build_sequences(spec)  # validate before creating anything

    start_date = spec.get("start_date") or datetime.date.today().isoformat()
    schedule = {**STANDARD_SCHEDULE,
                "schedule_start_time": f"{start_date}T13:00:00.000Z",
                **spec.get("schedule_overrides", {})}
    settings = {**STANDARD_SETTINGS, **spec.get("settings_overrides", {})}

    # 1. create
    if args.campaign_id:
        cid = args.campaign_id
        print(f"Resuming campaign {cid} (no new campaign created)")
    else:
        resp = require_ok(curl("POST", f"{BASE}/campaigns/create?api_key={key}", {"name": spec["name"]}),
                          "create campaign")
        cid = resp["id"]
        print(f"Created campaign {cid}: {resp['name']}")

    # 2. sequences
    require_ok(curl("POST", f"{BASE}/campaigns/{cid}/sequences?api_key={key}", {"sequences": sequences}),
               "save sequences")
    print(f"Saved {len(sequences)} sequence steps")

    # 3. schedule
    require_ok(curl("POST", f"{BASE}/campaigns/{cid}/schedule?api_key={key}", schedule), "schedule")
    print("Schedule applied")

    # 4. settings
    require_ok(curl("POST", f"{BASE}/campaigns/{cid}/settings?api_key={key}", settings), "settings")
    print("Settings applied")

    # 5. inboxes (batches of 100)
    ids = spec["email_account_ids"]
    for i in range(0, len(ids), 100):
        batch = ids[i:i + 100]
        require_ok(curl("POST", f"{BASE}/campaigns/{cid}/email-accounts?api_key={key}",
                        {"email_account_ids": batch}), f"attach inboxes batch {i // 100 + 1}")
    print(f"Attached {len(ids)} inboxes")

    # 6. verify
    camp = curl("GET", f"{BASE}/campaigns/{cid}?api_key={key}")
    seqs = curl("GET", f"{BASE}/campaigns/{cid}/sequences?api_key={key}")
    accounts = curl("GET", f"{BASE}/campaigns/{cid}/email-accounts?api_key={key}")

    problems = []
    if camp.get("status") != "DRAFTED":
        problems.append(f"status is {camp.get('status')}, expected DRAFTED")
    if len(seqs) != len(sequences):
        problems.append(f"{len(seqs)} steps stored, expected {len(sequences)}")
    if len(accounts) != len(ids):
        problems.append(f"{len(accounts)} inboxes attached, expected {len(ids)}")

    print("\n=== VERIFICATION ===")
    print(f"Campaign {cid} | {camp.get('name')} | status {camp.get('status')}")
    sched = camp.get("scheduler_cron_value", {})
    print(f"Schedule: {sched.get('tz')} days {sched.get('days')} {sched.get('startHour')}-{sched.get('endHour')} | "
          f"{camp.get('min_time_btwn_emails')}min btw | max {camp.get('max_leads_per_day')}/day | "
          f"start {camp.get('schedule_start_time')}")
    print(f"Settings: track {camp.get('track_settings')} | stop {camp.get('stop_lead_settings')} | "
          f"follow-up {camp.get('follow_up_percentage')}% | plain_text {camp.get('send_as_plain_text')} | "
          f"esp_match {camp.get('enable_ai_esp_matching')}")
    for s in seqs:
        variants = s.get("sequence_variants")
        kind = "MANUAL(assumed)" if variants is None else "EMAIL"
        subject = s.get("subject") if variants is None else variants[0].get("subject")
        print(f"  step {s['seq_number']}: delay {s['seq_delay_details'].get('delayInDays')}d | {kind} | "
              f"subject: {subject or '(in-thread)'}"
              + (f" | {len(variants)} variants" if variants and len(variants) > 1 else ""))
    print(f"Inboxes: {len(accounts)}")

    if problems:
        print("\nPROBLEMS: " + "; ".join(problems))
        sys.exit(1)
    print("\nOK — campaign is DRAFTED. Add leads and launch from the Smartlead UI.")


if __name__ == "__main__":
    main()
