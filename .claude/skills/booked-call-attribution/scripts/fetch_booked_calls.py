#!/usr/bin/env python3
"""Step 1-2 — pull the week's calls booked in HubSpot and keep the Email Outreach ones.

A booking is a MEETING_EVENT. Three populations share that object type and only the
first is a booking:

  * Chili Piper bookings          -> have `hs_activity_type`.            COUNT THESE
  * Fathom recording summaries    -> titled "Fathom summary for …".      never count
  * calendar-synced copies, kickoffs, candidate interviews, re-engagement
    "sync" calls                  -> no `hs_activity_type`.              never count,
                                     but the interesting ones get flagged for review

`hs_activity_type HAS_PROPERTY` separates them cleanly. That filter is load-bearing:
without it the 2026-08-24 week goes from 65 bookings to 154 rows, and Purpose, Zaelab,
Nerife and HypeProxies each get counted twice because their calendar copy is a
separate object.

The source lives on the CONTACT (`meeting_source__standardized_`), not the meeting,
so every booking needs an association hop. Both hops are batched — 100 ids per call —
which is the difference between ~3 requests per week and ~130.

Do NOT read the source out of the meeting body instead. "How did you hear about
Near?" is free text the prospect typed: real Email Outreach bookings answered it with
"They outreached", "Cold reach out!", and "cold email from Franco Pereyra". The CRM
property is the only consistent signal.

Usage:
    python3 fetch_booked_calls.py                      # previous full Mon-Sun week
    python3 fetch_booked_calls.py 2026-08-24           # the week containing this date
    python3 fetch_booked_calls.py 2026-08-24 --out bookings.json
Env: HUBSPOT_ACCESS_TOKEN
"""
import argparse
import sys

from common import (SOURCE_PROP, TARGET_SOURCE, OWN_DOMAINS, dump_json, hubspot,
                    iso_utc, norm_domain, parse_body_fields, resolve_week,
                    usable_domain)

# Titles of meetings that are delivery, not a booking. Post-sale work shares the
# MEETING_EVENT type with real calls and there is no property that separates them —
# lifecycle stage does not (Sana Benefits, a genuine booking, is "customer" like the
# rest) and the deals are shared. The title is the only signal, and in this account
# it is regular:
#
#   Charlie Wilkins + Sajid // Account Manager   candidate interview
#   Maria + Gautam // BDR                        candidate interview
#   Vello + Near // Weekly Sync                  client sync
#   Kickoff call - Hire with Near + Erica F.     post-sale kickoff
#   Kick Off: Near & Vimerson                    post-sale kickoff
#
# What survives is the sales-conversation shape — "sync: Near & Cactus",
# "Follow-up | Near", "30 min with Chris" — which is exactly the set worth a look.
# This is a heuristic over free text, so it drops rows rather than counting them
# silently: every exclusion is named in the Slack message.
DELIVERY_MARKERS = ("//", "kickoff", "kick off", "kick-off", "qbr",
                    "book time with", "weekly sync", "interview")


def delivery_marker(title):
    low = (title or "").lower()
    return next((m for m in DELIVERY_MARKERS if m in low), None)


CONTACT_PROPS = ["email", "firstname", "lastname", "company", "website",
                 "jobtitle", "createdate", SOURCE_PROP]


def search_meetings(lo, hi, require_activity_type):
    """Every MEETING_EVENT created in the window. Paginates; HubSpot caps at 100."""
    filters = [
        {"propertyName": "hs_createdate", "operator": "GTE", "value": iso_utc(lo)},
        {"propertyName": "hs_createdate", "operator": "LT", "value": iso_utc(hi)},
    ]
    if require_activity_type:
        filters.append({"propertyName": "hs_activity_type",
                        "operator": "HAS_PROPERTY"})
    results, after = [], None
    while True:
        body = {
            "filterGroups": [{"filters": filters}],
            "sorts": [{"propertyName": "hs_createdate", "direction": "ASCENDING"}],
            "properties": ["hs_meeting_title", "hs_createdate", "hs_activity_type",
                           "hs_meeting_body", "hs_meeting_start_time",
                           "hs_object_source_detail_1"],
            "limit": 100,
        }
        if after:
            body["after"] = after
        res = hubspot("/crm/v3/objects/meetings/search", "POST", body)
        results += res.get("results") or []
        after = ((res.get("paging") or {}).get("next") or {}).get("after")
        if not after:
            break
    return results


def contacts_for(meetings):
    """(meeting_id -> [contact_id], contact_id -> properties), both batched."""
    if not meetings:
        return {}, {}
    m2c = {}
    ids = [m["id"] for m in meetings]
    for i in range(0, len(ids), 100):
        res = hubspot("/crm/v4/associations/meetings/contacts/batch/read", "POST",
                      {"inputs": [{"id": x} for x in ids[i:i + 100]]})
        for row in res.get("results") or []:
            m2c[row["from"]["id"]] = [str(t["toObjectId"]) for t in row.get("to") or []]
    cids = sorted({c for v in m2c.values() for c in v})
    cmap = {}
    for i in range(0, len(cids), 100):
        res = hubspot("/crm/v3/objects/contacts/batch/read", "POST",
                      {"properties": CONTACT_PROPS,
                       "inputs": [{"id": x} for x in cids[i:i + 100]]})
        for row in res.get("results") or []:
            cmap[row["id"]] = row.get("properties") or {}
    return m2c, cmap


def booking_domain(contact, body_fields):
    """Company domain, best available. The website beats the email domain because
    booking addresses are often generic (info@, hello@) or, as Artic Grey showed,
    a helpdesk host (anthony.spallone@arcticgreyltd.zendesk.com) that would key a
    whole unrelated support-desk population."""
    for candidate in (contact.get("website"),
                      body_fields.get("company website"),
                      contact.get("email")):
        d = usable_domain(candidate)
        if d:
            return d
    return ""


def to_row(meeting, contact, contact_id):
    props = meeting.get("properties") or {}
    fields = parse_body_fields(props.get("hs_meeting_body"))
    email = (contact.get("email") or fields.get("email") or "").strip().lower()
    name = " ".join(x for x in (contact.get("firstname"), contact.get("lastname")) if x)
    return {
        "meeting_id": meeting["id"],
        "contact_id": contact_id,
        "booked_at": props.get("hs_createdate"),
        "meeting_start": props.get("hs_meeting_start_time"),
        "meeting_title": props.get("hs_meeting_title") or "",
        "activity_type": props.get("hs_activity_type"),
        "source": contact.get(SOURCE_PROP) or "",
        "booker_name": name or fields.get("first name", ""),
        "booker_email": email,
        "company_name": (contact.get("company")
                         or fields.get("company name") or "").strip(),
        "company_domain": booking_domain(contact, fields),
        "job_title": contact.get("jobtitle") or fields.get("job title", ""),
        "employees": fields.get("number of employees", ""),
        "roles": fields.get("roles you're hiring for", ""),
    }


def prior_bookings(contact_id, before_iso):
    """Every Chili Piper booking this contact made BEFORE the window, oldest first.

    Two different questions lean on this and they want different answers, so it
    returns the rows rather than a single date:

      * Is a flagged non-booking meeting really a re-engagement sync? Cactus Audio's
        2026-08-24 "sync: Near & Cactus" is not a new call — the account first booked
        2025-12-12. Same shape for Astrozon and Greenwich Metals.
      * Is a *counted* booking actually a RETURNING lead re-booking? That is the
        GrowthScribe case, and it needs the gap and the prior outcome to judge.

    `hs_meeting_start_time` and `hs_meeting_outcome` matter as much as the booked
    date, because a reschedule looks identical to a return from the booked date
    alone — see `_reschedule_of`.
    """
    res = hubspot(f"/crm/v4/objects/contacts/{contact_id}/associations/meetings")
    ids = [str(r["toObjectId"]) for r in (res.get("results") or [])][:50]
    if not ids:
        return []
    out = hubspot("/crm/v3/objects/meetings/batch/read", "POST",
                  {"properties": ["hs_createdate", "hs_activity_type",
                                  "hs_meeting_start_time", "hs_meeting_outcome"],
                   "inputs": [{"id": i} for i in ids]})
    prior = [r["properties"] for r in (out.get("results") or [])
             if (r.get("properties") or {}).get("hs_activity_type")
             and r["properties"].get("hs_createdate", "") < before_iso]
    return sorted(prior, key=lambda p: p.get("hs_createdate", ""))


def earlier_booking(contact_id, before_iso):
    """Oldest prior Chili Piper booking date, or None. Thin wrapper kept because the
    flagged-row path only needs the one date."""
    prior = prior_bookings(contact_id, before_iso)
    return prior[0]["hs_createdate"] if prior else None


# A RESCHEDULE is not a return — it is the same call, moved. Two shapes occur and
# both must survive the returning-lead check:
#
#   Whitehorse Partners  books 08-18 21:37 and 08-18 21:40, both for 08-25 14:30
#                        -> identical start time, one booking recorded twice
#   Cash Margin Partners books 07-28 for 08-24 17:30 (outcome RESCHEDULED), then
#                        08-14 for 08-24 19:00
#                        -> different start TIME, same calendar DAY, and the prior
#                           booking is explicitly marked RESCHEDULED
#
# So a prior booking is discounted when it points at the same calendar day as the
# new one, or when HubSpot already labelled it RESCHEDULED. Comparing the full
# timestamp alone would have miscounted Cash Margin as a returning lead.
def _reschedule_of(prior, new_start):
    prior_start = prior.get("hs_meeting_start_time") or ""
    if prior_start and new_start and prior_start[:10] == new_start[:10]:
        return True
    return (prior.get("hs_meeting_outcome") or "").upper() == "RESCHEDULED"


def returning_lead(contact_id, booking):
    """Is this counted booking a RETURNING lead rather than a new one?

    The routine counts by booking date, so a lead who first came through outbound
    months ago and books again now — via a reply to an old thread, a referral, the
    website, whatever — lands in the week as if new sending produced it. Nothing new
    is created in HubSpot, so Command Center never shows it, and the week reads one
    call high. GrowthScribe (first booked 2026-06-05, booked again 2026-09-04) is the
    case that exposed it.

    The contact's own booking history is the signal: a PRIOR Chili Piper booking for
    a DIFFERENT slot means we have already spoken to (or had on the calendar) this
    account, so the new call is a return, not new pipeline.

    ONLY FIRST BOOKINGS COUNT. This is not a judgement call per row — a second
    booking is excluded even when it is a genuine new conversation with a real
    prior call behind it (Whitehorse Partners booked 08-18 for an 08-25 call, then
    again 09-08 for a separate 09-09 call; the 09-08 one does not count). The metric
    asks what NEW email outreach produced, and an account that has already been on
    our calendar cannot answer it whichever channel brought them back.

    Returns (reason, first_prior_date) or (None, None).
    """
    prior = prior_bookings(contact_id, booking["booked_at"])
    start = booking.get("meeting_start") or ""
    prior = [p for p in prior if not _reschedule_of(p, start)]
    if not prior:
        return None, None
    first = prior[0]
    when = (first.get("hs_createdate") or "")[:10]
    outcome = (first.get("hs_meeting_outcome") or "").upper()
    detail = f" ({outcome.lower()})" if outcome else ""
    return (f"returning lead — account already booked {when}{detail}; "
            f"not new email-outreach pipeline"), when


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("week", nargs="?", help="any date in the target week (YYYY-MM-DD)")
    ap.add_argument("--out", default="bookings.json")
    ap.add_argument("--no-review", action="store_true",
                    help="skip the review sweep (saves ~2 requests, loses the flags)")
    ap.add_argument("--no-repeat-check", action="store_true",
                    help="skip the returning-lead check (counts repeat bookings as "
                         "new pipeline — matches pre-2026-09 behaviour)")
    a = ap.parse_args()

    lo, hi = resolve_week([a.week] if a.week else [])
    label = f"{lo.date()} → {(hi.date())} (Mon 00:00 ET, exclusive end)"
    print(f"[hubspot] week {label}", file=sys.stderr)

    booked = search_meetings(lo, hi, require_activity_type=True)
    m2c, cmap = contacts_for(booked)

    # One row per booking. Keyed by contact so a calendar-synced duplicate of the
    # same booking collapses; two different people at one company stay two rows,
    # because HubSpot really did record two bookings.
    rows = {}
    for m in booked:
        for cid in m2c.get(m["id"], []):
            contact = cmap.get(cid, {})
            if (contact.get(SOURCE_PROP) or "") != TARGET_SOURCE:
                continue
            if norm_domain(contact.get("email")) in OWN_DOMAINS:
                continue
            row = to_row(m, contact, cid)
            row["counted"] = True
            row["flag_reason"] = ""
            if cid not in rows or row["booked_at"] < rows[cid]["booked_at"]:
                rows[cid] = row

    # Meetings with an Email Outreach contact that are NOT Chili Piper bookings.
    # These are carried as rows rather than dropped: Cactus Audio's real 08-24 call
    # is one ("sync: Near & Cactus"), and a company silently missing from the report
    # is worse than one Gaston deletes. They are marked so they stay out of the
    # headline until he adjudicates them.
    # A counted booking whose contact has booked before is a RETURNING lead, not new
    # email-outreach pipeline, and is excluded — only FIRST bookings count. It is
    # carried as a flagged row rather than dropped so it still appears in the sheet
    # and Slack with its reason: a silent drop is exactly as hard to notice as the
    # silent over-count it replaces. The row is not a question for Gaston, though —
    # the exclusion is the rule, and the row is there to show the rule firing.
    if not a.no_repeat_check:
        for cid, row in rows.items():
            reason, first = returning_lead(cid, row)
            if reason:
                row["counted"] = False
                row["flag_reason"] = reason
                row["returning_since"] = first

    flagged, dropped = (uncounted_candidates(lo, hi, rows) if not a.no_review
                        else ([], []))
    bookings = sorted(list(rows.values()) + flagged, key=lambda r: r["booked_at"])

    review = []
    if not a.no_review:
        review = build_review(lo, hi, booked, m2c, cmap, rows)

    payload = {
        "week_start": lo.date().isoformat(),
        "week_end": (hi.date()).isoformat(),
        "week_label": label,
        "meetings_scanned": len(booked),
        "bookings": bookings,
        "review": review,
        "dropped_delivery": dropped,
    }
    dump_json(a.out, payload)

    n_counted = sum(1 for b in bookings if b["counted"])
    print(f"[hubspot] {len(booked)} booking(s) in window; {n_counted} tagged "
          f"'{TARGET_SOURCE}'; {len(bookings) - n_counted} flagged", file=sys.stderr)
    for b in bookings:
        mark = "  " if b["counted"] else "? "
        print(f"  {mark}{b['booked_at'][:10]}  {b['company_name'][:26]:26} "
              f"{b['booker_email'][:34]:34} {b['flag_reason'][:60]}",
              file=sys.stderr)
    for d in dropped:
        print(f"  x {d['company_name'][:26]:26} dropped as delivery "
              f"({d['marker']}): {d['meeting_title'][:44]}", file=sys.stderr)
    if review:
        print(f"[hubspot] {len(review)} row(s) flagged for review", file=sys.stderr)
        for r in review:
            print(f"    ? {r['company_name'][:28]:28} {r['reason']}", file=sys.stderr)
    print(f"[hubspot] wrote {a.out}", file=sys.stderr)


def uncounted_candidates(lo, hi, counted):
    """Email Outreach meetings in the window that are not Chili Piper bookings.

    Three shapes turn up here and only Gaston can tell them apart reliably, because
    the discriminator is what the meeting actually was:

        sync: Near & Cactus                          -> a real sales call (count it)
        Kickoff call - Hire with Near + Erica F.     -> post-sale delivery
        Charlie Wilkins + Sajid // Account Manager   -> a candidate interview

    So all three are emitted with the meeting title and, where one exists, the date
    the account originally booked — the two facts that decide it — and left for him
    to keep or delete. A contact that already has a counted booking this week is
    skipped: those are calendar-synced duplicates of a booking we already have, and
    including them would double-count Purpose, Zaelab, Nerife and HypeProxies.
    """
    others = [m for m in search_meetings(lo, hi, require_activity_type=False)
              if not (m["properties"].get("hs_meeting_title") or "")
              .lower().startswith("fathom summary")
              and not m["properties"].get("hs_activity_type")]
    o2c, ocmap = contacts_for(others)
    out, dropped, seen = [], [], set()
    for m in others:
        for cid in o2c.get(m["id"], []):
            c = ocmap.get(cid, {})
            if (cid in counted or cid in seen
                    or (c.get(SOURCE_PROP) or "") != TARGET_SOURCE):
                continue
            seen.add(cid)
            row = to_row(m, c, cid)
            title = (row.get("meeting_title") or "untitled").strip()
            marker = delivery_marker(title)
            if marker:
                dropped.append({"company_name": row["company_name"],
                                "booker_email": row["booker_email"],
                                "meeting_title": title, "marker": marker})
                continue
            prior = earlier_booking(cid, m["properties"]["hs_createdate"])
            reason = f"not a Chili Piper booking ({title})"
            if prior:
                reason += f"; account first booked {prior[:10]}"
            row["counted"] = False
            row["flag_reason"] = reason
            out.append(row)
    return out, dropped


def build_review(lo, hi, booked, m2c, cmap, counted):
    """Bookings excluded for a reason Gaston might disagree with, reported but not
    written as rows: the contact carries NO source tag at all, so the exclusion is a
    CRM data gap rather than a decision. (A contact tagged 'Friend' or 'Google
    Search' IS a decision — From The Future is tagged 'Friend'; if that is wrong it
    is wrong in HubSpot.) A meeting whose other contact is tagged has already been
    classified, so it is not a gap."""
    out = []
    for m in booked:
        cids = m2c.get(m["id"], [])
        if any((cmap.get(x, {}).get(SOURCE_PROP) or "").strip() for x in cids):
            continue
        for cid in cids:
            if cid in counted:
                continue
            row = to_row(m, cmap.get(cid, {}), cid)
            row["reason"] = "no source tag in HubSpot — booking excluded by default"
            out.append(row)
    return out


if __name__ == "__main__":
    main()
