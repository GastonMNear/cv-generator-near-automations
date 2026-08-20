#!/usr/bin/env python3
"""In-memory index of Smartlead leads, keyed by the things we match companies on.

STATELESS BY DESIGN. Cloud routine runs get a fresh checkout, so nothing persists
between runs — we crawl `/leads/all` into memory each run, match, and exit. At the
twice-daily cadence that's ~2 x 207 requests/day, a few minutes of a 200/min budget,
and it removes any staleness or persistence problem. Nothing is written to disk, so
no lead PII is ever left behind.

Why an index at all: Smartlead has no company-level lead search. `/leads/?email=`
takes only an exact email and `/leads/all` rejects every filter param we tried
(email_domain, company_url, domain, company_name, search, query -> HTTP 400). So
company->leads has to be resolved client-side over the full lead list.

Usage (normally called by pause_booked.py, not directly):
    python3 lead_index.py --stats
    python3 lead_index.py --lookup acme.com
Env: SMARTLEAD_API_KEY
"""
import json
import os
import subprocess
import sys
import threading
import time
from collections import defaultdict, deque

API = os.environ.get("SMARTLEAD_API_KEY")
if not API:
    sys.exit("ERROR: SMARTLEAD_API_KEY not set")

BASE = "https://server.smartlead.ai/api/v1"
PAGE = 1000          # max accepted by /leads/all (note: /campaigns/{id}/leads caps at 100)
MAX_PER_MIN = 175    # Smartlead hard cap is 200/min account-wide

# Generic mailboxes tell us nothing about a person, but their DOMAIN is still valid
# for company matching (real bookings come in as info@/hello@ constantly).
FREE_EMAIL_DOMAINS = {
    "aol.com", "gmail.com", "googlemail.com", "hotmail.com", "icloud.com",
    "live.com", "me.com", "msn.com", "outlook.com", "proton.me",
    "protonmail.com", "yahoo.com", "ymail.com", "hotmail.co.uk", "yahoo.co.uk",
}

# Never usable as a company key. `company_url` is enrichment output and sometimes
# holds a profile/aggregator URL instead of the company's own site: in this account
# `linkedin.com` alone carried ~1,870 leads spanning 1,532 unrelated email domains,
# while real companies top out around 65 leads. Keying on it would pause a whole
# unrelated book of business.
JUNK_DOMAINS = {
    "linkedin.com", "facebook.com", "twitter.com", "x.com", "instagram.com",
    "youtube.com", "crunchbase.com", "glassdoor.com", "indeed.com",
    "google.com", "sites.google.com", "wixsite.com", "wordpress.com",
    "squarespace.com", "godaddysites.com", "shopify.com", "medium.com",
    "github.com", "notion.site", "bit.ly", "angel.co", "wellfound.com",
    "ziprecruiter.com", "monster.com", "upwork.com",
} | FREE_EMAIL_DOMAINS

_lock = threading.Lock()
_stamps = deque()


def _throttle():
    while True:
        with _lock:
            now = time.monotonic()
            while _stamps and now - _stamps[0] > 60:
                _stamps.popleft()
            if len(_stamps) < MAX_PER_MIN:
                _stamps.append(now)
                return
            wait = 60 - (now - _stamps[0]) + 0.05
        time.sleep(wait)


def curl_json(path, tries=6):
    """Smartlead blocks python-requests with a Cloudflare 403, so shell out to curl."""
    sep = "&" if "?" in path else "?"
    url = f"{BASE}{path}{sep}api_key={API}"
    for attempt in range(tries):
        _throttle()
        out = subprocess.run(
            ["curl", "-s", "--max-time", "60", url],
            capture_output=True, text=True,
        ).stdout
        if "rate limit" in out.lower():
            time.sleep(15)
            continue
        try:
            r = json.loads(out)
        except Exception:
            time.sleep(3 * (attempt + 1))   # seen once at 75k depth under parallel load
            continue
        if isinstance(r, str):
            time.sleep(3)
            continue
        return r
    return None


# ---- normalisation ---------------------------------------------------------
def norm_domain(value):
    """Bare registrable-ish domain: strip scheme, www, path, port, mailto."""
    if not value:
        return ""
    d = str(value).strip().lower()
    if "@" in d:
        d = d.rsplit("@", 1)[-1]
    for prefix in ("https://", "http://", "//"):
        if d.startswith(prefix):
            d = d[len(prefix):]
    d = d.split("/")[0].split("?")[0].split(":")[0]
    if d.startswith("www."):
        d = d[4:]
    return d.strip(".")


def norm_linkedin(value):
    """Canonical LinkedIn slug — strips locale prefixes, query params, trailing junk."""
    if not value:
        return ""
    u = str(value).strip().lower()
    if "linkedin.com" not in u:
        return ""
    u = u.split("linkedin.com", 1)[1].split("?")[0].rstrip("/")
    parts = [p for p in u.split("/") if p]
    for kind in ("company", "school", "in"):
        if kind in parts:
            i = parts.index(kind)
            if i + 1 < len(parts):
                return f"{kind}/{parts[i + 1]}"
    return ""


def norm_email(value):
    return str(value or "").strip().lower()


def domain_stem(domain):
    """'acme-corp.co.uk' -> 'acmecorp'. Used to compare brand-variant domains."""
    d = norm_domain(domain)
    if not d:
        return ""
    parts = d.split(".")
    multi = {"co.uk", "com.au", "com.br", "com.mx", "co.in", "co.nz", "com.sg"}
    if len(parts) >= 3 and ".".join(parts[-2:]) in multi:
        stem = parts[-3]
    elif len(parts) >= 2:
        stem = parts[-2]
    else:
        stem = parts[0]
    return stem.replace("-", "").replace("_", "")


def _longest_common_substring(a, b):
    best = ""
    prev = [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        cur = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1] + 1
                if cur[j] > len(best):
                    best = a[i - cur[j]:i]
        prev = cur
    return best


def same_company(company_domain, email):
    """Does this lead's own email corroborate the company domain we matched on?

    `company_url` is enrichment output and disagrees with the lead's email domain
    ~15% of the time, from two very different causes:

      * benign  — the company uses a brand variant
                  (getforwardly.com vs liveforwardly.com, acilube.com vs aci-lubes.com)
      * harmful — the lead actually works somewhere else entirely
                  (patrick.mcgee@jpmorgan.com filed under huntington.com)

    Accept exact matches, shared brand stems, long common substrings, and free
    mailboxes (no signal — the company domain stays authoritative). Reject clear
    cross-company cases so a bad company_url can't pause an unrelated company.
    Deliberately errs toward inclusion on ambiguous pairs: wrongly pausing a
    possibly-related lead is recoverable, wrongly emailing a booked account is the
    failure we're preventing.
    """
    cd = norm_domain(company_domain)
    ed = norm_domain(email)
    if not cd or not ed:
        return True
    if cd == ed or ed in FREE_EMAIL_DOMAINS:
        return True
    a, b = domain_stem(cd), domain_stem(ed)
    if not a or not b or a == b:
        return True
    shorter, longer = sorted((a, b), key=len)
    if len(shorter) >= 5 and shorter in longer:
        return True
    # 6+ chars keeps generic words ("group", "health") from matching.
    return len(_longest_common_substring(a, b)) >= 6


# ---- crawl -----------------------------------------------------------------
class LeadIndex:
    """Every lead, bucketed by domain / linkedin / email. Built fresh per run."""

    def __init__(self):
        self.by_domain = defaultdict(list)
        self.by_linkedin = defaultdict(list)
        self.by_email = {}
        self.count = 0
        self.total_reported = None
        self.complete = False

    def add(self, lead):
        email = norm_email(lead.get("email"))

        domain = norm_domain(lead.get("company_url"))
        if domain in JUNK_DOMAINS:
            domain = ""
        if not domain:
            cand = norm_domain(lead.get("email_domain")) or norm_domain(email)
            if cand and cand not in JUNK_DOMAINS:
                domain = cand

        cf = lead.get("custom_fields") or {}
        linkedin = norm_linkedin(cf.get("company_linkedin_url"))

        rec = {
            "lead_id": int(lead["id"]),
            "email": email,
            "domain": domain,
            "company": (lead.get("company_name") or "").strip(),
        }
        if domain:
            self.by_domain[domain].append(rec)
        if linkedin:
            self.by_linkedin[linkedin].append(rec)
        if email:
            self.by_email[email] = rec
        self.count += 1

    def lookup(self, domain=None, linkedin=None, email=None):
        """Ordered fallback: domain -> company LinkedIn -> exact email.

        Stops at the first key that hits, so a domain match is never diluted by a
        broader fallback.
        """
        d = norm_domain(domain)
        if d and d not in JUNK_DOMAINS:
            rows = [r for r in self.by_domain.get(d, [])
                    if same_company(d, r["email"])]
            if rows:
                return "domain", rows

        li = norm_linkedin(linkedin)
        if li:
            rows = self.by_linkedin.get(li, [])
            if rows:
                return "company_linkedin", rows

        e = norm_email(email)
        if e and e in self.by_email:
            return "email", [self.by_email[e]]

        return None, []


def build(verbose=True):
    """Crawl /leads/all into memory. ~207 requests, ~5 min for ~205k leads.

    `/leads/all` is newest-first by lead id and paginates on `lastSeenLeadId`
    (camelCase — snake_case 400s). limit max 1000.
    """
    idx = LeadIndex()
    cursor = None
    reqs = 0
    t0 = time.time()

    while True:
        path = f"/leads/all?limit={PAGE}"
        if cursor:
            path += f"&lastSeenLeadId={cursor}"
        payload = curl_json(path)
        reqs += 1
        if not payload or "data" not in payload:
            print(f"[index] WARNING: crawl stopped early after {reqs} requests "
                  f"({idx.count} leads) — matching may be INCOMPLETE",
                  file=sys.stderr, flush=True)
            break

        data = payload["data"]
        idx.total_reported = data.get("totalCount") or idx.total_reported
        leads = data.get("leads") or []
        if not leads:
            idx.complete = True
            break

        for lead in leads:
            idx.add(lead)

        if verbose and reqs % 50 == 0:
            print(f"[index]   {idx.count} leads / {reqs} requests "
                  f"({time.time() - t0:.0f}s)", file=sys.stderr, flush=True)

        cursor = data.get("lastSeenLeadId")
        if not cursor:
            idx.complete = True
            break

    idx.elapsed = time.time() - t0
    idx.requests = reqs
    if verbose:
        print(f"[index] {idx.count} leads in {reqs} requests, {idx.elapsed:.0f}s "
              f"(Smartlead reports {idx.total_reported})",
              file=sys.stderr, flush=True)
    return idx


def main():
    args = sys.argv[1:]
    idx = build()
    if "--lookup" in args:
        term = args[args.index("--lookup") + 1]
        matched_by, rows = idx.lookup(domain=term, linkedin=term, email=term)
        print(f"matched_by: {matched_by}   leads: {len(rows)}")
        for r in rows:
            print(f"  {r['lead_id']}  {r['email']:42} {r['company'][:28]}")
    else:
        print(f"leads: {idx.count}   distinct domains: {len(idx.by_domain)}   "
              f"complete: {idx.complete}")


if __name__ == "__main__":
    main()
