#!/usr/bin/env python3
"""WEEKLY ONLY — append this week's KPI as a new column in the Google Sheet, so the
numbers accumulate over time for WoW comparisons and charts.

Tab 'Email Time-to-reply tracker'. Layout is metric-per-row; each weekly run writes the
next empty column to the right (first run fills column C). Per column:
  row 2  Start   = week Monday        row 9  Avg Time to Reply    (duration)
  row 3  End     = week Sunday        row 10 Median Time to Reply  (duration)
  row 4  Date    = report run date    row 11 Interested Replies    (positive replies count)
  row 7  % <5min (percent)            row 12 Answered Replies
  row 8  % <10min (percent)

Everything is written with valueInputOption=USER_ENTERED so Sheets stores REAL typed
values — dates as dates, "1.4%" as 0.014 (percent), "1:36" as a duration (numeric) — never
strings. That keeps the sheet analyzable: WoW math, trend charts, formulas all work.

Auth: Google OAuth refresh token (env GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET /
GOOGLE_REFRESH_TOKEN). The 'drive' scope on that token covers Sheets writes.
Reads kpi_output.json (written by run_weekly_kpi.py) from the same dir.
"""
import subprocess, json, os, sys, time
from urllib.parse import quote

SHEET_ID = "1Wklpdze9UReMsTxTtpYNs0dq6-xXYTeleHSn67te4wo"
SHEET_GID = 558240029
FIRST_COL = 2   # column C (0-based: A=0)
HERE = os.path.dirname(os.path.abspath(__file__))

CID = os.environ.get("GOOGLE_CLIENT_ID")
CSEC = os.environ.get("GOOGLE_CLIENT_SECRET")
RTOK = os.environ.get("GOOGLE_REFRESH_TOKEN")
if not (CID and CSEC and RTOK):
    sys.exit("ERROR: set GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN")

def access_token():
    for _ in range(4):
        out = subprocess.run(
            ["curl", "-s", "-X", "POST", "https://oauth2.googleapis.com/token",
             "-d", f"client_id={CID}", "-d", f"client_secret={CSEC}",
             "-d", f"refresh_token={RTOK}", "-d", "grant_type=refresh_token"],
            capture_output=True, text=True).stdout
        try:
            t = json.loads(out).get("access_token")
            if t:
                return t
        except Exception:
            pass
        time.sleep(2)
    sys.exit("ERROR: could not refresh Google access token")

TOKEN = access_token()

def gapi(method, url, body=None):
    args = ["curl", "-s", "-X", method, url, "-H", f"Authorization: Bearer {TOKEN}"]
    if body is not None:
        args += ["-H", "Content-Type: application/json", "--data", json.dumps(body)]
    out = subprocess.run(args, capture_output=True, text=True).stdout
    r = json.loads(out)
    if isinstance(r, dict) and r.get("error"):
        sys.exit(f"Google API error ({method} {url[:90]}): {r['error']}")
    return r

def col_letter(idx0):
    s, n = "", idx0
    while True:
        s = chr(65 + n % 26) + s
        n = n // 26 - 1
        if n < 0:
            break
    return s

def rng(a1):
    return quote(f"'{TITLE}'!{a1}")

def hm(h):
    """decimal hours -> 'H:MM' so USER_ENTERED stores it as a real duration/time value."""
    if h is None:
        return ""
    mins = round(h * 60)
    return f"{mins // 60}:{mins % 60:02d}"

# ---- load KPI ---------------------------------------------------------------
_data = json.load(open(os.path.join(HERE, "kpi_output.json")))
s = _data["summary"]

# ---- resolve the tab's title from its gid (ranges use the name, not the gid) -
meta = gapi("GET", f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}?fields=sheets.properties")
TITLE = next((sh["properties"]["title"] for sh in meta.get("sheets", [])
              if sh["properties"].get("sheetId") == SHEET_GID), None)
if not TITLE:
    sys.exit(f"ERROR: no tab with gid {SHEET_GID} in the spreadsheet")

# ---- find the next empty column (sentinel = the Avg row, 9) ------------------
base = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values"
row9 = gapi("GET", f"{base}/{rng(f'{col_letter(FIRST_COL)}9:9')}")
used = len(row9["values"][0]) if row9.get("values") else 0
col = col_letter(FIRST_COL + used)

run_date = _data.get("generated_at_utc", "")[:10] or s["period_end"]

# rows 2..12 for this column (5 and 6 stay blank)
column_values = [
    [s["period_start"]],                 # 2  Start (week Monday)
    [s["period_end"]],                   # 3  End   (week Sunday)
    [run_date],                          # 4  Date  (report run date)
    [""],                                # 5
    [""],                                # 6
    [f"{s['pct_under_5min']}%"],         # 7  % <5min
    [f"{s['pct_under_10min']}%"],        # 8  % <10min
    [hm(s["biz_avg_h"])],                # 9  Avg (duration)
    [hm(s["biz_median_h"])],             # 10 Median (duration)
    [s["positive_replies"]],             # 11 Interested Replies (all positive)
    [s["answered"]],                     # 12 Answered Replies
]

url = f"{base}/{rng(f'{col}2:{col}12')}?valueInputOption=USER_ENTERED"
gapi("PUT", url, {"values": column_values})

print(f"wrote week {s['period_label']} to tab '{TITLE}' column {col} "
      f"(avg {hm(s['biz_avg_h'])}, median {hm(s['biz_median_h'])}, "
      f"<5m {s['pct_under_5min']}%, <10m {s['pct_under_10min']}%, "
      f"interested {s['positive_replies']}, answered {s['answered']})")
