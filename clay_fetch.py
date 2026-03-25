import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
BASE = "https://api.clay.com/v3"
TABLE_ID = "t_0t5pvx3g4o5WfysopqA"
TARGET_EMAIL = "lynne@moraware.com"

# Step 1: Authenticate
login_data = json.dumps({
    "email": "kevin.dubon@hirewithnear.com",
    "password": "P$3NsPEHJu6se2p",
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
print(f"Authenticated OK")

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
print(f"\nFetching table metadata for {TABLE_ID}...")
table_meta = api_get(f"/tables/{TABLE_ID}")
table_info = table_meta.get("table", table_meta)
fields = table_info.get("fields", [])
views = table_info.get("views", [])

# Build field map
field_map = {}
for f in fields:
    field_map[f["id"]] = f["name"]

# Print fields related to our search
print(f"\nTotal fields: {len(fields)}")
interesting_keywords = ["email", "linkedin", "company size", "size", "headcount", "employees", "latam", "latin", "country", "countries"]
print("\nRelevant fields:")
for f in fields:
    name_lower = f["name"].lower()
    if any(kw in name_lower for kw in interesting_keywords):
        print(f"  {f['id']} — {f['name']} (type: {f.get('type', '?')})")

# Step 3: Get default view and record IDs
default_view = views[0] if views else None
if not default_view:
    print("No views found!")
    exit(1)

view_id = default_view["id"]
print(f"\nDefault view: {view_id} ({default_view.get('name', '')})")

print(f"\nFetching record IDs...")
ids_resp = api_get(f"/tables/{TABLE_ID}/views/{view_id}/records/ids")
record_ids = ids_resp.get("results", [])
print(f"Total records: {len(record_ids)}")

# Step 4: Batch fetch and search for email
BATCH_SIZE = 100
found = None
for i in range(0, len(record_ids), BATCH_SIZE):
    batch = record_ids[i:i+BATCH_SIZE]
    records = api_post(f"/tables/{TABLE_ID}/bulk-fetch-records", {"recordIds": batch})
    results = records.get("results", [])

    for rec in results:
        cells = rec.get("cells", {})
        # Check all cells for email match
        for fid, cell in cells.items():
            val = cell.get("value", "") if isinstance(cell, dict) else ""
            if isinstance(val, str) and TARGET_EMAIL.lower() in val.lower():
                found = rec
                print(f"\nFOUND record {rec['id']} (matched on field {field_map.get(fid, fid)})")
                break
        if found:
            break
    if found:
        break
    print(f"  Searched {min(i+BATCH_SIZE, len(record_ids))}/{len(record_ids)} records...")

if not found:
    print(f"\nNo record found with email {TARGET_EMAIL}")
    exit(1)

# Step 5: Extract requested fields
print(f"\n{'='*60}")
print(f"RESULTS FOR: {TARGET_EMAIL}")
print(f"{'='*60}")

cells = found.get("cells", {})
for fid, cell in cells.items():
    name = field_map.get(fid, fid)
    val = cell.get("value", "") if isinstance(cell, dict) else cell
    name_lower = name.lower()
    if any(kw in name_lower for kw in ["linkedin", "company size", "size", "headcount", "employees", "latam", "latin", "country", "countries"]):
        # Handle nested values
        if isinstance(val, dict):
            val = json.dumps(val, indent=2)
        elif isinstance(val, list):
            val = json.dumps(val, indent=2)
        print(f"\n{name}:")
        print(f"  {val}")
