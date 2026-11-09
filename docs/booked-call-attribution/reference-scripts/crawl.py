#!/usr/bin/env python3
"""Crawl /leads/all and keep only leads plausibly at one of the target companies.

Broad matcher on purpose — a false positive is cheap (I review the list), a false
negative silently drops a booking. Only matched leads are written to disk.
"""
import json, os, re, subprocess, sys, time
from collections import defaultdict

API = os.environ["SMARTLEAD_API_KEY"]
BASE = "https://server.smartlead.ai/api/v1"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "matched_leads.jsonl")

# target company -> list of normalised keys to look for
TARGETS = {
    "Hype Proxies":      ["hypeproxies", "hypeproxy"],
    "USAD":              ["usad"],
    "Cactus Audio":      ["cactusaudio", "cactus"],
    "Sana Benefits":     ["sanabenefits", "sana"],
    "Nerife":            ["nerife"],
    "Quieto":            ["quieto"],
    "Zaelab":            ["zaelab"],
    "Artic Grey":        ["articgrey", "arcticgrey"],
    "Purpose":           ["purpose"],
    "Cadana":            ["cadana"],
    "Blackout Coffee Co.": ["blackoutcoffee"],
    "Dance With Me":     ["dancewithme"],
    "GRADE CAPITAL":     ["gradecapital"],
}

def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())

def dom_stem(d):
    d = (d or "").lower().strip()
    if "@" in d: d = d.rsplit("@", 1)[-1]
    d = re.sub(r"^(https?://)?(www\.)?", "", d).split("/")[0].split(":")[0]
    return norm(d.rsplit(".", 1)[0] if "." in d else d)

def curl_json(path, tries=6):
    sep = "&" if "?" in path else "?"
    url = f"{BASE}{path}{sep}api_key={API}"
    for a in range(tries):
        out = subprocess.run(["curl", "-s", "--max-time", "60", url],
                             capture_output=True, text=True).stdout
        if "rate limit" in out.lower():
            time.sleep(15); continue
        try:
            r = json.loads(out)
        except Exception:
            time.sleep(3 * (a + 1)); continue
        if isinstance(r, str):
            time.sleep(3); continue
        return r
    return None

def match(lead):
    """Return list of target names this lead plausibly belongs to."""
    cn = norm(lead.get("company_name"))
    ncn = norm((lead.get("custom_fields") or {}).get("normalized_company_name")) if isinstance(lead.get("custom_fields"), dict) else ""
    stems = {dom_stem(lead.get("company_url")), dom_stem(lead.get("email_domain")), dom_stem(lead.get("email"))}
    stems.discard("")
    hits = []
    for name, keys in TARGETS.items():
        for k in keys:
            if (cn and k in cn) or (ncn and k in ncn) or any(k in s for s in stems):
                hits.append(name); break
    return hits

cursor, n, kept = None, 0, 0
t0 = time.time()
with open(OUT, "w") as fh:
    while True:
        path = f"/leads/all?limit=1000" + (f"&lastSeenLeadId={cursor}" if cursor else "")
        r = curl_json(path)
        if not r or not r.get("ok"):
            sys.exit(f"ABORT at depth {n}: crawl failed, partial index unusable. resp={str(r)[:200]}")
        d = r["data"]
        leads = d.get("leads") or []
        if not leads: break
        for L in leads:
            hits = match(L)
            if hits:
                kept += 1
                fh.write(json.dumps({
                    "targets": hits, "id": L.get("id"), "email": L.get("email"),
                    "first_name": L.get("first_name"), "last_name": L.get("last_name"),
                    "company_name": L.get("company_name"), "company_url": L.get("company_url"),
                    "email_domain": L.get("email_domain"), "created_at": L.get("created_at"),
                    "category_ids": L.get("category_ids"),
                }) + "\n")
        n += len(leads)
        cursor = d.get("lastSeenLeadId")
        if n % 20000 == 0:
            print(f"  {n} crawled, {kept} kept, {int(time.time()-t0)}s", flush=True)
        if not cursor: break
print(f"DONE: {n} leads crawled, {kept} matched, {int(time.time()-t0)}s -> {OUT}")
