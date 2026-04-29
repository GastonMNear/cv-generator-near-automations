#!/usr/bin/env python3
"""
Universal lead fetcher — works for all known Clay tables.
Usage: python scripts/fetch_lead.py --email EMAIL --table TABLE_ALIAS

Table aliases (case-insensitive partial match):
  us no hm        → US Open Jobs - No HM (searches 3 tables in order)
  us hm / us hms  → US Open Jobs - Hiring Managers
  latam no hm     → LatAm Open Jobs - No HMs (searches 2 tables in order)
  latam hm        → LatAm Open Jobs - Hiring Managers
  canada no hm    → Canada Open Jobs - No HM (searches 2 tables in order)
  canada hm       → Canada Open Jobs - HMs
"""
import urllib.request, json, ssl, sys, io, argparse, os
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

CLAY_USERNAME = os.getenv("CLAY_USERNAME")
CLAY_PASSWORD = os.getenv("CLAY_PASSWORD")
if not CLAY_USERNAME or not CLAY_PASSWORD:
    print("ERROR: Missing CLAY_USERNAME or CLAY_PASSWORD in .env")
    sys.exit(1)
BASE = "https://api.clay.com/v3"
ctx  = ssl.create_default_context()

# ── Table configs — fields match known-tables.md exactly ────────────────────
# "fallbacks": ordered list of table IDs to try if lead not found in this table
TABLES = {
    # ── US Open Jobs - No HM (primary — search first) ──
    "t_0tdyro7QesUNY3WJrt2": {
        "name":       "US Open Jobs - No HM (new primary)",
        "aliases":    ["us no hm", "us oj no hm", "us open jobs no hm", "us open jobs - no hiring manager"],
        "view":       "gv_TgwDWXPdg8Ci",          # Assumed — verify on first run
        "email":      "f_0tc2a2qEFRZthdct3Cs",    # Assumed same as t_0t59d... — update known-tables.md if wrong
        "linkedin":   "f_QIP4GfH5XFZo",
        "first_name": "f_hiEPcKlj0lTB",
        "last_name":  "f_fvs0rK0ntN1H",
        "ec":         "f_0t5mtcfvJknGywASv4z",
        "fallbacks":  ["t_0t59d2y3ZuD4396Kz5B", "t_0tbt48xVeCFCi8pFzip"],
    },
    "t_0t59d2y3ZuD4396Kz5B": {
        "name":       "US Open Jobs - No Hiring Manager",
        "aliases":    [],  # Aliases moved to new primary above
        "view":       "gv_TgwDWXPdg8Ci",
        "email":      "f_0tc2a2qEFRZthdct3Cs",    # Work Email
        "linkedin":   "f_QIP4GfH5XFZo",           # Written Job URL
        "first_name": "f_hiEPcKlj0lTB",           # First Name (cleaned)
        "last_name":  "f_fvs0rK0ntN1H",           # Last Name (cleaned)
        "ec":         "f_0t5mtcfvJknGywASv4z",    # Employee Count
        "fallbacks":  ["t_0tbt48xVeCFCi8pFzip"],
    },
    "t_0tbt48xVeCFCi8pFzip": {
        "name":       "Copy of Leads - US OJ No Hiring Manager (fallback)",
        "aliases":    [],  # Reached only via fallback chain
        "view":       "gv_TgwDWXPdg8Ci",
        "email":      "f_0tbt65uGbguMonif8dU",    # Work Email
        "linkedin":   "f_QIP4GfH5XFZo",           # Written Job URL
        "first_name": "f_hiEPcKlj0lTB",           # First Name (cleaned)
        "last_name":  "f_fvs0rK0ntN1H",           # Last Name (cleaned)
        "ec":         "f_0t5mtcfvJknGywASv4z",    # Employee Count
        "fallbacks":  [],
    },
    # ── US Open Jobs - Hiring Managers ──
    "t_0t5pvx3g4o5WfysopqA": {
        "name":       "US Open Jobs - Hiring Managers",
        "aliases":    ["us hm", "us hms", "us oj hm", "us oj hms", "us open jobs hm", "us open jobs - hiring managers"],
        "view":       "gv_TgwDWXPdg8Ci",
        "email":      "f_0t063ygVDhWMs5MT4MD",    # Work Email
        "linkedin":   "f_0t06147KZtafpAaiDTz",    # Job LinkedIn URL
        "first_name": "f_0t063qfcKw3gnzRcxxG",    # First Name (cleaned)
        "last_name":  "f_0t063qh6gvgnYPy4av4",    # Last Name (cleaned)
        "ec":         "f_0t062fr5fKsUy27nJhf",    # Employee Count
        "fallbacks":  [],
    },
    # ── LatAm Open Jobs - No HMs (primary — search first) ──
    "t_0te5kjxke6yWVRzedb7": {
        "name":       "LatAm Open Jobs - No HMs (new primary)",
        "aliases":    ["latam no hm", "latam no hms", "latam oj no hm", "latam open jobs no hm", "latam open jobs - no hms"],
        "view":       "gv_TgwDWXPdg8Ci",          # Assumed — verify on first run
        "email":      "f_0tckabyNnK9wNBNNUWm",    # Assumed same as t_aNvk4... — update known-tables.md if wrong
        "linkedin":   "f_QIP4GfH5XFZo",
        "first_name": "f_hiEPcKlj0lTB",
        "last_name":  "f_fvs0rK0ntN1H",
        "ec":         "f_0t6acqvuQxjjQNTWhbK",
        "fallbacks":  ["t_aNvk4jWMNeG7"],
    },
    "t_aNvk4jWMNeG7": {
        "name":       "LatAm Open Jobs - No HMs",
        "aliases":    [],  # Aliases moved to new primary above
        "view":       "gv_TgwDWXPdg8Ci",
        "email":      "f_0tckabyNnK9wNBNNUWm",    # Work Email
        "linkedin":   "f_QIP4GfH5XFZo",           # Written Job URL
        "first_name": "f_hiEPcKlj0lTB",           # First Name (cleaned)
        "last_name":  "f_fvs0rK0ntN1H",           # Last Name (cleaned)
        "ec":         "f_0t6acqvuQxjjQNTWhbK",    # Employee Count
        "fallbacks":  [],
    },
    # ── LatAm Open Jobs - Hiring Managers ──
    "t_0t6ghvgCsvvvqAus4bp": {
        "name":       "LatAm Open Jobs - Hiring Managers",
        "aliases":    ["latam hm", "latam hms", "latam oj hm", "latam oj hms", "latam open jobs hm", "latam open jobs - hiring managers"],
        "view":       "gv_TgwDWXPdg8Ci",          # 45,127 records — scan may take ~85s
        "email":      "f_0t063ygVDhWMs5MT4MD",    # Work Email
        "linkedin":   "f_0t06147KZtafpAaiDTz",    # Job LinkedIn URL
        "first_name": "f_0t063qfcKw3gnzRcxxG",    # First Name (cleaned)
        "last_name":  "f_0t063qh6gvgnYPy4av4",    # Last Name (cleaned)
        "ec":         "f_0t062fr5fKsUy27nJhf",    # Employee Count
        "fallbacks":  [],
    },
    # ── Canada Open Jobs - No HM (primary — search first) ──
    "t_0te5lh6AoWkxd39ktT8": {
        "name":       "Canada Open Jobs - No HM (new primary)",
        "aliases":    ["canada no hm", "canada no hms", "canada oj no hm", "canada open jobs no hm", "canada open jobs - no hm"],
        "view":       "gv_3cMh8vzuFqm4",          # Assumed same view as t_0taasak... — verify on first run
        "email":      "f_0taaxyjNBGfFWKYUnxK",    # Assumed same as t_0taasak... — update known-tables.md if wrong
        "linkedin":   "f_0taawsuMjxnV74YtCZ8",
        "first_name": "f_0taaxkd4HWteakU9qwZ",
        "last_name":  "f_0taaxkl9BQmnF5u9PVG",
        "ec":         "f_0taayd3VvuPn9po6cYQ",
        "fallbacks":  ["t_0taasak5KAa5zbTmTJd"],
    },
    "t_0taasak5KAa5zbTmTJd": {
        "name":       "Canada Open Jobs - No HM",
        "aliases":    [],  # Aliases moved to new primary above
        "view":       "gv_3cMh8vzuFqm4",
        "email":      "f_0taaxyjNBGfFWKYUnxK",    # Work Email
        "linkedin":   "f_0taawsuMjxnV74YtCZ8",    # Job LinkedIn Url
        "first_name": "f_0taaxkd4HWteakU9qwZ",    # First Name (clean)
        "last_name":  "f_0taaxkl9BQmnF5u9PVG",    # Last Name (clean)
        "ec":         "f_0taayd3VvuPn9po6cYQ",    # Employee Count
        "fallbacks":  [],
    },
    # ── Canada Open Jobs - Hiring Managers ──
    "t_0t746txPqz5sjFMtut2": {
        "name":       "Canada Open Jobs - HMs",
        "aliases":    ["canada hm", "canada hms", "canada oj hm", "canada oj hms", "canada open jobs hm", "canada open jobs - hms"],
        "view":       "gv_TgwDWXPdg8Ci",
        "email":      "f_0t063ygVDhWMs5MT4MD",    # Work Email
        "linkedin":   "f_0t06147KZtafpAaiDTz",    # Job LinkedIn URL
        "first_name": "f_0t063qfcKw3gnzRcxxG",    # First Name (cleaned)
        "last_name":  "f_0t063qh6gvgnYPy4av4",    # Last Name (cleaned)
        "ec":         "f_0t062fr5fKsUy27nJhf",    # Employee Count
        "fallbacks":  [],
    },
}

# ── CLI ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument("--email",  required=True, help="Lead email address")
parser.add_argument("--table",  required=True, help="Table alias (e.g. 'canada hms', 'us no hm')")
args = parser.parse_args()

LEAD_EMAIL   = args.email.strip().lower()
TABLE_QUERY  = args.table.strip().lower()

# ── Resolve table ───────────────────────────────────────────────────────────
table_id = None
table_cfg = None
for tid, cfg in TABLES.items():
    for alias in cfg["aliases"]:
        if TABLE_QUERY in alias or alias in TABLE_QUERY:
            table_id  = tid
            table_cfg = cfg
            break
    if table_id:
        break

if not table_id:
    names = [f"  {cfg['name']}" for cfg in TABLES.values()]
    print("ERROR: Table not recognised. Known tables:\n" + "\n".join(names))
    sys.exit(1)

print(f"Table: {table_cfg['name']} ({table_id})")

# ── Auth ────────────────────────────────────────────────────────────────────
login_data = json.dumps({"email": CLAY_USERNAME, "password": CLAY_PASSWORD, "source": "web"}).encode()
req = urllib.request.Request(f"{BASE}/auth/login", data=login_data,
    headers={"Content-Type": "application/json", "Origin": "https://app.clay.com", "Referer": "https://app.clay.com/"},
    method="POST")
resp = urllib.request.urlopen(req, context=ctx, timeout=30)
session = resp.headers.get("Set-Cookie", "").split(";")[0]
print(f"Auth OK")

def api_get(path):
    r = urllib.request.Request(f"{BASE}{path}", headers={"Cookie": session})
    return json.loads(urllib.request.urlopen(r, context=ctx, timeout=30).read())

def api_post(path, data):
    r = urllib.request.Request(f"{BASE}{path}", data=json.dumps(data).encode(),
        headers={"Cookie": session, "Content-Type": "application/json"}, method="POST")
    return json.loads(urllib.request.urlopen(r, context=ctx, timeout=90).read())

def search_in_table(tid, cfg, email):
    """Search for email in a single table. Returns record dict or None."""
    ids_resp = api_get(f"/tables/{tid}/views/{cfg['view']}/records/ids")
    record_ids = ids_resp.get("results", [])
    print(f"  Records: {len(record_ids)}")
    for i in range(0, len(record_ids), BATCH_SIZE):
        batch = record_ids[i:i+BATCH_SIZE]
        print(f"  Searching {i+1}-{min(i+BATCH_SIZE, len(record_ids))}...")
        resp_data = api_post(f"/tables/{tid}/bulk-fetch-records", {"recordIds": batch})
        for rec in resp_data.get("results", []):
            cell = rec.get("cells", {}).get(cfg["email"], {})
            val  = cell.get("value", "") if isinstance(cell, dict) else str(cell)
            val  = val.replace("✅ ", "").strip() if isinstance(val, str) else ""
            if email in val.lower():
                return rec
    return None

# ── Build ordered search chain: primary table + its fallbacks ───────────────
BATCH_SIZE = 10_000
chain = [(table_id, table_cfg)]
for fb_id in table_cfg.get("fallbacks", []):
    if fb_id in TABLES:
        chain.append((fb_id, TABLES[fb_id]))

# ── Search each table in order ───────────────────────────────────────────────
found = None
found_table_id  = None
found_table_cfg = None

for tid, cfg in chain:
    print(f"\nSearching: {cfg['name']} ({tid})")
    found = search_in_table(tid, cfg, LEAD_EMAIL)
    if found:
        found_table_id  = tid
        found_table_cfg = cfg
        break
    print(f"  Not found.")

if not found:
    checked = ", ".join(cfg["name"] for _, cfg in chain)
    print(f"ERROR: '{LEAD_EMAIL}' not found. Checked: {checked}")
    sys.exit(1)

table_id  = found_table_id
table_cfg = found_table_cfg

print(f"Found! Record ID: {found['id']}")
cells = found.get("cells", {})

def cell_val(fid):
    c = cells.get(fid, {})
    return c.get("value", "") if isinstance(c, dict) else ""

first = cell_val(table_cfg["first_name"]).strip()
last  = cell_val(table_cfg["last_name"]).strip()
result = {
    "email":          args.email,
    "name":           f"{first} {last}".strip(),
    "linkedin_url":   cell_val(table_cfg["linkedin"]),
    "employee_count": cell_val(table_cfg["ec"]) or None,
}
print("\n--- RESULT ---")
print(json.dumps(result, indent=2))
