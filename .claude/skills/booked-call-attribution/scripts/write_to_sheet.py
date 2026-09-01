#!/usr/bin/env python3
"""Step 8 — append the week's attribution to the tracking Google Sheet.

Tab 'Email Lead-Conversion-Timing-Analysis' in the Outbound metrics spreadsheet.

COLUMNS ARE RESOLVED BY HEADER NAME, not by fixed position. The header row is found
by locating 'Week' in column B, then each column is matched to a field by its label.
This survives reordering, inserted columns, and renames within the aliases below —
the layout has already changed once during development, so pinning positions would
just guarantee a silent mis-write later. A header this script doesn't recognise is
left alone; a field the sheet doesn't have is simply not written.

Current layout (2026-09-01):

    A x | B Week | C Start | D End | E Company | F Contact | G Email
    H Bucket (SAME/PREV) | I Campaign | J First reply (ET) | K Booked (ET)

One blank row separates week blocks, and the first row of each block carries an 'x'
in column A. That is a readability choice with a cost worth knowing: Sheets' native
filter and pivot auto-ranges stop at a blank row, so build those over an explicit
range (A5:K996) rather than letting Sheets guess.

Values go in with USER_ENTERED so dates land as real dates — the tab stays chartable
and formula-friendly rather than holding strings that merely look like dates.

Usage:
    python3 write_to_sheet.py --attribution attribution.json
    python3 write_to_sheet.py --attribution attribution.json --dry-run
Env: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN
"""
import argparse
import json
import os
import subprocess
import sys
import urllib.parse
from datetime import datetime, timedelta

from common import ET, load_json, norm_name, parse_ts

SHEET_ID = "1Wklpdze9UReMsTxTtpYNs0dq6-xXYTeleHSn67te4wo"
TAB = "Email Lead-Conversion-Timing-Analysis"
GID = 1651055580
SCAN_COLS = "AA"          # how far right to read when locating the header

# header label (lowercased, punctuation-insensitive) -> field key
ALIASES = {
    "x": "marker",
    "week": "week", "week label": "week",
    "start": "start", "week start": "start",
    "end": "end", "week end": "end",
    "company": "company",
    "contact": "contact", "lead": "contact", "booker": "contact",
    "email": "email", "lead email": "email",
    "bucket same prev": "bucket", "bucket": "bucket", "attribution": "bucket",
    "campaign": "campaign", "campaigns": "campaign", "campaign name": "campaign",
    "first reply et": "first_reply", "first reply": "first_reply",
    "booked et": "booked", "booked": "booked", "booked date": "booked",
    "match": "match",
    "note": "note", "notes": "note", "flag": "note", "comment": "note",
    "total": "total", "same": "same", "prev": "prev",
    "same %": "same_pct", "same pct": "same_pct",
}


def norm_header(text):
    """'Bucket (SAME/PREV)' -> 'bucket same prev'. Punctuation is dropped rather
    than mapped, so parentheses, slashes and hyphens in a header never matter."""
    cleaned = "".join(c if (c.isalnum() or c == "%") else " "
                      for c in (text or "").lower())
    return " ".join(cleaned.split())


def access_token():
    for var in ("GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "GOOGLE_REFRESH_TOKEN"):
        if not os.environ.get(var):
            sys.exit(f"ERROR: {var} not set")
    out = subprocess.run(
        ["curl", "-s", "-X", "POST", "https://oauth2.googleapis.com/token",
         "-d", f"client_id={os.environ['GOOGLE_CLIENT_ID']}",
         "-d", f"client_secret={os.environ['GOOGLE_CLIENT_SECRET']}",
         "-d", f"refresh_token={os.environ['GOOGLE_REFRESH_TOKEN']}",
         "-d", "grant_type=refresh_token"],
        capture_output=True, text=True).stdout
    tok = json.loads(out).get("access_token")
    if not tok:
        sys.exit(f"ERROR: Google token refresh failed: {out[:200]}")
    return tok


def gapi(token, method, url, body=None):
    cmd = ["curl", "-s", "--max-time", "60", "-X", method, url,
           "-H", f"Authorization: Bearer {token}",
           "-H", "Content-Type: application/json"]
    if body is not None:
        cmd += ["--data-raw", json.dumps(body)]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    try:
        data = json.loads(out)
    except Exception:
        sys.exit(f"ERROR: unparseable Sheets response: {out[:300]}")
    if isinstance(data, dict) and data.get("error"):
        sys.exit(f"ERROR: Sheets: {data['error'].get('message')}")
    return data


def enc(a1):
    """A1 ranges carry ! and quotes; they must be percent-encoded as a path segment."""
    return urllib.parse.quote(a1, safe="")


def col_letter(i):
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


# --------------------------------------------------------------------------- #
def us_date(iso):
    y, m, d = (int(x) for x in iso.split("-"))
    return f"{m}/{d}/{y}"


def et_short(label):
    """'Tue 2026-08-25 10:09' -> '8/25/2026 10:09' so Sheets stores a real datetime."""
    parts = (label or "").split()
    if len(parts) < 3:
        return label or ""
    try:
        y, m, d = (int(x) for x in parts[1].split("-"))
    except ValueError:
        return label
    return f"{m}/{d}/{y} {parts[2]}"


def booked_et(row):
    dt = parse_ts(row.get("booked_at"))
    return dt.astimezone(ET).strftime("%-m/%-d/%Y %H:%M") if dt else ""


def campaign_label(row):
    """Campaign names, deduped and in order. Falls back to the id when a name is
    missing so the cell is never silently empty."""
    seen, out = set(), []
    for c in row.get("campaigns") or []:
        name = (c.get("campaign_name") or "").strip() or str(c.get("campaign_id"))
        if name not in seen:
            seen.add(name)
            out.append(name)
    return ", ".join(out)


def match_label(row):
    """Match method, naming the measured lead when it is not the person who booked.

    A domain match can land on a colleague: HubSpot records Awan Ali as booking for
    HypeProxies while the lead we emailed and tagged is Gunnar Catlett. Only written
    if the sheet has a Match column; otherwise the divergence is reported in Slack.
    """
    match = row.get("match") or ""
    if match.endswith(":email"):
        return match
    sl = (row.get("smartlead_name") or "").strip()
    if sl and norm_name(sl) != norm_name(row.get("booker_name")):
        return f"{match} → {sl}"
    return match


def build_records(data):
    """Field dicts, one per booking, ordered SAME → PREV → UNRESOLVED then by time."""
    s = data["summary"]
    start_iso = s["week_start"]
    y, m, d = (int(x) for x in s["week_end"].split("-"))     # exclusive Monday
    end_iso = (datetime(y, m, d) - timedelta(days=1)).date().isoformat()
    sy, sm, sd = (int(x) for x in start_iso.split("-"))
    ey, em, ed = (int(x) for x in end_iso.split("-"))
    label = f"Mon {sm}/{sd} → Sun {em:02d}/{ed:02d}/{ey}"

    order = {"SAME": 0, "PREV": 1, "UNRESOLVED": 2}
    rows = sorted(data["rows"],
                  key=lambda r: (0 if r.get("counted", True) else 1,
                                 order.get(r["bucket"], 3), r["booked_at"]))
    recs = []
    for i, r in enumerate(rows):
        rec = {
            "marker": "x" if i == 0 else "",
            "week": label,
            "start": us_date(start_iso),
            "end": us_date(end_iso),
            "company": r.get("company_name") or "",
            "contact": r.get("booker_name") or "",
            "email": r.get("smartlead_email") or r.get("booker_email") or "",
            # Flagged rows are written so no company goes missing, but the bucket
            # cell says so — one column, sortable, and obvious enough to delete.
            "bucket": (r.get("bucket") or "") if r.get("counted", True)
                      else f"REVIEW – {r.get('bucket') or ''}",
            "note": r.get("flag_reason") or "",
            "campaign": campaign_label(r),
            "first_reply": et_short(r.get("first_reply_et")),
            "booked": booked_et(r),
            "match": match_label(r),
        }
        if i == 0:
            rec.update({"total": s["total_booked"], "same": s["same_week"],
                        "prev": s["prev_week"],
                        "same_pct": (f"{s['same_pct']}%"
                                     if s.get("same_pct") is not None else "")})
        recs.append(rec)

    return recs, label, us_date(start_iso)


def totals_row(colmap, first_row, last_row):
    """Gaston's Totals row, built from FORMULAS rather than baked-in numbers.

    It has to be live because the sheet is a working document: rows flagged
    `REVIEW – …` get kept or deleted by hand, and a booking Smartlead couldn't match
    gets its bucket typed in. Cactus Audio is the standing case — no Smartlead
    record, so it lands as UNRESOLVED, and the moment PREV is typed over it the split
    moves from 7/5 to 7/6 on its own. Static numbers would go stale the first time he
    touched the block, which is worse than no totals at all.

    COUNTIF matches the bucket exactly, so `REVIEW – SAME` is deliberately NOT
    counted as SAME — a flagged row stays out of the split until it is adjudicated.
    Deleting a row inside the block is safe: Sheets rewrites the ranges.
    """
    def rng(key):
        return (f"{col_letter(colmap[key])}{first_row}"
                f":{col_letter(colmap[key])}{last_row}")

    row = {"marker": "Totals"}
    if "company" in colmap:
        row["company"] = f"=COUNTUNIQUE({rng('company')})"
    if "contact" in colmap:
        row["contact"] = f"=COUNTA({rng('contact')})"
    if "bucket" in colmap:
        b = rng("bucket")
        same, prev = f'COUNTIF({b},"SAME")', f'COUNTIF({b},"PREV")'
        denom = f"MAX(1,{same}+{prev})"
        row["bucket"] = (
            f'={same}&" same ("&ROUND(100*{same}/{denom},0)&"%) | "'
            f'&{prev}&" Prev ("&ROUND(100*{prev}/{denom},0)&"%)"')
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--attribution", default="attribution.json")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true",
                    help="append even if this week is already in the sheet")
    ap.add_argument("--replace", action="store_true",
                    help="rewrite this week's existing block in place instead of "
                         "appending — for correcting a week already written")
    a = ap.parse_args()

    data = load_json(a.attribution)
    recs, label, start_cell = build_records(data)
    if not recs:
        print("[sheet] no bookings this week — nothing appended")
        return

    token = access_token()
    base = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}"
    grid = gapi(token, "GET",
                f"{base}/values/{enc(f'{TAB}!A1:{SCAN_COLS}996')}").get("values") or []

    header_idx = next((i for i, r in enumerate(grid)
                       if len(r) > 1 and norm_header(r[1]) == "week"), None)
    if header_idx is None:
        sys.exit(f"ERROR: no header row found in '{TAB}' (expected 'Week' in col B)")
    header = grid[header_idx]
    colmap = {}
    for i, cell in enumerate(header):
        key = ALIASES.get(norm_header(cell))
        if key and key not in colmap:
            colmap[key] = i
    missing = [k for k in ("week", "company", "bucket") if k not in colmap]
    if missing:
        sys.exit(f"ERROR: header row is missing {missing} — got "
                 f"{[c for c in header if c]}")
    width = max(colmap.values()) + 1

    body = grid[header_idx + 1:]
    start_col = colmap.get("start")
    existing = []
    if start_col is not None:
        existing = [header_idx + 2 + i for i, r in enumerate(body)
                    if len(r) > start_col and (r[start_col] or "").strip()
                    == start_cell]

    last_filled = header_idx + 1
    for i, r in enumerate(body):
        if any((c or "").strip() for c in r):
            last_filled = header_idx + 2 + i
    has_data = any(any((c or "").strip() for c in r) for r in body)

    clear_to = None
    if a.replace:
        if not existing:
            sys.exit(f"ERROR: --replace given but week {start_cell} is not in "
                     f"'{TAB}' yet. Run without --replace to append it.")
        first_row, block_end = min(existing), max(existing)
        # The Totals row deliberately carries no Start date (Gaston's layout leaves
        # B-D blank there), so the date scan misses it. Without this it would be
        # orphaned above the rewritten block.
        marker_col = colmap.get("marker")
        nxt = block_end + 1
        if (marker_col is not None and nxt - header_idx - 2 < len(body)
                and len(body[nxt - header_idx - 2]) > marker_col
                and (body[nxt - header_idx - 2][marker_col] or "").strip().lower()
                == "totals"):
            block_end = nxt
        # Growing a block in the middle of the sheet would silently overwrite the
        # week below it. Rewriting the LAST block is safe; anything else needs the
        # rows inserted by hand, so say so rather than destroy data.
        if len(recs) > (block_end - first_row + 1) and block_end < last_filled:
            sys.exit(f"ERROR: the new block is {len(recs)} rows but only "
                     f"{block_end - first_row + 1} are free before the next week at "
                     f"row {block_end + 1}. Insert "
                     f"{len(recs) - (block_end - first_row + 1)} row(s) below row "
                     f"{block_end} first, then re-run.")
        clear_to = block_end
    elif existing and not a.force:
        sys.exit(f"ERROR: week starting {start_cell} is already in '{TAB}' at row "
                 f"{min(existing)}. Use --replace to rewrite it in place, or "
                 f"--force to append a second copy. (Weeks are frozen once computed "
                 f"— Smartlead category tags mutate, so recomputing history "
                 f"silently changes past numbers.)")
    else:
        first_row = last_filled + 2 if has_data else header_idx + 2  # blank separator

    recs = recs + [totals_row(colmap, first_row, first_row + len(recs) - 1)]

    values = []
    for rec in recs:
        row = [""] * width
        for key, idx in colmap.items():
            if key in rec:
                row[idx] = rec[key]
        values.append(row)

    rng = (f"'{TAB}'!A{first_row}:"
           f"{col_letter(width - 1)}{first_row + len(values) - 1}")

    if a.dry_run:
        used = ", ".join(f"{col_letter(i)}={k}" for k, i in sorted(colmap.items(),
                                                                  key=lambda x: x[1]))
        print(f"[sheet] header row {header_idx + 1}; mapped {used}")
        print(f"[sheet] would {'replace' if clear_to is not None else 'append'} "
              f"{len(values)} row(s) at {rng}")
        for row in values:
            print("   " + " | ".join((c or "")[:24] if isinstance(c, str) else str(c)
                                     for c in row))
        return

    if clear_to is not None and clear_to >= first_row:
        old_rng = (f"'{TAB}'!A{first_row}:"
                   f"{col_letter(width - 1)}{max(clear_to, first_row + len(values) - 1)}")
        gapi(token, "POST", f"{base}/values/{enc(old_rng)}:clear", {})

    gapi(token, "PUT",
         f"{base}/values/{enc(rng)}?valueInputOption=USER_ENTERED",
         {"range": rng, "majorDimension": "ROWS", "values": values})
    verb = "replaced" if clear_to is not None else "appended"
    print(f"[sheet] {verb} {len(values)} row(s) for {label} starting row "
          f"{first_row} ({data['summary']['same_week']} SAME / "
          f"{data['summary']['prev_week']} PREV)")
    print(f"[sheet] https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid={GID}")


if __name__ == "__main__":
    main()
