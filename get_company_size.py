import urllib.request
import json
import ssl

# Configuration
ctx = ssl.create_default_context()
BASE = "https://api.clay.com/v3"
TABLE_ID = "t_0t5pvx3g4o5WfysopqA"  # US Open Jobs - Hiring Managers
RECORD_ID = "r_0tayqg9kjiFqaNfsh4R"  # Kyle's record

# Clay credentials
CLAY_USERNAME = "kevin.dubon@hirewithnear.com"
CLAY_PASSWORD = "P$3NsPEHJu6se2p"

print("Fetching company size information from Clay...")

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

# Build field map
field_map = {}
for f in fields:
    field_map[f["id"]] = f["name"]

# Look for company size/employee count fields
size_keywords = ["size", "employee", "headcount", "company size", "employees", "count"]
print("\nFields related to company size:")
for fid, fname in field_map.items():
    name_lower = fname.lower()
    if any(kw in name_lower for kw in size_keywords):
        print(f"  - {fname} ({fid})")

# Fetch the specific record
print(f"\nFetching record {RECORD_ID}...")
record_resp = api_post(f"/tables/{TABLE_ID}/bulk-fetch-records", {"recordIds": [RECORD_ID]})
record = record_resp.get("results", [{}])[0]
cells = record.get("cells", {})

print(f"\n{'='*60}")
print(f"COMPANY SIZE INFORMATION FOR: kyle@ctibusinesstravel.com")
print(f"{'='*60}\n")

# Extract and display size-related fields
found_any = False
for fid, cell in cells.items():
    fname = field_map.get(fid, fid)
    name_lower = fname.lower()

    if any(kw in name_lower for kw in size_keywords):
        val = cell.get("value", "") if isinstance(cell, dict) else cell
        if val:
            print(f"{fname}:")
            if isinstance(val, dict):
                print(f"  {json.dumps(val, indent=2)}")
            elif isinstance(val, list):
                print(f"  {json.dumps(val, indent=2)}")
            else:
                print(f"  {val}")
            print()
            found_any = True

if not found_any:
    print("No company size information found in this record.")
