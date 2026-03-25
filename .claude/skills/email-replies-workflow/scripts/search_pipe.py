import urllib.request
import json
import ssl
import os
from dotenv import load_dotenv

load_dotenv()
CLAY_USERNAME = os.getenv("CLAY_USERNAME")
CLAY_PASSWORD = os.getenv("CLAY_PASSWORD")

ctx = ssl.create_default_context()
BASE = "https://api.clay.com/v3"
TABLE_ID = "t_0t5pvx3g4o5WfysopqA"
SEARCH_TERMS = ["pipe.org", "pipe", "@pipe"]

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

# Get metadata
table_meta = api_get(f"/tables/{TABLE_ID}")
table_info = table_meta.get("table", table_meta)
fields = table_info.get("fields", [])
views = table_info.get("views", [])

field_map = {}
for f in fields:
    field_map[f["id"]] = f["name"]

# Get records
default_view = views[0]
view_id = default_view["id"]
ids_resp = api_get(f"/tables/{TABLE_ID}/views/{view_id}/records/ids")
record_ids = ids_resp.get("results", [])

print(f"Searching for pipe.org in {len(record_ids)} records...")

matches = []
BATCH_SIZE = 100

for i in range(0, len(record_ids), BATCH_SIZE):
    if i % 1000 == 0:
        print(f"  Checked {i}/{len(record_ids)} records...")

    batch = record_ids[i:i+BATCH_SIZE]
    records_resp = api_post(f"/tables/{TABLE_ID}/bulk-fetch-records", {"recordIds": batch})
    results = records_resp.get("results", [])

    for rec in results:
        cells = rec.get("cells", {})
        record_data = {}

        # Check all cells
        for fid, cell in cells.items():
            val = cell.get("value", "") if isinstance(cell, dict) else ""
            if isinstance(val, str):
                for term in SEARCH_TERMS:
                    if term.lower() in val.lower():
                        field_name = field_map.get(fid, fid)
                        if not record_data:
                            record_data = {"record_id": rec["id"], "matches": []}
                        record_data["matches"].append({
                            "field": field_name,
                            "value": val
                        })
                        break

        if record_data:
            matches.append(record_data)
            print(f"\n[Match] Record: {rec['id']}")
            for match in record_data["matches"]:
                print(f"  {match['field']}: {match['value']}")

print(f"\n{'='*60}")
print(f"Total records with 'pipe' or 'pipe.org': {len(matches)}")

if not matches:
    print("\nNo matches found. The email markb@pipe.org does not exist in this table.")
    print("\nPlease verify:")
    print("  1. The email address is correct")
    print("  2. The lead exists in the 'US Open Jobs - Hiring Managers' table")
    print("  3. The lead might be in a different table")
