#!/usr/bin/env python3
"""Pull cumulative Smartlead numbers for every experiment arm and benchmark.

    python3 pull_stats.py --out <scratch>/stats.json [--only EXP-012,EXP-013] [--asof 2026-10-27]

Reads references/experiments.json. For each arm it pages /campaigns/{id}/statistics for the
parent and every non-DRAFTED child (children found by parent_campaign_id, never by name: many
"SUB | [EXP012] ..." children belong to other parents). Per lead:
  - received Email N   = the lead has a sent row at sequence_number N in the parent
  - category           = union of the lead's current categories across parent + children;
                         any positive-sentiment one wins, Meeting Booked over the rest
  - reply step         = sequence_number of the lead's first parent reply
  - actual reply       = replied, not bounced, category not OOO / bounce / uncategorized / null
Categories are *current*, so counts can drop when a lead is re-tagged.

curl, not requests: Smartlead's Cloudflare 403s python-requests. An empty or slow page is
retried, never treated as "no rows" (2026-10-20: 56 s calls produced false zeros).
"""
import argparse
import json
import os
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "..", "references", "experiments.json")
BASE = "https://server.smartlead.ai/api/v1"
NOT_ACTUAL = {None, "Out Of Office", "Sender Originated Bounce", "Uncategorizable by Ai"}


def env_key():
    if os.environ.get("SMARTLEAD_API_KEY"):
        return os.environ["SMARTLEAD_API_KEY"]
    d = HERE
    while d != "/":
        p = os.path.join(d, ".env")
        if os.path.exists(p):
            for line in open(p):
                if line.startswith("SMARTLEAD_API_KEY="):
                    return line.split("=", 1)[1].strip().strip("'\"")
        d = os.path.dirname(d)
    sys.exit("SMARTLEAD_API_KEY not found")


KEY = env_key()


def get(path, want=None, tries=6):
    sep = "&" if "?" in path else "?"
    url = f"{BASE}{path}{sep}api_key={KEY}"
    for attempt in range(1, tries + 1):
        out = subprocess.run(["curl", "-s", "--max-time", "120", url],
                             capture_output=True, text=True).stdout
        try:
            data = json.loads(out, strict=False)
        except ValueError:
            data = None
        if data is not None and not isinstance(data, str) and (want is None or want(data)):
            return data
        time.sleep(4 * attempt)
    raise RuntimeError(f"Smartlead GET {path} failed after {tries} tries")


def stats_rows(cid):
    rows, offset = [], 0
    while True:
        page = get(f"/campaigns/{cid}/statistics?limit=500&offset={offset}",
                   want=lambda d: isinstance(d, dict) and "data" in d)
        rows += page["data"]
        offset += 500
        if offset >= int(page.get("total_stats") or 0):
            return rows


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None


def build_leads(parent_ids, children, sentiment):
    leads = defaultdict(lambda: {"steps": set(), "first_e1": None, "reply": None,
                                 "cats": set(), "bounced": False})
    for pid in parent_ids:
        for r in stats_rows(pid):
            L = leads[r["lead_email"].lower()]
            n, sent = r["sequence_number"], ts(r["sent_time"])
            if sent:
                L["steps"].add(n)
                if n == 1 and (L["first_e1"] is None or sent < L["first_e1"]):
                    L["first_e1"] = sent
            rt = ts(r["reply_time"])
            if rt and (L["reply"] is None or rt < L["reply"][0]):
                L["reply"] = (rt, n)
            L["cats"].add(r["lead_category"])
            L["bounced"] |= bool(r["is_bounced"])
        for cid in children.get(pid, []):
            for r in stats_rows(cid):
                e = r["lead_email"].lower()
                if e in leads:
                    leads[e]["cats"].add(r["lead_category"])
    for L in leads.values():
        cats = {c for c in L["cats"] if c}
        pos = [c for c in cats if sentiment.get(c) == "positive"]
        L["booked"] = "Meeting Booked" in cats
        L["category"] = ("Meeting Booked" if L["booked"] else sorted(pos)[0] if pos
                         else sorted(cats)[0] if cats else None)
        L["positive"] = bool(pos)
    return leads


def summarize(leads, asof, first_from=None, first_to=None):
    sel = {e: L for e, L in leads.items() if L["first_e1"]}
    if first_from:
        lo = datetime.fromisoformat(first_from).replace(tzinfo=timezone.utc)
        sel = {e: L for e, L in sel.items() if L["first_e1"] >= lo}
    if first_to:
        hi = datetime.fromisoformat(first_to).replace(tzinfo=timezone.utc) + timedelta(days=1)
        sel = {e: L for e, L in sel.items() if L["first_e1"] < hi}
    week_ago = asof - timedelta(days=7)
    received, pos_step, cats_step = Counter(), Counter(), defaultdict(Counter)
    out = {"contacted": len(sel), "replied": 0, "actual_replies": 0, "positives": 0,
           "positives_excl_not_qualified": 0,
           "booked": 0, "new_e1_last_7d": 0, "last_e1": None, "positive_leads": []}
    for e, L in sel.items():
        for n in L["steps"]:
            received[n] += 1
        if L["first_e1"] > week_ago:
            out["new_e1_last_7d"] += 1
        if out["last_e1"] is None or L["first_e1"] > out["last_e1"]:
            out["last_e1"] = L["first_e1"]
        step = L["reply"][1] if L["reply"] else None
        if L["reply"]:
            out["replied"] += 1
            cats_step[step][L["category"] or "Uncategorized"] += 1
            if not L["bounced"] and L["category"] not in NOT_ACTUAL:
                out["actual_replies"] += 1
        if L["positive"]:
            out["positives"] += 1
            out["positives_excl_not_qualified"] += L["category"] != "Not Qualified"
            pos_step[step or "sub-only"] += 1
            out["positive_leads"].append({"email": e, "domain": e.split("@")[-1],
                                          "step": step, "category": L["category"]})
        if L["booked"]:
            out["booked"] += 1
    out["received_by_step"] = {str(k): received[k] for k in sorted(received)}
    out["positives_by_step"] = {str(k): v for k, v in sorted(pos_step.items(), key=str)}
    out["reply_categories_by_step"] = {str(k): dict(v) for k, v in sorted(cats_step.items(), key=str)}
    out["last_e1"] = out["last_e1"].date().isoformat() if out["last_e1"] else None
    c = out["contacted"] or 1
    out["rates"] = {k: round(100 * out[k] / c, 2) for k in ("actual_replies", "positives", "booked")}
    out["positive_share"] = round(100 * out["positives"] / out["actual_replies"], 1) if out["actual_replies"] else None
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", help="comma-separated experiment ids")
    ap.add_argument("--asof", help="YYYY-MM-DD, default now")
    a = ap.parse_args()
    cfg = json.load(open(CONFIG))
    asof = (datetime.fromisoformat(a.asof).replace(tzinfo=timezone.utc) + timedelta(days=1)
            if a.asof else datetime.now(timezone.utc))
    exps = [x for x in cfg["experiments"] if not a.only or x["id"] in a.only.split(",")]

    sentiment = {c["name"]: c["sentiment_type"] for c in get("/leads/fetch-categories")}
    camps = get("/campaigns", want=lambda d: isinstance(d, list) and d)
    by_id = {c["id"]: c for c in camps}
    children = defaultdict(list)
    for c in camps:
        if c.get("parent_campaign_id") and c["status"] != "DRAFTED":
            children[c["parent_campaign_id"]].append(c["id"])

    cache, result = {}, {"pulled_at": datetime.now(timezone.utc).isoformat(timespec="minutes"),
                         "experiments": [], "benchmarks": {}}

    def leads_for(ids):
        k = tuple(ids)
        if k not in cache:
            cache[k] = build_leads(ids, children, sentiment)
        return cache[k]

    for x in exps:
        arms = []
        for arm in x["arms"]:
            s = summarize(leads_for(arm["campaign_ids"]), asof)
            s.update(label=arm["label"], campaign_ids=arm["campaign_ids"],
                     status=[by_id.get(i, {}).get("status") for i in arm["campaign_ids"]],
                     progress_pct=round(100 * s["contacted"] / x["threshold"]))
            arms.append(s)
        result["experiments"].append({k: x[k] for k in ("id", "name", "tests", "status", "threshold", "benchmark")}
                                     | {"arms": arms, "focus_steps": x.get("focus_steps")})
    for key in {x["benchmark"] for x in exps}:
        b = cfg["benchmarks"][key]
        s = summarize(leads_for(b["campaign_ids"]), asof, b.get("first_e1_from"), b.get("first_e1_to"))
        result["benchmarks"][key] = s | {"label": b["label"], "why": b["why"]}

    json.dump(result, open(a.out, "w"), indent=1, default=str)
    for x in result["experiments"]:
        print(x["id"], x["name"])
        for s in x["arms"]:
            print(f"  {s['label']:<22} contacted {s['contacted']:>5} ({s['progress_pct']}%)  "
                  f"actual {s['actual_replies']:>3}  pos {s['positives']:>3} ({s['rates']['positives']}%)  "
                  f"booked {s['booked']}  new7d {s['new_e1_last_7d']}  lastE1 {s['last_e1']}  {s['status']}")
    for k, s in result["benchmarks"].items():
        print(f"BENCH {k:<18} contacted {s['contacted']:>5}  pos {s['positives']} ({s['rates']['positives']}%)  "
              f"booked {s['booked']} ({s['rates']['booked']}%)")
    print("wrote", a.out)


if __name__ == "__main__":
    main()
