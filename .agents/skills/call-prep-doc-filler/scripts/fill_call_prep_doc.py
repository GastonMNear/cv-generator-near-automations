#!/usr/bin/env python3
"""
Fill a call prep Google Doc template with lead data.

Usage:
    python fill_call_prep_doc.py <doc_url> <job_title> <linkedin_url> <employee_count> <job_post_url>

Pass "" for any field you want to skip.

The doc must contain a table with rows labelled:
  - Job Title
  - LinkedIn
  - # Employees (or Employees)
  - Roles they're looking to hire for (or Roles)
"""

import os
import re
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN")

if not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN]):
    print("ERROR: Missing Google credentials in .env (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN)")
    sys.exit(1)

if len(sys.argv) < 6:
    print("Usage: fill_call_prep_doc.py <doc_url> <job_title> <linkedin_url> <employee_count> <job_post_url>")
    sys.exit(1)

DOC_URL        = sys.argv[1]
JOB_TITLE      = sys.argv[2].strip() or None
LINKEDIN_URL   = sys.argv[3].strip() or None
EMPLOYEE_COUNT = sys.argv[4].strip() or None
JOB_POST_URL   = sys.argv[5].strip() or None

# ── Extract document ID ───────────────────────────────────────────────────────
match = re.search(r"/document/d/([a-zA-Z0-9_-]+)", DOC_URL)
if not match:
    print(f"ERROR: Cannot extract document ID from URL: {DOC_URL}")
    sys.exit(1)

DOC_ID = match.group(1)
print(f"Document ID: {DOC_ID}")
print(f"Values to fill:")
print(f"  Job Title:      {JOB_TITLE}")
print(f"  LinkedIn:       {LINKEDIN_URL}")
print(f"  Employee Count: {EMPLOYEE_COUNT}")
print(f"  Job Post URL:   {JOB_POST_URL}")


# ── Google OAuth ──────────────────────────────────────────────────────────────
def get_access_token():
    resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": REFRESH_TOKEN,
            "grant_type": "refresh_token",
        }
    )
    if resp.status_code != 200:
        raise Exception(f"Token refresh failed: {resp.text}")
    return resp.json()["access_token"]


print("\nRefreshing Google access token...")
try:
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    print("[OK] Token refreshed")
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)


# ── Read the document ─────────────────────────────────────────────────────────
print(f"\nReading document {DOC_ID}...")
resp = requests.get(f"https://docs.googleapis.com/v1/documents/{DOC_ID}", headers=headers)
if resp.status_code != 200:
    print(f"ERROR: Failed to read document: {resp.status_code} {resp.text}")
    sys.exit(1)

doc = resp.json()
body_content = doc.get("body", {}).get("content", [])
print(f"[OK] Document read ({len(body_content)} content elements)")


# ── Helper: extract all text from a cell ─────────────────────────────────────
def cell_text(cell):
    """Return concatenated text content of a table cell."""
    parts = []
    for elem in cell.get("content", []):
        para = elem.get("paragraph", {})
        for pe in para.get("elements", []):
            tr = pe.get("textRun", {})
            parts.append(tr.get("content", ""))
    return "".join(parts)


def cell_text_range(cell):
    """
    Return (start_index, end_index) of the text content area inside a cell.
    This is the range you can delete/insert within.
    """
    paragraphs = cell.get("content", [])
    if not paragraphs:
        return None, None
    first_para = paragraphs[0].get("paragraph", {})
    last_para  = paragraphs[-1].get("paragraph", {})

    # Get first element's startIndex
    first_elems = first_para.get("elements", [])
    if not first_elems:
        return None, None
    start = first_elems[0].get("startIndex", None)

    # Get last element's endIndex (the mandatory \n is at endIndex-1)
    last_elems = last_para.get("elements", [])
    if not last_elems:
        return None, None
    end = last_elems[-1].get("endIndex", None)

    return start, end


def cell_append_index(cell):
    """
    Return the index at which to insert appended text (just before the final \n
    of the last paragraph in the cell).
    """
    paragraphs = cell.get("content", [])
    if not paragraphs:
        return None
    last_para  = paragraphs[-1].get("paragraph", {})
    last_elems = last_para.get("elements", [])
    if not last_elems:
        return None
    # endIndex of last element includes the final \n — insert before it
    return last_elems[-1].get("endIndex", None) - 1


# ── Find the table and match rows ─────────────────────────────────────────────
LABEL_MAP = {
    "job title": ("replace", JOB_TITLE),
    "linkedin":  ("replace", LINKEDIN_URL),
    "employee":  ("replace", EMPLOYEE_COUNT),
    "roles":     ("append",  JOB_POST_URL),
}

found_cells = {}   # keyword → (mode, value, value_cell)
found_labels = []  # for diagnostics

table_found = False
for element in body_content:
    table = element.get("table")
    if not table:
        continue
    table_found = True
    print(f"\nTable found ({table.get('rows', '?')} rows). Matching labels...")

    for row in table.get("tableRows", []):
        cells = row.get("tableCells", [])
        if len(cells) < 2:
            continue

        label_cell = cells[0]
        value_cell = cells[1]
        label = cell_text(label_cell).strip().lower().rstrip(":")
        found_labels.append(label)

        for keyword, (mode, value) in LABEL_MAP.items():
            if keyword in label and keyword not in found_cells:
                found_cells[keyword] = (mode, value, value_cell)
                print(f"  [MATCH] '{label}' → keyword='{keyword}', mode={mode}, value={repr(value)}")
                break

    break  # only process first table

if not table_found:
    print("ERROR: No table found in the document. Verify the doc URL and structure.")
    sys.exit(1)

if not found_cells:
    print("ERROR: No label rows matched. Labels found in table:")
    for lbl in found_labels:
        print(f"  - {lbl}")
    sys.exit(1)


# ── Build batchUpdate requests (highest index first to avoid shifts) ───────────
updates = []  # list of (index, requests_list)

for keyword, (mode, value, value_cell) in found_cells.items():
    if value is None:
        print(f"  [SKIP] '{keyword}' — no value provided")
        continue

    if mode == "replace":
        start, end = cell_text_range(value_cell)
        if start is None or end is None:
            print(f"  [WARN] Cannot determine range for '{keyword}', skipping")
            continue

        # The mandatory final \n must stay — delete up to end-1
        deletable_end = end - 1
        if deletable_end > start:
            updates.append((deletable_end, [
                {
                    "deleteContentRange": {
                        "range": {
                            "startIndex": start,
                            "endIndex": deletable_end
                        }
                    }
                },
                {
                    "insertText": {
                        "location": {"index": start},
                        "text": value
                    }
                }
            ]))
        else:
            # Cell is already empty — just insert
            updates.append((start, [
                {
                    "insertText": {
                        "location": {"index": start},
                        "text": value
                    }
                }
            ]))

    elif mode == "append":
        idx = cell_append_index(value_cell)
        if idx is None:
            print(f"  [WARN] Cannot determine append index for '{keyword}', skipping")
            continue
        updates.append((idx, [
            {
                "insertText": {
                    "location": {"index": idx},
                    "text": f"\n{value}"
                }
            }
        ]))

# Sort by index descending so earlier insertions don't shift later ones
updates.sort(key=lambda x: x[0], reverse=True)
all_requests = []
for _, reqs in updates:
    all_requests.extend(reqs)

if not all_requests:
    print("\nNothing to update (all values were empty/null).")
    sys.exit(0)


# ── Send batchUpdate ──────────────────────────────────────────────────────────
print(f"\nSending {len(all_requests)} batchUpdate operations...")
update_resp = requests.post(
    f"https://docs.googleapis.com/v1/documents/{DOC_ID}:batchUpdate",
    headers=headers,
    json={"requests": all_requests}
)

if update_resp.status_code != 200:
    print(f"ERROR: batchUpdate failed: {update_resp.status_code}")
    print(update_resp.text)
    sys.exit(1)

print("[OK] Document updated successfully!")
print(f"\nDoc URL: {DOC_URL}")

# Summary
print("\nFields filled:")
for keyword, (mode, value, _) in found_cells.items():
    if value is not None:
        action = "appended" if mode == "append" else "replaced"
        print(f"  [{action}] {keyword}: {value}")
    else:
        print(f"  [skipped] {keyword}: no value")
