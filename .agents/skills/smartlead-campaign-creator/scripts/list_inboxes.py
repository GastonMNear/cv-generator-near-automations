#!/usr/bin/env python3
"""List Smartlead email accounts (inboxes), filtered for campaign inbox selection.

Read-only. Calls go through curl because Cloudflare blocks Python HTTP clients.

Usage:
  python3 list_inboxes.py --tag "A"                      # all inboxes tagged "A"
  python3 list_inboxes.py --campaign 3596793             # inboxes attached to an existing campaign
  python3 list_inboxes.py --tag "A" --exclude hayden     # tag A minus addresses containing "hayden"
  python3 list_inboxes.py --match neartalent             # addresses containing a substring
  python3 list_inboxes.py --tags                         # just list available tags with counts

Prints one line per inbox: id | from_email | from_name | tags
Last line: "IDS: [comma-separated ids]" ready to paste into a spec.
"""
import argparse
import json
import os
import subprocess
import sys

BASE = "https://server.smartlead.ai/api/v1"


def load_api_key():
    key = os.environ.get("SMARTLEAD_API_KEY")
    if key:
        return key
    # walk up from this script to find the project .env
    d = os.path.dirname(os.path.abspath(__file__))
    while d != "/":
        env_path = os.path.join(d, ".env")
        if os.path.exists(env_path):
            for line in open(env_path):
                line = line.strip()
                if line.startswith("SMARTLEAD_API_KEY="):
                    return line.split("=", 1)[1].strip().strip("'\"")
        d = os.path.dirname(d)
    sys.exit("SMARTLEAD_API_KEY not found in environment or any parent .env")


def curl_get(url):
    out = subprocess.run(["curl", "-s", url], capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        sys.exit(f"curl failed: {out.stderr}")
    return json.loads(out.stdout)


def fetch_all_accounts(key):
    accounts, offset = [], 0
    while True:
        page = curl_get(f"{BASE}/email-accounts/?api_key={key}&offset={offset}&limit=100")
        accounts += page
        if len(page) < 100:
            return accounts
        offset += 100


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--tag", help="filter: inbox has this tag (exact, case-insensitive)")
    p.add_argument("--campaign", type=int, help="list inboxes attached to this campaign id (read-only)")
    p.add_argument("--match", action="append", default=[], help="keep addresses containing substring (repeatable, OR)")
    p.add_argument("--exclude", action="append", default=[], help="drop addresses containing substring (repeatable)")
    p.add_argument("--tags", action="store_true", help="list all tags with counts and exit")
    args = p.parse_args()

    key = load_api_key()

    if args.campaign:
        accounts = curl_get(f"{BASE}/campaigns/{args.campaign}/email-accounts?api_key={key}")
    else:
        accounts = fetch_all_accounts(key)

    if args.tags:
        from collections import Counter
        counts = Counter(t["tag_name"] for a in accounts for t in (a.get("tags") or []))
        for name, c in counts.most_common():
            print(f"{name}: {c}")
        return

    def keep(a):
        email = (a.get("from_email") or "").lower()
        if args.tag:
            names = [t["tag_name"].lower() for t in (a.get("tags") or [])]
            if args.tag.lower() not in names:
                return False
        if args.match and not any(m.lower() in email for m in args.match):
            return False
        if any(x.lower() in email for x in args.exclude):
            return False
        return True

    kept = [a for a in accounts if keep(a)]
    for a in kept:
        tags = ",".join(t["tag_name"] for t in (a.get("tags") or []))
        print(f"{a['id']} | {a.get('from_email')} | {a.get('from_name')} | {tags}")
    print(f"COUNT: {len(kept)}")
    print(f"IDS: {','.join(str(a['id']) for a in kept)}")


if __name__ == "__main__":
    main()
