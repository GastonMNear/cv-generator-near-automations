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

# ── Known table cache ─────────────────────────────────────────────────────────
# Skips the metadata API call for known tables — speeds up runs by ~0.5–1s.
#
# HOW TO UPDATE when field IDs change:
#   1. Find the new ID in Clay (or check known-tables.md)
#   2. Edit the matching table entry below
#   3. The change takes effect immediately on next run
#
# SAFE TO LEAVE STALE: if a cached email ID is wrong, the script automatically
# falls back to dynamic field discovery and retries — stale entries cause a
# slow retry, not a crash. Other stale IDs (title/employee/job_post) just
# return None for that field; the dynamic fallback will find the right one.
#
# Canonical field ID source: .claude/skills/clay-api/references/known-tables.md
#
# Per-entry keys:
#   view     — Default View ID
#   emails   — ALL email field IDs to search, in priority order (checked per-record)
#   employee — employee count field ID (or None to discover dynamically)
#   job_post — job posting URL field ID (linkedin.com/jobs/view/...) (or None)
#   title    — lead's personal job title field ID (or None)
#   linkedin — lead's personal LinkedIn profile field ID (or None)
KNOWN_TABLES = {
    "t_0t59d2y3ZuD4396Kz5B": {  # US Open Jobs - No Hiring Manager
        "view":     "gv_TgwDWXPdg8Ci",
        "emails":   ["f_0tc2a2qEFRZthdct3Cs"],   # Work Email
        "employee": "f_0t5mtcfvJknGywASv4z",
        "job_post": "f_QIP4GfH5XFZo",             # Written Job URL
        "title":    "f_9XFV2vIqjwAh",             # open_role_title (call-prep only)
        "linkedin": None,                          # personal profile URL — discover dynamically
    },
    "t_0tbt48xVeCFCi8pFzip": {  # Copy of Leads - US OJ No HM (fallback table)
        "view":     "gv_TgwDWXPdg8Ci",
        "emails":   ["f_0tbt65uGbguMonif8dU"],    # Work Email
        "employee": "f_0t5mtcfvJknGywASv4z",
        "job_post": "f_QIP4GfH5XFZo",             # Written Job URL
        "title":    None,
        "linkedin": None,
    },
    "t_0t5pvx3g4o5WfysopqA": {  # US Open Jobs - Hiring Managers
        "view":     "gv_TgwDWXPdg8Ci",
        "emails":   ["f_0t063ygVDhWMs5MT4MD"],    # Work Email
        "employee": "f_0t062fr5fKsUy27nJhf",
        "job_post": "f_0t06147KZtafpAaiDTz",      # Job LinkedIn URL
        "title":    "f_0t060rsDJXy6EbBFdCD",      # Imported Job Title (call-prep only)
        "linkedin": None,
    },
    "t_aNvk4jWMNeG7": {  # LatAm Open Jobs - No HMs
        "view":     "gv_TgwDWXPdg8Ci",
        "emails":   ["f_SUTHMU5bi2XD"],           # Validated Email
        "employee": "f_0t6acqvuQxjjQNTWhbK",
        "job_post": "f_QIP4GfH5XFZo",             # Written Job URL
        "title":    None,
        "linkedin": None,
    },
    "t_0t6ghvgCsvvvqAus4bp": {  # LatAm Open Jobs - Hiring Managers
        "view":     "gv_TgwDWXPdg8Ci",
        "emails":   ["f_0t063ygVDhWMs5MT4MD"],    # Work Email
        "employee": "f_0t062fr5fKsUy27nJhf",
        "job_post": "f_0t06147KZtafpAaiDTz",      # Job LinkedIn URL
        "title":    "f_0t060rsDJXy6EbBFdCD",      # Imported Job Title (call-prep only)
        "linkedin": None,
    },
    "t_0taasak5KAa5zbTmTJd": {  # Canada Open Jobs - No HM
        "view":     "gv_3cMh8vzuFqm4",
        "emails":   ["f_0taaxyjNBGfFWKYUnxK"],    # Work Email
        "employee": "f_0taayd3VvuPn9po6cYQ",
        "job_post": "f_0taawsuMjxnV74YtCZ8",      # Job LinkedIn Url
        "title":    "f_0taaxpwuXVMYbRoGAA7",      # Lead Title (call-prep only)
        "linkedin": None,
    },
    "t_0t746txPqz5sjFMtut2": {  # Canada Open Jobs - HMs
        "view":     "gv_TgwDWXPdg8Ci",
        "emails":   ["f_0t063ygVDhWMs5MT4MD"],    # Work Email
        "employee": "f_0t062fr5fKsUy27nJhf",
        "job_post": "f_0t06147KZtafpAaiDTz",      # Job LinkedIn URL
        "title":    "f_0t060rsDJXy6EbBFdCD",      # Imported Job Title (call-prep only)
        "linkedin": None,
    },
}

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


def fetch_metadata_and_resolve_fields(missing_only=None):
    """Fetch table metadata and resolve field IDs via pattern matching.
    missing_only: set of field names to resolve ('title','linkedin','employee','job_post','email').
                  If None, resolve all.
    Returns (view_id, email_fids, title_id, linkedin_id, employee_id, jobpost_id, fields_list).
    """
    print(f"  Fetching table metadata for {TABLE_ID}...")
    table_meta = api_get(f"/tables/{TABLE_ID}")
    table_info = table_meta.get("table", table_meta)
    fields = table_info.get("fields", [])
    views  = table_info.get("views", [])

    if not fields:
        print(f"ERROR: Table {TABLE_ID} has no fields"); sys.exit(1)
    if not views:
        print("ERROR: Table has no views"); sys.exit(1)

    default_view = next((v for v in views if "default" in v.get("name","").lower()), views[0])
    v_id = default_view["id"]
    print(f"  [OK] {len(fields)} fields, view: {default_view.get('name', v_id)}")

    EMAIL_PATTERNS = ["work email", "find work email", "validated email", "contact email", "email"]
    EMAIL_EXCLUDE  = ["email one", "email two", "email three", "email body", "email copy"]
    TITLE_PATTERNS = ["job title", "title", "position", "role"]
    TITLE_EXCLUDE  = ["company", "url", "link"]
    LINKEDIN_PATTERNS  = ["prospect linkedin", "contact linkedin", "person linkedin", "linkedin url", "linkedin profile"]
    EMPLOYEE_PATTERNS  = ["employee count", "# employees", "num employees", "headcount", "company size", "employees"]
    JOB_POST_PATTERNS  = ["job post url", "job post linkedin", "linkedin job", "opening url", "posting url", "job url", "job link"]
    JOB_POST_EXCLUDE   = ["prospect", "person", "profile", "company linkedin"]

    target = missing_only or {"email", "title", "linkedin", "employee", "job_post"}

    e_id, e_name   = find_field(fields, EMAIL_PATTERNS, EMAIL_EXCLUDE, "email") if "email" in target else (None, None)
    t_id, t_name   = find_field(fields, TITLE_PATTERNS, TITLE_EXCLUDE, "title") if "title" in target else (None, None)
    li_id, li_name = find_field(fields, LINKEDIN_PATTERNS, label="linkedin")     if "linkedin" in target else (None, None)
    ec_id, ec_name = find_field(fields, EMPLOYEE_PATTERNS, label="employee")     if "employee" in target else (None, None)
    jp_id, jp_name = find_field(fields, JOB_POST_PATTERNS, JOB_POST_EXCLUDE, "job_post") if "job_post" in target else (None, None)

    return v_id, ([e_id] if e_id else []), t_id, t_name, li_id, li_name, ec_id, ec_name, jp_id, jp_name, fields


# ── Step 2: Resolve field IDs ─────────────────────────────────────────────────
cache = KNOWN_TABLES.get(TABLE_ID)

if cache:
    print(f"\n[2/5] Known table — using cached field IDs (metadata call skipped)")
    view_id       = cache["view"]
    search_email_fids = cache["emails"]

    title_field_id    = cache.get("title")
    title_field_name  = "cached" if title_field_id else None
    linkedin_field_id = cache.get("linkedin")
    linkedin_field_name = "cached" if linkedin_field_id else None
    employee_field_id = cache.get("employee")
    employee_field_name = "cached" if employee_field_id else None
    jobpost_field_id  = cache.get("job_post")
    jobpost_field_name = "cached" if jobpost_field_id else None

    # Fetch metadata only for fields not in cache
    uncached = {k for k, v in [("title", title_field_id), ("linkedin", linkedin_field_id),
                                ("employee", employee_field_id), ("job_post", jobpost_field_id)] if v is None}
    if uncached:
        print(f"  Fields not cached ({', '.join(uncached)}) — fetching metadata to resolve them...")
        try:
            _, _, t, tn, li, lin, ec, ecn, jp, jpn, _ = fetch_metadata_and_resolve_fields(uncached)
            if "title"    in uncached: title_field_id,    title_field_name    = t,  tn
            if "linkedin" in uncached: linkedin_field_id, linkedin_field_name = li, lin
            if "employee" in uncached: employee_field_id, employee_field_name = ec, ecn
            if "job_post" in uncached: jobpost_field_id,  jobpost_field_name  = jp, jpn
        except Exception as e:
            print(f"  [WARN] Partial metadata fetch failed: {e}. Affected fields will be None.")

    email_field_id   = search_email_fids[0]
    email_field_name = "Work Email (cached)"

else:
    # Unknown table — full dynamic discovery
    print(f"\n[2/5] Unknown table — fetching metadata + discovering fields dynamically...")
    try:
        view_id, efids, title_field_id, title_field_name, linkedin_field_id, linkedin_field_name, \
            employee_field_id, employee_field_name, jobpost_field_id, jobpost_field_name, _ \
            = fetch_metadata_and_resolve_fields()

        if not efids:
            print("ERROR: Cannot identify email field in table"); sys.exit(1)
        search_email_fids = efids
        email_field_id    = efids[0]
        email_field_name  = "discovered"
    except Exception as e:
        print(f"ERROR: Failed to fetch table metadata: {e}"); sys.exit(1)

# Report field resolution
print(f"[OK] Email fields: {search_email_fids}")
for label, fid, fname in [("title", title_field_id, title_field_name),
                           ("linkedin", linkedin_field_id, linkedin_field_name),
                           ("employee", employee_field_id, employee_field_name),
                           ("job_post", jobpost_field_id, jobpost_field_name)]:
    if fid:
        print(f"[OK] {label}: {fname} ({fid})")
    else:
        print(f"[WARN] {label}: not found")


# ── Step 3: Search for lead by email ─────────────────────────────────────────
def scan_for_lead(table_id, view_id, email_fids):
    """Scan table batches for a lead matching TARGET_EMAIL. Returns record or None."""
    ids_resp   = api_get(f"/tables/{table_id}/views/{view_id}/records/ids")
    record_ids = ids_resp.get("results", [])
    print(f"  Total records: {len(record_ids)}")

    if not record_ids:
        return None

    BATCH_SIZE = 10_000  # tested — Clay handles up to 10k records per call
    for i in range(0, len(record_ids), BATCH_SIZE):
        batch = record_ids[i:i + BATCH_SIZE]
        print(f"  Scanning {i+1}–{min(i+BATCH_SIZE, len(record_ids))} of {len(record_ids)}...")
        resp = api_post(f"/tables/{table_id}/bulk-fetch-records", {"recordIds": batch})
        for rec in resp.get("results", []):
            cells = rec.get("cells", {})
            for fid in email_fids:
                cell = cells.get(fid, {})
                val  = cell.get("value", "") if isinstance(cell, dict) else ""
                val  = val.replace("✅ ", "").strip() if isinstance(val, str) else ""
                if TARGET_EMAIL in val.lower():
                    return rec
    return None


print(f"\n[3/5] Searching for lead '{TARGET_EMAIL}'...")
try:
    found_record = scan_for_lead(TABLE_ID, view_id, search_email_fids)

    # If not found and we used cached IDs, the cache may be stale — retry with dynamic discovery
    if not found_record and cache:
        print(f"\n[WARN] Lead not found using cached email field IDs.")
        print(f"       Cached IDs may be stale. Falling back to dynamic field discovery...")
        print(f"       Fix: update the '{TABLE_ID}' entry in KNOWN_TABLES (emails list) in this script.")
        print(f"       Reference: .claude/skills/clay-api/references/known-tables.md")
        try:
            _, efids, title_field_id, title_field_name, linkedin_field_id, linkedin_field_name, \
                employee_field_id, employee_field_name, jobpost_field_id, jobpost_field_name, _ \
                = fetch_metadata_and_resolve_fields()
            if efids:
                search_email_fids = efids
                email_field_id    = efids[0]
                email_field_name  = "dynamically discovered"
                print(f"  Retrying with discovered email field(s): {efids}")
                found_record = scan_for_lead(TABLE_ID, view_id, search_email_fids)
        except Exception as e:
            print(f"ERROR: Dynamic discovery fallback failed: {e}"); sys.exit(1)

    if not found_record:
        print(f"ERROR: Lead '{TARGET_EMAIL}' not found in table {TABLE_ID}")
        sys.exit(1)

    print(f"[OK] Found lead — record ID: {found_record['id']}")

except SystemExit:
    raise
except Exception as e:
    print(f"ERROR: Search failed: {e}"); sys.exit(1)


# ── Step 4: Extract fields ────────────────────────────────────────────────────
print(f"\n[4/5] Extracting fields...")
cells = found_record.get("cells", {})


def get_cell_value(field_id):
    if not field_id:
        return None
    cell = cells.get(field_id, {})
    if isinstance(cell, dict):
        return cell.get("value") or None
    return None


job_title      = get_cell_value(title_field_id)
linkedin_url   = get_cell_value(linkedin_field_id)
employee_count = get_cell_value(employee_field_id)
job_post_url   = get_cell_value(jobpost_field_id)

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
