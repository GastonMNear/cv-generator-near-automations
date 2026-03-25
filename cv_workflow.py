#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Email Replies CV Generation Workflow
Orchestrates Clay data fetch → LinkedIn extraction → CV generation
"""

import urllib.request
import json
import ssl
import sys
import os
from dotenv import load_dotenv

# Fix encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

# Configuration
CLAY_USERNAME = os.getenv("CLAY_USERNAME")
CLAY_PASSWORD = os.getenv("CLAY_PASSWORD")
BASE = "https://api.clay.com/v3"
WORKSPACE_ID = "447061"

# Input from command line
if len(sys.argv) < 3:
    print("Usage: python cv_workflow.py <email> <table_id>")
    sys.exit(1)

TARGET_EMAIL = sys.argv[1]
TABLE_ID = sys.argv[2]

print(f"\n{'='*60}")
print(f"CV GENERATION WORKFLOW")
print(f"{'='*60}")
print(f"Email: {TARGET_EMAIL}")
print(f"Table ID: {TABLE_ID}")
print(f"{'='*60}\n")

# SSL context
ctx = ssl.create_default_context()

# ============================================================================
# STEP 1: AUTHENTICATE WITH CLAY
# ============================================================================

print("STEP 1: Authenticating with Clay API...")

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

try:
    resp = urllib.request.urlopen(req, context=ctx)
    cookie_header = resp.headers.get("Set-Cookie", "")
    session = cookie_header.split(";")[0]

    if not session.startswith("claysession="):
        print("❌ Authentication failed: invalid session cookie format")
        sys.exit(1)

    print("✓ Clay authentication successful\n")
except Exception as e:
    print(f"❌ Authentication error: {e}")
    sys.exit(1)

# API helpers
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

# ============================================================================
# STEP 2: FETCH TABLE METADATA
# ============================================================================

print("STEP 2: Fetching table metadata...")

try:
    table_meta = api_get(f"/tables/{TABLE_ID}")
    table_info = table_meta.get("table", table_meta)
    fields = table_info.get("fields", [])
    views = table_info.get("views", [])

    if not fields:
        print(f"❌ Table {TABLE_ID} has no fields")
        sys.exit(1)

    # Build field map
    field_map = {}
    for f in fields:
        field_map[f["id"]] = f["name"]

    print(f"✓ Table metadata fetched: {len(fields)} fields found")

    # Get default view
    if not views:
        print(f"❌ Table {TABLE_ID} has no views")
        sys.exit(1)

    default_view = views[0]
    view_id = default_view["id"]
    print(f"✓ Default view: {view_id} ({default_view.get('name', 'Unnamed')})\n")

except Exception as e:
    print(f"❌ Error fetching table metadata: {e}")
    sys.exit(1)

# ============================================================================
# STEP 3: RESOLVE FIELD IDs
# ============================================================================

print("STEP 3: Resolving field IDs...")

# Email field patterns (priority order)
EMAIL_PATTERNS = [
    "validated email",
    "email one",
    "email",
    "contact email",
    "work email"
]

email_field_id = None
email_field_name = None

for f in fields:
    name_lower = f["name"].lower()
    for pattern in EMAIL_PATTERNS:
        if pattern in name_lower:
            email_field_id = f["id"]
            email_field_name = f["name"]
            print(f"✓ Email field identified: {email_field_name} ({email_field_id})")
            break
    if email_field_id:
        break

if not email_field_id:
    print("❌ Could not identify email field in table")
    print("\nText fields found:")
    for f in fields[:10]:
        if f.get("type") in ["text", "formula"]:
            print(f"  - {f['name']} ({f['id']})")
    sys.exit(1)

# LinkedIn job URL patterns (priority order)
LINKEDIN_JOB_PATTERNS = [
    "job post url",
    "job linkedin url",
    "job linkedin",
    "linkedin job",
    "job url",
    "opening url",
    "posting url",
    "job posting"
]

# Exclude patterns (to avoid prospect LinkedIn URLs)
EXCLUDE_PATTERNS = ["prospect", "person", "profile"]

linkedin_field_id = None
linkedin_field_name = None

for f in fields:
    name_lower = f["name"].lower()

    # Must NOT contain exclude patterns
    if any(exclude in name_lower for exclude in EXCLUDE_PATTERNS):
        continue

    # Check if matches job URL patterns
    for pattern in LINKEDIN_JOB_PATTERNS:
        if pattern in name_lower:
            linkedin_field_id = f["id"]
            linkedin_field_name = f["name"]
            print(f"✓ LinkedIn job URL field identified: {linkedin_field_name} ({linkedin_field_id})")
            break
    if linkedin_field_id:
        break

if not linkedin_field_id:
    print("❌ Could not identify LinkedIn job URL field")
    print("\nURL fields found (excluding prospect LinkedIn):")
    for f in fields[:15]:
        name_lower = f["name"].lower()
        if ("url" in name_lower or "link" in name_lower) and \
           not any(exclude in name_lower for exclude in EXCLUDE_PATTERNS):
            print(f"  - {f['name']} ({f['id']})")
    sys.exit(1)

# Name field patterns (optional)
NAME_PATTERNS = [
    "full name cleaned",
    "full name",
    "name",
    "contact name"
]

name_field_id = None
name_field_name = None

for f in fields:
    name_lower = f["name"].lower()
    # Exclude company name fields
    if "company" in name_lower:
        continue
    for pattern in NAME_PATTERNS:
        if pattern in name_lower:
            name_field_id = f["id"]
            name_field_name = f["name"]
            print(f"✓ Name field identified: {name_field_name} ({name_field_id})")
            break
    if name_field_id:
        break

if not name_field_id:
    print("⚠ Name field not identified (optional)")

print()

# ============================================================================
# STEP 4: SEARCH FOR LEAD RECORD
# ============================================================================

print("STEP 4: Searching for lead record...")

try:
    # Get all record IDs
    ids_resp = api_get(f"/tables/{TABLE_ID}/views/{view_id}/records/ids")
    record_ids = ids_resp.get("results", [])
    print(f"✓ Total records in table: {len(record_ids)}")

    if len(record_ids) == 0:
        print(f"❌ Table {TABLE_ID} is empty")
        sys.exit(1)

    # Batch fetch and search
    BATCH_SIZE = 100
    found_record = None
    TARGET_EMAIL_LOWER = TARGET_EMAIL.lower()

    for i in range(0, len(record_ids), BATCH_SIZE):
        batch = record_ids[i:i+BATCH_SIZE]
        print(f"  Searching records {i+1}-{min(i+BATCH_SIZE, len(record_ids))} of {len(record_ids)}...")

        records_resp = api_post(
            f"/tables/{TABLE_ID}/bulk-fetch-records",
            {"recordIds": batch}
        )
        results = records_resp.get("results", [])

        for rec in results:
            cells = rec.get("cells", {})
            email_cell = cells.get(email_field_id, {})
            email_value = email_cell.get("value", "") if isinstance(email_cell, dict) else ""

            # Case-insensitive email comparison
            if isinstance(email_value, str) and TARGET_EMAIL_LOWER in email_value.lower():
                found_record = rec
                print(f"✓ Lead found: Record ID {rec['id']}")
                break

        if found_record:
            break

    if not found_record:
        print(f"\n❌ Lead email '{TARGET_EMAIL}' not found in table")
        print("\nSuggestions:")
        print("- Check email spelling")
        print("- Verify the lead is in the correct table")
        print("- Ensure the email field contains the expected data")
        sys.exit(1)

    print()

except Exception as e:
    print(f"❌ Error searching for lead: {e}")
    sys.exit(1)

# ============================================================================
# STEP 5: EXTRACT DATA FROM RECORD
# ============================================================================

print("STEP 5: Extracting data from record...")

cells = found_record.get("cells", {})

# Extract LinkedIn URL
linkedin_cell = cells.get(linkedin_field_id, {})
linkedin_url = linkedin_cell.get("value", "") if isinstance(linkedin_cell, dict) else ""

# Extract name (if available)
candidate_name = None
if name_field_id:
    name_cell = cells.get(name_field_id, {})
    candidate_name = name_cell.get("value", "") if isinstance(name_cell, dict) else ""
    if candidate_name:
        print(f"✓ Candidate name: {candidate_name}")

# Validate LinkedIn URL
if not linkedin_url or not isinstance(linkedin_url, str):
    print(f"❌ LinkedIn job URL field '{linkedin_field_name}' is empty or invalid")
    print("\nCannot proceed without a valid job posting URL")
    sys.exit(1)

# Validate URL format
if "linkedin.com/jobs/view/" not in linkedin_url:
    # Check if this is a prospect LinkedIn URL
    if "linkedin.com/in/" in linkedin_url:
        print(f"❌ Found a prospect LinkedIn profile URL, not a job posting URL:")
        print(f"   {linkedin_url}")
        print("\nThis is the lead's personal LinkedIn profile.")
        print("The workflow requires the job posting URL.")
        sys.exit(1)
    else:
        print(f"❌ Invalid LinkedIn job URL format:")
        print(f"   {linkedin_url}")
        print("\nExpected format: https://www.linkedin.com/jobs/view/[job_id]")
        sys.exit(1)

print(f"✓ LinkedIn job URL: {linkedin_url}")
print()

# ============================================================================
# OUTPUT RESULTS FOR NEXT STEPS
# ============================================================================

print(f"\n{'='*60}")
print(f"DATA EXTRACTION COMPLETE")
print(f"{'='*60}")

# Save results to JSON for next steps
workflow_data = {
    "lead_email": TARGET_EMAIL,
    "candidate_name": candidate_name,
    "table_id": TABLE_ID,
    "record_id": found_record["id"],
    "linkedin_job_url": linkedin_url,
    "email_field": email_field_name,
    "linkedin_field": linkedin_field_name,
    "name_field": name_field_name
}

output_file = "workflow_data.json"
with open(output_file, "w") as f:
    json.dump(workflow_data, f, indent=2)

print(f"\n✓ Workflow data saved to: {output_file}")
print(f"\nNext steps:")
print(f"1. Extract job details from LinkedIn URL")
print(f"2. Generate LATAM CV using job details")
print(f"\nLinkedIn URL to process:")
print(f"{linkedin_url}")
print()
