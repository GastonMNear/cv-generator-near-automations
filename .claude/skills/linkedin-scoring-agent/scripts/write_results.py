#!/usr/bin/env python3
"""
Phase 3 of the LinkedIn Scoring Agent: re-verify row identity, write cells, verify.

Reads the manifest produced by plan_and_fetch.py plus verdicts.json (the agent's
col K classifications, keyed by job ID) and writes single-cell ranges into
columns I and K only.

Usage:
    python3 write_results.py --workdir tmp/linkedin-scoring/<ts> --dry-run   # review first
    python3 write_results.py --workdir tmp/linkedin-scoring/<ts>            # write

Guards, in order, per row:
  1. run aborted / leave_unknown        -> write nothing
  2. identity mismatch at fetch time    -> write nothing
  3. identity re-check against the CURRENT sheet row -> write nothing on mismatch
  4. target cell no longer reads 'unknown' -> skip that cell (never overwrite a real value)
"""

import argparse
import json
import os
import re
import sys
import urllib.parse

import requests
from dotenv import load_dotenv

SPREADSHEET_ID = "1nkf2qDx06lY14cXUUj_S7rFbUNsu_Xo547yqWAEwOEk"
TAB_GID = 1674515397
COL_IDX = {"G": 6, "I": 8, "K": 10, "M": 12, "O": 14, "AB": 27, "AC": 28}
EXPECTED_HEADERS = {"G": "Imported Job Title", "I": "Work Model", "K": "AI JD Verifier",
                    "M": "Job LinkedIn URL", "O": "Company Name"}

TRIGGER = "unknown"
HUMAN_REVIEW = "Human review"
WRITABLE = ("I", "K")
# The classifier's Unknown is legitimate upstream but must never reach the sheet,
# or the row would be re-fetched every run for no gain.
VERDICT_MAP = {"remote-friendly": "Remote-friendly", "us-specific": "US-Specific",
               "unknown": HUMAN_REVIEW}
ALLOWED = {"I": ("Remote", "Hybrid", "On-site", HUMAN_REVIEW),
           "K": ("Remote-friendly", "US-Specific", HUMAN_REVIEW)}
BATCH_SIZE = 20                      # checkpoint as we go rather than one big final write


def die(msg):
    print("\nERROR: " + msg)
    sys.exit(2)


def norm(value):
    return re.sub(r"\s+", " ", (value or "").strip().lower())


def get_access_token():
    load_dotenv()
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")
    if not all([client_id, client_secret, refresh_token]):
        die("Missing Google credentials in .env (GOOGLE_CLIENT_ID / _SECRET / _REFRESH_TOKEN)")
    resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={"client_id": client_id, "client_secret": client_secret,
              "refresh_token": refresh_token, "grant_type": "refresh_token"},
        timeout=30,
    )
    if resp.status_code != 200:
        die("Token refresh failed: {} {}".format(resp.status_code, resp.text))
    return resp.json()["access_token"]


def a1(tab_title, ref):
    return "'" + tab_title.replace("'", "''") + "'!" + ref


def get_values(token, tab_title, ref):
    rng = urllib.parse.quote(a1(tab_title, ref), safe="")
    url = "https://sheets.googleapis.com/v4/spreadsheets/{}/values/{}".format(SPREADSHEET_ID, rng)
    resp = requests.get(url, headers={"Authorization": "Bearer " + token}, timeout=60)
    if resp.status_code != 200:
        die("Sheet read failed for {}: {} {}".format(ref, resp.status_code, resp.text))
    return resp.json().get("values", [])


def resolve_tab(token):
    url = ("https://sheets.googleapis.com/v4/spreadsheets/{}"
           "?fields=sheets(properties(sheetId,title))".format(SPREADSHEET_ID))
    resp = requests.get(url, headers={"Authorization": "Bearer " + token}, timeout=60)
    if resp.status_code != 200:
        die("Spreadsheet metadata read failed: {} {}".format(resp.status_code, resp.text))
    for sheet in resp.json().get("sheets", []):
        if sheet["properties"].get("sheetId") == TAB_GID:
            return sheet["properties"]["title"]
    die("STRUCTURAL: no tab with gid {}. Stop and raise it.".format(TAB_GID))


def verify_headers(token, tab_title):
    header = (get_values(token, tab_title, "A1:AP1") or [[]])[0]
    for letter, expected in EXPECTED_HEADERS.items():
        idx = COL_IDX[letter]
        actual = header[idx].strip() if idx < len(header) else ""
        if norm(actual) != norm(expected):
            die("STRUCTURAL: col {} reads {!r}, expected {!r}. Columns moved since the fetch — "
                "writing now could hit the wrong column. Stop and raise it.".format(
                    letter, actual, expected))


def cell(row, letter):
    idx = COL_IDX[letter]
    return row[idx].strip() if idx < len(row) else ""


def identity_verdict(sheet_value, payload_value):
    a, b = norm(sheet_value), norm(payload_value)
    if not a or not b:
        return "mismatch"
    if a == b:
        return "exact"
    shorter, longer = (a, b) if len(a) <= len(b) else (b, a)
    if len(shorter) >= 8 and shorter in longer:
        return "loose"
    return "mismatch"


def count_unknowns(rows):
    counts = {"I": 0, "K": 0}
    for row in rows:
        for letter in WRITABLE:
            if cell(row, letter).lower() == TRIGGER:
                counts[letter] += 1
    return counts


def resolve_k_value(entry, verdicts):
    """Prefer an explicit pre-set value (error/no-body rows), else the agent's verdict."""
    preset = entry.get("writes", {}).get("K")
    if preset:
        return preset, None
    verdict = verdicts.get(entry.get("job_id"))
    if verdict is None:
        return None, "no verdict in verdicts.json for job {}".format(entry.get("job_id"))
    mapped = VERDICT_MAP.get(norm(verdict))
    if mapped is None:
        return None, "verdict {!r} is not Remote-friendly / US-Specific / Unknown".format(verdict)
    return mapped, None


def main():
    parser = argparse.ArgumentParser(description="Write phase for the LinkedIn Scoring Agent.")
    parser.add_argument("--workdir", required=True, help="work directory from plan_and_fetch.py")
    parser.add_argument("--dry-run", action="store_true",
                        help="report the exact cell writes without writing anything")
    args = parser.parse_args()

    manifest_path = os.path.join(args.workdir, "manifest.json")
    if not os.path.exists(manifest_path):
        die("No manifest.json in {}".format(args.workdir))
    with open(manifest_path) as handle:
        manifest = json.load(handle)

    if manifest.get("mode") == "dry-run":
        die("That manifest came from a --dry-run plan; there is nothing to write.")

    verdicts = {}
    verdicts_path = os.path.join(args.workdir, "verdicts.json")
    if os.path.exists(verdicts_path):
        with open(verdicts_path) as handle:
            verdicts = json.load(handle)

    # Every fetched body must have a verdict, or phase 2 is unfinished.
    missing = sorted(set(e["job_id"] for e in manifest["entries"]
                         if e.get("body_file") and e.get("identity_ok")
                         and not e.get("writes", {}).get("K")
                         and e.get("job_id") not in verdicts))
    if missing:
        die("verdicts.json is missing {} job ID(s): {}\nClassify those bodies first — writing a "
            "partial batch is fine, but silently dropping rows is not.".format(
                len(missing), ", ".join(missing)))

    token = get_access_token()
    tab_title = resolve_tab(token)
    if tab_title != manifest.get("tab_title"):
        die("STRUCTURAL: tab gid {} is now titled {!r} but was {!r} at fetch time.".format(
            TAB_GID, tab_title, manifest.get("tab_title")))
    verify_headers(token, tab_title)

    rows = get_values(token, tab_title, "A2:O")
    before = count_unknowns(rows)

    planned = []      # (row, letter, value)
    skipped = []      # (row, reason)

    for entry in manifest["entries"]:
        row_num = entry["row"]
        if entry.get("leave_unknown"):
            skipped.append((row_num, "run aborted while in flight — stays 'unknown' for a retry"))
            continue
        if entry.get("identity_ok") is False:
            skipped.append((row_num, "identity mismatch at fetch: sheet {!r}/{!r} vs payload "
                                     "{!r}/{!r}".format(entry.get("sheet_company"),
                                                        entry.get("sheet_title"),
                                                        entry.get("payload_company"),
                                                        entry.get("payload_title"))))
            continue
        writes = entry.get("writes") or {}
        needs = entry.get("needs") or []
        if not writes and "K" not in needs:
            skipped.append((row_num, "nothing to write"))
            continue

        offset = row_num - 2
        if offset < 0 or offset >= len(rows):
            skipped.append((row_num, "row no longer exists in the sheet"))
            continue
        current = rows[offset]

        # Re-check identity against the CURRENT contents of that row. Rows can be
        # sorted or inserted between phases, and a stale row number would stomp
        # another lead's data.
        if entry.get("fetch_status") == "ok":
            company_ok = identity_verdict(cell(current, "O"), entry.get("payload_company")) != "mismatch"
            title_ok = identity_verdict(cell(current, "G"), entry.get("payload_title")) != "mismatch"
            if not (company_ok and title_ok):
                skipped.append((row_num, "row moved since fetch: now {!r}/{!r}".format(
                    cell(current, "O"), cell(current, "G"))))
                continue
        elif cell(current, "M") != (entry.get("url") or ""):
            # Failed/no-ID rows have no payload to match on; the URL is the only anchor.
            skipped.append((row_num, "col M changed since the scan — cannot confirm the row"))
            continue

        for letter in WRITABLE:
            value = writes.get(letter)
            if letter == "K" and "K" in needs and not value:
                value, problem = resolve_k_value(entry, verdicts)
                if problem:
                    skipped.append((row_num, problem))
                    continue
            if not value:
                continue
            if value not in ALLOWED[letter]:
                skipped.append((row_num, "refusing to write {!r} to col {}".format(value, letter)))
                continue
            if cell(current, letter).lower() != TRIGGER:
                skipped.append((row_num, "col {} no longer reads 'unknown' (now {!r}) — left "
                                         "alone".format(letter, cell(current, letter))))
                continue
            planned.append((row_num, letter, value))

    print("\n── Planned writes ─────────────────────────────────────────")
    print("  tab            {!r} (gid {})".format(tab_title, TAB_GID))
    print("  unknown now    I: {}   K: {}".format(before["I"], before["K"]))
    print("  cells to write {}".format(len(planned)))
    for row_num, letter, value in planned:
        print("    {}{:<5} <- {}".format(letter, row_num, value))
    if skipped:
        print("\n  not written ({}):".format(len(skipped)))
        for row_num, reason in skipped:
            print("    row {:<5} {}".format(row_num, reason))

    if args.dry_run:
        print("\nDRY RUN — nothing written.")
        return
    if not planned:
        print("\nNothing to write.")
        return

    written = []
    for start in range(0, len(planned), BATCH_SIZE):
        chunk = planned[start:start + BATCH_SIZE]
        data = [{"range": a1(tab_title, letter + str(row_num)), "values": [[value]]}
                for row_num, letter, value in chunk]
        url = "https://sheets.googleapis.com/v4/spreadsheets/{}/values:batchUpdate".format(
            SPREADSHEET_ID)
        resp = requests.post(
            url,
            headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
            json={"valueInputOption": "USER_ENTERED", "data": data},
            timeout=120,
        )
        if resp.status_code != 200:
            print("\nERROR: batchUpdate failed on cells {}-{}: {} {}".format(
                start + 1, start + len(chunk), resp.status_code, resp.text))
            print("Cells written before this failure are safe: {}".format(len(written)))
            sys.exit(2)
        written.extend(chunk)
        print("  wrote {} cells ({}/{})".format(len(chunk), len(written), len(planned)))

    # Verify: read the touched rows back and confirm each cell holds what we sent. Reading out to
    # AL also proves the spilled ARRAYFORMULAs in row 2 still recalculate — a broken score column
    # is the one way an I/K write could damage the sheet.
    after_rows = get_values(token, tab_title, "A2:AL")
    bad = []
    for row_num, letter, value in written:
        offset = row_num - 2
        actual = cell(after_rows[offset], letter) if offset < len(after_rows) else ""
        if norm(actual) != norm(value):
            bad.append((row_num, letter, value, actual))
    after = count_unknowns(after_rows)

    print("\n── Result ─────────────────────────────────────────────────")
    print("  cells written  {}".format(len(written)))
    print("  verified       {}".format(len(written) - len(bad)))
    for row_num, letter, expected, actual in bad:
        print("    MISMATCH {}{}: sent {!r}, sheet reads {!r}".format(letter, row_num, expected, actual))
    for letter in WRITABLE:
        expected_delta = sum(1 for _, col, _ in written if col == letter)
        actual_delta = before[letter] - after[letter]
        flag = "ok" if expected_delta == actual_delta else "CHECK — someone else may have edited"
        print("  col {} unknown  {} -> {} (delta {}, expected {}) {}".format(
            letter, before[letter], after[letter], actual_delta, expected_delta, flag))

    print("\n  recalculated scores on touched rows:")
    scores = []
    for row_num in sorted(set(r for r, _, _ in written)):
        offset = row_num - 2
        row = after_rows[offset] if offset < len(after_rows) else []
        total, priority = cell(row, "AB"), cell(row, "AC")
        scores.append({"row": row_num, "total_score": total, "priority": priority})
        blank = "  <- BLANK: check the ARRAYFORMULA in row 2" if not total and not priority else ""
        print("    row {:<5} I={:<13} K={:<15} score={:<5} priority={}{}".format(
            row_num, cell(row, "I"), cell(row, "K"), total, priority, blank))

    report = {"tab_title": tab_title, "written": [{"row": r, "col": c, "value": v}
                                                  for r, c, v in written],
              "skipped": [{"row": r, "reason": m} for r, m in skipped],
              "unknown_before": before, "unknown_after": after, "scores_after": scores,
              "verify_mismatches": [{"row": r, "col": c, "sent": e, "sheet": a}
                                    for r, c, e, a in bad]}
    report_path = os.path.join(args.workdir, "write_report.json")
    with open(report_path, "w") as handle:
        json.dump(report, handle, indent=2)
    print("\n  report: {}".format(report_path))
    if bad:
        sys.exit(1)


if __name__ == "__main__":
    main()
