#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Search for email across ALL fields in Clay table
"""

import urllib.request
import json
import ssl
import sys
import os
from dotenv import load_dotenv

load_dotenv()

CLAY_USERNAME = os.getenv("CLAY_USERNAME")
CLAY_PASSWORD = os.getenv("CLAY_PASSWORD")
BASE = "https://api.clay.com/v3"
TABLE_ID = "t_0t5pvx3g4o5WfysopqA"
TARGET_EMAIL = "markb@pipe.org"

ctx = ssl.create_default_context()

# Fix encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

print(f"Searching for: {TARGET_EMAIL}")

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
print(f"Searching ALL fields for email...\n")

# Search in batches
BATCH_SIZE = 100
TARGET_EMAIL_LOWER = TARGET_EMAIL.lower()
found = None

for i in range(0, min(500, len(record_ids)), BATCH_SIZE):
    batch = record_ids[i:i+BATCH_SIZE]
    records = api_post(f"/tables/{TABLE_ID}/bulk-fetch-records", {"recordIds": batch})
    results = records.get("results", [])

    for rec in results:
        cells = rec.get("cells", {})

        # Check ALL cells for email
        for fid, cell in cells.items():
            val = cell.get("value", "") if isinstance(cell, dict) else ""

            if isinstance(val, str) and TARGET_EMAIL_LOWER in val.lower():
                found = rec
                field_name = field_map.get(fid, fid)
                print(f"\n✓✓✓ FOUND in field: {field_name} ({fid})")
                print(f"    Value: {val}")
                print(f"    Record ID: {rec['id']}")

                # Print all relevant fields from this record
                print(f"\n{'='*60}")
                print(f"ALL FIELDS FOR THIS RECORD:")
                print(f"{'='*60}")

                for fid2, cell2 in cells.items():
                    val2 = cell2.get("value", "") if isinstance(cell2, dict) else ""
                    if val2:  # Only print non-empty fields
                        fname = field_map.get(fid2, fid2)
                        if len(str(val2)) > 100:
                            val2 = str(val2)[:100] + "..."
                        print(f"{fname}: {val2}")

                break

        if found:
            break

    if found:
        break

    print(f"Searched {min(i+BATCH_SIZE, len(record_ids))} records...")

if not found:
    print(f"\n❌ Email not found in first 500 records")
    print("Trying partial domain search...")

    # Try searching just for the domain
    domain = TARGET_EMAIL.split("@")[1]
    print(f"Searching for domain: {domain}")
