#!/usr/bin/env python3
"""
Extract LinkedIn URL from found record
"""
import urllib.request
import json
import ssl
import sys
import os
from dotenv import load_dotenv

load_dotenv()

RECORD_ID = "r_0tb0lolyJMBRP5nyfS8"
TABLE_ID = "t_aNvk4jWMNeG7"

CLAY_USERNAME = os.getenv("CLAY_USERNAME")
CLAY_PASSWORD = os.getenv("CLAY_PASSWORD")

ctx = ssl.create_default_context()
BASE = "https://api.clay.com/v3"

# Authenticate
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
session = resp.headers.get("Set-Cookie", "").split(";")[0]
print("[OK] Authenticated")

def api_post(path, data):
    r = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(data).encode(),
        headers={"Cookie": session, "Content-Type": "application/json"},
        method="POST"
    )
    return json.loads(urllib.request.urlopen(r, context=ctx).read())

def api_get(path):
    r = urllib.request.Request(f"{BASE}{path}", headers={"Cookie": session})
    return json.loads(urllib.request.urlopen(r, context=ctx).read())

# Get table metadata
table_meta = api_get(f"/tables/{TABLE_ID}")
table_info = table_meta.get("table", table_meta)
fields = table_info.get("fields", [])

field_map = {}
for f in fields:
    field_map[f["id"]] = f["name"]

# Fetch the specific record
print(f"[FETCH] Fetching record {RECORD_ID}...")
records_resp = api_post(f"/tables/{TABLE_ID}/bulk-fetch-records", {"recordIds": [RECORD_ID]})
results = records_resp.get("results", [])

if not results:
    print(f"[ERROR] Record not found")
    sys.exit(1)

record = results[0]
cells = record.get("cells", {})

# Find LinkedIn job URL
linkedin_url = None
linkedin_field_name = None

# Priority patterns for LinkedIn job URL fields
JOB_URL_PATTERNS = ["job post url", "job url", "linkedin job", "opening url", "posting url", "lookup job url"]
EXCLUDE_PATTERNS = ["prospect", "person", "profile"]

for fid, cell in cells.items():
    name = field_map.get(fid, "")
    name_lower = name.lower()

    # Skip prospect LinkedIn
    if any(exclude in name_lower for exclude in EXCLUDE_PATTERNS):
        continue

    # Check if matches job URL patterns
    for pattern in JOB_URL_PATTERNS:
        if pattern in name_lower:
            val = cell.get("value", "") if isinstance(cell, dict) else ""
            if val and isinstance(val, str) and "linkedin.com" in val:
                linkedin_url = val
                linkedin_field_name = name
                break

    if linkedin_url:
        break

if not linkedin_url:
    print("[WARN] No LinkedIn URL found in priority fields")
    print("[SEARCH] Searching all fields for LinkedIn URLs...")

    # Search all fields
    for fid, cell in cells.items():
        name = field_map.get(fid, "")
        val = cell.get("value", "") if isinstance(cell, dict) else ""

        if isinstance(val, str) and "linkedin.com/jobs/view/" in val:
            linkedin_url = val
            linkedin_field_name = name
            print(f"[FOUND] LinkedIn URL in field: {name}")
            break

if not linkedin_url:
    print("[ERROR] No LinkedIn job URL found in any field")
    print("[DEBUG] Available fields with 'job' or 'url' or 'linkedin':")
    for fid, cell in cells.items():
        name = field_map.get(fid, "")
        name_lower = name.lower()
        if "job" in name_lower or "url" in name_lower or "linkedin" in name_lower:
            val = cell.get("value", "") if isinstance(cell, dict) else ""
            val_str = str(val)[:100] if val else "(empty)"
            # Encode safely for Windows console
            try:
                print(f"  {name}: {val_str}")
            except:
                print(f"  {name}: <encoding error>")
    sys.exit(1)

# Validate URL
if "linkedin.com/jobs/view/" not in linkedin_url:
    if "linkedin.com/in/" in linkedin_url:
        print(f"[ERROR] Found prospect LinkedIn profile, not job posting:")
        print(f"  {linkedin_url}")
        sys.exit(1)
    else:
        print(f"[WARN] URL may not be a job posting: {linkedin_url}")

print(f"\n{'='*60}")
print(f"[SUCCESS] LinkedIn job URL extracted")
print(f"{'='*60}")
print(f"Field: {linkedin_field_name}")
print(f"URL: {linkedin_url}")
print(f"{'='*60}\n")

# Save for next step
output_data = {
    "lead_email": "william@longevity-x.com",
    "table_id": TABLE_ID,
    "record_id": RECORD_ID,
    "linkedin_url": linkedin_url,
    "linkedin_field_name": linkedin_field_name
}

with open("c:/Users/lenovo/Documents/Kevin - Near automations/workflow_data.json", "w") as f:
    json.dump(output_data, f, indent=2)

print("[SAVE] Workflow data saved")
print(f"\nReady for LinkedIn extraction: {linkedin_url}")
