#!/usr/bin/env python3
"""Roll the duplicated volume session deck forward to this session. It edits text only, on
these slides: intro date, both to-do slides, Headlines, KPI scorecard, Email overview,
email capacity and Issues to discuss.

    python3 update_deck.py --deck <new deck id> --metrics metrics.json            # dry run
    python3 update_deck.py --deck <new deck id> --metrics metrics.json --apply    # write

metrics.json = fetch_metrics.py output (both weeks), plus "dashboard" added by the agent
(schema in SKILL.md). The dry run prints every change as old -> new.

The session is bi-weekly, so the last deck's "last week" is not this deck's "previous
week". Both week columns are written from metrics.json; nothing is shifted over.

Elements are found by objectId. Drive copies keep IDs, so they carry from week to week.
If a slide was rebuilt by hand, the preflight stops with the missing ID instead of
guessing which box to write into.

A second run would copy the already-cleared to-dos onto slide 2 and empty Headlines and
Issues again. To prevent that, the run refuses if slide 4 already shows the target week
(override with --force).
"""
import argparse
import json
import os
import re
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from slides_lib import (batch, cell_text, clear_shape, get_presentation, index,
                        set_cell, set_shape, shape_text, token)

ID = {
    "date": "p1_i18",
    "todo_last": "g3fb501e6008_1_0",      # slide 2 table
    "todo_this": "g3f011bbda02_2_3",      # slide 15 table
    "booked_label": "p4_i59", "booked_total": "p4_i60", "booked_prior": "p4_i61",
    "mix_label": "p4_i67", "mix": "p4_i68",
    "qual_rate": "p4_i72",
    "weekly_metrics": "g3f6c51d60cb_0_1",
    "value_table": "g3fb501e6008_1_10",
    "email_overview": "g3f3a4fe1476_0_4",
    "cap_title": "g3f74d375066_0_4", "cap_caption": "g3f74d375066_0_5",
    "cap_bar": ["g3f74d375066_0_6", "g3f74d375066_0_7", "g3f74d375066_0_8"],
    "cap_lbl_oj": "g3f74d375066_0_9", "cap_lbl_other": "g3f74d375066_0_10",
    "cap_lbl_unused": "capacity_unused_label_0914",
    "cap_table": "g3f74d375066_0_14",
}
CLEAR_SLIDES = ["Headlines", "Issues to discuss"]  # clear every body text box on these
FOOTER = "Near Outbound · Weekly Huddle"
CHANNELS = ["email", "linkedin", "cold_calling"]  # deck order: Email | LinkedIn | Cold Calling
VALUE_ROWS = {"Email": "email", "LinkedIn": "linkedin", "Cold Calling": "cold_calling"}

MON = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


# ---- formatting (matches how the deck has always written numbers) ----------

def week_label(s, e):  # "Oct 5–11" / "Sep 28–Oct 4"
    if s.month == e.month:
        return f"{MON[s.month-1]} {s.day}–{e.day}"
    return f"{MON[s.month-1]} {s.day}–{MON[e.month-1]} {e.day}"


def k_lower(n):  # 17878 -> 17.9k, 19956 -> 20k
    return f"{n/1000:.1f}".rstrip("0").rstrip(".") + "k"


def k_upper(n):  # capacity table: 11312 -> 11.3K, 2254 -> 2.25K, 423 -> 423
    if n >= 10000:
        return f"{n/1000:.1f}".rstrip("0").rstrip(".") + "K"
    if n >= 1000:
        return f"{n/1000:.2f}".rstrip("0").rstrip(".") + "K"
    return str(n)


def pct1(s):  # "56.10%" -> "56.1%"
    return f"{float(str(s).rstrip('%')):.1f}%"


def minutes(hms):  # "0:08" -> "8 min"
    h, m = hms.split(":")[:2]
    return f"{int(h)*60 + int(m)} min"


# ---- slide sections -------------------------------------------------------

def plan(P, m, groups_cfg):
    E = index(P)
    missing = [i for v in ID.values() for i in (v if isinstance(v, list) else [v]) if i not in E]
    if missing:
        sys.exit(f"Preflight: these elements are gone from the deck (slide rebuilt?): {missing}")
    R, log, warn = [], [], list(m.get("warnings", []))

    def shape(key, new, el=None):
        el = el or E[ID[key]]
        old = shape_text(el)
        if old != new:
            log.append((key, old, new)); R.extend(set_shape(el, new))

    def cell(tkey, r, c, new, style_from=None):
        el = E[ID[tkey]]
        old = cell_text(el, r, c)
        if old != new or style_from:
            if old != new:
                log.append((f"{tkey}[{r},{c}]", old, new))
            R.extend(set_cell(el, r, c, new, style_from))

    def label(w):
        return week_label(date.fromisoformat(w["week"]["start"]), date.fromisoformat(w["week"]["end"]))

    p = m["prev"]
    wk, wk_prev = label(m), label(p)
    b = m["booked"]
    if E[ID["booked_label"]] and wk.upper() in shape_text(E[ID["booked_label"]]) and not m.get("_force"):
        sys.exit(f"Slide 4 already shows {wk.upper()}: this deck looks updated. Use --force to re-run.")

    # Slide 1: session date
    sd = date.fromisoformat(m["session_date"])
    shape("date", f"{sd.strftime('%B')} {sd.day}, {sd.year}")

    # Slides 2 + 15: last session's "To-dos for this week" become this week's "from last week", verbatim
    src, dst = E[ID["todo_this"]], E[ID["todo_last"]]
    n_src, n_dst = src["table"]["rows"], dst["table"]["rows"]
    todos = [[cell_text(src, r, c) for c in range(4)] for r in range(1, n_src)]
    while todos and not any(todos[-1]):
        todos.pop()  # trailing blank rows on slide 15
    pre = []
    if len(todos) > n_dst - 1:
        pre.append({"insertTableRows": {"tableObjectId": dst["objectId"], "cellLocation": {"rowIndex": n_dst - 1},
                                        "insertBelow": True, "number": len(todos) - (n_dst - 1)}})
        warn.append(f"Slide 2: added {len(todos) - (n_dst - 1)} table row(s) to fit {len(todos)} to-dos")
    todo_plan = (todos, src)

    # Slides 3 + 14: empty every body text box (keep the boxes)
    for s_ in P["slides"]:
        texts = [shape_text(x) for x in s_.get("pageElements", []) if "shape" in x]
        title = next((t for t in texts if t in CLEAR_SLIDES), None)
        if not title:
            continue
        for x in s_["pageElements"]:
            if "shape" not in x:
                continue
            t = shape_text(x)
            if t and t != title and t != FOOTER and not t.isdigit():
                log.append((f"clear '{title}'", t[:60] + "…", "")); R.extend(clear_shape(x))

    # Slide 4: KPI scorecard
    prior = sum(p["booked"][ch] for ch in CHANNELS)
    total = sum(b[ch] for ch in CHANNELS)
    shape("booked_label", f"BOOKED CALLS · {wk.upper()}")
    shape("booked_total", str(total))
    shape("booked_prior", re.sub(r"Prior week: \S+", f"Prior week: {prior}", shape_text(E[ID["booked_prior"]])))
    shape("mix_label", f"BOOKED CALL MIX · {wk.upper()}")
    shape("mix", f"{b['email']}  |  {b['linkedin']} |  {b['cold_calling']}")
    q = m["dashboard"]["qualified_rate"]
    shape("qual_rate", " | ".join(q[ch] for ch in CHANNELS))

    wm = E[ID["weekly_metrics"]]
    def wm_values(w):
        dials = w["cold_calling"]["dials"]
        return {"Email sent": k_lower(w["email"]["sent"]), "Email positive replies": str(w["email"]["positive"]),
                "Email calls booked": str(w["booked"]["email"]), "Cold Calling dials": f"{dials:,}" if dials else "",
                "Cold Calling booked calls": str(w["booked"]["cold_calling"])}
    new_prev, new_last = wm_values(p), wm_values(m)
    for r in range(1, wm["table"]["rows"]):
        lbl = cell_text(wm, r, 0)
        if lbl not in new_last:
            sys.exit(f"Weekly metrics table has an unknown row '{lbl}'")
        cell("weekly_metrics", r, 1, new_prev[lbl], style_from=(r, 3))
        cell("weekly_metrics", r, 2, new_last[lbl], style_from=(r, 3))

    vt = E[ID["value_table"]]
    quarters = m["dashboard"]["quarters"]
    seen = set()
    for c in range(1, vt["table"]["columns"]):
        hdr = cell_text(vt, 0, c)
        mq = re.match(r"(Q\d) (cost|90-day)", hdr)
        if not mq:
            sys.exit(f"Value table: can't read header '{hdr}'")
        qn, kind = mq.group(1), ("cpqc" if mq.group(2) == "cost" else "v90")
        seen.add(qn)
        for r in range(1, vt["table"]["rows"]):
            ch = VALUE_ROWS[cell_text(vt, r, 0)]
            cell("value_table", r, c, quarters[qn][ch][kind], style_from=(r, 1))
    extra = sorted(set(quarters) - seen)
    if extra:
        warn.append(f"Dashboard has {extra} but the value table doesn't: ask Gaston before adding columns")

    # Slide 9: email overview. Both week columns from the sheets
    eo = E[ID["email_overview"]]

    def eo_values(w, wlabel):
        rs = w["reply_speed"]
        return {"Metric": wlabel, "Emails sent": k_lower(w["email"]["sent"]), "Reply rate": w["email"]["reply_rate"],
                "Positive replies": str(w["email"]["positive"]), "Calls booked": str(w["booked"]["email"]),
                "Median reply time": minutes(rs["median"]) if rs else "",
                "Reply speed": f"{pct1(rs['lt10'])} <10m\n{pct1(rs['lt5'])} <5m" if rs else ""}
    new9_prev, new9 = eo_values(p, wk_prev), eo_values(m, wk)
    for r in range(eo["table"]["rows"]):
        lbl = cell_text(eo, r, 0)
        cell("email_overview", r, 1, new9_prev[lbl], style_from=(r, 3))
        cell("email_overview", r, 2, new9[lbl], style_from=(r, 3))

    # Slide 12: email capacity
    cfg = groups_cfg
    def norm(n):  # the sheet and the map don't always agree on spacing ("[EXP012]  US…")
        return " ".join(n.split())
    name_to_group = {norm(n): g for g, names in cfg["groups"].items() for n in names}
    unknown = [c_ for c_ in m["campaigns"] if norm(c_["name"]) not in name_to_group]
    if unknown:
        sys.exit("Campaigns with sends but no group (ask Gaston, then add them to "
                 f"references/campaign-groups.json): {unknown}")
    sent, cap = m["email"]["sent"], m["email"]["capacity"]
    gsum = {g: 0 for g in cfg["groups"]}
    for c_ in m["campaigns"]:
        gsum[name_to_group[norm(c_["name"])]] += c_["sent"]
    gsum[cfg["unassigned_to"]] += m["unassigned_sends"]
    shape("cap_title", f"{wk.replace('–', ' – ')} · {k_lower(cap)} capacity · {k_lower(sent)} sent · "
                       f"{k_lower(cap - sent)} unused")
    shape("cap_caption", "")
    ct = E[ID["cap_table"]]
    rows = {cell_text(ct, r, 0) for r in range(1, ct["table"]["rows"])}
    no_row = {g: n for g, n in gsum.items() if n and g not in rows}
    if no_row:
        sys.exit(f"Groups with sends but no row in the capacity table: {no_row}. Adding rows is a "
                 "design change: ask Gaston, add the rows on the slide, then re-run.")
    for r in range(1, ct["table"]["rows"]):
        g = cell_text(ct, r, 0)
        if g not in gsum:
            sys.exit(f"Capacity table row '{g}' is not a group in campaign-groups.json")
        cell("cap_table", r, 1, k_upper(gsum[g]), style_from=(r, 0))
        cell("cap_table", r, 2, f"{gsum[g] / sent * 100:.1f}%", style_from=(r, 0))
    other = gsum[cfg["other_group"]]
    oj, unused = sent - other, cap - sent
    shape("cap_lbl_oj", f"Open jobs\n{oj / cap * 100:.1f}%")
    shape("cap_lbl_other", f"Other {other / cap * 100:.1f}%")
    shape("cap_lbl_unused", f"Unused {unused / cap * 100:.1f}%")
    segs = [E[i] for i in ID["cap_bar"]]
    x0 = segs[0]["transform"]["translateX"]
    end = segs[2]["transform"]["translateX"] + segs[2]["size"]["width"]["magnitude"] * segs[2]["transform"]["scaleX"]
    x = x0
    for el, n in zip(segs, [oj, other, unused]):  # same span, colors, height: only the split moves
        w = (end - x0) * n / cap
        t = dict(el["transform"]); t["translateX"] = x; t["scaleX"] = w / el["size"]["width"]["magnitude"]
        R.append({"updatePageElementTransform": {"objectId": el["objectId"], "applyMode": "ABSOLUTE", "transform": t}})
        x += w
    log.append(("capacity bar", "", f"open jobs {oj/cap:.1%} · other {other/cap:.1%} · unused {unused/cap:.1%}"))
    log.append(("capacity groups", "", json.dumps(gsum)))
    return pre, R, todo_plan, log, warn


def todo_requests(P, todos, src_id, dst_id):
    E = index(P)
    src, dst = E[src_id], E[dst_id]
    R = []
    for r in range(1, dst["table"]["rows"]):
        row = todos[r - 1] if r - 1 < len(todos) else ["", "", "", ""]
        for c in range(4):
            R += set_cell(dst, r, c, row[c])
    for r in range(1, src["table"]["rows"]):
        for c in range(4):
            R += set_cell(src, r, c, "")
    return R


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deck", required=True)
    ap.add_argument("--metrics", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    m = json.load(open(a.metrics)); m["_force"] = a.force
    cfg = json.load(open(os.path.join(HERE, "..", "references", "campaign-groups.json")))
    tok = token()
    P = get_presentation(tok, a.deck)
    pre, R, (todos, src), log, warn = plan(P, m, cfg)
    for k, old, new in log:
        print(f"{k}: {old!r} -> {new!r}")
    print(f"slide 2 to-dos ({len(todos)}):", *[f"  - {t[0]} | {t[1]}" for t in todos], sep="\n")
    for w in warn:
        print("WARNING:", w)
    if not a.apply:
        print("\nDry run, nothing written. Re-run with --apply.")
        return
    if pre:
        batch(tok, a.deck, pre)
        P = get_presentation(tok, a.deck)
    batch(tok, a.deck, R + todo_requests(P, todos, ID["todo_this"], ID["todo_last"]))
    print("\nApplied.")


if __name__ == "__main__":
    main()
