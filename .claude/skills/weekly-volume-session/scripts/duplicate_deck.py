#!/usr/bin/env python3
"""Copy the last volume session deck into the same Drive folder under this session's name.

    python3 duplicate_deck.py --session-date 2026-10-27             # finds the last deck
    python3 duplicate_deck.py --session-date 2026-10-27 --src <id>  # explicit source

The session is bi-weekly: the last deck should be 14 days before --session-date. If it
isn't, the script still copies but prints a warning (a skipped or moved session).

Name: MM-DD_Near_Weekly_Outbound_Volume_Session. If that name already exists in the
folder, the script prints the existing deck and stops, so it never makes a second copy.
"""
import argparse
import json
import os
import sys
import urllib.parse
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slides_lib import api, token

FOLDER = "1ANO1rNmzojy4zOKj3x2Z49Oed1ysp0iR"  # "volume session docs" folder
SUFFIX = "_Near_Weekly_Outbound_Volume_Session"
DRIVE = "https://www.googleapis.com/drive/v3/files"


def list_decks(tok):
    q = f"'{FOLDER}' in parents and trashed=false and name contains '{SUFFIX}'"
    u = f"{DRIVE}?q={urllib.parse.quote(q)}&fields=files(id,name,createdTime)&orderBy=createdTime%20desc" \
        "&supportsAllDrives=true&includeItemsFromAllDrives=true&pageSize=100"
    return api(tok, "GET", u)["files"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--session-date", required=True, help="date of the meeting, YYYY-MM-DD")
    ap.add_argument("--src")
    a = ap.parse_args()
    sd = date.fromisoformat(a.session_date)
    name = f"{sd.month:02d}-{sd.day:02d}{SUFFIX}"
    tok = token()
    decks = list_decks(tok)
    existing = [d for d in decks if d["name"] == name]
    if existing:
        print(json.dumps({"status": "exists", **existing[0],
                          "url": f"https://docs.google.com/presentation/d/{existing[0]['id']}/edit"}, indent=2))
        return
    src, warning = a.src, None
    if not src:
        # newest-created deck = the last session's (names are MM-DD, which don't sort across a new year)
        if not decks:
            sys.exit("No earlier deck found in the folder: pass --src")
        src = decks[0]["id"]
        print(f"Source: {decks[0]['name']} ({src})", file=sys.stderr)
        mm, dd = decks[0]["name"][:5].split("-")
        src_date = date(int(decks[0]["createdTime"][:4]), int(mm), int(dd))
        if (sd - src_date).days != 14:
            warning = (f"Last deck is {decks[0]['name'][:5]}, {(sd - src_date).days} days before "
                       f"{sd}, not 14: check the session date with Gaston")
            print("WARNING:", warning, file=sys.stderr)
    new = api(tok, "POST", f"{DRIVE}/{src}/copy?supportsAllDrives=true&fields=id,name",
              {"name": name, "parents": [FOLDER]})
    print(json.dumps({"status": "created", "source": src, "warning": warning, **new,
                      "url": f"https://docs.google.com/presentation/d/{new['id']}/edit"}, indent=2))


if __name__ == "__main__":
    main()
