#!/usr/bin/env python3
"""Per-campaign email metrics for the Monday campaign review.

    python3 campaign_metrics.py [--week-start YYYY-MM-DD] --out metrics.json

Reporting week defaults to the last full Mon–Sun week before today. Source is Outbound
metrics › 'Email Campaign Metrics (Weekly)': row 3 = week start, campaign blocks start
at an 'x' row under 'Breakdown by campaign' (row 24) and hold one row per column-B metric.

Windows (agreed with Gaston 2026-10-27): week, recent = last 4 weeks incl. the reporting
week, base = the 8 weeks before that, life = every week up to the reporting week.
Performance = calls per 1k emails sent. Campaign calls come from the sheet's campaign
rows; the official email total is the Command Center, and any gap is flagged.
"""
import argparse
import json
import math
import os
import re
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "../../weekly-volume-session/scripts"))
from fetch_metrics import COMMAND_CENTER, OUTBOUND, CC_BOOKED_ROWS, col_for, num, us, weeks_for
from slides_lib import sheet_values, token

METRICS = {"sent": "Emails sent", "calls": "Calls Booked", "replies": "Replies",
           "positives": "Positive replies", "new_leads": "New leads contacted"}
RECENT, BASE = 4, 8


def peer_group(name):
    n = name.lower()
    if re.search(r"ceo|coworker|rb2b|current clients", n):
        return "Other"
    if re.search(r"\bno hms?\b", n):
        return "No-HM"
    if re.search(r"\bhms?\b", n):
        return "HM"
    return "Other"


def window(s, cols):
    w = {k: sum(s[k][c] for c in cols) for k in METRICS}
    k = w["sent"] / 1000
    w["calls_per_1k"] = round(w["calls"] / k, 2) if k else None
    w["pos_per_1k"] = round(w["positives"] / k, 2) if k else None
    w["calls_per_pos"] = round(w["calls"] / w["positives"], 2) if w["positives"] else None
    w["weeks"] = len(cols)
    return w


def poisson_cdf(k, lam):
    return sum(math.exp(-lam) * lam ** i / math.factorial(i) for i in range(k + 1))


def surprise(observed, lam):
    """How unlikely the recent call count is if the base rate still held."""
    if lam <= 0:
        return None
    lo, hi = poisson_cdf(observed, lam), 1 - poisson_cdf(observed - 1, lam) if observed else 1.0
    return {"expected": round(lam, 1), "observed": observed,
            "p_this_low": round(lo, 3), "p_this_high": round(hi, 3)}


def parse_blocks(em, ncols):
    blocks, cur = [], None
    for i, r in enumerate(em[24:], start=25):
        if r and r[0].strip() == "x" and len(r) > 1:
            cur = {"name": " ".join(r[1].split()), "row": i,
                   "s": {k: [0] * ncols for k in METRICS}}
            blocks.append(cur)
        elif cur and len(r) > 1:
            key = next((k for k, lbl in METRICS.items() if r[1].strip() == lbl), None)
            if key:
                cur["s"][key] = [num(r[c]) or 0 if c < len(r) else 0 for c in range(ncols)]
    return blocks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--week-start", help="Monday of the reporting week (default: last full week)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    start = date.fromisoformat(a.week_start) if a.week_start else weeks_for(date.today())[0]
    if start + timedelta(days=6) >= date.today():
        print(f"WARNING: week of {start} isn't over yet, numbers are partial", file=sys.stderr)

    tok = token()
    em = sheet_values(tok, OUTBOUND, "'Email Campaign Metrics (Weekly)'!A1:CZ2000")
    cc = sheet_values(tok, COMMAND_CENTER, "'Weekly Data'!A1:CZ70")
    R = col_for(em, 3, start)
    if R is None:
        sys.exit(f"'Email Campaign Metrics (Weekly)' has no column for {us(start)}")
    first_col = 2  # column C = first week (8/4/2025)
    recent = list(range(R - RECENT + 1, R + 1))
    base = [c for c in range(R - RECENT - BASE + 1, R - RECENT + 1) if c >= first_col]
    week_starts = em[2]

    warnings, out_camps, dark = [], [], []
    for b in parse_blocks(em, R + 1):
        s = b["s"]
        lived = [c for c in range(first_col, R + 1) if s["sent"][c]]
        if not lived:
            continue
        calls_cols = [c for c in range(first_col, R + 1) if s["calls"][c]]
        last_call = week_starts[calls_cols[-1]] if calls_cols else None
        weeks_since_call = (R - calls_cols[-1]) if calls_cols else None
        row = {
            "name": b["name"], "row": b["row"], "peer": peer_group(b["name"]),
            "first_week": week_starts[lived[0]], "last_call_week": last_call,
            "weeks_since_call": weeks_since_call,
            "week": window(s, [R]), "recent": window(s, recent),
            "base": window(s, base) if base else None,
            "life": window(s, list(range(lived[0], R + 1))),
            "last12": [{"wk": week_starts[c], "sent": s["sent"][c], "calls": s["calls"][c]}
                       for c in range(max(first_col, R - 11), R + 1)],
        }
        bs = row["base"]
        if bs and bs["sent"]:
            row["vs_base"] = surprise(row["recent"]["calls"],
                                      bs["calls"] / bs["sent"] * row["recent"]["sent"])
        if s["sent"][R]:
            out_camps.append(row)
        elif any(s["sent"][c] for c in recent[:-1]):
            dark.append({k: row[k] for k in ("name", "peer", "last_call_week")} |
                        {"recent_calls": row["recent"]["calls"], "life_calls": row["life"]["calls"]})

    # Peer benchmark: pooled calls/1k over the last 12 weeks across active campaigns in
    # the group. Upside = calls/wk gained if a campaign hit its peer rate at its own volume.
    peers = {}
    for c in out_camps:
        twelve = [x for x in c["last12"]]
        c["_12"] = (sum(x["sent"] for x in twelve), sum(x["calls"] for x in twelve))
        p = peers.setdefault(c["peer"], [0, 0])
        p[0] += c["_12"][0]
        p[1] += c["_12"][1]
    peer_rate = {g: round(v[1] / v[0] * 1000, 2) for g, v in peers.items() if v[0]}
    for c in out_camps:
        sent12, calls12 = c.pop("_12")
        own = calls12 / sent12 * 1000 if sent12 else 0
        weekly_sent = c["recent"]["sent"] / RECENT
        c["rate_12w"] = round(own, 2)
        c["peer_rate_12w"] = peer_rate.get(c["peer"])
        c["upside_calls_per_wk"] = round(max(0, (peer_rate.get(c["peer"], 0) - own)) * weekly_sent / 1000, 2)

    top = {k: num(next((r[R] for r in em[:24] if len(r) > R and len(r) > 1 and r[1].strip() == lbl), ""))
           for k, lbl in METRICS.items()}
    cc_col = col_for(cc, 2, start)
    cc_email = num(cc[CC_BOOKED_ROWS["email"] - 1][cc_col]) if cc_col is not None else None
    camp_calls = sum(c["week"]["calls"] for c in out_camps)
    camp_sent = sum(c["week"]["sent"] for c in out_camps)
    if cc_email != top["calls"] or camp_calls != top["calls"]:
        warnings.append(f"Email calls: Command Center {cc_email} (official) vs sheet total "
                        f"{top['calls']} vs sum of campaign rows {camp_calls}")
    if top["sent"] and top["sent"] != camp_sent:
        warnings.append(f"{top['sent'] - camp_sent} emails sent are in no campaign row "
                        "(known open item)")

    out = {
        "week": {"start": str(start), "end": str(start + timedelta(days=6))},
        "windows": {"recent": f"{week_starts[recent[0]]}–{week_starts[recent[-1]]}",
                    "base": f"{week_starts[base[0]]}–{week_starts[base[-1]]}" if base else None},
        "totals": {"sheet": top, "command_center_email_calls": cc_email,
                   "campaign_rows_calls": camp_calls, "campaign_rows_sent": camp_sent},
        "peer_rate_12w": peer_rate,
        "campaigns": sorted(out_camps, key=lambda c: -c["week"]["sent"]),
        "went_dark": dark,
        "warnings": warnings,
    }
    json.dump(out, open(a.out, "w"), indent=2)

    print(f"Week {start} · recent {out['windows']['recent']} · base {out['windows']['base']}")
    print(f"Peer calls/1k (12w): {peer_rate}")
    hdr = f"{'campaign':48} {'peer':6} {'wk s/c':>10} {'4w s/c':>11} {'4w c/1k':>7} {'8w c/1k':>7} {'life c/1k':>9} {'p_low':>6} {'p_hi':>6} {'upside':>6} {'since':>5}"
    print(hdr)
    for c in out["campaigns"]:
        v = c.get("vs_base") or {}
        bs = c["base"] or {}
        print(f"{c['name'][:48]:48} {c['peer']:6} {c['week']['sent']:>6}/{c['week']['calls']:<3} "
              f"{c['recent']['sent']:>7}/{c['recent']['calls']:<3} {c['recent']['calls_per_1k'] or 0:>7} "
              f"{bs.get('calls_per_1k') or 0:>7} {c['life']['calls_per_1k'] or 0:>9} "
              f"{v.get('p_this_low', ''):>6} {v.get('p_this_high', ''):>6} {c['upside_calls_per_wk']:>6} "
              f"{'' if c['weeks_since_call'] is None else c['weeks_since_call']:>5}")
    if dark:
        print("Went dark (sent in prior 3 wks, 0 this week):", [d["name"] for d in dark])
    for w in warnings:
        print("WARNING:", w)


if __name__ == "__main__":
    main()
