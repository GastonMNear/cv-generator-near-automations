import urllib.request
import json
import ssl
import sys

# Configuration
ctx = ssl.create_default_context()
BASE = "https://api.clay.com/v3"
TABLE_ID = "t_0t5pvx3g4o5WfysopqA"  # US Open Jobs - Hiring Managers
TARGET_EMAIL = "kyle@ctibusinesstravel.com"

# Clay credentials
CLAY_USERNAME = "kevin.dubon@hirewithnear.com"
CLAY_PASSWORD = "P$3NsPEHJu6se2p"

print(f"Starting CV Generation Workflow")
print(f"=" * 60 + "\n")
print(f"Lead Email: {TARGET_EMAIL}")
print(f"Table: US Open Jobs - Hiring Managers ({TABLE_ID})\n")

# Step 1: Authenticate
print(f"Authenticating with Clay API...")
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
    print(f"OK Authentication successful\n")
except Exception as e:
    print(f"ERROR Authentication failed: {e}")
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

# Step 2: Get table metadata
print(f"Fetching table metadata...")
table_meta = api_get(f"/tables/{TABLE_ID}")
table_info = table_meta.get("table", table_meta)
fields = table_info.get("fields", [])
views = table_info.get("views", [])

# Build field map
field_map = {}
for f in fields:
    field_map[f["id"]] = f["name"]

print(f"OK Table metadata fetched: {len(fields)} fields found\n")

# Identify key fields
email_field_id = None
linkedin_job_field_id = None
name_field_id = None

# Email field patterns (priority ordered)
EMAIL_PATTERNS = ["validated email", "email one", "email", "contact email", "work email"]
# LinkedIn job URL patterns (excluding prospect LinkedIn)
LINKEDIN_JOB_PATTERNS = ["job post url", "job url", "linkedin job", "opening url", "posting url"]
EXCLUDE_PATTERNS = ["prospect", "person", "profile"]
# Name field patterns
NAME_PATTERNS = ["full name cleaned", "full name", "name", "contact name"]

print(f"Identifying key fields...")

# Find email field
for f in fields:
    name_lower = f["name"].lower()
    for pattern in EMAIL_PATTERNS:
        if pattern in name_lower:
            email_field_id = f["id"]
            print(f"  OK Email field: {f['name']} ({f['id']})")
            break
    if email_field_id:
        break

# Find LinkedIn job URL field
for f in fields:
    name_lower = f["name"].lower()
    # Must NOT contain exclude patterns
    if any(exclude in name_lower for exclude in EXCLUDE_PATTERNS):
        continue
    # Check for both "linkedin job" and "job linkedin" patterns
    if ("linkedin" in name_lower and "job" in name_lower) or \
       any(pattern in name_lower for pattern in LINKEDIN_JOB_PATTERNS):
        linkedin_job_field_id = f["id"]
        print(f"  OK LinkedIn job URL field: {f['name']} ({f['id']})")
        break

# Find name field
for f in fields:
    name_lower = f["name"].lower()
    if "company" in name_lower:
        continue
    for pattern in NAME_PATTERNS:
        if pattern in name_lower:
            name_field_id = f["id"]
            print(f"  OK Name field: {f['name']} ({f['id']})")
            break
    if name_field_id:
        break

if not email_field_id:
    print(f"\nERROR Could not identify email field")
    print("\nAvailable text fields:")
    for f in fields:
        if f.get("type") in ["text", "formula"]:
            print(f"  - {f['name']} ({f['id']})")
    sys.exit(1)

if not linkedin_job_field_id:
    print(f"\nWARNING Could not identify LinkedIn job URL field")
    print("\nURL/link fields found (excluding prospect LinkedIn):")
    for f in fields:
        name_lower = f["name"].lower()
        if ("url" in name_lower or "link" in name_lower) and \
           not any(exclude in name_lower for exclude in EXCLUDE_PATTERNS):
            print(f"  - {f['name']} ({f['id']})")

print()

# Step 3: Get default view and record IDs
default_view = views[0] if views else None
if not default_view:
    print("ERROR No views found in table")
    sys.exit(1)

view_id = default_view["id"]
print(f"Using view: {default_view.get('name', 'Default')} ({view_id})")

print(f"\nSearching for lead record...")
ids_resp = api_get(f"/tables/{TABLE_ID}/views/{view_id}/records/ids")
record_ids = ids_resp.get("results", [])
print(f"  Total records in table: {len(record_ids)}")

# Step 4: Batch fetch and search for email
BATCH_SIZE = 100
found_record = None
TARGET_EMAIL_LOWER = TARGET_EMAIL.lower()

for i in range(0, len(record_ids), BATCH_SIZE):
    batch = record_ids[i:i+BATCH_SIZE]
    print(f"  Searching records {i+1}-{min(i+BATCH_SIZE, len(record_ids))}...", end="\r")

    records_resp = api_post(f"/tables/{TABLE_ID}/bulk-fetch-records", {"recordIds": batch})
    results = records_resp.get("results", [])

    for rec in results:
        cells = rec.get("cells", {})
        email_cell = cells.get(email_field_id, {})
        email_value = email_cell.get("value", "") if isinstance(email_cell, dict) else ""

        if isinstance(email_value, str) and TARGET_EMAIL_LOWER in email_value.lower():
            found_record = rec
            print(f"  OK Lead found: Record ID {rec['id']}" + " " * 30)
            break

    if found_record:
        break

if not found_record:
    print(f"\nERROR Lead email '{TARGET_EMAIL}' not found in table")
    sys.exit(1)

# Step 5: Extract data from record
print(f"\nExtracting lead data...")
cells = found_record.get("cells", {})

# Extract email
email_cell = cells.get(email_field_id, {})
lead_email = email_cell.get("value", "") if isinstance(email_cell, dict) else ""

# Extract LinkedIn job URL
linkedin_url = None
if linkedin_job_field_id:
    linkedin_cell = cells.get(linkedin_job_field_id, {})
    linkedin_url = linkedin_cell.get("value", "") if isinstance(linkedin_cell, dict) else ""

# Extract name
candidate_name = None
if name_field_id:
    name_cell = cells.get(name_field_id, {})
    candidate_name = name_cell.get("value", "") if isinstance(name_cell, dict) else ""

# Print extracted data (handle Unicode encoding)
def safe_print(text):
    """Print text handling Unicode encoding issues"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback: encode to ASCII, replacing non-ASCII chars
        print(text.encode('ascii', 'replace').decode('ascii'))

safe_print(f"  OK Email: {lead_email}")
if candidate_name:
    safe_print(f"  OK Name: {candidate_name}")
if linkedin_url:
    safe_print(f"  OK LinkedIn Job URL: {linkedin_url}")
else:
    safe_print(f"  WARNING LinkedIn Job URL not found")

# Validate LinkedIn URL
if not linkedin_url or not isinstance(linkedin_url, str):
    print(f"\nERROR LinkedIn job URL field is empty or invalid")
    print(f"Cannot proceed without a valid job posting URL")
    sys.exit(1)

if "linkedin.com/jobs/view/" not in linkedin_url:
    if "linkedin.com/in/" in linkedin_url:
        print(f"\nERROR Found a prospect LinkedIn profile URL, not a job posting URL:")
        print(f"  {linkedin_url}")
        print(f"\nThis is the lead's personal LinkedIn profile. The workflow requires the job posting URL.")
        sys.exit(1)
    else:
        print(f"\nERROR Invalid LinkedIn job URL format:")
        print(f"  {linkedin_url}")
        print(f"\nExpected format: https://www.linkedin.com/jobs/view/[job_id]")
        sys.exit(1)

# Output results for next steps
print(f"\n{'='*60}")
print(f"CLAY DATA EXTRACTION COMPLETE")
print(f"{'='*60}\n")

# Save results to JSON file for skill invocation
results = {
    "lead_email": lead_email,
    "candidate_name": candidate_name,
    "linkedin_url": linkedin_url,
    "table_id": TABLE_ID,
    "table_name": "US Open Jobs - Hiring Managers",
    "record_id": found_record.get("id")
}

with open("workflow_results.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"Results saved to workflow_results.json")
print(f"\nNext steps:")
print(f"  1. Extract job details from LinkedIn URL")
print(f"  2. Generate LATAM CV using latam-cv-generator skill")
print(f"\nLinkedIn URL to process: {linkedin_url}")
