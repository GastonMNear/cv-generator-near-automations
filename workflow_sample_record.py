#!/usr/bin/env python3
"""
Fetch a sample record to inspect email fields
"""

import urllib.request
import json
import ssl
import sys

# Session cookie from authentication
SESSION = "claysession=s%3AN0IwvD7t5LSWoQW6Wjc3vuCfFbjNsXDJ.ectFpxgbhtIRsqk%2B6kwaVh3VqaPiZG47pQg35bx%2BUzI"
TABLE_ID = "t_0t6ghvgCsvvvqAus4bp"
VIEW_ID = "gv_TgwDWXPdg8Ci"
BASE = "https://api.clay.com/v3"

def api_get(path):
    """Make GET request to Clay API"""
    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        f"{BASE}{path}",
        headers={"Cookie": SESSION}
    )
    try:
        resp = urllib.request.urlopen(req, context=ctx)
        return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        return {"error": str(e)}

def api_post(path, data):
    """Make POST request to Clay API"""
    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(data).encode(),
        headers={
            "Cookie": SESSION,
            "Content-Type": "application/json"
        },
        method="POST"
    )
    try:
        resp = urllib.request.urlopen(req, context=ctx)
        return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        return {"error": str(e)}

def extract_value(cell):
    """Extract value from cell"""
    if not cell or not isinstance(cell, dict):
        return None
    return cell.get("value")

def main():
    """Fetch sample records and inspect email fields"""

    # Get record IDs
    ids_resp = api_get(f"/tables/{TABLE_ID}/views/{VIEW_ID}/records/ids")
    record_ids = ids_resp.get("results", [])[:50]  # Get first 50

    # Fetch first batch
    records_resp = api_post(f"/tables/{TABLE_ID}/bulk-fetch-records", {"recordIds": record_ids})
    results = records_resp.get("results", [])

    if not results:
        print(json.dumps({"error": "No records found"}))
        return

    # Get first 3 records with email data
    samples = []
    for rec in results[:10]:
        cells = rec.get("cells", {})

        # Extract various email fields
        sample = {
            "record_id": rec["id"],
            "emails": {}
        }

        # Check multiple email field patterns
        for field_id, field_value in cells.items():
            # Get field name from metadata (we'll just use IDs for now)
            value = extract_value(field_value)
            if value and "@" in str(value):
                sample["emails"][field_id] = value

        if sample["emails"]:
            samples.append(sample)
            if len(samples) >= 3:
                break

    print(json.dumps({"sample_records": samples}, indent=2))

if __name__ == "__main__":
    main()
