#!/usr/bin/env python3
"""Shared plumbing for the booked-call attribution pipeline.

Everything in here is here because a step needs it twice. The two API clients are
separate functions on purpose — Smartlead and HubSpot fail in different ways and
want different retry rules.
"""
import html
import json
import os
import re
import subprocess
import sys
import threading
import time
from collections import deque
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
UTC = timezone.utc

SMARTLEAD_BASE = "https://server.smartlead.ai/api/v1"
HUBSPOT_BASE = "https://api.hubapi.com"

SMARTLEAD_KEY = os.environ.get("SMARTLEAD_API_KEY")
HUBSPOT_TOKEN = (os.environ.get("HUBSPOT_ACCESS_TOKEN")
                 or os.environ.get("HUBSPOT_PRIVATE_APP_TOKEN"))

# The HubSpot property that carries the booking source. Values seen live include
# Email Outreach, LinkedIn Outreach, Google Search, Google Ad, LLM, Friend, Girdley,
# Atlas, Deel — a wider vocabulary than the property's declared enum options, so
# match the target value exactly rather than trying to enumerate the rest.
SOURCE_PROP = "meeting_source__standardized_"
TARGET_SOURCE = "Email Outreach"

FREE_EMAIL_DOMAINS = {
    "aol.com", "gmail.com", "googlemail.com", "hotmail.com", "icloud.com",
    "live.com", "me.com", "msn.com", "outlook.com", "proton.me",
    "protonmail.com", "yahoo.com", "ymail.com", "hotmail.co.uk", "yahoo.co.uk",
}

# Never usable as a company key. Carried over from booked-call-pause (where
# linkedin.com alone spanned 1,532 unrelated email domains) plus the helpdesk hosts,
# which this pipeline discovered on its own: Artic Grey books from
# anthony.spallone@arcticgreyltd.zendesk.com. Keying on `zendesk.com` would join
# every company that routes its support desk through the same vendor.
HELPDESK_DOMAINS = {
    "zendesk.com", "freshdesk.com", "helpscout.net", "intercom.io",
    "hubspot.com", "salesforce.com", "front.com", "zohodesk.com",
}
JUNK_DOMAINS = {
    "linkedin.com", "facebook.com", "twitter.com", "x.com", "instagram.com",
    "youtube.com", "crunchbase.com", "glassdoor.com", "indeed.com",
    "google.com", "sites.google.com", "wixsite.com", "wordpress.com",
    "squarespace.com", "godaddysites.com", "shopify.com", "medium.com",
    "github.com", "notion.site", "bit.ly", "angel.co", "wellfound.com",
    "ziprecruiter.com", "monster.com", "upwork.com",
} | FREE_EMAIL_DOMAINS | HELPDESK_DOMAINS

OWN_DOMAINS = {"hirewithnear.com", "near.com", "hirewithnear.co"}


# --------------------------------------------------------------------------- #
# Throttle — Smartlead's 200/min ceiling is account-wide and shared with the
# booked-call-pause runs (09:03, 13:27 ET) and the reply-time KPI runs (~08:00 ET).
# 170 leaves headroom for a neighbour that overlaps by accident.
# --------------------------------------------------------------------------- #
MAX_PER_MIN = 170
_lock = threading.Lock()
_stamps = deque()


def throttle():
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


def smartlead(path, tries=6):
    """GET a Smartlead path. Returns parsed JSON, or None once retries are spent.

    curl, not requests: Smartlead sits behind Cloudflare, which 403s python-requests.
    The three retry branches each correspond to a failure observed live — a plain
    JSON *string* body is Smartlead's undocumented way of reporting a transient
    error, and looks nothing like an error object.
    """
    if not SMARTLEAD_KEY:
        sys.exit("ERROR: SMARTLEAD_API_KEY not set")
    sep = "&" if "?" in path else "?"
    url = f"{SMARTLEAD_BASE}{path}{sep}api_key={SMARTLEAD_KEY}"
    for attempt in range(1, tries + 1):
        throttle()
        out = subprocess.run(["curl", "-s", "--max-time", "90", url],
                             capture_output=True, text=True).stdout
        if "rate limit" in out.lower():
            time.sleep(15)
            continue
        try:
            data = json.loads(out)
        except Exception:
            time.sleep(3 * attempt)
            continue
        if isinstance(data, str):        # transient API error, not a payload
            time.sleep(3)
            continue
        return data
    return None


def hubspot(path, method="GET", body=None, tries=4):
    if not HUBSPOT_TOKEN:
        sys.exit("ERROR: HUBSPOT_ACCESS_TOKEN not set (private-app token, pat-na1-…)")
    url = f"{HUBSPOT_BASE}{path}"
    cmd = ["curl", "-s", "--max-time", "90", "-X", method, url,
           "-H", f"Authorization: Bearer {HUBSPOT_TOKEN}",
           "-H", "Content-Type: application/json"]
    if body is not None:
        cmd += ["--data-raw", json.dumps(body)]
    for attempt in range(1, tries + 1):
        out = subprocess.run(cmd, capture_output=True, text=True).stdout
        try:
            data = json.loads(out)
        except Exception:
            time.sleep(2 * attempt)
            continue
        if isinstance(data, dict) and data.get("status") == "error":
            if data.get("category") == "RATE_LIMITS":
                time.sleep(5 * attempt)
                continue
            sys.exit(f"ERROR: HubSpot {path}: {data.get('message')}")
        return data
    sys.exit(f"ERROR: HubSpot {path} unparseable after {tries} tries")


# --------------------------------------------------------------------------- #
# Time
# --------------------------------------------------------------------------- #
def parse_ts(value):
    """Smartlead mixes timestamp formats *within a single response* — trailing Z or
    +00:00, with or without microseconds. Anything unparseable returns None rather
    than raising, because one odd row must not abort a run."""
    if not value:
        return None
    s = str(value).strip().replace("Z", "+0000")
    if re.search(r"[+-]\d{2}:\d{2}$", s):
        s = s[:-3] + s[-2:]
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z",
                "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.strptime(s, fmt)
            return dt if dt.tzinfo else dt.replace(tzinfo=UTC)
        except ValueError:
            continue
    return None


def resolve_week(args):
    """(week_start, week_end_exclusive) as ET-aware datetimes.

    No args = the previous full Mon–Sun week, which is what a Monday-morning routine
    wants. The Monday-00:00-ET boundary is load-bearing: three of the 74 rows in the
    regression fixture first replied on a Saturday or Sunday, so a Sunday-start week
    would move them into the other bucket.
    """
    if not args:
        today = datetime.now(ET).date()
        last_monday = today - timedelta(days=today.weekday())
        start = last_monday - timedelta(days=7)
    else:
        y, m, d = (int(x) for x in args[0].split("-"))
        start = datetime(y, m, d).date()
        start -= timedelta(days=start.weekday())     # snap to that week's Monday
    lo = datetime(start.year, start.month, start.day, tzinfo=ET)
    return lo, lo + timedelta(days=7)


def iso_utc(dt):
    return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def et_label(dt):
    return dt.astimezone(ET).strftime("%a %Y-%m-%d %H:%M") if dt else ""


# --------------------------------------------------------------------------- #
# Matching
# --------------------------------------------------------------------------- #
def norm_domain(value):
    """Bare domain: strip scheme, www, path, port, mailto.

    Deliberately keeps the FULL domain. An earlier build stripped the last segment
    as a 'TLD', which turned grade.capital into 'grade' and silently lost that
    booking. New gTLDs are common in this book (.capital .app .io .ai .shop .health).
    """
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


def usable_domain(value):
    """A domain we're allowed to treat as a company key."""
    d = norm_domain(value)
    return "" if (not d or d in JUNK_DOMAINS or d in OWN_DOMAINS) else d


def norm_name(value):
    """Lowercased, punctuation-free name for equality comparison.

    Equality only — never substring. Measured false-positive counts for substring
    matching on this book: 'usad' hit 25 unrelated leads, 'cactus' 23, 'sana' 93,
    'purpose' 61. A short company key matched loosely is worse than no match.
    """
    if not value:
        return ""
    s = html.unescape(str(value)).lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    s = re.sub(r"\b(inc|llc|ltd|limited|corp|corporation|co|company|the|group|"
               r"holdings|labs|studio|studios|agency|partners|solutions)\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def norm_person(first, last):
    return norm_name(f"{first or ''} {last or ''}")


def norm_linkedin(value):
    if not value:
        return ""
    m = re.search(r"linkedin\.com/(?:[a-z]{2}/)?in/([^/?#]+)", str(value).lower())
    return m.group(1).strip("-") if m else ""


def strip_html(text):
    """Chili Piper writes the booking form into hs_meeting_body as HTML."""
    if not text:
        return ""
    return html.unescape(re.sub(r"<[^>]+>", "\n", text))


def parse_body_fields(body_text):
    out = {}
    for line in strip_html(body_text).splitlines():
        m = re.match(r"\s*([A-Za-z][A-Za-z0-9 '/?&-]{2,40})\s*:\s*(.+?)\s*$", line)
        if m:
            out.setdefault(m.group(1).strip().lower(), m.group(2).strip())
    return out


def load_json(path):
    with open(path) as f:
        return json.load(f)


def dump_json(path, payload):
    with open(path, "w") as f:
        json.dump(payload, f, indent=2, default=str)
    return path
