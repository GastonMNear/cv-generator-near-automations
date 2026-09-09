#!/usr/bin/env python3
"""
Domain/substring scanner for Clay tables — recovery tool for when
fetch_lead.py reports "not found".

Scans ALL fields of every record in a table chain for a substring
(usually the email domain, e.g. "curogram") and prints the matching
fields. Use it to discover the lead's real email when the address
supplied by the user is a variant (michael@ vs michael.hsu@).

Usage:
  python3 scripts/find_by_domain.py --needle curogram --table "asia no hm"

NOTE: load_dotenv() must be given an explicit path — a bare load_dotenv()
raises AssertionError when the script is piped via stdin.
"""
import urllib.request, json, ssl, os, sys, time, argparse

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(HERE, ".env"))
except ImportError:
    pass

sys.path.insert(0, os.path.join(HERE, "scripts"))

ap = argparse.ArgumentParser()
ap.add_argument("--needle", required=True, help="substring to search, e.g. a domain")
ap.add_argument("--table",  required=True, help="table alias, same as fetch_lead.py")
args = ap.parse_args()

# Reuse fetch_lead's table registry so the two stay in sync.
import importlib.util
spec = importlib.util.spec_from_file_location("fl", os.path.join(HERE, "scripts", "fetch_lead.py"))
# fetch_lead.py runs top-to-bottom, so import its TABLES dict by parsing instead.
src = open(os.path.join(HERE, "scripts", "fetch_lead.py")).read()
ns = {}
start = src.index("TABLES = {")
end   = src.index("\n}\n", start) + 3
exec(src[start:end], ns)
TABLES = ns["TABLES"]

alias = args.table.lower().strip()
table_id = None
for tid, cfg in TABLES.items():
    if any(a in alias or alias in a for a in cfg.get("aliases", [])):
        table_id = tid
        break
if not table_id:
    print("Unknown table alias. Known aliases:")
    for tid, cfg in TABLES.items():
        if cfg.get("aliases"):
            print("  ", cfg["aliases"][0], "->", cfg["name"])
    sys.exit(1)

U = os.getenv("CLAY_USERNAME"); P = os.getenv("CLAY_PASSWORD")
BASE = "https://api.clay.com/v3"
ctx = ssl.create_default_context()

req = urllib.request.Request(f"{BASE}/auth/login",
    data=json.dumps({"email": U, "password": P, "source": "web"}).encode(),
    headers={"Content-Type": "application/json",
             "Origin": "https://app.clay.com", "Referer": "https://app.clay.com/"},
    method="POST")
session = urllib.request.urlopen(req, context=ctx, timeout=30).headers.get("Set-Cookie", "").split(";")[0]
print("Auth OK")

def get(p):
    return json.loads(urllib.request.urlopen(
        urllib.request.Request(BASE + p, headers={"Cookie": session}), context=ctx, timeout=60).read())

def post(p, d, retries=3):
    for a in range(retries):
        try:
            return json.loads(urllib.request.urlopen(urllib.request.Request(BASE + p,
                data=json.dumps(d).encode(),
                headers={"Cookie": session, "Content-Type": "application/json"},
                method="POST"), context=ctx, timeout=180).read())
        except Exception:
            if a < retries - 1: time.sleep(5 * (a + 1))
            else: raise

chain = [(table_id, TABLES[table_id])]
for fb in TABLES[table_id].get("fallbacks", []):
    if fb in TABLES:
        chain.append((fb, TABLES[fb]))

needle = args.needle.lower()
for tid, cfg in chain:
    ids = get(f"/tables/{tid}/views/{cfg['view']}/records/ids").get("results", [])
    print(f"\n{cfg['name']} ({tid}): {len(ids)} records")
    hits = 0
    for i in range(0, len(ids), 300):
        for rec in post(f"/tables/{tid}/bulk-fetch-records", {"recordIds": ids[i:i+300]}).get("results", []):
            if needle in json.dumps(rec.get("cells", {})).lower():
                hits += 1
                print(f"  HIT record {rec['id']}")
                for fid, c in rec.get("cells", {}).items():
                    v = c.get("value", "") if isinstance(c, dict) else c
                    if isinstance(v, str) and needle in v.lower():
                        print(f"    {fid} = {v[:200]}")
    print(f"  total hits: {hits}")
