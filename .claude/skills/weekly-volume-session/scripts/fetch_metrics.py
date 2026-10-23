#!/usr/bin/env python3
"""Pull every sheet-based number the volume session deck needs, for the two Mon–Sun
weeks it shows: the reporting week ("last week") and the one before it ("previous week").

    python3 fetch_metrics.py --session-date 2026-10-27 --out metrics.json

The session is bi-weekly, so the previous week was never on a deck. Both weeks are read
from the sheets; nothing is carried over from the last deck.

Dashboard numbers (qualified rate, quarterly cost / value) are NOT fetched here. The
CAC dashboard is a JS app, so the agent reads it in the browser and adds them to
metrics.json under "dashboard" (see SKILL.md).

Rows are found by their column-B label wherever the sheet has one. The Command Center
booked-call rows (61/62/63) have no label, so those row numbers are fixed. If the
Command Center layout changes, update CC_BOOKED_ROWS.
"""
import argparse
import json
import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slides_lib import sheet_values, token

COMMAND_CENTER = "1bQQnsUQy1SqTnBhfAacu0szycyBN7SIM9bcIqtLQlBM"
OUTBOUND = "1Wklpdze9UReMsTxTtpYNs0dq6-xXYTeleHSn67te4wo"
CC_BOOKED_ROWS = {"email": 61, "linkedin": 62, "cold_calling": 63}  # 1-based, 'Weekly Data'


def us(d):
    return f"{d.month}/{d.day}/{d.year}"


def col_for(rows, header_row, start):
    hdr = rows[header_row - 1]
    for i, v in enumerate(hdr):
        if v.strip() == us(start):
            return i
    return None


def by_label(rows, label, col, first_only=True):
    """Value in `col` on the first row whose column B equals `label`."""
    for r in rows:
        if len(r) > 1 and r[1].strip() == label:
            return r[col] if col < len(r) else ""
    return None


def num(v):
    v = (v or "").replace(",", "").strip()
    try:
        return int(float(v))
    except ValueError:
        return None


def weeks_for(session):
    """Mondays of the reporting week (the last full Mon–Sun week that ended before the
    session) and of the week before it. Tue 2026-10-27 -> Oct 19–25 and Oct 12–18."""
    last_sun = session - timedelta(days=(session.weekday() + 1) % 7 or 7)
    last_mon = last_sun - timedelta(days=6)
    return last_mon, last_mon - timedelta(days=7)


def load_sheets(tok):
    return {
        "cc": sheet_values(tok, COMMAND_CENTER, "'Weekly Data'!A1:CZ70"),
        "em": sheet_values(tok, OUTBOUND, "'Email Campaign Metrics (Weekly)'!A1:CZ2000"),
        "tt": sheet_values(tok, OUTBOUND, "'Email Time-to-reply tracker'!A1:CZ15"),
        "ccw": sheet_values(tok, OUTBOUND, "'Cold Calling (Weekly)'!A1:CZ20"),
    }


def fetch_week(sh, start):
    end = start + timedelta(days=6)
    out = {"week": {"start": str(start), "end": str(end)}, "warnings": []}

    # 1. Booked calls per channel: Command Center > Weekly Data, header row 2 = week start
    cc = sh["cc"]
    c = col_for(cc, 2, start)
    if c is None:
        sys.exit(f"Command Center 'Weekly Data' has no column for week starting {us(start)}")
    out["booked"] = {ch: num(cc[r - 1][c] if c < len(cc[r - 1]) else "") for ch, r in CC_BOOKED_ROWS.items()}

    # 2. Email weekly metrics + per-campaign sends: Outbound metrics, header row 3 = start
    em = sh["em"]
    c = col_for(em, 3, start)
    if c is None:
        sys.exit(f"'Email Campaign Metrics (Weekly)' has no column for {us(start)}")
    key = em[:24]  # 'Key Metrics' block sits above 'Breakdown by campaign' (row 24)
    out["email"] = {
        "sent": num(by_label(key, "Emails sent", c)),
        "capacity": num(by_label(key, "Email Capacity", c)),
        "reply_rate": by_label(key, "Reply Rate", c),
        "positive": num(by_label(key, "Positive replies", c)),
        "booked_outbound_sheet": num(by_label(key, "Calls Booked", c)),  # info only: deck uses Command Center
    }
    camps, current = [], None
    for i, r in enumerate(em[24:], start=25):
        if r and r[0].strip() == "x" and len(r) > 1:
            current = r[1].strip()
        elif len(r) > 1 and r[1].strip() == "Emails sent":
            n = num(r[c] if c < len(r) else "")
            if n:  # a block with no campaign header (e.g. row 610) gets flagged, not merged
                camps.append({"name": current or f"(unnamed block, row {i})", "sent": n})
            current = None
    out["campaigns"] = camps
    out["unassigned_sends"] = out["email"]["sent"] - sum(x["sent"] for x in camps)

    # 3. Reply speed: 'Email Time-to-reply tracker', header row 2 = start
    tt = sh["tt"]
    c = col_for(tt, 2, start)
    if c is None:
        out["warnings"].append("Time-to-reply tracker has no column for this week")
        out["reply_speed"] = None
    else:
        out["reply_speed"] = {
            "lt5": by_label(tt, "% Replies in <5 min", c),
            "lt10": by_label(tt, "% Replies in <10 min", c),
            "median": by_label(tt, "Median Time to Reply", c),
        }

    # 4. Cold calling dials: 'Cold Calling (Weekly)', header row 3 = start
    ccw = sh["ccw"]
    c = col_for(ccw, 3, start)
    dials = num(by_label(ccw, "Dials", c)) if c is not None else None
    if not dials:  # 0 means the sheet wasn't filled, not a week with no calls
        out["warnings"].append(f"Cold Calling (Weekly) shows {dials!r} dials for this week: cell left blank")
    out["cold_calling"] = {"dials": dials}

    if out["email"]["booked_outbound_sheet"] != out["booked"]["email"]:
        out["warnings"].append(
            f"Email booked: Command Center {out['booked']['email']} vs Outbound sheet "
            f"{out['email']['booked_outbound_sheet']}. Deck uses Command Center.")
    if out["unassigned_sends"]:
        out["warnings"].append(f"{out['unassigned_sends']} emails sent are not in any campaign "
                               "breakdown row: added to Open Jobs (open item, source unknown)")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--session-date", required=True, help="date of the meeting, YYYY-MM-DD")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    session = date.fromisoformat(a.session_date)
    last, prev = weeks_for(session)
    print(f"Session {session:%a %b %d}: last week starts {last}, previous week starts {prev}", file=sys.stderr)
    if last + timedelta(days=6) >= date.today():
        print(f"WARNING: the week of {last} isn't over yet, so its numbers are partial", file=sys.stderr)
    sh = load_sheets(token())
    out = {"session_date": str(session), **fetch_week(sh, last)}
    out["prev"] = fetch_week(sh, prev)
    out["warnings"] += [f"Previous week: {w}" for w in out["prev"].pop("warnings")]
    json.dump(out, open(a.out, "w"), indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
