"""Shared Smartlead helpers for this skill's scripts (curl only: Cloudflare blocks Python HTTP clients)."""
import json, os, subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
BASE = "https://server.smartlead.ai/api/v1"


def _key():
    for line in open(os.path.join(ROOT, ".env")):
        if line.startswith("SMARTLEAD_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("SMARTLEAD_API_KEY not in .env")


KEY = _key()


def call(method, path, body=None):
    sep = "&" if "?" in path else "?"
    cmd = ["curl", "-s", "-X", method, f"{BASE}{path}{sep}api_key={KEY}", "-H", "Content-Type: application/json"]
    if body is not None:
        cmd += ["--data-binary", json.dumps(body)]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    try:
        return json.loads(out)
    except ValueError:
        raise SystemExit(f"{method} {path} -> non-JSON: {out[:300]}")


def get(path):
    return call("GET", path)


def read_dump(path):
    """Payload of a cb.dump() result saved by the harness, as a string.

    Handles the harness's file format (JSON array of {type, text}, the first text being the tool's
    JSON-quoted return value + a "(captured at …)" note), a bare JSON string, or raw text."""
    raw = open(path).read()
    try:
        d = json.loads(raw)
        if isinstance(d, list) and d and isinstance(d[0], dict) and "text" in d[0]:
            raw = d[0]["text"]
        elif isinstance(d, str):
            raw = d
    except ValueError:
        pass
    if raw.lstrip().startswith('"'):
        raw = json.JSONDecoder().raw_decode(raw.lstrip())[0]
    return raw.split("\n" + "X" * 1000)[0]


def campaign_leads(cid):
    leads, off = [], 0
    while True:
        d = get(f"/campaigns/{cid}/leads?offset={off}&limit=100").get("data", [])
        leads += d
        if len(d) < 100:
            return leads
        off += 100
