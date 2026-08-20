#!/usr/bin/env python3
"""Post a booked-call auto-pause run summary to Slack.

Reads the JSON written by `pause_booked.py --json-out` and posts one message per run.
Quiet by default: if nothing matched and nothing failed there is no message, so the
channel only gets traffic when something actually happened (or broke).

Channel: PAUSE_SLACK_CHANNEL_ID — deliberately NOT the KPI channel that
SLACK_CHANNEL_ID points at. The bot must be invited to it or chat.postMessage
returns not_in_channel.

Usage:
    python3 post_to_slack.py /tmp/pause_run.json
    python3 post_to_slack.py /tmp/pause_run.json --always   # post even if empty
Env: SLACK_BOT_TOKEN, PAUSE_SLACK_CHANNEL_ID
"""
import json
import os
import subprocess
import sys

TOKEN = os.environ.get("SLACK_BOT_TOKEN")
# A channel ID is an identifier, not a secret, so it's defaulted here — that way a
# cloud routine only needs the real secrets in its environment. Override with
# PAUSE_SLACK_CHANNEL_ID if the channel ever changes.
DEFAULT_CHANNEL = "C0BRJAFNUG5"   # #outbound auto-pause reports
CHANNEL = (os.environ.get("PAUSE_SLACK_CHANNEL_ID")
           or os.environ.get("BOOKED_PAUSE_SLACK_CHANNEL_ID")
           or DEFAULT_CHANNEL)


def api(method, payload):
    args = ["curl", "-s", "-X", "POST", f"https://slack.com/api/{method}",
            "-H", f"Authorization: Bearer {TOKEN}",
            "-H", "Content-Type: application/json; charset=utf-8",
            "--data", json.dumps(payload)]
    out = subprocess.run(args, capture_output=True, text=True).stdout
    r = json.loads(out)
    if not r.get("ok"):
        sys.exit(f"Slack error on {method}: {r.get('error')} | {out[:300]}")
    return r


def build_message(data):
    live = data.get("live")
    results = data.get("results") or []
    sync = data.get("sync") or {}

    paused = [p for r in results for p in r["paused"]]
    errors = [e for r in results for e in r["errors"]]
    matched_companies = [r for r in results if r["leads_matched"]]

    head = "*Booked-call auto-pause*" + ("" if live else " — DRY RUN, nothing changed")
    verb = "Paused" if live else "Would pause"
    lines = [
        head,
        f"{verb} *{len(paused)}* lead(s) across *{len(matched_companies)}* "
        f"of {len(results)} booking(s)  ·  crawled {sync.get('stored', '?')} leads",
    ]

    for r in matched_companies:
        lines.append(f"\n• *{r['company']}*  `{r['company_domain']}`  "
                     f"— {r['leads_matched']} lead(s) via `{r['matched_by']}`")
        for p in r["paused"]:
            lines.append(f"     • {p['email']} — {p['campaign']}")
        for e in r["not_in_active_campaign"]:
            lines.append(f"     ◦ {e} (no active campaign)")

    if errors:
        lines.append(f"\n:warning: *{len(errors)} failure(s)*")
        for e in errors[:10]:
            lines.append(f"     • {e.get('email')} — {e.get('error')}")

    no_match = [r for r in results if not r["leads_matched"]]
    if no_match:
        lines.append(f"\n_{len(no_match)} booking(s) had no Smartlead leads "
                     f"(inbound, not from cold email)_")

    return "\n".join(lines), len(paused), len(errors)


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: post_to_slack.py <run.json> [--always]")
    if not TOKEN:
        sys.exit("ERROR: SLACK_BOT_TOKEN not set")
    if not CHANNEL:
        sys.exit("ERROR: PAUSE_SLACK_CHANNEL_ID not set — create a channel for these "
                 "reports, invite the bot, and set its channel ID. (Deliberately not "
                 "reusing SLACK_CHANNEL_ID, which is the reply-time KPI channel.)")

    data = json.load(open(sys.argv[1]))
    text, n_paused, n_err = build_message(data)

    if not n_paused and not n_err and "--always" not in sys.argv:
        print("[slack] nothing to report — no message posted")
        return

    api("chat.postMessage", {"channel": CHANNEL, "text": text,
                             "unfurl_links": False, "unfurl_media": False})
    print(f"[slack] posted to {CHANNEL} ({n_paused} paused, {n_err} errors)")


if __name__ == "__main__":
    main()
