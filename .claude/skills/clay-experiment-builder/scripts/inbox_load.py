"""Inbox load (read-only): capacity of a campaign's inbox set vs every ACTIVE campaign sharing it.

  python3 inbox_load.py <campaign_id> [<campaign_id> …]

The first ID defines the inbox set. Prints capacity (sum of message_per_day), today's sent count,
the given campaigns' caps, and every active campaign that shares inboxes (overlap, cap). ~1 GET per
active campaign, so it takes a minute or two.
"""
import sys, time
from sl import get

ids = [int(x) for x in sys.argv[1:]]
accs = get(f"/campaigns/{ids[0]}/email-accounts")
pool = {a["id"] for a in accs}
cap = sum(a.get("message_per_day") or 0 for a in accs)
sent = sum(int(a.get("daily_sent_count") or 0) for a in accs)
allc = get("/campaigns/")
active = [c for c in allc if c["status"] == "ACTIVE"]
mine = {c["id"]: c for c in allc if c["id"] in ids}
print(f"inbox set: {len(pool)} inboxes, capacity {cap}/day, sent today {sent}")
print(f"given campaigns: {len(ids)}, sum of max_leads_per_day {sum(c.get('max_leads_per_day') or 0 for c in mine.values())}")
share = []
for c in active:
    try:
        ov = len(pool & {a["id"] for a in get(f"/campaigns/{c['id']}/email-accounts")})
    except SystemExit:
        ov = None
    if ov:
        share.append((ov, c))
    time.sleep(0.25)
full = [c for ov, c in share if ov == len(pool) and not c.get("parent_campaign_id")]
print(f"active campaigns sharing these inboxes: {len(share)} (parents using all of them: {len(full)}, their caps sum {sum(c.get('max_leads_per_day') or 0 for c in full)})")
for ov, c in sorted(share, key=lambda x: -x[0])[:40]:
    print(f"  {c['id']} overlap {ov} cap {c.get('max_leads_per_day')} {'SUB ' if c.get('parent_campaign_id') else ''}{c['name'][:80]}")
