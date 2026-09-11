#!/usr/bin/env python3
"""Post the weekly KPI to Slack as a threaded message.

Message 1 (channel): headline summary + per-category table.
Reply in thread:      the full lead-by-lead breakdown as a CSV file attachment.

Why a CSV file for the detail: a week's table is wide (categories, timestamps, two
metrics, email) and Slack code blocks wrap wide lines into an unreadable mess. An
uploaded file renders in Slack's scrollable viewer and opens cleanly as a spreadsheet.

Threading requires a Bot token (chat.postMessage returns the parent `ts`, which we pass
as `thread_ts`). The file upload uses Slack's external-upload flow (3 calls).

Env:
  SLACK_BOT_TOKEN   xoxb-... , app needs scopes chat:write AND files:write, in the channel
  SLACK_CHANNEL_ID  e.g. C0123456789  (channel ID, not the name)
Reads kpi_output.json (written by run_weekly_kpi.py) from the same dir.
"""
import subprocess, json, os, sys, csv, io

TOKEN = os.environ.get("SLACK_BOT_TOKEN")
CHANNEL = os.environ.get("SLACK_CHANNEL_ID")
if not TOKEN or not CHANNEL:
    sys.exit("ERROR: set SLACK_BOT_TOKEN and SLACK_CHANNEL_ID")

HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(HERE, "kpi_output.json")))
s = data["summary"]

def api(method, payload, as_json=True):
    args = ["curl", "-s", "-X", "POST", f"https://slack.com/api/{method}",
            "-H", f"Authorization: Bearer {TOKEN}"]
    if as_json:
        args += ["-H", "Content-Type: application/json; charset=utf-8", "--data", json.dumps(payload)]
    else:
        for k, v in payload.items():
            args += ["--data-urlencode", f"{k}={v}"]
    out = subprocess.run(args, capture_output=True, text=True).stdout
    r = json.loads(out)
    if not r.get("ok"):
        sys.exit(f"Slack error on {method}: {r.get('error')} | {out[:300]}")
    return r

def fmt(h):
    """Decimal hours -> human HH:MM style, e.g. 1.6 -> '1h 36m', 0.05 -> '3m'."""
    if h is None:
        return "—"
    mins = round(h * 60)
    hh, mm = divmod(mins, 60)
    if hh and mm:
        return f"{hh}h {mm}m"
    return f"{hh}h" if hh else f"{mm}m"

# ---- Message 1: summary + per-category table --------------------------------
avg, med = fmt(s["biz_avg_h"]), fmt(s["biz_median_h"])
lines = [
    "*📬 Smartlead — Response time to positive replies*",
    f"*Period (ET):* {s['period_label']}",
    "",
    f"*Positive replies:* {s['positive_replies']}   "
    f"*Answered:* {s['answered']}   *Pending:* {s['pending']}",
    f"*Business-hours response* (Mon–Fri 9–18 ET) → *avg {avg}* · *median {med}* "
    f"· min {fmt(s['biz_min_h'])} · max {fmt(s['biz_max_h'])}",
    f"*⚡ Responded (real time):* <5 min *{s['pct_under_5min']}%* "
    f"({s['under_5min_count']}/{s['answered']})  ·  <10 min *{s['pct_under_10min']}%* "
    f"({s['under_10min_count']}/{s['answered']})",
    f"_Raw wall-clock for reference: avg {fmt(s['raw_avg_h'])} · median {fmt(s['raw_median_h'])}_",
]
cb = data["category_breakdown"]
tbl = [f"{'Category':<26}{'n':>4}{'ans':>5}{'avg':>9}{'median':>9}", "-" * 53]
for cat, v in sorted(cb.items(), key=lambda kv: (kv[1]["avg_h"] is None, kv[1]["avg_h"] or 0)):
    tbl.append(f"{cat[:25]:<26}{v['count']:>4}{v['answered']:>5}"
               f"{fmt(v['avg_h']):>9}{fmt(v['median_h']):>9}")
msg1 = "\n".join(lines) + "\n\n```\n" + "\n".join(tbl) + "\n```"
if s["errors"]:
    msg1 += f"\n:warning: {s['errors']} lead(s) could not be resolved (see logs)."

parent_ts = api("chat.postMessage",
                {"channel": CHANNEL, "text": msg1, "unfurl_links": False, "unfurl_media": False})["ts"]
print(f"posted message 1, ts={parent_ts}")

# ---- Build the CSV in memory ------------------------------------------------
buf = io.StringIO()
w = csv.writer(buf)
w.writerow(["category", "lead_name", "lead_email", "biz_hours", "raw_hours",
            "reply_et", "we_replied_et", "campaign"])
for r in data["leads"]:
    w.writerow([r["lead_category"], r.get("lead_name"), r["lead_email"],
                r["response_business_hours"], r["response_raw_hours"],
                r["positive_reply_at_et"], r["our_reply_at_et"] or "PENDING",
                r.get("campaign_name")])
csv_bytes = buf.getvalue().encode("utf-8")
fname = (f"positive-replies-{s['period_start']}.csv" if s["period_start"] == s["period_end"]
         else f"positive-replies-{s['period_start']}_{s['period_end']}.csv")

# ---- Upload CSV and share into the thread (files.upload external flow) -------
# 1) reserve an upload URL
up = api("files.getUploadURLExternal",
         {"filename": fname, "length": str(len(csv_bytes))}, as_json=False)
upload_url, file_id = up["upload_url"], up["file_id"]

# 2) PUT the bytes to that URL (write to a temp file so curl can -F it)
tmp = os.path.join(HERE, "_upload.csv")
with open(tmp, "wb") as f:
    f.write(csv_bytes)
try:
    subprocess.run(["curl", "-s", "-F", f"file=@{tmp}", upload_url],
                   capture_output=True, text=True)
finally:
    os.remove(tmp)

# 3) complete the upload, sharing it as a reply in the thread
api("files.completeUploadExternal", {
    "files": [{"id": file_id, "title": fname}],
    "channel_id": CHANNEL,
    "thread_ts": parent_ts,
    "initial_comment": f"*Full lead breakdown* — {s['positive_replies']} positive replies. "
                       f"biz_hours = business hours (Mon–Fri 9–18 ET); raw_hours = wall-clock.",
})
print(f"uploaded {fname} to thread")
print("done")
