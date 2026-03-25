#!/usr/bin/env python3
"""
Email Replies Workflow Script
Orchestrates: Clay data fetch → LinkedIn extraction → CV generation
"""
import urllib.request
import json
import ssl
import sys
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configuration
LEAD_EMAIL = "william@longevity-x.com"
TABLE_ID = "t_aNvk4jWMNeG7"  # LatAm Open Jobs - No HMs
TABLE_NAME = "LatAm Open Jobs - No HMs"

CLAY_USERNAME = os.getenv("CLAY_USERNAME")
CLAY_PASSWORD = os.getenv("CLAY_PASSWORD")

if not CLAY_USERNAME or not CLAY_PASSWORD:
    print("❌ Missing Clay credentials in .env")
    sys.exit(1)

# Setup
ctx = ssl.create_default_context()
BASE = "https://api.clay.com/v3"

print(f"{'='*60}")
print(f"EMAIL REPLIES WORKFLOW")
print(f"{'='*60}")
print(f"Lead Email: {LEAD_EMAIL}")
print(f"Table: {TABLE_NAME} ({TABLE_ID})")
print(f"{'='*60}\n")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1: AUTHENTICATE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print("[AUTH] Authenticating with Clay API...")
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
        print("[ERROR] Authentication failed: invalid session format")
        sys.exit(1)

    print("[OK] Clay authentication successful\n")
except Exception as e:
    print(f"[ERROR] Authentication failed: {e}")
    sys.exit(1)

# Helper functions
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

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2: FETCH TABLE METADATA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print("[METADATA] Fetching table metadata...")
table_meta = api_get(f"/tables/{TABLE_ID}")
table_info = table_meta.get("table", table_meta)
fields = table_info.get("fields", [])
views = table_info.get("views", [])

if not fields:
    print(f"[ERROR] Table {TABLE_ID} has no fields")
    sys.exit(1)

if not views:
    print(f"[ERROR] Table {TABLE_ID} has no views")
    sys.exit(1)

# Build field map
field_map = {}
for f in fields:
    field_map[f["id"]] = f["name"]

print(f"[OK] Table metadata fetched: {len(fields)} fields found\n")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 3: RESOLVE FIELD IDs
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print("[FIELDS] Identifying email and LinkedIn URL fields...")

# Email field patterns (priority order)
EMAIL_PATTERNS = ["validated email", "email one", "email", "contact email", "work email"]
email_field_id = None
email_field_name = None

for f in fields:
    name_lower = f["name"].lower()
    for pattern in EMAIL_PATTERNS:
        if pattern in name_lower:
            email_field_id = f["id"]
            email_field_name = f["name"]
            break
    if email_field_id:
        break

if not email_field_id:
    print("[ERROR] Could not identify email field")
    print("Available text fields:")
    for f in fields:
        if f.get("type") in ["text", "formula"]:
            print(f"  - {f['name']} ({f['id']})")
    sys.exit(1)

print(f"[OK] Email field: {email_field_name} ({email_field_id})")

# LinkedIn job URL field patterns (exclude prospect LinkedIn!)
JOB_URL_PATTERNS = ["job post url", "job url", "linkedin job", "opening url", "posting url"]
EXCLUDE_PATTERNS = ["prospect", "person", "profile"]

linkedin_field_id = None
linkedin_field_name = None

for f in fields:
    name_lower = f["name"].lower()

    # Skip if contains exclude patterns
    if any(exclude in name_lower for exclude in EXCLUDE_PATTERNS):
        continue

    # Check for job URL patterns
    for pattern in JOB_URL_PATTERNS:
        if pattern in name_lower:
            linkedin_field_id = f["id"]
            linkedin_field_name = f["name"]
            break
    if linkedin_field_id:
        break

if not linkedin_field_id:
    print("[ERROR] Could not identify LinkedIn job URL field")
    print("Available URL fields (excluding prospect LinkedIn):")
    for f in fields:
        name_lower = f["name"].lower()
        if ("url" in name_lower or "link" in name_lower) and \
           not any(exclude in name_lower for exclude in EXCLUDE_PATTERNS):
            print(f"  - {f['name']} ({f['id']})")
    sys.exit(1)

print(f"[OK] LinkedIn job URL field: {linkedin_field_name} ({linkedin_field_id})")

# Name field (optional)
NAME_PATTERNS = ["full name cleaned", "full name", "name", "contact name"]
name_field_id = None
name_field_name = None

for f in fields:
    name_lower = f["name"].lower()
    if "company" in name_lower:
        continue
    for pattern in NAME_PATTERNS:
        if pattern in name_lower:
            name_field_id = f["id"]
            name_field_name = f["name"]
            break
    if name_field_id:
        break

if name_field_id:
    print(f"[OK] Name field: {name_field_name} ({name_field_id})")
else:
    print("[WARN] Name field not identified (optional)")

print()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 4: SEARCH FOR LEAD RECORD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print(f"[SEARCH] Searching for lead: {LEAD_EMAIL}...")

# Get default view
default_view = views[0]
view_id = default_view["id"]
print(f"Using view: {view_id} ({default_view.get('name', 'Unnamed')})")

# Get all record IDs
ids_resp = api_get(f"/tables/{TABLE_ID}/views/{view_id}/records/ids")
record_ids = ids_resp.get("results", [])
print(f"Total records in table: {len(record_ids)}")

if len(record_ids) == 0:
    print("[ERROR] Table is empty")
    sys.exit(1)

# Batch search
BATCH_SIZE = 100
found_record = None
TARGET_EMAIL = LEAD_EMAIL.lower()

for i in range(0, len(record_ids), BATCH_SIZE):
    batch = record_ids[i:i+BATCH_SIZE]
    print(f"Searching records {i+1}-{min(i+BATCH_SIZE, len(record_ids))} of {len(record_ids)}...")

    records_resp = api_post(f"/tables/{TABLE_ID}/bulk-fetch-records", {"recordIds": batch})
    results = records_resp.get("results", [])

    for rec in results:
        cells = rec.get("cells", {})
        email_cell = cells.get(email_field_id, {})
        email_value = email_cell.get("value", "") if isinstance(email_cell, dict) else ""

        if isinstance(email_value, str) and TARGET_EMAIL in email_value.lower():
            found_record = rec
            print(f"[OK] Lead found: Record ID {rec['id']}\n")
            break

    if found_record:
        break

if not found_record:
    print(f"[ERROR] Lead email '{LEAD_EMAIL}' not found in table")
    sys.exit(1)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 5: EXTRACT DATA FROM RECORD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print("[EXTRACT] Extracting data from record...")

cells = found_record.get("cells", {})

# Extract LinkedIn URL
linkedin_cell = cells.get(linkedin_field_id, {})
linkedin_url = linkedin_cell.get("value", "") if isinstance(linkedin_cell, dict) else ""

# Extract name
candidate_name = None
if name_field_id:
    name_cell = cells.get(name_field_id, {})
    candidate_name = name_cell.get("value", "") if isinstance(name_cell, dict) else ""
    if candidate_name:
        print(f"[OK] Candidate name: {candidate_name}")

# Validate LinkedIn URL
if not linkedin_url or not isinstance(linkedin_url, str):
    print(f"[ERROR] LinkedIn job URL field '{linkedin_field_name}' is empty")
    sys.exit(1)

# Check URL format
if "linkedin.com/jobs/view/" not in linkedin_url:
    if "linkedin.com/in/" in linkedin_url:
        print(f"[ERROR] Found prospect LinkedIn profile, not job posting:")
        print(f"   {linkedin_url}")
        print(f"\n[ERROR] This is the lead's personal LinkedIn. Need the job posting URL.")
        sys.exit(1)
    else:
        print(f"[ERROR] Invalid LinkedIn job URL format:")
        print(f"   {linkedin_url}")
        print(f"\n[ERROR] Expected: https://www.linkedin.com/jobs/view/[job_id]")
        sys.exit(1)

print(f"[OK] LinkedIn job URL: {linkedin_url}\n")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 6: OUTPUT FOR NEXT STAGES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print(f"{'='*60}")
print("CLAY DATA EXTRACTION COMPLETE")
print(f"{'='*60}")
print(f"\n[SUCCESS] Lead found and data extracted successfully")
print(f"\n[LEAD] Lead Information:")
print(f"   Email: {LEAD_EMAIL}")
if candidate_name:
    print(f"   Name: {candidate_name}")
print(f"   Source Table: {TABLE_NAME} ({TABLE_ID})")
print(f"\n[JOB] Job Details:")
print(f"   LinkedIn URL: {linkedin_url}")
print(f"\n{'='*60}")
print("READY FOR NEXT STEPS:")
print("1. Extract job details from LinkedIn")
print("2. Generate LATAM CV")
print(f"{'='*60}\n")

# Output JSON for programmatic access
output_data = {
    "lead_email": LEAD_EMAIL,
    "candidate_name": candidate_name,
    "table_id": TABLE_ID,
    "table_name": TABLE_NAME,
    "linkedin_url": linkedin_url,
    "record_id": found_record["id"]
}

# Save to temp file for next steps
with open("c:/Users/lenovo/Documents/Kevin - Near automations/workflow_data.json", "w") as f:
    json.dump(output_data, f, indent=2)

print("[SAVE] Workflow data saved to: workflow_data.json")
print(f"\nLinkedIn URL for next step:\n{linkedin_url}")
