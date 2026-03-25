#!/usr/bin/env python3
"""
Fetch Clay table metadata and identify field IDs
"""

import urllib.request
import json
import ssl
import sys

# Session cookie from authentication
SESSION = "claysession=s%3AN0IwvD7t5LSWoQW6Wjc3vuCfFbjNsXDJ.ectFpxgbhtIRsqk%2B6kwaVh3VqaPiZG47pQg35bx%2BUzI"
TABLE_ID = "t_0t6ghvgCsvvvqAus4bp"
BASE = "https://api.clay.com/v3"

# Field name patterns for identification
EMAIL_PATTERNS = [
    "validated email",
    "email one",
    "email",
    "contact email",
    "work email"
]

LINKEDIN_JOB_PATTERNS = [
    "job post url",
    "job url",
    "linkedin job",
    "opening url",
    "posting url",
    "job posting"
]

NAME_PATTERNS = [
    "full name cleaned",
    "full name",
    "name",
    "contact name"
]

# Exclude patterns for LinkedIn (to avoid prospect LinkedIn)
EXCLUDE_PATTERNS = ["prospect", "person", "profile"]

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

def find_field_by_patterns(fields, patterns, exclude_patterns=None):
    """Find field ID by matching patterns"""
    for f in fields:
        name_lower = f["name"].lower()

        # Check exclude patterns first
        if exclude_patterns and any(exclude in name_lower for exclude in exclude_patterns):
            continue

        # Check if matches patterns
        for pattern in patterns:
            if pattern in name_lower:
                return {
                    "id": f["id"],
                    "name": f["name"],
                    "type": f.get("type", "unknown")
                }
    return None

def main():
    """Fetch table metadata and identify fields"""

    # Get table metadata
    print(f"Fetching table metadata for {TABLE_ID}...", file=sys.stderr)
    table_meta = api_get(f"/tables/{TABLE_ID}")

    if "error" in table_meta:
        print(json.dumps({"success": False, "error": table_meta["error"]}))
        return

    table_info = table_meta.get("table", table_meta)
    fields = table_info.get("fields", [])
    views = table_info.get("views", [])

    if not fields:
        print(json.dumps({"success": False, "error": "No fields found in table"}))
        return

    print(f"✓ Found {len(fields)} fields", file=sys.stderr)

    # Identify email field
    email_field = find_field_by_patterns(fields, EMAIL_PATTERNS)
    if email_field:
        print(f"✓ Email field: {email_field['name']} ({email_field['id']})", file=sys.stderr)
    else:
        print("⚠ Email field not identified", file=sys.stderr)

    # Identify LinkedIn job URL field
    linkedin_field = find_field_by_patterns(fields, LINKEDIN_JOB_PATTERNS, EXCLUDE_PATTERNS)
    if linkedin_field:
        print(f"✓ LinkedIn job URL field: {linkedin_field['name']} ({linkedin_field['id']})", file=sys.stderr)
    else:
        print("⚠ LinkedIn job URL field not identified", file=sys.stderr)

    # Identify name field (optional)
    name_field = find_field_by_patterns(fields, NAME_PATTERNS, ["company"])
    if name_field:
        print(f"✓ Name field: {name_field['name']} ({name_field['id']})", file=sys.stderr)
    else:
        print("⚠ Name field not identified (optional)", file=sys.stderr)

    # Get default view
    if not views:
        print(json.dumps({"success": False, "error": "No views found in table"}))
        return

    default_view = views[0]
    view_id = default_view["id"]
    print(f"✓ Default view: {view_id} ({default_view.get('name', 'Unnamed')})", file=sys.stderr)

    # Output results
    result = {
        "success": True,
        "table_id": TABLE_ID,
        "table_name": table_info.get("name", "Unknown"),
        "total_fields": len(fields),
        "view_id": view_id,
        "email_field": email_field,
        "linkedin_field": linkedin_field,
        "name_field": name_field,
        "all_fields": [{"id": f["id"], "name": f["name"], "type": f.get("type")} for f in fields[:20]]  # First 20 for reference
    }

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
