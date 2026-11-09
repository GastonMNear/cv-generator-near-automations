#!/usr/bin/env python3
"""For an ambiguous company: find its HubSpot bookings and pull the booker email
out of hs_meeting_body (it is not a clean property)."""
import json, os, re, html, subprocess, sys

TOKEN = os.environ["HUBSPOT_ACCESS_TOKEN"]
H = ["-H", f"Authorization: Bearer {TOKEN}", "-H", "Content-Type: application/json"]

def post(url, body):
    out = subprocess.run(["curl", "-s", "--max-time", "45", "-X", "POST", url, *H,
                          "-d", json.dumps(body)], capture_output=True, text=True).stdout
    return json.loads(out)

def get(url):
    out = subprocess.run(["curl", "-s", "--max-time", "45", url, *H],
                         capture_output=True, text=True).stdout
    return json.loads(out)

def field(body, label):
    m = re.search(rf"{label}:\s*([^\n<]+)", body)
    return m.group(1).strip() if m else None

for term in sys.argv[1:]:
    print(f"\n########## HubSpot search: {term!r}")
    r = post("https://api.hubapi.com/crm/v3/objects/companies/search",
             {"filterGroups": [{"filters": [{"propertyName": "name",
                                             "operator": "CONTAINS_TOKEN",
                                             "value": f"{term}*"}]}],
              "properties": ["name", "domain"], "limit": 10})
    for c in r.get("results", []):
        cid, props = c["id"], c["properties"]
        print(f"  company {cid} | {props.get('name')!r} | {props.get('domain')}")
        assoc = get(f"https://api.hubapi.com/crm/v4/objects/companies/{cid}/associations/meetings")
        mids = [x["toObjectId"] for x in assoc.get("results", [])]
        for mid in mids:
            m = get(f"https://api.hubapi.com/crm/v3/objects/meetings/{mid}"
                    f"?properties=hs_meeting_body,hs_createdate,hs_meeting_start_time,hs_activity_type")
            p = m.get("properties", {})
            raw = html.unescape(p.get("hs_meeting_body") or "")
            body = "\n".join(l.strip() for l in re.sub(r"<[^>]+>", "\n", raw).split("\n") if l.strip())
            if not p.get("hs_activity_type"):
                continue                       # Fathom summary, not a booking
            print(f"     booking {mid}: created={(p.get('hs_createdate') or '')[:10]} "
                  f"call={(p.get('hs_meeting_start_time') or '')[:10]}")
            print(f"        name={field(body,'First Name')} {field(body,'Last Name')} | "
                  f"email={field(body,'Email')} | company={field(body,'Company Name')}")
