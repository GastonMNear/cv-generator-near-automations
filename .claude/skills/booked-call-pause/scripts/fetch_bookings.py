#!/usr/bin/env python3
"""Fetch newly-booked calls from HubSpot and emit them as bookings JSON.

Bookings land as MEETING_EVENT objects created by Chili Piper. Two gotchas that
this filter exists to handle:

  1. Fathom writes its own MEETING_EVENTs ("Fathom summary for ...") — these are
     recordings of calls that already happened, not new bookings. They carry no
     `hs_activity_type`, so we require that property to be present.
  2. The booker's email is NOT a clean property — it's embedded in the
     `hs_meeting_body` text that Chili Piper fills in ("Email: neil@ftf.co").
     We parse it from there, and cross-check the associated contact when present.

Company domain is the primary match key because booking emails are frequently
generic mailboxes (info@, hello@) that no Smartlead lead will ever match on
address — but their domain matches fine.

Usage:
    python3 fetch_bookings.py --since 2026-08-20T00:00:00Z
    python3 fetch_bookings.py --hours 12 --out bookings.json
Env: HUBSPOT_ACCESS_TOKEN (private-app token, pat-na1-…)
"""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

# Repo .env names this HUBSPOT_ACCESS_TOKEN (a pat-na1-… private-app token).
TOKEN = (os.environ.get("HUBSPOT_ACCESS_TOKEN")
         or os.environ.get("HUBSPOT_PRIVATE_APP_TOKEN"))
BASE = "https://api.hubapi.com"

# Our own domains. Internal bookings ("Intro Call" for a Near employee) show up in
# the same meetings feed; keying on hirewithnear.com would pause our own domain if
# any internal address is ever sitting in a campaign as a test lead.
OWN_DOMAINS = {"hirewithnear.com", "near.com", "hirewithnear.co"}

FREE_MAILBOX_DOMAINS = {
    "gmail.com", "googlemail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "icloud.com", "aol.com", "live.com", "me.com", "msn.com", "proton.me",
    "protonmail.com", "ymail.com",
}


def api(path, method="GET", body=None):
    url = f"{BASE}{path}"
    cmd = ["curl", "-s", "--max-time", "60", "-X", method, url,
           "-H", f"Authorization: Bearer {TOKEN}",
           "-H", "Content-Type: application/json"]
    if body is not None:
        cmd += ["--data-raw", json.dumps(body)]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    try:
        return json.loads(out)
    except Exception:
        sys.exit(f"ERROR: unparseable HubSpot response: {out[:300]}")


def parse_body_fields(body_text):
    """Chili Piper writes 'Label: value' lines into hs_meeting_body."""
    out = {}
    for line in (body_text or "").splitlines():
        m = re.match(r"\s*([A-Za-z][A-Za-z0-9 '/?&-]{2,40})\s*:\s*(.+?)\s*$", line)
        if m:
            out.setdefault(m.group(1).strip().lower(), m.group(2).strip())
    return out


def domain_from_email(email):
    if not email or "@" not in email:
        return ""
    return email.rsplit("@", 1)[-1].strip().lower().strip(".")


def fetch(since_iso, limit=100):
    """MEETING_EVENTs created since `since_iso` that look like real bookings."""
    body = {
        "filterGroups": [{
            "filters": [
                {"propertyName": "hs_createdate", "operator": "GTE",
                 "value": since_iso},
                # Fathom-generated summaries lack this property entirely.
                {"propertyName": "hs_activity_type",
                 "operator": "HAS_PROPERTY"},
            ]
        }],
        "sorts": [{"propertyName": "hs_createdate", "direction": "DESCENDING"}],
        "properties": ["hs_meeting_title", "hs_createdate", "hs_activity_type",
                       "hs_meeting_body", "hs_meeting_outcome",
                       "hs_meeting_start_time", "hs_object_source_detail_1"],
        "limit": limit,
    }
    res = api("/crm/v3/objects/meetings/search", "POST", body)
    if "results" not in res:
        sys.exit(f"ERROR: HubSpot search failed: {json.dumps(res)[:300]}")
    return res["results"]


def contact_for_meeting(meeting_id):
    """Associated contact gives us a verified email + company, when linked."""
    res = api(f"/crm/v4/objects/meetings/{meeting_id}/associations/contacts")
    ids = [r["toObjectId"] for r in (res.get("results") or [])]
    if not ids:
        return {}
    cid = ids[0]
    c = api(f"/crm/v3/objects/contacts/{cid}"
            f"?properties=email,company,website,firstname,lastname")
    return c.get("properties") or {}


def to_booking(meeting, with_contact=True):
    props = meeting.get("properties") or {}
    fields = parse_body_fields(props.get("hs_meeting_body"))

    email = (fields.get("email") or "").lower()
    company_name = fields.get("company name") or ""

    contact = contact_for_meeting(meeting["id"]) if with_contact else {}
    if not email:
        email = (contact.get("email") or "").lower()
    if not company_name:
        company_name = contact.get("company") or ""

    # Prefer the contact's website for the domain; fall back to the email domain,
    # but never key on a free mailbox domain (gmail.com would match everything).
    domain = ""
    site = contact.get("website") or ""
    if site:
        d = site.replace("https://", "").replace("http://", "")
        d = d.split("/")[0].lower()
        if d.startswith("www."):
            d = d[4:]
        domain = d
    if not domain:
        d = domain_from_email(email)
        if d and d not in FREE_MAILBOX_DOMAINS:
            domain = d
    if domain in OWN_DOMAINS:
        domain = ""      # never treat an internal booking as a company to pause

    return {
        "meeting_id": meeting["id"],
        "company_name": (company_name or "").replace("&gt;", ">").strip(),
        "company_domain": domain,
        "company_linkedin": "",          # not present on ChiliPiper bookings
        "email": email,
        "booked_at": props.get("hs_createdate"),
        "meeting_start": props.get("hs_meeting_start_time"),
        "activity_type": props.get("hs_activity_type"),
        "source": props.get("hs_object_source_detail_1"),
        "free_mailbox": domain_from_email(email) in FREE_MAILBOX_DOMAINS,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", help="ISO8601 UTC lower bound on hs_createdate")
    ap.add_argument("--hours", type=float, default=12,
                    help="look back this many hours (default 12)")
    ap.add_argument("--out", help="write bookings JSON here")
    ap.add_argument("--no-contacts", action="store_true",
                    help="skip the association lookups (faster, less accurate)")
    a = ap.parse_args()

    if not TOKEN:
        sys.exit("ERROR: HUBSPOT_ACCESS_TOKEN not set. Needs a HubSpot private-app "
                 "token with crm.objects.meetings.read, "
                 "crm.objects.contacts.read, crm.objects.companies.read")

    since = a.since or (
        datetime.now(timezone.utc) - timedelta(hours=a.hours)
    ).strftime("%Y-%m-%dT%H:%M:%SZ")

    meetings = fetch(since)
    bookings = [to_booking(m, with_contact=not a.no_contacts) for m in meetings]
    # Nothing to match on without a domain or a non-generic email.
    usable = [b for b in bookings
              if (b["company_domain"] or b["email"])
              and domain_from_email(b["email"]) not in OWN_DOMAINS]
    skipped_internal = len(bookings) - len(usable)

    print(f"[hubspot] {len(meetings)} meeting(s) created since {since}; "
          f"{len(usable)} with a usable key"
          + (f"; skipped {skipped_internal} internal" if skipped_internal else ""),
          file=sys.stderr)
    for b in usable:
        print(f"  {b['company_name'][:34]:34} {b['company_domain'] or '-':28} "
              f"{b['email']}", file=sys.stderr)

    payload = json.dumps(usable, indent=2)
    if a.out:
        with open(a.out, "w") as f:
            f.write(payload + "\n")
    else:
        print(payload)


if __name__ == "__main__":
    main()
