#!/usr/bin/env python3
"""
Extract lead data from a Clay table for call prep.

Usage:
    python extract_lead_data.py <lead_email> <table_id>

Output:
    JSON with job_title, linkedin_url, employee_count, job_post_url
"""

import urllib.request
import json
import ssl
import sys
import os
from dotenv import load_dotenv

load_dotenv()
CLAY_USERNAME = os.getenv("CLAY_USERNAME")
CLAY_PASSWORD = os.getenv("CLAY_PASSWORD")

if not CLAY_USERNAME or not CLAY_PASSWORD:
    print("ERROR: Missing Clay credentials in .env (CLAY_USERNAME, CLAY_PASSWORD)")
    sys.exit(1)

if len(sys.argv) < 3:
    print("Usage: python extract_lead_data.py <lead_email> <table_id>")
    sys.exit(1)

TARGET_EMAIL = sys.argv[1].lower()
TABLE_ID = sys.argv[2]

ctx = ssl.create_default_context()
BASE = "https://api.clay.com/v3"

print(f"Starting lead data extraction...")
print(f"  Lead email: {TARGET_EMAIL}")
print(f"  Table ID:   {TABLE_ID}")

# ── Step 1: Authenticate ──────────────────────────────────────────────────────
print("\n[1/5] Authenticating with Clay...")
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
    print("[OK] Authenticated")
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


# ── Step 2: Table metadata + field map ───────────────────────────────────────
print(f"\n[2/5] Fetching table metadata for {TABLE_ID}...")
try:
    table_meta = api_get(f"/tables/{TABLE_ID}")
    table_info = table_meta.get("table", table_meta)
    fields = table_info.get("fields", [])
    views = table_info.get("views", [])

    if not fields:
        print(f"ERROR: Table {TABLE_ID} has no fields")
        sys.exit(1)
    if not views:
        print("ERROR: Table has no views")
        sys.exit(1)

    view_id = views[0]["id"]
    print(f"[OK] {len(fields)} fields found, view: {views[0].get('name', view_id)}")
except Exception as e:
    print(f"ERROR: Failed to fetch table metadata: {e}")
    sys.exit(1)


# ── Step 3: Resolve field IDs ─────────────────────────────────────────────────
print("\n[3/5] Resolving field IDs...")

def find_field(fields, patterns, exclude_patterns=None, label="field"):
    """Find first field whose name contains any pattern (and none of the exclude patterns)."""
    for f in fields:
        name_lower = f["name"].lower()
        if exclude_patterns and any(ex in name_lower for ex in exclude_patterns):
            continue
        for pattern in patterns:
            if pattern in name_lower:
                return f["id"], f["name"]
    return None, None


# Email field (to find the record)
EMAIL_PATTERNS = ["validated email", "email one", "email", "contact email", "work email"]
email_field_id, email_field_name = find_field(fields, EMAIL_PATTERNS, label="email")
if not email_field_id:
    print("ERROR: Cannot identify email field. Available fields:")
    for f in fields[:30]:
        print(f"  - {f['name']} ({f['id']})")
    sys.exit(1)
print(f"[OK] Email field: {email_field_name}")

# Job title (lead's personal title)
TITLE_PATTERNS = ["job title", "title", "position", "role"]
TITLE_EXCLUDE = ["company", "url", "link"]
title_field_id, title_field_name = find_field(fields, TITLE_PATTERNS, TITLE_EXCLUDE, "job title")
if title_field_id:
    print(f"[OK] Job title field: {title_field_name}")
else:
    print("[WARN] Job title field not found")

# Lead's personal LinkedIn URL
LINKEDIN_PERSON_PATTERNS = ["prospect linkedin", "contact linkedin", "person linkedin", "linkedin url", "linkedin profile"]
linkedin_field_id, linkedin_field_name = find_field(fields, LINKEDIN_PERSON_PATTERNS, label="lead LinkedIn")
if linkedin_field_id:
    print(f"[OK] Lead LinkedIn field: {linkedin_field_name}")
else:
    print("[WARN] Lead LinkedIn URL field not found")

# Employee count
EMPLOYEE_PATTERNS = ["employee count", "# employees", "num employees", "headcount", "company size", "employees"]
employee_field_id, employee_field_name = find_field(fields, EMPLOYEE_PATTERNS, label="employee count")
if employee_field_id:
    print(f"[OK] Employee count field: {employee_field_name}")
else:
    print("[WARN] Employee count field not found")

# Job post LinkedIn URL (job being hired for — NOT the lead's profile)
JOB_POST_PATTERNS = ["job post url", "job post linkedin", "linkedin job", "opening url", "posting url", "job url", "job link"]
JOB_POST_EXCLUDE = ["prospect", "person", "profile", "company linkedin"]
jobpost_field_id, jobpost_field_name = find_field(fields, JOB_POST_PATTERNS, JOB_POST_EXCLUDE, "job post URL")
if jobpost_field_id:
    print(f"[OK] Job post URL field: {jobpost_field_name}")
else:
    print("[WARN] Job post URL field not found")

# ── Step 4: Search for lead by email ─────────────────────────────────────────
print(f"\n[4/5] Searching for lead '{TARGET_EMAIL}'...")
try:
    ids_resp = api_get(f"/tables/{TABLE_ID}/views/{view_id}/records/ids")
    record_ids = ids_resp.get("results", [])
    print(f"[OK] Total records: {len(record_ids)}")

    if not record_ids:
        print("ERROR: Table is empty")
        sys.exit(1)

    BATCH_SIZE = 100
    found_record = None

    for i in range(0, len(record_ids), BATCH_SIZE):
        batch = record_ids[i:i + BATCH_SIZE]
        print(f"  Scanning records {i+1}–{min(i+BATCH_SIZE, len(record_ids))} of {len(record_ids)}...")
        records_resp = api_post(f"/tables/{TABLE_ID}/bulk-fetch-records", {"recordIds": batch})
        for rec in records_resp.get("results", []):
            cells = rec.get("cells", {})
            email_cell = cells.get(email_field_id, {})
            email_val = (email_cell.get("value", "") or "") if isinstance(email_cell, dict) else ""
            if TARGET_EMAIL in email_val.lower():
                found_record = rec
                print(f"[OK] Found lead — record ID: {rec['id']}")
                break
        if found_record:
            break

    if not found_record:
        print(f"ERROR: Lead '{TARGET_EMAIL}' not found in table {TABLE_ID}")
        sys.exit(1)

except Exception as e:
    print(f"ERROR: Search failed: {e}")
    sys.exit(1)


# ── Step 5: Extract fields ────────────────────────────────────────────────────
print(f"\n[5/5] Extracting fields...")
cells = found_record.get("cells", {})


def get_cell_value(field_id):
    if not field_id:
        return None
    cell = cells.get(field_id, {})
    if isinstance(cell, dict):
        return cell.get("value") or None
    return None


job_title     = get_cell_value(title_field_id)
linkedin_url  = get_cell_value(linkedin_field_id)
employee_count = get_cell_value(employee_field_id)
job_post_url  = get_cell_value(jobpost_field_id)

# Normalise employee count — may be int or string
if isinstance(employee_count, (int, float)):
    employee_count = str(int(employee_count))

print(f"  job_title:      {job_title}")
print(f"  linkedin_url:   {linkedin_url}")
print(f"  employee_count: {employee_count}")
print(f"  job_post_url:   {job_post_url}")

result = {
    "success": True,
    "lead_email": TARGET_EMAIL,
    "table_id": TABLE_ID,
    "record_id": found_record["id"],
    "job_title": job_title,
    "linkedin_url": linkedin_url,
    "employee_count": employee_count,
    "job_post_url": job_post_url,
    "fields_found": {
        "email":    {"id": email_field_id,    "name": email_field_name},
        "title":    {"id": title_field_id,    "name": title_field_name},
        "linkedin": {"id": linkedin_field_id, "name": linkedin_field_name},
        "employees":{"id": employee_field_id, "name": employee_field_name},
        "job_post": {"id": jobpost_field_id,  "name": jobpost_field_name},
    }
}

print(f"\n{'='*60}")
print(json.dumps(result, indent=2))
