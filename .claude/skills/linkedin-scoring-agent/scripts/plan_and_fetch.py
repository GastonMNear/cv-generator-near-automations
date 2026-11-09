#!/usr/bin/env python3
"""
Phase 1 of the LinkedIn Scoring Agent: scan the sheet, plan the work, fetch job posts.

Deterministic half of the skill. Everything that protects the LinkedIn account
(sequential order, jittered pacing, run cap, abort conditions) lives here so it
cannot be forgotten mid-run. Badge reading (col I) is mechanical and decided here.
Body text for col K is written to disk for the agent to classify in phase 2.

Usage:
    python3 plan_and_fetch.py --dry-run                 # plan only: no LinkedIn calls, no writes
    python3 plan_and_fetch.py                           # live, default 40-fetch cap
    python3 plan_and_fetch.py --limit 3                 # small live batch
    python3 plan_and_fetch.py --workdir tmp/foo         # explicit work directory

Outputs (live mode) into the work directory:
    manifest.json          one entry per row needing work, rewritten after every fetch
    bodies/<job_id>.txt    job description body, only for rows needing col K
    payloads/<job_id>.txt  raw payload, so a re-parse never costs another fetch
"""

import argparse
import atexit
import json
import os
import random
import re
import subprocess
import sys
import time
import urllib.parse
from datetime import datetime

import requests
from dotenv import load_dotenv

# ── Target sheet (see docs/unknown-filler-build-notes.md §2) ──────────────────
SPREADSHEET_ID = "1nkf2qDx06lY14cXUUj_S7rFbUNsu_Xo547yqWAEwOEk"
TAB_GID = 1674515397                     # resolve by gid, NEVER by name — 3 near-identical tabs
EXPECTED_TAB_TITLE = "HMs list | No Email Found | Scoring System"
EXPECTED_COL_COUNT = 42

# letter -> 0-based index
COL_IDX = {"D": 3, "E": 4, "F": 5, "G": 6, "I": 8, "J": 9, "K": 10, "M": 12, "O": 14}
EXPECTED_HEADERS = {
    "E": "Prospect Title",
    "F": "HM Bucket Label",
    "G": "Imported Job Title",
    "I": "Work Model",
    "J": "Near Fillability",
    "K": "AI JD Verifier",
    "M": "Job LinkedIn URL",
    "O": "Company Name",
}

TRIGGER = "unknown"                      # the ONLY value that makes a cell eligible
BADGES = ("Remote", "Hybrid", "On-site")  # LinkedIn emits exactly this casing
HUMAN_REVIEW = "Human review"

BODY_START = "About the job"
BODY_END = (
    "Set alert for similar jobs",
    "Put your best foot forward",
    "Job search faster with Premium",
    "Benefits found in job post",
    "Featured benefits",
)

# Only ever matched against a payload that FAILED to yield a job posting.
# Never scanned against JD body text — words like "challenge" are common in JDs.
ABORT_MARKERS = (
    "unusual activity",
    "captcha",
    "security verification",
    "please verify",
    "authwall",
    "sign in to linkedin",
    "join linkedin to",
    "log in to continue",
    "session expired",
    "not logged in",
    "no active session",
)

SLEEP_MIN = 2.0
SLEEP_MAX = 5.0
FETCH_TIMEOUT_MS = 150000                # cold start is ~30 s; a slow first call is not a hang

LOCK_PATH = os.path.join("tmp", "linkedin-scoring", ".fetch.lock")
LOCK_STALE_SECONDS = 1800


# ── Google Sheets ─────────────────────────────────────────────────────────────
def get_access_token():
    """Fresh 1 h token. Each script invocation gets its own, so no batch outlives it."""
    load_dotenv()
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")
    if not all([client_id, client_secret, refresh_token]):
        die("Missing Google credentials in .env (GOOGLE_CLIENT_ID / _SECRET / _REFRESH_TOKEN)")
    resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
        timeout=30,
    )
    if resp.status_code != 200:
        die("Token refresh failed: {} {}".format(resp.status_code, resp.text))
    return resp.json()["access_token"]


def a1(tab_title, ref):
    """Quoted A1 range. The tab name contains '|' and spaces, so quoting is mandatory."""
    return "'" + tab_title.replace("'", "''") + "'!" + ref


def get_values(token, tab_title, ref):
    rng = urllib.parse.quote(a1(tab_title, ref), safe="")
    url = "https://sheets.googleapis.com/v4/spreadsheets/{}/values/{}".format(SPREADSHEET_ID, rng)
    resp = requests.get(url, headers={"Authorization": "Bearer " + token}, timeout=60)
    if resp.status_code != 200:
        die("Sheet read failed for {}: {} {}".format(ref, resp.status_code, resp.text))
    return resp.json().get("values", [])


def resolve_tab(token):
    """Resolve the tab by gid. Structural authority — a missing gid stops the run."""
    url = ("https://sheets.googleapis.com/v4/spreadsheets/{}"
           "?fields=sheets(properties(sheetId,title,gridProperties))".format(SPREADSHEET_ID))
    resp = requests.get(url, headers={"Authorization": "Bearer " + token}, timeout=60)
    if resp.status_code != 200:
        die("Spreadsheet metadata read failed: {} {}".format(resp.status_code, resp.text))
    for sheet in resp.json().get("sheets", []):
        props = sheet["properties"]
        if props.get("sheetId") == TAB_GID:
            return props
    die("STRUCTURAL: no tab with gid {} in this spreadsheet. The tab moved or was deleted — "
        "stop and raise this with Gaston rather than guessing another tab.".format(TAB_GID))


def verify_structure(token, tab_title):
    """Column letters can shift in a 42-column sheet, so re-verify against row 1 every run."""
    header = (get_values(token, tab_title, "A1:AP1") or [[]])[0]
    problems = []
    for letter in sorted(EXPECTED_HEADERS, key=lambda x: COL_IDX[x]):
        idx = COL_IDX[letter]
        actual = header[idx].strip() if idx < len(header) else ""
        if norm(actual) != norm(EXPECTED_HEADERS[letter]):
            problems.append((letter, EXPECTED_HEADERS[letter], actual))
    if problems:
        print("\nSTRUCTURAL MISMATCH — headers are not where the spec says they are:")
        for letter, expected, actual in problems:
            print("  col {}: expected {!r}, found {!r}".format(letter, expected, actual))
        print("\nRow 1 as read: {}".format(header))
        die("Stop here. A moved or renamed column means writing to I/K could corrupt the wrong "
            "column. Raise it with Gaston and update docs/unknown-filler-build-notes.md.")
    return header


# ── Small helpers ─────────────────────────────────────────────────────────────
def die(msg):
    print("\nERROR: " + msg)
    sys.exit(2)


def norm(value):
    return re.sub(r"\s+", " ", (value or "").strip().lower())


def cell(row, letter):
    idx = COL_IDX[letter]
    return row[idx].strip() if idx < len(row) else ""


def is_trigger(value):
    return value.strip().lower() == TRIGGER


def extract_job_id(url):
    """Trailing numeric segment. Some URLs are percent-encoded, so never URL-parse the slug."""
    if not url:
        return None
    trimmed = re.split(r"[?#]", url)[0].rstrip("/")
    match = re.search(r"(\d{5,})$", trimmed)
    return match.group(1) if match else None


def identity_verdict(sheet_value, payload_value):
    """exact | loose | mismatch. Loose tolerates suffixes/abbreviations on long names only."""
    a, b = norm(sheet_value), norm(payload_value)
    if not a or not b:
        return "mismatch"
    if a == b:
        return "exact"
    shorter, longer = (a, b) if len(a) <= len(b) else (b, a)
    if len(shorter) >= 8 and shorter in longer:
        return "loose"
    return "mismatch"


# ── LinkedIn fetch ────────────────────────────────────────────────────────────
def find_job_posting(node):
    """Pull sections.job_posting out of mcporter's output, tolerating JSON-in-text-block."""
    if isinstance(node, dict):
        value = node.get("job_posting")
        if isinstance(value, str) and value.strip():
            return value
        for child in node.values():
            found = find_job_posting(child)
            if found:
                return found
    elif isinstance(node, list):
        for child in node:
            found = find_job_posting(child)
            if found:
                return found
    elif isinstance(node, str):
        stripped = node.strip()
        if stripped.startswith("{"):
            try:
                return find_job_posting(json.loads(stripped))
            except ValueError:
                return None
    return None


def fetch_job(job_id):
    """
    Return (text, raw, error). text is the job_posting blob on success, else None.
    One fetch per job ID, ever — the caller is responsible for never calling twice.
    """
    cmd = [
        "mcporter", "call",
        "linkedin-scraper.get_job_details(job_id: \"{}\")".format(job_id),
        "--output", "json",
        "--timeout", str(FETCH_TIMEOUT_MS),
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=(FETCH_TIMEOUT_MS / 1000.0) + 30)
    except subprocess.TimeoutExpired:
        return None, "", "timeout"
    raw = (proc.stdout or "") + "\n" + (proc.stderr or "")
    if proc.returncode != 0:
        return None, raw, "mcporter exit {}".format(proc.returncode)
    try:
        data = json.loads(proc.stdout)
    except ValueError:
        return None, raw, "output was not JSON"
    text = find_job_posting(data)
    if not text or len(text.strip()) < 200:
        return None, raw, "no job_posting text in payload (deleted or blocked post?)"
    return text, raw, None


def abort_marker(raw):
    low = raw.lower()
    for marker in ABORT_MARKERS:
        if marker in low:
            return marker
    return None


def payload_lines(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def parse_badge(lines):
    """Exact match in the first ~10 non-blank lines. Never by line index — the optional
    promo and salary lines shift everything (ACM Global's salary sat right above the badge)."""
    for line in lines[:10]:
        if line in BADGES:
            return line
    return None


def extract_body(text):
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip().startswith(BODY_START):
            start = i + 1
            break
    if start is None:
        return None
    end = len(lines)
    for i in range(start, len(lines)):
        stripped = lines[i].strip()
        if any(stripped.startswith(marker) for marker in BODY_END):
            end = i
            break
    body = "\n".join(lines[start:end]).strip()
    # LinkedIn leaves its "…more" expander at the tail of the description block. Observed on
    # 2/2 payloads, both of which still reached their natural footer (EEO / benefits), so this
    # is UI chrome rather than a truncated fetch — strip it and keep the body.
    body = re.sub(r"(?:…|\.\.\.)\s*(?:see\s+)?more\s*$", "", body).strip()
    return body or None


def release_fetch_lock():
    if os.path.exists(LOCK_PATH):
        os.remove(LOCK_PATH)


def acquire_fetch_lock():
    """
    One fetch process at a time, machine-wide.

    Sequential order and jitter inside a single run are worthless if a second run is fetching
    concurrently — both share the one browser session backing Gaston's real account, and a
    duplicate run is precisely what an agent would start after losing track mid-task. The
    staleness window covers a process killed hard enough to skip its atexit handler.
    """
    os.makedirs(os.path.dirname(LOCK_PATH), exist_ok=True)
    if os.path.exists(LOCK_PATH):
        age = time.time() - os.path.getmtime(LOCK_PATH)
        with open(LOCK_PATH) as handle:
            holder = handle.read().strip()
        if age < LOCK_STALE_SECONDS:
            die("another fetch run looks active ({}), {:.0f} s ago.\n"
                "Two concurrent runs share one LinkedIn session and defeat every pacing rule in "
                "this script. Wait for it to finish, or delete {} if you are certain it "
                "died.".format(holder, age, LOCK_PATH))
        print("Clearing a stale fetch lock ({:.0f} s old, {})".format(age, holder))
        os.remove(LOCK_PATH)
    handle = os.open(LOCK_PATH, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.write(handle, "pid {} started {}Z".format(
        os.getpid(), datetime.utcnow().isoformat()).encode())
    os.close(handle)
    atexit.register(release_fetch_lock)


# ── Plan ──────────────────────────────────────────────────────────────────────
def build_plan(rows):
    """
    rows: values from A2:O, index 0 == sheet row 2.
    Returns (jobs, skipped, stats) where jobs is an ordered list of one entry per
    distinct job ID — deduped so two rows sharing a URL cost one fetch.
    """
    jobs = []
    by_job = {}
    skipped = []
    stats = {"data_rows": 0, "i_only": 0, "k_only": 0, "both": 0, "no_job_id": 0,
             "unknown_i": 0, "unknown_k": 0}

    for offset, row in enumerate(rows):
        sheet_row = offset + 2
        if not cell(row, "M") and not cell(row, "D"):
            continue                              # col A is empty on every data row; M/D define extent
        stats["data_rows"] += 1

        needs = []
        if is_trigger(cell(row, "I")):
            needs.append("I")
            stats["unknown_i"] += 1
        if is_trigger(cell(row, "K")):
            needs.append("K")
            stats["unknown_k"] += 1
        if not needs:
            continue

        if len(needs) == 2:
            stats["both"] += 1
        elif needs[0] == "I":
            stats["i_only"] += 1
        else:
            stats["k_only"] += 1

        url = cell(row, "M")
        job_id = extract_job_id(url)
        row_entry = {
            "row": sheet_row,
            "needs": needs,
            "url": url,
            "sheet_company": cell(row, "O"),
            "sheet_title": cell(row, "G"),
        }
        if not job_id:
            stats["no_job_id"] += 1
            row_entry["reason"] = "col M empty or no extractable job ID"
            row_entry["writes"] = dict((col, HUMAN_REVIEW) for col in needs)
            skipped.append(row_entry)
            continue

        if job_id in by_job:
            by_job[job_id]["rows"].append(row_entry)
        else:
            entry = {"job_id": job_id, "url": url, "rows": [row_entry]}
            by_job[job_id] = entry
            jobs.append(entry)

    return jobs, skipped, stats


def needs_classifier(job):
    return any("K" in row["needs"] for row in job["rows"])


def report_plan(stats, jobs, skipped, limit):
    planned = jobs[:limit]
    deferred = jobs[len(planned):]
    classifier_runs = sum(1 for job in planned if needs_classifier(job))
    print("\n── Work plan ──────────────────────────────────────────────")
    print("  data rows scanned          {}".format(stats["data_rows"]))
    print("  cells reading 'unknown'    I: {}   K: {}".format(stats["unknown_i"], stats["unknown_k"]))
    print("  rows needing work          {} (I only {} · K only {} · both {})".format(
        stats["i_only"] + stats["k_only"] + stats["both"],
        stats["i_only"], stats["k_only"], stats["both"]))
    print("  rows with no job ID        {}  -> {} without any fetch".format(
        stats["no_job_id"], HUMAN_REVIEW))
    print("  distinct job IDs to fetch  {}".format(len(jobs)))
    print("  run cap                    {}".format(limit))
    print("  fetches this run           {}".format(len(planned)))
    print("  classifier runs (col K)    {}".format(classifier_runs))
    print("  deferred to a later run    {}".format(len(deferred)))
    est = len(planned) * 11.5 / 60.0
    print("  estimated fetch time       ~{:.0f} min at ~11.5 s/row".format(est))
    if skipped:
        print("\n  no-job-ID rows: {}".format(", ".join(str(r["row"]) for r in skipped)))
    if planned:
        preview = planned[:10]
        print("\n  first {} planned fetches:".format(len(preview)))
        for job in preview:
            rows = ",".join(str(r["row"]) for r in job["rows"])
            cols = "+".join(sorted(set(c for r in job["rows"] for c in r["needs"])))
            print("    row {:<6} job {:<12} needs {}".format(rows, job["job_id"], cols))
    return planned, deferred


# ── Run ───────────────────────────────────────────────────────────────────────
def save_manifest(workdir, manifest):
    path = os.path.join(workdir, "manifest.json")
    with open(path, "w") as handle:
        json.dump(manifest, handle, indent=2)
    return path


def main():
    parser = argparse.ArgumentParser(description="Plan and fetch for the LinkedIn Scoring Agent.")
    parser.add_argument("--dry-run", action="store_true",
                        help="scan and report the plan; zero LinkedIn calls, zero writes")
    parser.add_argument("--limit", type=int, default=40,
                        help="max LinkedIn fetches this run (default 40)")
    parser.add_argument("--workdir", default=None,
                        help="work directory (default tmp/linkedin-scoring/<timestamp>)")
    parser.add_argument("--rows", default=None,
                        help="comma-separated sheet rows to restrict this run to, e.g. 97,72,96. "
                             "Lets a run target rows by score upside instead of sheet order.")
    args = parser.parse_args()

    if args.limit < 1:
        die("--limit must be at least 1")

    only_rows = None
    if args.rows:
        try:
            only_rows = {int(part) for part in args.rows.split(",") if part.strip()}
        except ValueError:
            die("--rows must be comma-separated integers, e.g. 97,72,96")
        if not only_rows:
            die("--rows was empty")

    token = get_access_token()
    props = resolve_tab(token)
    tab_title = props["title"]
    print("Tab gid {} resolved to {!r}".format(TAB_GID, tab_title))
    if tab_title != EXPECTED_TAB_TITLE:
        print("  WARNING: tab was renamed (spec expects {!r}). gid is authoritative, "
              "continuing.".format(EXPECTED_TAB_TITLE))
    col_count = props.get("gridProperties", {}).get("columnCount")
    if col_count != EXPECTED_COL_COUNT:
        print("  WARNING: {} columns, spec expects {}. Columns were added or removed — "
              "header check below is the real guard.".format(col_count, EXPECTED_COL_COUNT))
    verify_structure(token, tab_title)
    print("Column headers verified against row 1: E F G I J K M O all in place")

    rows = get_values(token, tab_title, "A2:O")
    jobs, skipped, stats = build_plan(rows)
    if only_rows is not None:
        # A job is kept whole when any of its rows was selected — two rows sharing one post
        # share one fetch and one verdict, so splitting them would be wrong.
        jobs = [job for job in jobs if any(r["row"] in only_rows for r in job["rows"])]
        skipped = [r for r in skipped if r["row"] in only_rows]
        selected = {r["row"] for job in jobs for r in job["rows"]} | {r["row"] for r in skipped}
        missing = sorted(only_rows - selected)
        print("\n--rows filter: {} of {} requested rows need work; {} job(s) to fetch".format(
            len(only_rows) - len(missing), len(only_rows), len(jobs)))
        if missing:
            print("  requested but not in the work plan (already filled, or no job URL): {}".format(
                ", ".join(str(r) for r in missing)))
        if not jobs and not skipped:
            die("No requested row needs work. Nothing to do.")
    planned, deferred = report_plan(stats, jobs, skipped, args.limit)

    workdir = args.workdir or os.path.join(
        "tmp", "linkedin-scoring", datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"))

    manifest = {
        "mode": "dry-run" if args.dry_run else "live",
        "started_utc": datetime.utcnow().isoformat() + "Z",
        "spreadsheet_id": SPREADSHEET_ID,
        "tab_gid": TAB_GID,
        "tab_title": tab_title,
        "limit": args.limit,
        "stats": stats,
        "status": "planned",
        "abort_reason": None,
        "deferred_job_ids": [job["job_id"] for job in deferred],
        "entries": [],
    }

    # Rows we can finish without any fetch (no job ID) are terminal immediately.
    for row_entry in skipped:
        entry = dict(row_entry)
        entry["job_id"] = None
        entry["fetch_status"] = "no_job_id"
        manifest["entries"].append(entry)

    if args.dry_run:
        os.makedirs(workdir, exist_ok=True)
        for job in planned:
            for row_entry in job["rows"]:
                entry = dict(row_entry)
                entry["job_id"] = job["job_id"]
                entry["fetch_status"] = "planned"
                manifest["entries"].append(entry)
        manifest["status"] = "dry-run"
        path = save_manifest(workdir, manifest)
        print("\nDRY RUN — no LinkedIn calls made, no cells written.")
        print("Plan written to {}".format(path))
        return

    acquire_fetch_lock()
    os.makedirs(os.path.join(workdir, "bodies"), exist_ok=True)
    os.makedirs(os.path.join(workdir, "payloads"), exist_ok=True)
    print("\nWork directory: {}".format(workdir))
    print("Fetching {} job posts sequentially with 2-5 s jitter. Do not run this in "
          "parallel.\n".format(len(planned)))

    consecutive_failures = []       # entries provisionally Human review; a 2nd failure aborts
    fetched = 0

    for index, job in enumerate(planned):
        if index > 0:
            pause = random.uniform(SLEEP_MIN, SLEEP_MAX)
            time.sleep(pause)
        rows_label = ",".join(str(r["row"]) for r in job["rows"])
        print("[{}/{}] row {} job {} ... ".format(index + 1, len(planned), rows_label, job["job_id"]),
              end="", flush=True)

        text, raw, error = fetch_job(job["job_id"])
        fetched += 1

        if error:
            marker = abort_marker(raw)
            failed_entries = []
            for row_entry in job["rows"]:
                entry = dict(row_entry)
                entry["job_id"] = job["job_id"]
                entry["fetch_status"] = "error"
                entry["reason"] = error
                entry["writes"] = dict((col, HUMAN_REVIEW) for col in row_entry["needs"])
                manifest["entries"].append(entry)
                failed_entries.append(entry)
            print("FAILED ({})".format(error))
            print("      raw output: {}".format(raw.strip()[:800].replace("\n", " | ")))

            if marker:
                # Account-level trouble. Stop immediately and leave these rows untouched.
                for entry in failed_entries + consecutive_failures:
                    entry["writes"] = {}
                    entry["leave_unknown"] = True
                manifest["status"] = "aborted"
                manifest["abort_reason"] = "block/challenge signal in response: " + marker
                save_manifest(workdir, manifest)
                print("\nABORTED — {}".format(manifest["abort_reason"]))
                print("Rows in flight keep 'unknown'. Check the LinkedIn session before retrying.")
                break

            consecutive_failures.extend(failed_entries)
            if len(consecutive_failures) >= 2:
                for entry in consecutive_failures:
                    entry["writes"] = {}
                    entry["leave_unknown"] = True
                manifest["status"] = "aborted"
                manifest["abort_reason"] = "two consecutive failed fetches"
                save_manifest(workdir, manifest)
                print("\nABORTED — two consecutive failed fetches. A run of failures is what "
                      "precedes a restriction; not grinding through.")
                print("Rows in flight keep 'unknown'.")
                break
            save_manifest(workdir, manifest)
            continue

        consecutive_failures = []

        # Keep the raw payload. It costs nothing, and because we never fetch a link twice it is
        # the only way to re-parse a badge or body later without spending another request.
        with open(os.path.join(workdir, "payloads", job["job_id"] + ".txt"), "w") as handle:
            handle.write(text)

        lines = payload_lines(text)
        payload_company = lines[0] if lines else ""
        payload_title = lines[1] if len(lines) > 1 else ""
        badge = parse_badge(lines)
        body = extract_body(text)

        body_file = None
        if body and needs_classifier(job):
            body_file = os.path.join("bodies", job["job_id"] + ".txt")
            with open(os.path.join(workdir, body_file), "w") as handle:
                handle.write(body)

        job_entries = []
        for row_entry in job["rows"]:
            entry = dict(row_entry)
            entry["job_id"] = job["job_id"]
            entry["fetch_status"] = "ok"
            entry["payload_company"] = payload_company
            entry["payload_title"] = payload_title
            entry["company_match"] = identity_verdict(row_entry["sheet_company"], payload_company)
            entry["title_match"] = identity_verdict(row_entry["sheet_title"], payload_title)
            entry["identity_ok"] = (entry["company_match"] != "mismatch"
                                    and entry["title_match"] != "mismatch")
            entry["badge"] = badge
            entry["body_file"] = body_file if "K" in row_entry["needs"] else None
            entry["body_chars"] = len(body) if body else 0

            writes = {}
            if "I" in row_entry["needs"]:
                writes["I"] = badge if badge else HUMAN_REVIEW
            if "K" in row_entry["needs"] and not entry["body_file"]:
                # Page loaded but no readable body -> the classifier's Unknown, mapped at write time.
                writes["K"] = HUMAN_REVIEW
                entry["reason"] = "no 'About the job' body found in payload"
            entry["writes"] = writes
            manifest["entries"].append(entry)
            job_entries.append(entry)

        flags = ["badge=" + badge if badge else "badge=none"]
        if body:
            flags.append("body={} chars".format(len(body)))
        if any(not entry["identity_ok"] for entry in job_entries):
            flags.append("IDENTITY MISMATCH — nothing will be written for this row")
        print("ok ({})".format(", ".join(flags)))
        save_manifest(workdir, manifest)

    if manifest["status"] != "aborted":
        manifest["status"] = "cap-reached" if deferred else "complete"
    manifest["finished_utc"] = datetime.utcnow().isoformat() + "Z"
    path = save_manifest(workdir, manifest)

    pending_k = sorted(set(e["job_id"] for e in manifest["entries"]
                           if e.get("body_file") and e.get("identity_ok")))
    mismatches = [e["row"] for e in manifest["entries"] if e.get("identity_ok") is False]

    print("\n── Fetch summary ──────────────────────────────────────────")
    print("  status                {}".format(manifest["status"]))
    print("  fetches made          {}".format(fetched))
    print("  rows in manifest      {}".format(len(manifest["entries"])))
    print("  job IDs awaiting col K classification  {}".format(len(pending_k)))
    if mismatches:
        print("  IDENTITY MISMATCH rows (nothing will be written): {}".format(
            ", ".join(str(r) for r in mismatches)))
    if deferred:
        print("  deferred job IDs      {} (still 'unknown', no sentinel written)".format(len(deferred)))
    print("\n  manifest: {}".format(path))
    print("  work dir: {}".format(workdir))
    if pending_k:
        print("\nNext: classify each body in {}/bodies/ per the skill's JD Compliance Scan prompt, "
              "then write verdicts.json in the work directory.".format(workdir))
    else:
        print("\nNext: no col K work — run write_results.py --dry-run to review the col I writes.")


if __name__ == "__main__":
    main()
