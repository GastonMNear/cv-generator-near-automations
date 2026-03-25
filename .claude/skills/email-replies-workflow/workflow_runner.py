#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Email Replies Workflow Runner
Fetches lead data from Clay, extracts LinkedIn job URL, prepares for CV generation
"""

import urllib.request
import json
import ssl
import os
import sys
import re
from dotenv import load_dotenv

# Fix Windows console encoding for Unicode
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Load environment variables
load_dotenv()
CLAY_USERNAME = os.getenv("CLAY_USERNAME")
CLAY_PASSWORD = os.getenv("CLAY_PASSWORD")

# Configuration
WORKSPACE_ID = "447061"
TABLE_ID = "t_0taasak5KAa5zbTmTJd"  # Canada Open Jobs | No HM
LEAD_EMAIL = "ashley.pomeranz@ehousestudio.com"

# Create SSL context
ctx = ssl.create_default_context()
BASE = "https://api.clay.com/v3"

def api_post(session, path, data):
    """POST request to Clay API"""
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
    """GET request to Clay API"""
    req = urllib.request.Request(
        f"{BASE}{path}",
        headers={"Cookie": session}
    )
    return json.loads(urllib.request.urlopen(req, context=ctx).read())

def authenticate():
    """Authenticate with Clay API"""
    print("🔐 Authenticating with Clay...")

    if not CLAY_USERNAME or not CLAY_PASSWORD:
        raise ValueError("Missing Clay credentials. Set CLAY_USERNAME and CLAY_PASSWORD in .env")

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

    if not session.startswith("claysession="):
        raise ValueError("Clay authentication failed: invalid session cookie")

    print("✓ Authentication successful\n")
    return session

def fetch_table_metadata(session):
    """Fetch table metadata and build field map"""
    print(f"📋 Fetching table metadata for {TABLE_ID}...")

    table_meta = api_get(session, f"/tables/{TABLE_ID}")
    table_info = table_meta.get("table", table_meta)
    fields = table_info.get("fields", [])
    views = table_info.get("views", [])

    if not fields:
        raise ValueError(f"Table {TABLE_ID} has no fields")

    if not views:
        raise ValueError(f"Table {TABLE_ID} has no views")

    # Build field map
    field_map = {f["id"]: f["name"] for f in fields}
    view_id = views[0]["id"]

    print(f"✓ Found {len(fields)} fields")
    print(f"✓ Default view: {view_id}\n")

    return fields, field_map, view_id

def resolve_fields(fields):
    """Identify email, LinkedIn URL, and name fields"""
    print("🔍 Resolving field IDs...")

    # Email field patterns (priority ordered)
    EMAIL_PATTERNS = ["validated email", "email one", "email", "contact email", "work email"]

    # LinkedIn job URL patterns (exclude prospect patterns)
    LINKEDIN_PATTERNS = ["job post url", "job linkedin url", "job url", "linkedin job", "opening url", "posting url"]
    EXCLUDE_PATTERNS = ["prospect", "person", "profile"]

    # Name patterns
    NAME_PATTERNS = ["full name cleaned", "full name", "name", "contact name"]

    email_fields = []  # Track all email fields
    linkedin_field = None
    name_field = None

    # Find ALL email fields (we'll search across all of them)
    for f in fields:
        name_lower = f["name"].lower()
        for pattern in EMAIL_PATTERNS:
            if pattern in name_lower:
                email_fields.append((f["id"], f["name"]))
                print(f"✓ Email field: {f['name']} ({f['id']})")
                break

    # Find LinkedIn URL field
    for f in fields:
        name_lower = f["name"].lower()
        # Skip prospect/lead LinkedIn fields
        if any(exclude in name_lower for exclude in EXCLUDE_PATTERNS):
            continue
        # Also skip if it's explicitly about lead or company
        if "lead" in name_lower or "company" in name_lower:
            continue
        for pattern in LINKEDIN_PATTERNS:
            if pattern in name_lower:
                linkedin_field = (f["id"], f["name"])
                print(f"✓ LinkedIn job URL field: {f['name']} ({f['id']})")
                break
        if linkedin_field:
            break

    # Find name field (optional)
    for f in fields:
        name_lower = f["name"].lower()
        if "company" in name_lower:
            continue
        for pattern in NAME_PATTERNS:
            if pattern in name_lower:
                name_field = (f["id"], f["name"])
                print(f"✓ Name field: {f['name']} ({f['id']})")
                break
        if name_field:
            break

    if not email_fields:
        text_fields = [f for f in fields if f.get("type") in ["text", "formula"]][:5]
        field_list = "\n".join([f"  - {f['name']} ({f['id']})" for f in text_fields])
        raise ValueError(f"Could not identify email field. Text fields:\n{field_list}")

    if not linkedin_field:
        url_fields = []
        for f in fields:
            name_lower = f["name"].lower()
            if ("url" in name_lower or "link" in name_lower) and \
               not any(exclude in name_lower for exclude in EXCLUDE_PATTERNS):
                url_fields.append(f)

        field_list = "\n".join([f"  - {f['name']} ({f['id']})" for f in url_fields[:5]])
        raise ValueError(f"Could not identify LinkedIn job URL field. URL fields:\n{field_list}")

    print()
    return email_fields, linkedin_field, name_field

def search_lead(session, view_id, email_field_ids):
    """Search for lead record by email across multiple email fields"""
    print(f"🔍 Searching for lead: {LEAD_EMAIL}...")
    print(f"   Searching across {len(email_field_ids)} email field(s)")

    # Get all record IDs
    ids_resp = api_get(session, f"/tables/{TABLE_ID}/views/{view_id}/records/ids")
    record_ids = ids_resp.get("results", [])
    print(f"✓ Total records in table: {len(record_ids)}")

    if len(record_ids) == 0:
        raise ValueError(f"Table {TABLE_ID} is empty")

    # Batch search
    BATCH_SIZE = 100
    found_record = None
    found_field = None
    TARGET_EMAIL = LEAD_EMAIL.lower()

    for i in range(0, len(record_ids), BATCH_SIZE):
        batch = record_ids[i:i+BATCH_SIZE]
        print(f"  Searching records {i+1}-{min(i+BATCH_SIZE, len(record_ids))}...")

        records_resp = api_post(
            session,
            f"/tables/{TABLE_ID}/bulk-fetch-records",
            {"recordIds": batch}
        )
        results = records_resp.get("results", [])

        for rec in results:
            cells = rec.get("cells", {})

            # Check all email fields
            for field_id, field_name in email_field_ids:
                email_cell = cells.get(field_id, {})
                email_value = email_cell.get("value", "") if isinstance(email_cell, dict) else ""

                if isinstance(email_value, str) and TARGET_EMAIL in email_value.lower():
                    found_record = rec
                    found_field = (field_id, field_name)
                    print(f"✓ Lead found! Record ID: {rec['id']}")
                    print(f"   Matched in field: {field_name}\n")
                    break

            if found_record:
                break

        if found_record:
            break

    if not found_record:
        raise ValueError(
            f"Lead email '{LEAD_EMAIL}' not found in table.\n"
            f"Suggestions:\n"
            f"  - Check email spelling\n"
            f"  - Verify lead is in correct table\n"
            f"  - Check email field contains expected data"
        )

    return found_record, found_field

def extract_data(record, email_field_id, linkedin_field_id, name_field_id):
    """Extract LinkedIn URL and name from record"""
    print("📄 Extracting data from record...")

    cells = record.get("cells", {})

    # Extract email (for verification)
    email_cell = cells.get(email_field_id, {})
    email_value = email_cell.get("value", "") if isinstance(email_cell, dict) else ""
    print(f"✓ Email: {email_value}")

    # Extract name (optional)
    candidate_name = None
    if name_field_id:
        name_cell = cells.get(name_field_id, {})
        candidate_name = name_cell.get("value", "") if isinstance(name_cell, dict) else ""
        if candidate_name:
            print(f"✓ Name: {candidate_name}")

    # Extract LinkedIn URL
    linkedin_cell = cells.get(linkedin_field_id, {})
    linkedin_url = linkedin_cell.get("value", "") if isinstance(linkedin_cell, dict) else ""

    # Validate LinkedIn URL
    if not linkedin_url or not isinstance(linkedin_url, str):
        raise ValueError(
            f"LinkedIn job URL field is empty or invalid.\n"
            f"Cannot proceed without a valid job posting URL."
        )

    # Validate URL format
    if "linkedin.com/jobs/view/" not in linkedin_url:
        if "linkedin.com/in/" in linkedin_url:
            raise ValueError(
                f"Found a prospect LinkedIn profile URL, not a job posting:\n{linkedin_url}\n\n"
                f"This is a personal profile. Need the job posting URL."
            )
        else:
            raise ValueError(
                f"Invalid LinkedIn job URL format:\n{linkedin_url}\n\n"
                f"Expected: https://www.linkedin.com/jobs/view/[job_id]"
            )

    print(f"✓ LinkedIn job URL: {linkedin_url}\n")

    return {
        "email": email_value,
        "name": candidate_name,
        "linkedin_url": linkedin_url
    }

def main():
    """Main workflow execution"""
    try:
        print("=" * 60)
        print("📧 EMAIL REPLIES WORKFLOW")
        print("=" * 60)
        print(f"Lead: {LEAD_EMAIL}")
        print(f"Table: Canada Open Jobs - No HMs ({TABLE_ID})")
        print("=" * 60)
        print()

        # Step 1: Authenticate
        session = authenticate()

        # Step 2: Fetch table metadata
        fields, field_map, view_id = fetch_table_metadata(session)

        # Step 3: Resolve fields
        email_fields, linkedin_field, name_field = resolve_fields(fields)
        linkedin_field_id = linkedin_field[0]
        name_field_id = name_field[0] if name_field else None

        # Step 4: Search for lead
        record, found_email_field = search_lead(session, view_id, email_fields)
        email_field_id = found_email_field[0]

        # Step 5: Extract data
        data = extract_data(record, email_field_id, linkedin_field_id, name_field_id)

        # Output results
        print("=" * 60)
        print("✅ CLAY DATA EXTRACTION COMPLETE")
        print("=" * 60)
        print(json.dumps(data, indent=2))
        print()

        return data

    except Exception as e:
        print(f"\n❌ ERROR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
