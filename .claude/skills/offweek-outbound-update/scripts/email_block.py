#!/usr/bin/env python3
"""Print the booked-calls headline and the Email metric bullets for the off-week update.

    python3 email_block.py metrics.json

metrics.json = weekly-volume-session/scripts/fetch_metrics.py output, run with
--session-date set to the off-week Tuesday: the top level is the reporting week, "prev"
is the week before it. Numbers are formatted the way the Oct 20 update wrote them.
"""
import json
import sys


def k(n):  # 17329 -> 17.3K
    return f"{n/1000:.1f}K"


def change(new, old):  # 17329 vs 17878 -> "−3%"
    if not old:
        return ""
    p = round((new - old) / old * 100)
    return f"{'+' if p > 0 else '−' if p < 0 else '±'}{abs(p)}% "


def minutes(hms):  # "0:25" -> "25 min"
    h, m = hms.split(":")[:2]
    return f"{int(h)*60 + int(m)} min"


m = json.load(open(sys.argv[1]))
p = m["prev"]
b, pb = m["booked"], p["booked"]
tot, ptot = sum(b.values()), sum(pb.values())
print(f"• {tot} calls booked: {b['email']} email, {b['linkedin']} LinkedIn, {b['cold_calling']} cold calling "
      f"(last week {ptot}: {pb['email']} / {pb['linkedin']} / {pb['cold_calling']})")
print()
e, pe = m["email"], p["email"]
print(f"• Emails sent: {k(e['sent'])} ({change(e['sent'], pe['sent'])}vs {k(pe['sent'])})")
print(f"• Reply rate: {e['reply_rate']} (vs {pe['reply_rate']})")
print(f"• Positive replies: {e['positive']} (vs {pe['positive']})")
print(f"• Calls booked: {b['email']} (vs {pb['email']})")
rs, prs = m["reply_speed"], p["reply_speed"]
if rs and prs:
    print(f"• Median time to reply to a positive: {minutes(rs['median'])} (vs {minutes(prs['median'])})")
else:
    print("• Median time to reply to a positive: [MISSING: no Time-to-reply column for one of the weeks]")
print(f"\n(capacity {k(e['capacity'])}, unused {k(e['capacity'] - e['sent'])})", file=sys.stderr)
for w in m.get("warnings", []):
    print("WARNING:", w, file=sys.stderr)
