#!/usr/bin/env python3
"""
List all fields in Clay table to identify correct email field
"""

import urllib.request
import json
import ssl
import sys

# Session cookie from authentication
SESSION = "claysession=s%3AN0IwvD7t5LSWoQW6Wjc3vuCfFbjNsXDJ.ectFpxgbhtIRsqk%2B6kwaVh3VqaPiZG47pQg35bx%2BUzI"
TABLE_ID = "t_0t6ghvgCsvvvqAus4bp"
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
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "details": error_body}

def main():
    """List all fields in table"""

    # Get table metadata
    table_meta = api_get(f"/tables/{TABLE_ID}")
    table_info = table_meta.get("table", table_meta)
    fields = table_info.get("fields", [])

    # Create JSON output
    output = {
        "total_fields": len(fields),
        "fields": []
    }

    # Collect all fields
    for idx, f in enumerate(fields, 1):
        name = f.get("name", "Unnamed")
        field_id = f.get("id", "N/A")
        field_type = f.get("type", "unknown")

        # Flag fields that might contain email
        is_email_related = "email" in name.lower() or "contact" in name.lower() or "recruiter" in name.lower()

        output["fields"].append({
            "index": idx,
            "name": name,
            "id": field_id,
            "type": field_type,
            "email_related": is_email_related
        })

    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
