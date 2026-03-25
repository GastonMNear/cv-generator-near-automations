#!/usr/bin/env python3
"""
Diagnostic: Search for email across ALL fields
"""
import urllib.request
import json
import ssl
import sys
import os
from dotenv import load_dotenv

load_dotenv()

LEAD_EMAIL = "william@longevity-x.com"
TABLE_ID = "t_aNvk4jWMNeG7"

CLAY_USERNAME = os.getenv("CLAY_USERNAME")
CLAY_PASSWORD = os.getenv("CLAY_PASSWORD")

ctx = ssl.create_default_context()
BASE = "https://api.clay.com/v3"

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
print("[OK] Authenticated")

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
print(f"[METADATA] Fetching table metadata...")
table_meta = api_get(f"/tables/{TABLE_ID}")
table_info = table_meta.get("table", table_meta)
fields = table_info.get("fields", [])
views = table_info.get("views", [])

# Build field map
field_map = {}
email_fields = []
for f in fields:
    field_map[f["id"]] = f["name"]
    name_lower = f["name"].lower()
    if "email" in name_lower or "mail" in name_lower:
        email_fields.append(f)

print(f"\n[FOUND] {len(email_fields)} email-related fields:")
for f in email_fields:
    print(f"  {f['id']} — {f['name']}")

# Get view and records
default_view = views[0]
view_id = default_view["id"]

ids_resp = api_get(f"/tables/{TABLE_ID}/views/{view_id}/records/ids")
record_ids = ids_resp.get("results", [])
print(f"\n[SEARCH] Total records: {len(record_ids)}")
print(f"[SEARCH] Searching for: {LEAD_EMAIL}")
print(f"[SEARCH] Checking ALL fields (not just email fields)...\n")

# Search ALL fields
BATCH_SIZE = 100
found_record = None
TARGET_EMAIL = LEAD_EMAIL.lower()
matched_field = None

for i in range(0, len(record_ids), BATCH_SIZE):
    batch = record_ids[i:i+BATCH_SIZE]
    print(f"Searching records {i+1}-{min(i+BATCH_SIZE, len(record_ids))} of {len(record_ids)}...")

    records_resp = api_post(f"/tables/{TABLE_ID}/bulk-fetch-records", {"recordIds": batch})
    results = records_resp.get("results", [])

    for rec in results:
        cells = rec.get("cells", {})
        # Check ALL cells
        for fid, cell in cells.items():
            val = cell.get("value", "") if isinstance(cell, dict) else ""
            if isinstance(val, str) and TARGET_EMAIL in val.lower():
                found_record = rec
                matched_field = fid
                print(f"\n[FOUND] Record ID: {rec['id']}")
                print(f"[FOUND] Matched in field: {field_map.get(fid, fid)}")
                break
        if found_record:
            break

    if found_record:
        break

if not found_record:
    print(f"\n[NOT FOUND] Email '{LEAD_EMAIL}' not found in any field")
    print(f"\n[SUGGESTION] Check:")
    print(f"  1. Email spelling")
    print(f"  2. Correct table (try other LatAm tables)")
    print(f"  3. Email domain only: @longevity-x.com")
    sys.exit(1)

# Extract all data
print(f"\n{'='*60}")
print(f"RECORD DATA")
print(f"{'='*60}")

cells = found_record.get("cells", {})

# Show email fields
print(f"\nEMAIL FIELDS:")
for f in email_fields:
    cell = cells.get(f["id"], {})
    val = cell.get("value", "") if isinstance(cell, dict) else ""
    if val:
        print(f"  {f['name']}: {val}")

# Show LinkedIn fields
print(f"\nLINKEDIN FIELDS:")
for fid, cell in cells.items():
    name = field_map.get(fid, fid)
    if "linkedin" in name.lower() or "job" in name.lower() and "url" in name.lower():
        val = cell.get("value", "") if isinstance(cell, dict) else ""
        if val:
            print(f"  {name}: {val}")

# Show name fields
print(f"\nNAME FIELDS:")
for fid, cell in cells.items():
    name = field_map.get(fid, fid)
    name_lower = name.lower()
    if ("name" in name_lower or "first" in name_lower or "last" in name_lower) and "company" not in name_lower:
        val = cell.get("value", "") if isinstance(cell, dict) else ""
        if val:
            print(f"  {name}: {val}")

print(f"\n{'='*60}")
