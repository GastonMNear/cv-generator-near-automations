#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Search for similar emails in the table
"""

import urllib.request
import json
import ssl
import os
from dotenv import load_dotenv

load_dotenv()

CLAY_USERNAME = os.getenv("CLAY_USERNAME")
CLAY_PASSWORD = os.getenv("CLAY_PASSWORD")
BASE = "https://api.clay.com/v3"
TABLE_ID = "t_0t5pvx3g4o5WfysopqA"
TARGET_EMAIL = "markb@pipe.org"

ctx = ssl.create_default_context()

if os.sys.platform == "win32":
    os.sys.stdout.reconfigure(encoding='utf-8')

# Authenticate
login_data = json.dumps({
    "email": CLAY_USERNAME,
    "password": CLAY_PASSWORD,
    "source": "web"
}).encode()

req = urllib.request.Request(
    f"{BASE}/auth/login",
    data=login_data,
    headers={
        "Content-Type": "application/json",
        "Origin": "https://app.clay.com",
        "Referer": "https://app.clay.com/"
    },
    method="POST"
)

resp = urllib.request.urlopen(req, context=ctx)
session = resp.headers.get("Set-Cookie", "").split(";")[0]

def api_get(path):
    r = urllib.request.Request(f"{BASE}{path}", headers={"Cookie": session})
    return json.loads(urllib.request.urlopen(r, context=ctx).read())

def api_post(path, data):
    r = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(data).encode(),
        headers={"Cookie": session, "Content-Type": "application/json"},
        method="POST"
    )
    return json.loads(urllib.request.urlopen(r, context=ctx).read())

print(f"Searching for emails similar to: {TARGET_EMAIL}")
print(f"Target domain: pipe.org")
print(f"Target username: markb")
print()

# Get table metadata
table_meta = api_get(f"/tables/{TABLE_ID}")
table_info = table_meta.get("table", table_meta)
fields = table_info.get("fields", [])
views = table_info.get("views", [])

field_map = {}
for f in fields:
    field_map[f["id"]] = f["name"]

view_id = views[0]["id"]

# Get record IDs
ids_resp = api_get(f"/tables/{TABLE_ID}/views/{view_id}/records/ids")
record_ids = ids_resp.get("results", [])

print(f"Total records: {len(record_ids)}")
print(f"Searching for emails containing 'pipe' or 'markb'...\n")

# Search first 1000 records for similar emails
BATCH_SIZE = 100
found_emails = []

for i in range(0, min(1000, len(record_ids)), BATCH_SIZE):
    batch = record_ids[i:i+BATCH_SIZE]
    records = api_post(f"/tables/{TABLE_ID}/bulk-fetch-records", {"recordIds": batch})
    results = records.get("results", [])

    for rec in results:
        cells = rec.get("cells", {})

        # Check all cells for emails containing our search terms
        for fid, cell in cells.items():
            val = cell.get("value", "") if isinstance(cell, dict) else ""

            if isinstance(val, str):
                val_lower = val.lower()
                if "pipe" in val_lower or "markb" in val_lower or "@pipe.org" in val_lower:
                    field_name = field_map.get(fid, fid)
                    found_emails.append({
                        "field": field_name,
                        "value": val,
                        "record_id": rec['id']
                    })
                    print(f"Found: {val} in field '{field_name}' (Record: {rec['id']})")

if not found_emails:
    print("\n❌ No emails found containing 'pipe' or 'markb' in first 1000 records")
    print("\nLet me show a sample record to see what the data looks like...")

    # Get one sample record
    if record_ids:
        sample = api_post(f"/tables/{TABLE_ID}/bulk-fetch-records", {"recordIds": [record_ids[0]]})
        if sample.get("results"):
            rec = sample["results"][0]
            cells = rec.get("cells", {})
            print(f"\nSample record ({rec['id']}):")
            for fid, cell in list(cells.items())[:10]:
                val = cell.get("value", "") if isinstance(cell, dict) else ""
                if val:
                    fname = field_map.get(fid, fid)
                    if len(str(val)) > 80:
                        val = str(val)[:80] + "..."
                    print(f"  {fname}: {val}")
else:
    print(f"\n✓ Found {len(found_emails)} matching email(s)")
