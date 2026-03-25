import urllib.request
import json
import ssl
import sys

# Fix Windows encoding
sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
BASE = "https://api.clay.com/v3"
TABLE_ID = "t_0t59d2y3ZuD4396Kz5B"  # US Open Jobs - No Hiring Manager
TARGET_EMAIL = "dahuja@onemindservices.com"
RECORD_ID = "r_0tb67vzT8RrjRn9m9xj"  # Already found

# Authenticate
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
print("Authenticated OK")

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
field_map = {f["id"]: f["name"] for f in fields}

# Fetch specific record
records_resp = api_post(f"/tables/{TABLE_ID}/bulk-fetch-records", {"recordIds": [RECORD_ID]})
results = records_resp.get("results", [])

if not results:
    print("Record not found!")
    sys.exit(1)

rec = results[0]
cells = rec.get("cells", {})

print(f"\nALL NON-EMPTY FIELDS FOR: {TARGET_EMAIL}")
print("=" * 60)
for fid, cell in cells.items():
    name = field_map.get(fid, fid)
    val = cell.get("value", "") if isinstance(cell, dict) else cell
    if val and val != "" and val != [] and val != {}:
        if isinstance(val, (dict, list)):
            val = json.dumps(val, ensure_ascii=False)
        print(f"{name}: {val}")
