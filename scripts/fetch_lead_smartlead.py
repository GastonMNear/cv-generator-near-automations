#!/usr/bin/env python3
"""
Fetch a lead from Smartlead by email address.

Usage:
  python3 scripts/fetch_lead_smartlead.py --email EMAIL [--json] [--raw]

Prints the normalized fields the CV pipeline needs, as JSON on stdout:

  {"source": "smartlead", "email", "name", "first_name", "last_name",
   "company_name", "job_title", "linkedin_url", "employee_count",
   "prospect_linkedin", "campaigns": [...]}

Exit codes:
  0  lead found
  1  lead not found (Smartlead returned no record for that email)
  2  configuration / auth error (missing or rejected API key)
  3  transient API failure that survived retries (rate limit, network)

Exit code 1 is the signal for the caller to fall back to the Clay path;
codes 2 and 3 mean Smartlead never got to answer, so a Clay fallback is
also reasonable but the underlying problem should be reported.
"""
import argparse, json, os, sys, time, urllib.error, urllib.parse, urllib.request

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE = "https://server.smartlead.ai/api/v1"

# Smartlead sits behind Cloudflare, which blocks Python's default urllib
# User-Agent outright with "403 Forbidden / error code: 1010" (a browser-
# signature block). It looks exactly like rate limiting but is permanent —
# no amount of backoff clears it, while the same URL via curl succeeds. Sending
# any real User-Agent fixes it, so always set this header.
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0 Safari/537.36")

# Genuine throttling arrives as 429 and is reported in the x-ratelimit-*
# response headers (limit is 200/window). 403 is deliberately NOT retried —
# see the UA note above; retrying it just burns minutes.
RETRY_STATUS = (429, 500, 502, 503, 504)


def fetch_lead(email, api_key, tries=4, base_delay=5):
    url = f"{BASE}/leads/?email={urllib.parse.quote(email)}&api_key={urllib.parse.quote(api_key)}"
    delay = base_delay
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8", "replace")[:200]
            except Exception:
                pass
            if e.code == 401:
                print(f"ERROR: Smartlead rejected the API key (401). {body}", file=sys.stderr)
                print("Check SMARTLEAD_API_KEY in .env — it may have been rotated.", file=sys.stderr)
                sys.exit(2)
            if e.code == 403:
                print("ERROR: Smartlead returned 403 (Cloudflare error 1010 — blocked "
                      "User-Agent). This is not rate limiting and will not clear on retry; "
                      "the request must send a real User-Agent header.", file=sys.stderr)
                sys.exit(2)
            last = f"HTTP {e.code} {body}"
            if e.code in RETRY_STATUS and attempt < tries - 1:
                print(f"  Smartlead returned {e.code} (likely throttling) — "
                      f"retrying in {delay}s ({attempt + 1}/{tries})", file=sys.stderr)
                time.sleep(delay)
                delay *= 2
                continue
            break
        except Exception as e:
            last = str(e)
            if attempt < tries - 1:
                time.sleep(delay)
                delay *= 2
                continue
            break
    print(f"ERROR: Smartlead request failed after {tries} attempts: {last}", file=sys.stderr)
    sys.exit(3)


def normalize(d):
    """Flatten the Smartlead record into the fields the CV pipeline consumes."""
    cf = d.get("custom_fields") or {}

    def pick(*keys):
        """First non-empty value among the given custom-field keys."""
        for k in keys:
            v = cf.get(k)
            if v not in (None, "", []):
                return v
        return None

    first = (d.get("first_name") or "").strip()
    last = (d.get("last_name") or "").strip()
    name = " ".join(p for p in (first, last) if p) or None

    # Two company-name fields exist and at least one is always populated, but
    # either can be empty individually — so take whichever is present rather
    # than trusting one. When both exist, prefer the longer: normalized_company_name
    # is shortened for email copy and drops meaningful words ("Mach33" vs
    # "Mach33 Media", "Entry" vs "Entry Capital"). Step 2 still overrides both
    # when the job post yields a name, since that is the public, correct one.
    company_full = (d.get("company_name") or "").strip()
    company_norm = (pick("normalized_company_name") or "").strip()
    candidates = [c for c in (company_full, company_norm) if c]
    company = max(candidates, key=len) if candidates else None

    # Older leads commonly lack a headcount; newer ones carry it. Null is a
    # normal, expected value — the workflow reports it as unavailable alongside
    # the CV rather than treating it as a failure or going hunting for it.
    ec = pick("employee_count", "employees", "company_size", "headcount")
    if isinstance(ec, str):
        digits = "".join(ch for ch in ec if ch.isdigit())
        ec = int(digits) if digits else None

    return {
        "source": "smartlead",
        "email": d.get("email"),
        "name": name,
        "first_name": first or None,
        "last_name": last or None,
        "company_name": company,
        # Both raw values, so a caller can see what was actually stored.
        "company_name_raw": company_full or None,
        "company_name_normalized": company_norm or None,
        # open_role_title is written for email personalization, so it is often
        # lowercase or abbreviated ("estimators", "founding AE") rather than the
        # posting's real title. Useful as a cross-check that the job URL matches
        # the right role — not as the title the CV targets.
        "job_title_hint": pick("open_role_title", "job_title", "role_title"),
        # job_url is the canonical job-post field. job_linkedin_url is the legacy
        # name, still the only one populated on some leads (verified: Apollo's
        # awollmann@horvath-partners.com and Asia's michael.hsu@curogram.com have
        # job_url null). The two are never both set, so falling through to the
        # legacy name costs nothing and keeps those leads working.
        "linkedin_url": pick("job_url", "job_linkedin_url", "job_post_url", "linkedin_job_url"),
        "employee_count": ec,
        # The lead's own profile — never the job post. Kept for context only so
        # it can't be mistaken for the job URL downstream.
        "prospect_linkedin": d.get("linkedin_profile"),
        "campaigns": [c.get("campaign_name") for c in (d.get("lead_campaign_data") or []) if c.get("campaign_name")],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--email", required=True)
    ap.add_argument("--raw", action="store_true", help="print the full Smartlead record too")
    args = ap.parse_args()

    api_key = os.getenv("SMARTLEAD_API_KEY")
    if not api_key:
        print("ERROR: Missing SMARTLEAD_API_KEY in .env", file=sys.stderr)
        sys.exit(2)

    d = fetch_lead(args.email, api_key)

    # A miss comes back as an empty body, an empty list, or an object with no id
    # — not as a 404, so check the payload rather than the status code.
    if not d or (isinstance(d, list) and not d) or (isinstance(d, dict) and not d.get("id")):
        print(f"Lead not found in Smartlead: {args.email}", file=sys.stderr)
        sys.exit(1)
    if isinstance(d, list):
        d = d[0]

    out = normalize(d)
    if args.raw:
        out["_raw"] = d
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
