#!/usr/bin/env python3
"""Find HubSpot contacts at an email domain and print their bookings (from hs_meeting_body)."""
import json, os, re, html, subprocess, sys

TOKEN = os.environ["HUBSPOT_ACCESS_TOKEN"]
H = ["-H", f"Authorization: Bearer {TOKEN}", "-H", "Content-Type: application/json"]

def post(url, body):
    return json.loads(subprocess.run(["curl", "-s", "--max-time", "45", "-X", "POST", url, *H,
                                      "-d", json.dumps(body)], capture_output=True, text=True).stdout)
def get(url):
    return json.loads(subprocess.run(["curl", "-s", "--max-time", "45", url, *H],
                                     capture_output=True, text=True).stdout)
def field(body, label):
    m = re.search(rf"{label}:\s*([^\n<]+)", body)
    return m.group(1).strip() if m else None

for dom in sys.argv[1:]:
    print(f"\n########## contacts at {dom}")
    r = post("https://api.hubapi.com/crm/v3/objects/contacts/search",
             {"filterGroups": [{"filters": [{"propertyName": "email", "operator": "CONTAINS_TOKEN",
                                             "value": f"*@{dom}"}]}],
              "properties": ["email", "firstname", "lastname", "company", "createdate"], "limit": 20})
    res = r.get("results", [])
    if not res: print("   none |", str(r)[:200])
    for c in res:
        p = c["properties"]
        print(f"  contact {c['id']} | {p.get('firstname')} {p.get('lastname')} | {p.get('email')} "
              f"| co={p.get('company')} | created={(p.get('createdate') or '')[:10]}")
        assoc = get(f"https://api.hubapi.com/crm/v4/objects/contacts/{c['id']}/associations/meetings")
        for x in assoc.get("results", []):
            m = get(f"https://api.hubapi.com/crm/v3/objects/meetings/{x['toObjectId']}"
                    f"?properties=hs_meeting_body,hs_createdate,hs_meeting_start_time,hs_activity_type")
            pr = m.get("properties", {})
            if not pr.get("hs_activity_type"): continue
            raw = html.unescape(pr.get("hs_meeting_body") or "")
            body = "\n".join(l.strip() for l in re.sub(r"<[^>]+>", "\n", raw).split("\n") if l.strip())
            print(f"     BOOKING created={(pr.get('hs_createdate') or '')[:10]} "
                  f"call={(pr.get('hs_meeting_start_time') or '')[:10]} "
                  f"| {field(body,'First Name')} {field(body,'Last Name')} "
                  f"| {field(body,'Email')} | {field(body,'Company Name')}")
