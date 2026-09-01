#!/usr/bin/env python3
"""Steps 4-7 — match each booking to its Smartlead lead, find that person's FIRST
reply ever, and bucket the booking as same-week or previous-week pipeline.

The question this answers: of the calls booked this week, how many came from emails
we sent this week, versus contacts who replied earlier and only booked now?

    first reply inside  the booked week  -> SAME  (new sending produced this)
    first reply before  the booked week  -> PREV  (harvested from the backlog)

Two rules decide almost every row, and both are easy to get subtly wrong:

  * ONLY THE FIRST REPLY COUNTS. `last_reply_at` on the lead object is the single
    most tempting wrong field here — it would mis-bucket Hype Proxies (last reply
    08-27, first 08-21) and USAD (last 08-26, first 07-15). Long ongoing threads are
    normal and must not drag an old lead into the current week.
  * THE SEARCH IS UNBOUNDED. USAD first replied 07-15 and booked in the 08-24 week,
    a six-week gap. Any "look back two weeks" shortcut silently reclassifies long
    nurtures as same-week.

A lead is routinely in two campaigns (20 of 49 in the reference batch), and their
first reply can sit in a campaign that does NOT hold the Meeting Booked tag — so the
minimum is taken across every campaign the lead appears in.

Usage:
    python3 attribute.py --bookings bookings.json --out attribution.json
    python3 attribute.py --bookings bookings.json --scan-mode always
Env: SMARTLEAD_API_KEY
"""
import argparse
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from common import (ET, dump_json, et_label, load_json, norm_name,
                    norm_person, parse_ts, smartlead, usable_domain)

HERE = os.path.dirname(os.path.abspath(__file__))


# --------------------------------------------------------------------------- #
# Lead lookup + first-reply measurement
# --------------------------------------------------------------------------- #
def lead_by_email(email):
    """`/leads/?email=` returns {} (HTTP 200) for an unknown address."""
    if not email:
        return None
    data = smartlead(f"/leads/?email={email}")
    return data if isinstance(data, dict) and data.get("id") else None


def first_reply(lead):
    """Earliest REPLY across every campaign this lead appears in.

    Manual replies sent from the Master Inbox come back as type SENT with a null
    email_seq_number, so filtering on type alone is correct — we want inbound only.
    """
    best, seen = None, []
    for entry in lead.get("lead_campaign_data") or []:
        cid = entry.get("campaign_id")
        if not cid:
            continue
        hist = smartlead(f"/campaigns/{cid}/leads/{lead['id']}/message-history")
        msgs = (hist or {}).get("history") or []
        replies = [parse_ts(m.get("time")) for m in msgs
                   if (m.get("type") or "").upper() == "REPLY"]
        replies = [r for r in replies if r]
        seen.append({"campaign_id": cid,
                     "campaign_name": entry.get("campaign_name") or "",
                     "category_id": entry.get("lead_category_id"),
                     "messages": len(msgs),
                     "first_reply": min(replies).isoformat() if replies else None})
        if replies and (best is None or min(replies) < best):
            best = min(replies)
    return best, seen


# --------------------------------------------------------------------------- #
# Resolution ladder — Smartlead first, HubSpot identity is already in the booking
# --------------------------------------------------------------------------- #
def build_index(booked_leads):
    by_email, by_domain, by_person = {}, {}, {}
    for L in booked_leads:
        e = L["email"]
        by_email[e] = L
        d = usable_domain(e)
        if d:
            by_domain.setdefault(d, []).append(L)
        p = norm_name(L.get("name"))
        if p:
            by_person.setdefault(p, []).append(L)
    return by_email, by_domain, by_person


def resolve(booking, index):
    """Return (email, how, note). Escalates cheapest-and-surest first.

    Never falls back to substring matching on a company name. Measured on this book,
    'usad' matches 25 leads, 'cactus' 23, 'sana' 93 — a loose match here produces a
    confident wrong answer, which is worse than an honest unresolved row.
    """
    by_email, by_domain, by_person = index
    email = booking.get("booker_email") or ""
    person = norm_person(*_split_name(booking.get("booker_name")))
    domain = booking.get("company_domain") or usable_domain(email)

    if email in by_email:
        return email, "booked-set:email", ""
    if email and lead_by_email(email):
        return email, "smartlead:email", "not in booked set (tag may have moved)"
    if domain and len(by_domain.get(domain, [])) == 1:
        L = by_domain[domain][0]
        return L["email"], "booked-set:domain", f"booking address was {email}"
    if person and len(by_person.get(person, [])) == 1:
        L = by_person[person][0]
        return L["email"], "booked-set:person", (
            f"name match; booking address {email} != Smartlead {L['email']}")
    if domain and len(by_domain.get(domain, [])) > 1:
        cands = by_domain[domain]
        hit = [L for L in cands if norm_name(L.get("name")) == person]
        if len(hit) == 1:
            return hit[0]["email"], "booked-set:domain+person", ""
        return "", "", (f"{len(cands)} booked leads at {domain}: "
                        + ", ".join(L["email"] for L in cands))
    return "", "", "no Smartlead lead found by email, domain, or person name"


def _split_name(full):
    parts = (full or "").split()
    return (parts[0] if parts else "", " ".join(parts[1:]) if len(parts) > 1 else "")


# --------------------------------------------------------------------------- #
def measure(booking, index, week_start):
    email, how, note = resolve(booking, index)
    row = dict(booking)
    row.update({"smartlead_email": email, "match": how, "match_note": note,
                "smartlead_name": "",
                "first_reply_utc": None, "first_reply_et": "", "bucket": "UNRESOLVED",
                "campaigns": [], "booked_tag": None})
    if not email:
        return row
    lead = lead_by_email(email)
    if not lead:
        row["match_note"] = (note + "; lookup returned empty").strip("; ")
        return row
    row["smartlead_lead_id"] = lead.get("id")
    row["smartlead_company"] = lead.get("company_name") or ""
    # Who we actually measured. When the match was by domain rather than by address
    # this can be a DIFFERENT PERSON at the same company — HubSpot says Awan Ali
    # booked for HypeProxies, but the lead we emailed and tagged is Gunnar Catlett.
    # Recording it keeps the report from silently pairing one person's name with
    # another person's email.
    row["smartlead_name"] = " ".join(
        x for x in (lead.get("first_name"), lead.get("last_name")) if x).strip()
    reply, campaigns = first_reply(lead)
    row["campaigns"] = campaigns
    # A resolved lead that has LOST the Meeting Booked tag is a signal the identity
    # match may be wrong — surfaced rather than acted on.
    row["booked_tag"] = any(c.get("category_id") for c in campaigns)
    if not reply:
        row["match_note"] = (note + "; no reply found in any campaign").strip("; ")
        return row
    row["first_reply_utc"] = reply.isoformat()
    row["first_reply_et"] = et_label(reply)
    row["bucket"] = "SAME" if reply.astimezone(ET) >= week_start else "PREV"
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bookings", default="bookings.json")
    ap.add_argument("--booked-leads", default="booked_leads.json")
    ap.add_argument("--out", default="attribution.json")
    ap.add_argument("--scan-mode", choices=["auto", "always", "never"], default="auto",
                    help="auto (default) runs the 7-min campaign scan only if a "
                         "direct email lookup left something unresolved")
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()

    data = load_json(a.bookings)
    bookings = data["bookings"]
    y, m, d = (int(x) for x in data["week_start"].split("-"))
    week_start = datetime(y, m, d, tzinfo=ET)

    booked_leads = []
    if a.scan_mode != "never":
        need_scan = a.scan_mode == "always"
        if not need_scan:
            # Cheap probe: can every booking address be looked up directly? In the
            # reference week 8 of 12 could, so the scan usually still runs — but on a
            # clean week this skips ~1,400 requests and ~7 minutes for nothing lost.
            with ThreadPoolExecutor(max_workers=a.workers) as pool:
                hits = list(pool.map(lambda b: bool(lead_by_email(b["booker_email"])),
                                     bookings))
            need_scan = not all(hits)
            print(f"[attribute] direct email lookup resolved {sum(hits)}/{len(hits)}",
                  file=sys.stderr)
        if need_scan:
            if not os.path.exists(a.booked_leads):
                print("[attribute] running the booked-lead scan (~7 min)…",
                      file=sys.stderr)
                subprocess.run([sys.executable,
                                os.path.join(HERE, "scan_booked_leads.py"),
                                "--out", a.booked_leads], check=True)
            booked_leads = load_json(a.booked_leads)["leads"]
        else:
            print("[attribute] every booking resolved directly — scan skipped",
                  file=sys.stderr)
    elif os.path.exists(a.booked_leads):
        booked_leads = load_json(a.booked_leads)["leads"]

    index = build_index(booked_leads)
    print(f"[attribute] measuring {len(bookings)} booking(s) against "
          f"{len(booked_leads)} booked lead(s)…", file=sys.stderr)

    rows = [None] * len(bookings)
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        futs = {pool.submit(measure, b, index, week_start): i
                for i, b in enumerate(bookings)}
        for f in as_completed(futs):
            rows[futs[f]] = f.result()

    # Flagged rows ride along so nothing is silently missing from the sheet, but
    # they stay out of the headline until Gaston adjudicates them — a kickoff call
    # or a candidate interview is not a booking, and counting one would inflate the
    # metric in exactly the direction that looks like good news.
    counted = [r for r in rows if r.get("counted", True)]
    flagged = [r for r in rows if not r.get("counted", True)]
    same = [r for r in counted if r["bucket"] == "SAME"]
    prev = [r for r in counted if r["bucket"] == "PREV"]
    unres = [r for r in counted if r["bucket"] == "UNRESOLVED"]
    attributed = len(same) + len(prev)
    summary = {
        "week_start": data["week_start"], "week_end": data["week_end"],
        "week_label": data["week_label"],
        "total_booked": len(counted), "same_week": len(same),
        "prev_week": len(prev), "unresolved": len(unres),
        "flagged": len(flagged),
        "companies": len({(r.get("company_domain") or r.get("company_name") or "")
                          .lower() for r in counted}),
        # Percentages are of what we could attribute, not of the raw total — an
        # unresolved row is missing information, not evidence of an old lead.
        "same_pct": round(100 * len(same) / attributed, 1) if attributed else None,
        "prev_pct": round(100 * len(prev) / attributed, 1) if attributed else None,
    }
    dump_json(a.out, {"summary": summary, "rows": rows,
                      "review": data.get("review", []),
                      "dropped_delivery": data.get("dropped_delivery", [])})

    print(f"\n[attribute] {data['week_label']}", file=sys.stderr)
    print(f"[attribute] booked {summary['total_booked']}  "
          f"SAME {summary['same_week']}  PREV {summary['prev_week']}  "
          f"unresolved {summary['unresolved']}  flagged {summary['flagged']}",
          file=sys.stderr)
    for r in sorted(rows, key=lambda x: (x["bucket"], x["booked_at"])):
        tag = r["bucket"] if r.get("counted", True) else "flag:" + r["bucket"][:4]
        print(f"    {tag:10} {(r['company_name'] or '?')[:26]:26} "
              f"{(r['smartlead_email'] or r['booker_email'])[:36]:36} "
              f"first_reply={r['first_reply_et'] or '-':22} {r['match']}",
              file=sys.stderr)
    print(f"[attribute] wrote {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
