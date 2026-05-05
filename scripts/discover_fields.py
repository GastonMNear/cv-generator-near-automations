#!/usr/bin/env python3
"""Discover field IDs in a Clay table by inspecting real records."""
import urllib.request, json, ssl, os, io, sys
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
try:
    from dotenv import load_dotenv; load_dotenv()
except: pass

BASE = "https://api.clay.com/v3"
ctx = ssl.create_default_context()
USERNAME = os.getenv("CLAY_USERNAME")
PASSWORD = os.getenv("CLAY_PASSWORD")

login_data = json.dumps({"email": USERNAME, "password": PASSWORD, "source": "web"}).encode()
req = urllib.request.Request(f"{BASE}/auth/login", data=login_data,
    headers={"Content-Type": "application/json", "Origin": "https://app.clay.com", "Referer": "https://app.clay.com/"}, method="POST")
resp = urllib.request.urlopen(req, context=ctx, timeout=30)
session = resp.headers.get("Set-Cookie", "").split(";")[0]
print("Auth OK")

TABLE_ID = "t_0te5kjxke6yWVRzedb7"
VIEW_ID = "gv_TgwDWXPdg8Ci"

r = urllib.request.Request(f"{BASE}/tables/{TABLE_ID}/views/{VIEW_ID}/records/ids", headers={"Cookie": session})
ids_resp = json.loads(urllib.request.urlopen(r, context=ctx, timeout=30).read())
record_ids = ids_resp.get("results", [])
print(f"Total records: {len(record_ids)}")

first3 = record_ids[:3]
post_req = urllib.request.Request(f"{BASE}/tables/{TABLE_ID}/bulk-fetch-records",
    data=json.dumps({"recordIds": first3}).encode(),
    headers={"Cookie": session, "Content-Type": "application/json"}, method="POST")
resp_data = json.loads(urllib.request.urlopen(post_req, context=ctx, timeout=30).read())
records = resp_data.get("results", [])

if records:
    rec = records[0]
    print(f"\nAll non-empty fields in first record (ID: {rec['id']}):")
    for fid, cell in sorted(rec.get("cells", {}).items()):
        val = cell.get("value", "") if isinstance(cell, dict) else str(cell)
        if val and str(val).strip():
            print(f"  [{fid}] = {str(val)[:100]}")
