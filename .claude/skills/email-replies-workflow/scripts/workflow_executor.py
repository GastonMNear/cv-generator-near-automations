import urllib.request
import json
import ssl
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
CLAY_USERNAME = os.getenv("CLAY_USERNAME")
CLAY_PASSWORD = os.getenv("CLAY_PASSWORD")

if not CLAY_USERNAME or not CLAY_PASSWORD:
    print("ERROR: Missing Clay credentials in .env")
    sys.exit(1)

# Configuration
ctx = ssl.create_default_context()
BASE = "https://api.clay.com/v3"

# Parse command line arguments
if len(sys.argv) < 3:
    print("Usage: python workflow_executor.py <email> <table_id>")
    sys.exit(1)

TARGET_EMAIL = sys.argv[1].lower()
TABLE_ID = sys.argv[2]

print(f"Starting email replies workflow...")
print(f"  Lead email: {TARGET_EMAIL}")
print(f"  Table ID: {TABLE_ID}")

# Step 1: Authenticate
print(f"\n[1/6] Authenticating with Clay API...")
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
        print("ERROR: Invalid session cookie format")
        sys.exit(1)

    print("[OK] Clay authentication successful")
except Exception as e:
    print(f"ERROR: Clay authentication failed: {e}")
    sys.exit(1)

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

# Step 2: Get table metadata and build field map
print(f"\n[2/6] Fetching table metadata for {TABLE_ID}...")
try:
    table_meta = api_get(f"/tables/{TABLE_ID}")
    table_info = table_meta.get("table", table_meta)
    fields = table_info.get("fields", [])
    views = table_info.get("views", [])

    if not fields:
        print(f"ERROR: Table {TABLE_ID} has no fields")
        sys.exit(1)

    # Build field map
    field_map = {}
    for f in fields:
        field_map[f["id"]] = f["name"]

    print(f"[OK] Table metadata fetched: {len(fields)} fields found")

    if not views:
        print("ERROR: Table has no views")
        sys.exit(1)

    default_view = views[0]
    view_id = default_view["id"]
    print(f"[OK] Default view: {view_id} ({default_view.get('name', 'Unnamed')})")

except Exception as e:
    print(f"ERROR: Failed to fetch table metadata: {e}")
    sys.exit(1)

# Step 3: Resolve field IDs
print(f"\n[3/6] Resolving field IDs...")

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
    print("ERROR: Could not identify email field. Available fields:")
    for f in fields[:20]:
        print(f"  - {f['name']} ({f['id']})")
    sys.exit(1)

print(f"[OK] Email field: {email_field_name} ({email_field_id})")

# LinkedIn job URL field patterns - more flexible matching
EXCLUDE_PATTERNS = ["prospect", "person", "profile", "company linkedin", "imported company"]

linkedin_field_id = None
linkedin_field_name = None

for f in fields:
    name_lower = f["name"].lower()

    # Must NOT contain exclude patterns
    if any(exclude in name_lower for exclude in EXCLUDE_PATTERNS):
        continue

    # Must contain both "job" and "linkedin" OR both "job" and "url"
    has_job = "job" in name_lower
    has_linkedin = "linkedin" in name_lower
    has_url = "url" in name_lower

    if has_job and (has_linkedin or has_url):
        linkedin_field_id = f["id"]
        linkedin_field_name = f["name"]
        break

if not linkedin_field_id:
    print("ERROR: Could not identify LinkedIn job URL field. Available URL fields:")
    for f in fields:
        name_lower = f["name"].lower()
        if "url" in name_lower or "link" in name_lower:
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
    print("[WARN] Name field not found (optional)")

# Step 4: Search for lead record by email
print(f"\n[4/6] Searching for lead record...")
try:
    ids_resp = api_get(f"/tables/{TABLE_ID}/views/{view_id}/records/ids")
    record_ids = ids_resp.get("results", [])
    print(f"[OK] Total records in table: {len(record_ids)}")

    if len(record_ids) == 0:
        print("ERROR: Table is empty")
        sys.exit(1)

    # Batch fetch and search
    BATCH_SIZE = 100
    found_record = None

    for i in range(0, len(record_ids), BATCH_SIZE):
        batch = record_ids[i:i+BATCH_SIZE]
        print(f"  Searching records {i+1}-{min(i+BATCH_SIZE, len(record_ids))} of {len(record_ids)}...")

        records_resp = api_post(f"/tables/{TABLE_ID}/bulk-fetch-records", {"recordIds": batch})
        results = records_resp.get("results", [])

        for rec in results:
            cells = rec.get("cells", {})
            email_cell = cells.get(email_field_id, {})
            email_value = email_cell.get("value", "") if isinstance(email_cell, dict) else ""

            # Case-insensitive email comparison
            if isinstance(email_value, str) and TARGET_EMAIL in email_value.lower():
                found_record = rec
                print(f"[OK] Lead found: Record ID {rec['id']}")
                break

        if found_record:
            break

    if not found_record:
        print(f"ERROR: Lead email '{TARGET_EMAIL}' not found in table")
        sys.exit(1)

except Exception as e:
    print(f"ERROR: Failed to search for lead: {e}")
    sys.exit(1)

# Step 5: Extract LinkedIn job URL from record
print(f"\n[5/6] Extracting LinkedIn job URL...")
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
        print(f"[OK] Candidate name: {candidate_name}")

# Validate LinkedIn URL
if not linkedin_url or not isinstance(linkedin_url, str):
    print(f"ERROR: LinkedIn job URL field '{linkedin_field_name}' is empty or invalid")
    sys.exit(1)

# Validate URL format
if "linkedin.com/jobs/view/" not in linkedin_url:
    if "linkedin.com/in/" in linkedin_url:
        print(f"ERROR: Found a prospect LinkedIn profile URL, not a job posting URL:")
        print(f"  {linkedin_url}")
        print(f"\nThis is the lead's personal LinkedIn profile.")
        print(f"The workflow requires the job posting URL.")
        sys.exit(1)
    else:
        print(f"ERROR: Invalid LinkedIn job URL format:")
        print(f"  {linkedin_url}")
        print(f"\nExpected format: https://www.linkedin.com/jobs/view/[job_id]")
        sys.exit(1)

print(f"[OK] LinkedIn job URL: {linkedin_url}")

# Step 6: Output results as JSON
print(f"\n[6/6] Workflow data extraction complete!")
print(f"\n{'='*60}")

# Output JSON for consumption by skill orchestrator
result = {
    "success": True,
    "lead_email": TARGET_EMAIL,
    "table_id": TABLE_ID,
    "record_id": found_record["id"],
    "candidate_name": candidate_name,
    "linkedin_url": linkedin_url,
    "email_field": {"id": email_field_id, "name": email_field_name},
    "linkedin_field": {"id": linkedin_field_id, "name": linkedin_field_name},
    "name_field": {"id": name_field_id, "name": name_field_name} if name_field_id else None
}

print(json.dumps(result, indent=2))
