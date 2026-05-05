#!/usr/bin/env python3
"""Verify Work Email and Employee Count field IDs for specified tables."""
import urllib.request, json, ssl, os, io, sys
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
try:
    from dotenv import load_dotenv; load_dotenv()
except: pass

BASE = "https://api.clay.com/v3"
ctx = ssl.create_default_context()

login_data = json.dumps({"email": os.getenv("CLAY_USERNAME"), "password": os.getenv("CLAY_PASSWORD"), "source": "web"}).encode()
req = urllib.request.Request(f"{BASE}/auth/login", data=login_data,
    headers={"Content-Type": "application/json", "Origin": "https://app.clay.com", "Referer": "https://app.clay.com/"}, method="POST")
resp = urllib.request.urlopen(req, context=ctx, timeout=30)
session = resp.headers.get("Set-Cookie", "").split(";")[0]
print("Auth OK\n")

TABLES_TO_CHECK = [
    {"name": "US No HM (new primary)",     "id": "t_0tdyro7QesUNY3WJrt2", "view": "gv_TgwDWXPdg8Ci",
     "expected_email": "f_0tc2a2qEFRZthdct3Cs", "expected_ec": "f_0t5mtcfvJknGywASv4z"},
    {"name": "Canada No HM (new primary)", "id": "t_0te5lh6AoWkxd39ktT8", "view": "gv_3cMh8vzuFqm4",
     "expected_email": "f_0taaxyjNBGfFWKYUnxK", "expected_ec": "f_0taayd3VvuPn9po6cYQ"},
]

EMAIL_PATTERNS = ["@", ".com", ".io", ".net", ".org"]

for t in TABLES_TO_CHECK:
    print(f"=== {t['name']} ({t['id']}) ===")
    try:
        r = urllib.request.Request(f"{BASE}/tables/{t['id']}/views/{t['view']}/records/ids", headers={"Cookie": session})
        ids_resp = json.loads(urllib.request.urlopen(r, context=ctx, timeout=30).read())
        record_ids = ids_resp.get("results", [])
        print(f"  Total records: {len(record_ids)}")

        sample = record_ids[:5]
        post_req = urllib.request.Request(f"{BASE}/tables/{t['id']}/bulk-fetch-records",
            data=json.dumps({"recordIds": sample}).encode(),
            headers={"Cookie": session, "Content-Type": "application/json"}, method="POST")
        resp_data = json.loads(urllib.request.urlopen(post_req, context=ctx, timeout=30).read())
        records = resp_data.get("results", [])

        if not records:
            print("  ERROR: No records returned")
            continue

        # Find email field: field whose value contains @ across sample records
        email_field_candidates = {}
        ec_field_candidates = {}

        for rec in records:
            for fid, cell in rec.get("cells", {}).items():
                val = cell.get("value", "") if isinstance(cell, dict) else str(cell)
                if not val:
                    continue
                val_str = str(val).replace("✅ ", "").strip()
                # Email pattern
                if any(p in val_str for p in EMAIL_PATTERNS) and "@" in val_str and len(val_str) < 100:
                    email_field_candidates[fid] = val_str
                # Employee count: numeric value reasonable for company size
                try:
                    num = float(str(val_str).replace(",", ""))
                    if 10 <= num <= 1_000_000:
                        ec_field_candidates[fid] = val_str
                except: pass

        # Report
        exp_email = t["expected_email"]
        exp_ec = t["expected_ec"]

        print(f"\n  Email field candidates (fields with @ values):")
        for fid, val in email_field_candidates.items():
            marker = " ← CONFIGURED" if fid == exp_email else ""
            print(f"    [{fid}] = {val}{marker}")

        print(f"\n  Employee count candidates (numeric fields 10–1M):")
        for fid, val in ec_field_candidates.items():
            marker = " ← CONFIGURED" if fid == exp_ec else ""
            print(f"    [{fid}] = {val}{marker}")

        # Verdict
        email_ok = exp_email in email_field_candidates
        ec_ok = exp_ec in ec_field_candidates
        print(f"\n  Work Email [{exp_email}]: {'✅ CORRECT' if email_ok else '❌ NOT FOUND in sample'}")
        print(f"  Employee Count [{exp_ec}]: {'✅ CORRECT' if ec_ok else '❌ NOT FOUND in sample'}")

    except Exception as e:
        print(f"  ERROR: {e}")
    print()
