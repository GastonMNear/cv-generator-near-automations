#!/usr/bin/env python3
"""
Search for lead record by email in Clay table
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

# Field IDs
EMAIL_FIELD_ID = "f_0t063y8WdAS99js4V3X"  # Find Work Email
LINKEDIN_FIELD_ID = "f_0t06147KZtafpAaiDTz"  # Job LinkedIn URL
NAME_FIELD_ID = "f_0t06398Jpx33mhUdC2F"  # Recruiter Name (uncleaned)

# Target email
TARGET_EMAIL = "leslie@zamorausa.com"
TARGET_EMAIL_LOWER = TARGET_EMAIL.lower()

BATCH_SIZE = 100

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
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "details": error_body}

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
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "details": error_body}

def extract_cell_value(cell):
    """Extract value from cell object"""
    if not cell:
        return None
    if isinstance(cell, dict):
        return cell.get("value", None)
    return cell

def main():
    """Search for lead record by email"""

    # Step 1: Get all record IDs
    print(f"Fetching record IDs from view {VIEW_ID}...", file=sys.stderr)
    ids_resp = api_get(f"/tables/{TABLE_ID}/views/{VIEW_ID}/records/ids")

    if "error" in ids_resp:
        print(json.dumps({"success": False, "error": ids_resp["error"]}))
        return

    record_ids = ids_resp.get("results", [])
    print(f"✓ Total records in table: {len(record_ids)}", file=sys.stderr)

    if len(record_ids) == 0:
        print(json.dumps({"success": False, "error": "Table is empty"}))
        return

    # Step 2: Batch fetch and search
    found_record = None
    found_index = -1

    for i in range(0, len(record_ids), BATCH_SIZE):
        batch = record_ids[i:i+BATCH_SIZE]
        print(f"Searching records {i+1}-{min(i+BATCH_SIZE, len(record_ids))} of {len(record_ids)}...", file=sys.stderr)

        records_resp = api_post(
            f"/tables/{TABLE_ID}/bulk-fetch-records",
            {"recordIds": batch}
        )

        if "error" in records_resp:
            print(json.dumps({"success": False, "error": records_resp["error"]}))
            return

        results = records_resp.get("results", [])

        for idx, rec in enumerate(results):
            cells = rec.get("cells", {})
            email_cell = cells.get(EMAIL_FIELD_ID, {})
            email_value = extract_cell_value(email_cell)

            # Case-insensitive email comparison
            if email_value and isinstance(email_value, str):
                if TARGET_EMAIL_LOWER in email_value.lower():
                    found_record = rec
                    found_index = i + idx
                    print(f"✓ Lead found at position {found_index + 1}: Record ID {rec['id']}", file=sys.stderr)
                    break

        if found_record:
            break

    if not found_record:
        print(json.dumps({
            "success": False,
            "error": f"Lead email '{TARGET_EMAIL}' not found in table",
            "searched_records": len(record_ids)
        }))
        return

    # Step 3: Extract data from found record
    cells = found_record.get("cells", {})

    # Extract email
    email_value = extract_cell_value(cells.get(EMAIL_FIELD_ID, {}))

    # Extract LinkedIn URL
    linkedin_value = extract_cell_value(cells.get(LINKEDIN_FIELD_ID, {}))

    # Extract name
    name_value = extract_cell_value(cells.get(NAME_FIELD_ID, {}))

    print(f"✓ Email: {email_value}", file=sys.stderr)
    print(f"✓ Name: {name_value or 'Not specified'}", file=sys.stderr)
    print(f"✓ LinkedIn URL: {linkedin_value or 'NOT FOUND'}", file=sys.stderr)

    # Output results
    result = {
        "success": True,
        "record_id": found_record["id"],
        "position": found_index + 1,
        "total_records": len(record_ids),
        "email": email_value,
        "name": name_value,
        "linkedin_url": linkedin_value,
        "has_linkedin_url": bool(linkedin_value)
    }

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
