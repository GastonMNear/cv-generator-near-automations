import urllib.request
import json
import ssl
import sys
import os
from dotenv import load_dotenv

load_dotenv()
CLAY_USERNAME = os.getenv("CLAY_USERNAME")
CLAY_PASSWORD = os.getenv("CLAY_PASSWORD")

ctx = ssl.create_default_context()
BASE = "https://api.clay.com/v3"
TABLE_ID = "t_0t5pvx3g4o5WfysopqA"
SEARCH_TERM = "markb"

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
cookie_header = resp.headers.get("Set-Cookie", "")
session = cookie_header.split(";")[0]

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

# Get table metadata
table_meta = api_get(f"/tables/{TABLE_ID}")
table_info = table_meta.get("table", table_meta)
fields = table_info.get("fields", [])
views = table_info.get("views", [])

field_map = {}
for f in fields:
    field_map[f["id"]] = f["name"]

# Get record IDs
default_view = views[0]
view_id = default_view["id"]
ids_resp = api_get(f"/tables/{TABLE_ID}/views/{view_id}/records/ids")
record_ids = ids_resp.get("results", [])

print(f"Searching for '{SEARCH_TERM}' in {len(record_ids)} records...")
print(f"\nEmail-related fields in table:")
for f in fields:
    if "email" in f["name"].lower():
        print(f"  - {f['name']} ({f['id']})")

matches = []
BATCH_SIZE = 100

for i in range(0, min(1000, len(record_ids)), BATCH_SIZE):  # Only check first 1000
    batch = record_ids[i:i+BATCH_SIZE]
    records_resp = api_post(f"/tables/{TABLE_ID}/bulk-fetch-records", {"recordIds": batch})
    results = records_resp.get("results", [])

    for rec in results:
        cells = rec.get("cells", {})
        # Check all cells for search term
        for fid, cell in cells.items():
            val = cell.get("value", "") if isinstance(cell, dict) else ""
            if isinstance(val, str) and SEARCH_TERM.lower() in val.lower():
                field_name = field_map.get(fid, fid)
                matches.append({
                    "record_id": rec["id"],
                    "field": field_name,
                    "value": val
                })
                print(f"\nMatch found in record {rec['id']}:")
                print(f"  Field: {field_name}")
                print(f"  Value: {val}")

if not matches:
    print(f"\nNo matches found for '{SEARCH_TERM}' in first 1000 records")
else:
    print(f"\nTotal matches: {len(matches)}")
