"""Full pre-launch lead check: every lead in each Smartlead campaign vs Clay (read-only).

1. In the browser: `cb.dump(await cb.leadHashes({<campaignId>: <leadsTableId>, …}, <emailFieldId>, [<varFieldIds>]))`
   (var fields in the same order as --vars). The harness saves the output to a file.
2. python3 lead_check.py --clay-file <that file> --vars subject_line,email_one,email_two,email_three

Checks, per lead: present in Clay, in the right arm (campaign ↔ leads table), every variable equal
(SHA-256 of the trimmed text), no empty variable. Prints counts + the first problems. Exit 1 on any problem.
"""
import argparse, hashlib, sys
from sl import campaign_leads, read_dump

ap = argparse.ArgumentParser()
ap.add_argument("--clay-file", required=True)
ap.add_argument("--vars", default="subject_line,email_one,email_two,email_three")
a = ap.parse_args()
vars_ = a.vars.split(",")
h = lambda s: hashlib.sha256((s or "").strip().encode()).hexdigest()[:12]

raw = read_dump(a.clay_file)
clay = {}
for line in raw.strip().splitlines():
    cid, email, *hs = line.split(",")
    clay.setdefault(email, []).append((cid, hs))

stats = {"leads": 0, "ok": 0}
problems = {"not_in_clay": [], "wrong_arm": [], "mismatch": [], "empty_var": []}
for cid in sorted({c for v in clay.values() for c, _ in v}):
    for x in campaign_leads(cid):
        stats["leads"] += 1
        L = x["lead"]; e = L["email"].lower(); cf = L.get("custom_fields") or {}
        vals = [cf.get(k) for k in vars_]
        if any(not (v or "").strip() for v in vals):
            problems["empty_var"].append(f"{cid} {e}")
        rows = clay.get(e)
        if not rows:
            problems["not_in_clay"].append(f"{cid} {e}"); continue
        same = [hs for c, hs in rows if c == cid]
        if not same:
            problems["wrong_arm"].append(f"{e}: Smartlead {cid}, Clay {[c for c, _ in rows]}"); continue
        if [h(v) for v in vals] in same:
            stats["ok"] += 1
        else:
            problems["mismatch"].append(f"{cid} {e}")

print("checked", stats["leads"], "ok", stats["ok"], {k: len(v) for k, v in problems.items()})
for k, v in problems.items():
    for p in v[:10]:
        print(f"  {k}: {p}")
sys.exit(1 if any(problems.values()) else 0)
