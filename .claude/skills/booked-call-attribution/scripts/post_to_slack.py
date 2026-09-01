#!/usr/bin/env python3
"""Step 9 — post the weekly headline to Slack.

Headline only, with a link to the sheet for detail. The per-lead table lives in
Google Sheets because that is where it can be sorted, filtered and kept; repeating
it in Slack would make a long message nobody reads on a phone.

One reporting rule is baked in rather than left to the reader: weekly volume is
5-13 calls, so the weekly percentage is mostly noise. The two best-looking weeks in
the eight-week baseline (80%, 86%) were the two smallest (5 and 7 calls) — one
booking moves them 14-20 points. The message therefore always shows the counts next
to the percentage, and states the Mon-00:00-ET boundary, since three of those 74
rows turned on it.

Usage:
    python3 post_to_slack.py --attribution attribution.json
    python3 post_to_slack.py --attribution attribution.json --dry-run
Env: SLACK_BOT_TOKEN, optional BOOKED_ATTRIBUTION_SLACK_CHANNEL_ID
"""
import argparse
import json
import os
import subprocess
import sys

from common import load_json

# A channel ID is an identifier, not a secret, so it is defaulted here — that way a
# cloud routine needs no extra configuration. #outbound auto-pause reports, the same
# channel the booked-call-pause runs report into, so all booked-call signal lands
# together. Override with BOOKED_ATTRIBUTION_SLACK_CHANNEL_ID.
DEFAULT_CHANNEL = "C0BRJAFNUG5"
CHANNEL = (os.environ.get("BOOKED_ATTRIBUTION_SLACK_CHANNEL_ID")
           or os.environ.get("PAUSE_SLACK_CHANNEL_ID")
           or DEFAULT_CHANNEL)
TOKEN = os.environ.get("SLACK_BOT_TOKEN")


def slack(method, payload):
    out = subprocess.run(
        ["curl", "-s", "--max-time", "45", "-X", "POST",
         f"https://slack.com/api/{method}",
         "-H", f"Authorization: Bearer {TOKEN}",
         "-H", "Content-Type: application/json; charset=utf-8",
         "--data-raw", json.dumps(payload)],
        capture_output=True, text=True).stdout
    try:
        return json.loads(out)
    except Exception:
        return {"ok": False, "error": out[:200]}


def _differs(a, b):
    from common import norm_name
    return norm_name(a) != norm_name(b)


def build_message(data, sheet_url):
    s = data["summary"]
    rows, review = data["rows"], data.get("review") or []
    attributed = s["same_week"] + s["prev_week"]

    lines = [
        f"*Booked-call pipeline attribution — {s['week_start']} → {s['week_end']}*",
        "",
        f"*{s['total_booked']}* calls booked from Email Outreach "
        f"across *{s['companies']}* {'company' if s['companies'] == 1 else 'companies'}."
        + (f" (+{s['flagged']} flagged for review)" if s.get("flagged") else ""),
    ]
    if attributed:
        lines += [
            f"• *Same-week pipeline:* {s['same_week']}/{attributed} "
            f"({s['same_pct']}%) — first replied inside this week",
            f"• *Previous-week pipeline:* {s['prev_week']}/{attributed} "
            f"({s['prev_pct']}%) — replied earlier, booked now",
        ]
    elif s["total_booked"]:
        lines.append("• None could be matched to a Smartlead lead — see below.")
    else:
        lines.append("_A quiet week: no calls booked from Email Outreach._")

    if s["unresolved"]:
        names = ", ".join((r["company_name"] or r["booker_email"])
                          for r in rows if r["bucket"] == "UNRESOLVED"
                          and r.get("counted", True))
        lines += ["", f"⚠️ *{s['unresolved']} unresolved* (no Smartlead lead found): "
                      f"{names}. Percentages are of the {attributed} attributed."]

    # Rows written to the sheet but held out of the headline. They are in the sheet
    # marked "REVIEW – …" so no company goes missing; naming them here is what turns
    # a silent exclusion into a decision Gaston actually makes.
    flagged = [r for r in rows if not r.get("counted", True)]
    if flagged:
        lines += ["", f"🔎 *{len(flagged)} in the sheet as `REVIEW`* — a real call "
                      "or not; keep or delete the row:"]
        for r in flagged:
            lines.append(f"    • {r['company_name'] or r['booker_email']} — "
                         f"{r.get('flag_reason', '')}")

    dropped = data.get("dropped_delivery") or []
    if dropped:
        lines += ["", f"🗑️ *{len(dropped)} excluded as delivery, not bookings* — "
                      "kickoffs, candidate interviews and client syncs:"]
        for d in dropped:
            lines.append(f"    • {d['company_name'] or d['booker_email']} — "
                         f"“{d['meeting_title']}”")

    if review:
        lines += ["", f"⚙️ *{len(review)} booking(s) with no source tag in HubSpot* "
                      "— excluded, and not in the sheet:"]
        for r in review[:6]:
            lines.append(f"    • {r['company_name'] or r['booker_email']}")
        if len(review) > 6:
            lines.append(f"    • …and {len(review) - 6} more")

    # The sheet has no Match column, so the identity caveats have to live here.
    # A domain match can land on a colleague: HubSpot records Awan Ali as booking
    # for HypeProxies while the lead we emailed and measured is Gunnar Catlett.
    # Silently pairing one person's booking with another person's reply date is
    # exactly the kind of error that looks like clean data, so it gets named.
    mismatch = [r for r in rows if r["bucket"] != "UNRESOLVED"
                and r.get("counted", True)
                and r.get("match") not in ("booked-set:email", "smartlead:email")]
    if mismatch:
        lines += ["", "ℹ️ *Booked under a different address than we emailed* — "
                      "first-reply dates below come from the measured lead:"]
        for r in mismatch:
            sl = (r.get("smartlead_name") or "").strip()
            booker = (r.get("booker_name") or "").strip()
            who = (f"{booker} booked → measured {sl}"
                   if sl and _differs(sl, booker) else r.get("smartlead_email", ""))
            lines.append(f"    • {r['company_name']}: {who}")

    if sheet_url:
        lines += ["", f"<{sheet_url}|Full per-lead breakdown in the sheet →>"]
    lines += ["", "_Weeks run Mon 00:00 → Sun 23:59 America/New_York; a call counts "
                  "in the week it was booked. At 5-13 calls a week the percentage "
                  "swings hard on one booking — read the counts, not just the %._"]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--attribution", default="attribution.json")
    ap.add_argument("--sheet-url", default=os.environ.get("BOOKED_ATTRIBUTION_SHEET_URL", ""))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    data = load_json(a.attribution)
    text = build_message(data, a.sheet_url)

    if a.dry_run:
        print(text)
        return
    if not TOKEN:
        print(text)
        sys.exit("ERROR: SLACK_BOT_TOKEN not set — message printed above, not posted")

    res = slack("chat.postMessage", {"channel": CHANNEL, "text": text,
                                     "unfurl_links": False, "unfurl_media": False})
    if not res.get("ok"):
        print(text)
        sys.exit(f"ERROR: Slack post failed: {res.get('error')} "
                 f"(is the bot in {CHANNEL}?) — message printed above")
    print(f"[slack] posted to {CHANNEL}")


if __name__ == "__main__":
    main()
