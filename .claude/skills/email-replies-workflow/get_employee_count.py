#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Get employee count for a specific lead from Clay table
"""

import urllib.request
import json
import ssl
import os
import sys
import io
from dotenv import load_dotenv

# Fix Windows console encoding for Unicode
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Load environment variables
load_dotenv()
CLAY_USERNAME = os.getenv("CLAY_USERNAME")
CLAY_PASSWORD = os.getenv("CLAY_PASSWORD")

# Configuration
TABLE_ID = "t_0taasak5KAa5zbTmTJd"  # Canada Open Jobs | No HM
LEAD_EMAIL = "ashley.pomeranz@ehousestudio.com"
RECORD_ID = "r_0tb2o06yv2AyssMSGTv"  # From previous search

# Create SSL context
ctx = ssl.create_default_context()
BASE = "https://api.clay.com/v3"

def api_post(session, path, data):
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(data).encode(),
        headers={
            "Cookie": session,
            "Content-Type": "application/json"
        },
        method="POST"
    )
    return json.loads(urllib.request.urlopen(req, context=ctx).read())

def api_get(session, path):
    req = urllib.request.Request(
        f"{BASE}{path}",
        headers={"Cookie": session}
    )
    return json.loads(urllib.request.urlopen(req, context=ctx).read())

def authenticate():
    print("Authenticating with Clay...")
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
    cookie_header = resp.headers.get("Set-Cookie", "")
    session = cookie_header.split(";")[0]
    print("✓ Authenticated\n")
    return session

def main():
    session = authenticate()

    # Get table metadata to see all fields
    print(f"Fetching table metadata...")
    table_meta = api_get(session, f"/tables/{TABLE_ID}")
    table_info = table_meta.get("table", table_meta)
    fields = table_info.get("fields", [])

    # Build field map
    field_map = {f["id"]: f["name"] for f in fields}

    # Look for employee count related fields
    print("Looking for employee count related fields...\n")
    employee_fields = []
    for f in fields:
        name_lower = f["name"].lower()
        if any(keyword in name_lower for keyword in ["employee", "size", "headcount", "staff", "people"]):
            employee_fields.append((f["id"], f["name"]))
            print(f"  Found: {f['name']} ({f['id']})")

    if not employee_fields:
        print("  No employee count fields found\n")
    else:
        print()

    # Fetch the specific record
    print(f"Fetching record for {LEAD_EMAIL}...")
    records_resp = api_post(
        session,
        f"/tables/{TABLE_ID}/bulk-fetch-records",
        {"recordIds": [RECORD_ID]}
    )

    results = records_resp.get("results", [])
    if not results:
        print("Record not found!")
        return

    record = results[0]
    cells = record.get("cells", {})

    print(f"✓ Record found\n")
    print("=" * 60)
    print("EMPLOYEE COUNT / COMPANY SIZE DATA")
    print("=" * 60)

    if employee_fields:
        for field_id, field_name in employee_fields:
            cell = cells.get(field_id, {})
            value = cell.get("value", "N/A") if isinstance(cell, dict) else "N/A"
            print(f"\n{field_name}: {value}")
    else:
        print("\nNo employee count fields found in this table.")
        print("Showing all company-related fields instead:\n")

        for field_id, field_name in field_map.items():
            if "company" in field_name.lower() or "organization" in field_name.lower():
                cell = cells.get(field_id, {})
                value = cell.get("value", "N/A") if isinstance(cell, dict) else "N/A"
                # Only show if value exists and isn't too long
                if value and value != "N/A" and len(str(value)) < 200:
                    print(f"{field_name}: {value}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
