#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check table details and show sample records
"""

import urllib.request
import json
import ssl
import os
from dotenv import load_dotenv

load_dotenv()

CLAY_USERNAME = os.getenv("CLAY_USERNAME")
CLAY_PASSWORD = os.getenv("CLAY_PASSWORD")
BASE = "https://api.clay.com/v3"
WORKSPACE_ID = "447061"

ctx = ssl.create_default_context()

if os.sys.platform == "win32":
    os.sys.stdout.reconfigure(encoding='utf-8')

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

# Get all tables
print("Fetching all tables in workspace...")
tables_resp = api_get(f"/workspaces/{WORKSPACE_ID}/tables")
tables = tables_resp.get("tables", [])

print(f"\nFound {len(tables)} tables:\n")

# Look for "US Open Jobs" tables
print("Tables matching 'US Open Jobs':")
for t in tables:
    name = t.get("name", "")
    if "US" in name and "Open Jobs" in name:
        print(f"  - {name}")
        print(f"    ID: {t['id']}")
        print(f"    Record count: {t.get('recordCount', 'unknown')}")
        print()
