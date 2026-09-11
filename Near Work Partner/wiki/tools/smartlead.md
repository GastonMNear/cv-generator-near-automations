---
type: tool
title: Smartlead — Reference
created: 2026-06-03
updated: 2026-09-01
tags: [tool, smartlead]
status: active
related: ["[[tools/clay]]", "[[context/outbound-engine]]", "[[tools/make]]"]
---

# Smartlead

Cold email sending + inbox/domain infrastructure. Gaston owns this end of the engine: inboxes, domains, campaign setup, sending capacity, deliverability/volume constraints. See [[context/outbound-engine]].

## Access

- Auth: API key (`SMARTLEAD_API_KEY` env var)
- Webhooks: Reply events can trigger downstream workflows
- API feeds reporting sync. As of July 2026, lead sync should use Paz's SmartLead batch-fetch action rather than Clay imports to BigQuery.

## Campaign Creation (agent skill)

The `smartlead-campaign-creator` skill creates new campaigns via API (sequences, schedule, settings, inboxes, ending manual "Send Lead to Justcall" step). Create-only — never edits existing campaigns. Verified API quirks (curl-only, `seq_variants`, `seq_type: MANUAL`, POST-vs-GET field names) live in the skill's `references/api-reference.md`. Creations are logged in `logs/smartlead-campaign-log.md`.

## Campaign Architecture

- **Baseline vs. Challenger** A/B split test, with **routing logic built in Clay**.
- US Open Jobs +50; US Open Jobs <50 (baseline + direct-booking variants).
- Replicating responsive campaigns onto new inbox sets (e.g. **Aniwa inboxes**) then re-positioning (those roles were on-site; Near's offer is usually remote).
- Fallback campaigns used so sending capacity isn't wasted when a test pauses.

## Reporting Sync Decision (July 2026)

Do **not** use Clay imports to BigQuery for lead sync anymore.

Current path:
- Paz's SmartLead batch-fetch action fetches leads directly from Smartlead.
- It uploads missing leads into the reporting system.
- It updates existing lead rows when Smartlead data changes.

Operational notes:
- Confirm the latest batch run before using BigQuery/reporting for leadership decisions.
- Monitor run time, error logs, missing-lead count, and changed-lead count.
- Add/verify `LeadSource` in the synced fields so reporting can compare contact quality by source: Clay vs AI researcher vs Apollo.
- Keep Smartlead campaign names aligned with the Outbound Metrics / Command Center names.

## Capacity & Cost

- Monitor sending volume vs. **max capacity**; decide whether to add inboxes/domains.
- Cost types are distinct — **inbox cost ≠ domain cost ≠ Smartlead sending cost ≠ Clay credits.** Roll up to cost per lead / per call booked.
- Don't expand capacity unless added volume reaches high-intent opportunities.

## Platform Analysis (alternatives)

- **Instantly** judged the strongest Smartlead alternative on **UX & variant management** — *not migrated.*
- Conclusion: **Clay layered on top of Smartlead** remains best for firmographic segmentation.

## Quirks / Notes

- **Expired API keys broke Make.com automations** — check key validity when scenarios silently fail. See [[tools/make]].
- QA rendered emails before launch: unfilled placeholders, grammar, spintax. See [[context/outreach-playbook]].
- Smartlead search can be imperfect for calls-booked attribution. Search by partial company name, lead name, and domain before marking attribution unresolved.
- Current known workflow gap: no-reply leads can enter Calling Sequences through Smartlead step/webhook logic; replied-then-ghosted leads need investigation for webhook or batch return to calling.

## Reporting API — verified endpoints (for automations)

Verified live 2026-07 while building the response-time KPI. Base `https://server.smartlead.ai/api/v1`, auth `?api_key=`. **curl only** — python-requests get a Cloudflare 403. Full, maintained reference lives in the `smartlead-weekly-response-kpi` skill (`.claude/skills/.../SKILL.md`, "Known API facts"); this is the quick pointer.

- **Rate limit: 200 requests/min** (account-wide). Throttle bulk scans (~175/min) with backoff.
- `GET /leads/fetch-categories` → categories with `sentiment_type` (`positive` / `negative` / null). Positive = Interested, Meeting Request, Information Request, Meeting Booked, Candidate sent - Follow Up, Send to Cold Call.
- `GET /campaigns/{id}/statistics?offset=&limit=` → per-email rows with `reply_time`, `lead_category`, `lead_email`, `sent_time`. Best way to find who replied + when, per campaign. `total_stats` can come back as a **string** (cast to int when paging).
- `GET /leads/?email=` → lead object incl. `id` (needed for message-history).
- `GET /campaigns/{id}/leads/{lead_id}/message-history` → `{history:[...]}`, each msg has `type` (`SENT`/`REPLY`), `time`, `email_seq_number`. **Manual Master-Inbox replies show as `type: SENT` with `email_seq_number: null`** — that's how we can measure our own reply times.
- **Categorization is live**: querying a past window later gives different counts as leads get re-categorized. For stable KPIs, measure on a fixed cadence and freeze the snapshot (we write it to a Google Sheet). See the KPI skill.
- Error responses come back as `{"message": "..."}` (e.g. `Invalid API Key` when a key rotates/expires — cf. [[tools/make]] key-expiry note).

## Booked-call attribution (same-week vs prev-week pipeline) — verified 2026-09-01

Built to answer "of the calls booked this week, how many came from emails sent this week vs.
contacts from earlier weeks". Rule: bucket on the lead's **first** reply — first reply inside the
booking week = that week's pipeline; first reply before it = a prior week's pipeline. Later replies
in an ongoing thread are irrelevant.

- **`GET /leads/?email=` also returns `lead_campaign_data[]`** — per campaign it carries
  `campaign_id`, `campaign_name`, `lead_category_id`, `last_reply_at`, `last_sent_at`,
  `campaign_lead_map_id`. **This is the cheap way to get a lead's category** — one request instead
  of paging a campaign's `/statistics`. The category lives on the **campaign↔lead mapping, not the
  lead**: the same lead is `101822` in one campaign and `null` in another.
- **`last_reply_at` is the LAST reply, not the first.** For first-reply attribution you must pull
  `/campaigns/{cid}/leads/{lid}/message-history` and take the earliest `type: REPLY`. Leads are
  routinely in 2 campaigns, so take the min across **all** campaigns in `lead_campaign_data`.
- **Category IDs** (from `/leads/fetch-categories`): `1` Interested, `2` Meeting Request,
  `3` Not Interested, `4` Do Not Contact, `5` Information Request, `6` Out Of Office,
  `7` Wrong Person, `8` Uncategorizable by Ai, `9` Sender Originated Bounce,
  `31756` Asked to Circle Back Later, `101821` Candidate sent - Follow Up,
  **`101822` Meeting Booked**, `127523` CV Sent - Opp Lost,
  `133363` Send to Cold Call (Lead went cold), `167092` Not Qualified.

### Finding who booked at a given company — scan categories, don't guess domains

Two routes were tried. **The statistics scan is the better one:**

- `GET /campaigns/{id}/statistics` over all non-DRAFTED campaigns, filtering
  `lead_category == "Meeting Booked"` → **139 campaigns scanned, 481 rows, 318 unique booked leads
  account-wide, ~7 min** at 8 workers / 170 req-per-min. Small enough to then match companies by eye.
- The `/leads/all` crawl (214,668 leads, 5.5 min) works for company→leads but needs the company's
  domain guessed up front, which is exactly what fails on ambiguous names.

**Why the scan wins:** it resolved the cases the domain crawl could not.
`Purpose` matched **6 unrelated companies** by name (purpose.app, teampurpose.com,
purpose-unlimited.com, purposebrands.com, …); the booked-lead list identified it as `purpose.app`
with no guessing. Only fall back to the domain crawl to find a company's *colleagues*.

> [!warning] **Don't strip the last dot-segment as a "TLD" when normalising domains.**
> A matcher that did this turned `grade.capital` into the stem `grade` and silently missed the
> GRADE CAPITAL booking. New gTLDs (`.capital`, `.app`, `.io`, `.ai`) are common in this book —
> match on the **full** domain. Cf. `norm_domain()` in the `booked-call-pause` skill, which
> correctly keeps the whole domain.

### Automated now — see the `booked-call-attribution` skill (added 2026-09-01)

The manual "Gaston pastes a company list" step is gone. HubSpot supplies the roster directly:
meetings created in the week with `hs_activity_type` present, whose associated **contact** carries
`meeting_source__standardized_ == "Email Outreach"`. Validated against the 74-row hand-built
baseline over 8 weeks — 5 weeks match exactly, and the filter independently found **3 bookings the
manual roster had missed** (Krece 08-03, which was the open question in the handoff, and Cash Margin
Partners twice). Full comparison in `.claude/skills/booked-call-attribution/references/regression.md`.

Two consequences for anything reading this section:

- **Because HubSpot hands over the booker's exact email, most bookings resolve with a single
  `/leads/?email=` call** — 8 of 12 in the 2026-08-24 week. The ~7-minute statistics scan is now a
  *fallback*, triggered only when something is left unresolved, rather than the first move.
- **Booking addresses can be helpdesk hosts.** Artic Grey books from
  `anthony.spallone@arcticgreyltd.zendesk.com` while the lead we emailed is
  `anthony.spallone@arcticgrey.com`. `zendesk.com`, `freshdesk.com`, `helpscout.net`, `intercom.io`
  and friends now sit in `JUNK_DOMAINS` next to LinkedIn and the free mailboxes — keying on one
  would join every company routing support through the same vendor.

Resolved end-to-end for the 2026-08-24 week: 12 bookings, **0 unresolved**, 7 same-week / 5 prev-week,
and every one of the six hand-verified first-reply timestamps reproduced to the minute.

### Company matching gotchas seen in this run

- **`company_name` is often a shortened brand**: `Sana` for Sana Benefits, `Grade` for GRADE
  CAPITAL, `HypeProxies` for Hype Proxies. Match on domain + name, never name alone.
- **Email domain ≠ company domain, legitimately.** The Blackout Coffee Co. booking is
  `john@howloo.com` with `company_url: blackoutcoffee.com`; the LinkedIn company and job post both
  confirm Blackout Coffee. Verify via `custom_fields.company_linkedin_url` / `job_url` before
  rejecting a mismatch (and cf. the cross-company guard in `booked-call-pause`).
- **Short/common company names generate heavy false positives** on substring matching: `usad`
  matched 25 leads (USADA, USA Diving, `adusasc.com`, `atticusadvantage.com`, …), `cactus` matched
  23 (Cactus Life Sciences / Materials / Wellhead / Inc). Always eyeball the matched name list
  before spending per-lead requests.

### The booking company is NOT always the lead's company — match on the person

The single hardest case in this run. The **USAD** booking came from `Yasha@usadistributions.com`,
which returns `{}` from `/leads/?email=` — that address is not in Smartlead at all. The same human is
in Smartlead as **`yasha@mercatodibellina.com`** ("Mercato Di Bellina", Founder,
`linkedin.com/in/yashasack/`), cold-emailed about an Amazon account-manager role at that company.
He booked under a *different* company he's involved with.

So when a company name and every plausible domain come up empty, **fall back to matching the
booker's name** against `lead_name` in the Meeting-Booked set, then confirm via
`linkedin_profile`. Founders with several ventures book under whichever entity is hiring.
Never conclude "not in Smartlead" from a domain miss alone.

(Cf. the milder version of this: Blackout Coffee's booker mails from `howloo.com`.)

### Long-nurture bookings are real — do not window the first-reply search

USAD first replied **2026-07-15**, went quiet for a month, re-engaged 08-17, and booked in the
08-24 week — a 6-week gap between first reply and booking. Any attribution query that only looks
back one or two weeks for the first reply will mis-bucket these as same-week. Search the lead's
**entire** message history, unbounded.

### Results — 8 weeks, 2026-07-06 → 2026-08-30 (measured 2026-09-01)

74 booked calls across 8 weeks: **42 same-week (57%), 32 prev-week (43%)**.

| Week (Mon–Sun) | Calls | Same wk | Prev wk | Same % |
|---|---|---|---|---|
| 07-06 → 07-12 | 10 | 5 | 5 | 50% |
| 07-13 → 07-19 | 5 | 2 | 3 | 40% |
| 07-20 → 07-26 | 12 | 8 | 4 | 67% |
| 07-27 → 08-02 | 10 | 4 | 6 | 40% |
| 08-03 → 08-09 | 5 | 4 | 1 | 80% |
| 08-10 → 08-16 | 7 | 6 | 1 | 86% |
| 08-17 → 08-23 | 12 | 6 | 6 | 50% |
| 08-24 → 08-30 | 13 | 7 | 6 | 54% |
| **Total** | **74** | **42** | **32** | **57%** |

Per-company detail is re-derivable; a CSV was handed to Gaston in-session.

> [!warning] **Weekly volume is 5–13 calls, so the weekly percentage is mostly noise.**
> The two highest same-week rates (80%, 86%) are the two **lowest-volume** weeks (5 and 7 calls) —
> one booking moves them 14–20 points. Read the 8-week pooled 57% as the real number and treat the
> weekly series as directional only. Do not report a single week's swing as a trend.

**A Mon/Tue-reply hypothesis was tested and refuted.** In the 08-24 week every same-week booking
first replied Mon or Tue, which suggested Wed–Fri replies always slip. Across all 8 weeks that is
false — same-week bookings first replied on every weekday, including Fri (Aventiqo 08-14, WebForce
07-24, Lindsey Self Storage 07-24) and Sat (Safeguard 07-11). Same-week conversion is not gated on
an early-week reply.

**Watch the weekend boundary — it decides real calls.** TheMCTTeam first replied **Sun 08-16 10:30**,
~14 h before its week opened; jmfbuilders **Sat 08-15 01:05**; Rex Developments **Sat 07-04**. A
Sunday-start week would move these to same-week. The Mon-00:00 ET cutoff is load-bearing, so state
it on any chart.

**Also expect off-hours first replies.** Maxim Group 05:03, AstroZon 02:42, AfterShip 06:23 ET —
overseas leads reply outside US hours. Nothing to fix; just don't treat them as data errors.

### Two more identity cases (both cracked by person, not company)

- **RISE Research** books as `yash@riseresearch.com` (HubSpot) but is `yash@riseglobaleducation.com`
  in Smartlead — same human, Yash Mundada. A colleague (`shreyans@riseglobaleducation.com`) is also
  tagged Meeting Booked, so domain-only matching returns two candidates and picks wrong 50% of the time.
- **Rex Developments** books as `design@rexarch.com`; Smartlead has `mahmad@rexmediausa.com`
  (`company_name: Rex`, `company_url: rexarch.com`, Mohadib Ahmad). HubSpot spells the surname
  *Bakali*, Smartlead *Ahmad* — first name + company domain is what ties them.

**When two leads at one company both carry the Meeting Booked tag, go to HubSpot for the tiebreak** —
`hs_createdate` on the booking says which one booked in the week you're measuring. Krece had two
genuine bookings 5 days apart (Samuel Gedaly 08-05, Jonathan Bentata 08-10) landing in *different*
weeks. Four of 49 companies in this run were ambiguous this way, so budget for it.

**A false positive to know about:** loose substring keys are dangerous on short names. `rex` matched
`cognitrex.com`, `rise` matched 10 unrelated HubSpot companies, `sana` matched 50+.
Require the key to match the **registrable domain or the full company name**, not any substring.

### Not every booked company is in Smartlead

**jmfbuilders** has no Smartlead lead at all — `info@jmfbuilders.com` and `mauricio@jmfbuilders.com`
both return `{}`, no booked lead matches "Mauricio Giron", and its HubSpot booking says
*"How did you hear about Near?: Email"* with no matching Smartlead record. Gaston supplied the reply
date (Sat 08-15 01:05) from his own inbox. So `Email` in the Chili Piper form does **not** imply a
Smartlead lead — some replies arrive on channels this pipeline can't see. Cf. the `booked-call-pause`
finding that 15 of 22 bookings in one window were genuinely absent from Smartlead.

**Escalation order when a company won't resolve** (do not skip ahead):
1. Smartlead Meeting-Booked set by domain, then by company-name variant.
2. Smartlead by **person name** → confirm on `linkedin_profile` (this is what cracked USAD).
3. HubSpot: company search → `/crm/v4/objects/companies/{id}/associations/contacts` → contact
   `email` → back to Smartlead. The booking form's own fields live in `hs_meeting_body` (HTML —
   strip tags) and carry First/Last Name, Company Name, Email, employee count and the role.
   **`hs_createdate` (when the booking was made) is the field this metric keys on** — confirmed by
   Gaston 2026-09-01. `hs_meeting_start_time` (when the call happens) is *not* used and often falls
   in a different week (jmfbuilders: booked 08-20, held 08-25 → counts in the 08-17 week). Whether
   the call was actually held is irrelevant: no filtering on attendance, no-shows or cancellations.
4. Only then ask Gaston.

## Per-lead pause API — verified 2026-08-20

Discovered while designing the booked-call auto-pause routine. Base `https://server.smartlead.ai/api/v1`, auth `?api_key=`.

- `POST /campaigns/{campaign_id}/leads/{lead_id}/pause` → `{"ok":true,"data":"success"}`. Sets that
  lead's per-campaign status to `PAUSED`. **Pauses one lead in one campaign — not the whole campaign.**
- `POST /campaigns/{campaign_id}/leads/{lead_id}/resume` → same shape, status returns to `INPROGRESS`.
  Verified the full round-trip live (INPROGRESS → PAUSED → INPROGRESS).
- `GET /leads/{lead_id}/campaigns` → `[{id, status, name}, ...]` — **the key endpoint.** Tells you every
  campaign a lead sits in plus each campaign's status, so you never have to crawl 70 active campaigns
  to find where a lead is running. Undocumented; not in the public docs.
- `GET /leads/?email=` → global lookup, returns the lead incl. `id`. **`email` is the ONLY accepted
  query param** — `company_url`, `company_name`, and a `/leads/search` route all 400. There is
  **no company-level lead search in the Smartlead API**; company→leads must be resolved from our own index.
- `GET /campaigns/{id}/leads?offset=&limit=` → `{total_leads, data:[{campaign_lead_map_id, status, lead:{...}}]}`.
  Per-lead `status` values seen: `INPROGRESS`, `PAUSED`, `COMPLETED`, `STOPPED`, `BLOCKED`.
  The nested `lead` carries `company_url` (bare domain) and `custom_fields.company_linkedin_url` —
  the two company keys usable for matching. Campaign sizes are large (12.5k leads in one), so
  full crawls are a batch job, never an inline webhook step.
- Account has ~145 campaigns, **70 ACTIVE** (2026-08-20) — a per-webhook full crawl is not viable.
- Domain density: in a 500-lead sample, **76% of leads shared a company domain with ≥1 sibling**
  (up to 8 leads per domain). Pausing only the booked lead's own email leaves most of the company
  still being emailed — the domain index is essential, not an optimisation.

### `GET /leads/all` — global bulk lead fetch (verified 2026-08-20)

The only way to get leads across the whole account. Undocumented; doesn't follow the other
`/leads/*` route patterns (which all fall through to a `leadId` param validator).

```
GET /leads/all?api_key=…&limit=1000&lastSeenLeadId={cursor}
→ {"ok":true,"data":{leads:[…], lastSeenLeadId, totalCount}}
```

- **Cursor pagination** via `lastSeenLeadId` — **camelCase**. `last_seen_lead_id`, `after`, `cursor`,
  `offset_id` all 400. `offset`/`page`/`page_size` are rejected ("not allowed").
- **`limit` max = 1000** here. ⚠️ **`/campaigns/{id}/leads` caps `limit` at 100** and 400s above that —
  the two endpoints have *different* caps. Exceeding it yields no usable rows, which is easy to
  misread as "no data" if the response isn't checked.
- Throughput ~1.0–1.2s per 1000 leads. **75,000 leads crawled in 79s**; full account (~205k) ≈ 3.5 min
  / ~205 requests. Contends with the 200 req/min account-wide limit — don't run alongside the
  weekly KPI job, and implement retry/resume on the cursor (one transient non-JSON
  response hit at 75k depth during parallel probing).
- **Fields (100% fill across a 6k sample):** `company_url`, `email_domain`, `linkedin_profile`,
  `company_name`. Richer than the per-campaign lead object — also has `seg_type`, `source`,
  `category_ids`, `email_campaign_leads_mappings_count`, `is_unsubscribed`.
  So domain / LinkedIn / email matching is all doable client-side from this one feed.

**Ordering — strictly newest-first by lead `id` desc.** `created_at` tracks it near-perfectly:
16 inversions per 20,000 leads (0.08%), largest backwards jump <1h. Depth→date is ~10k leads
per 10 days: 10k→2026-08-11, 30k→2026-07-15, 50k→2026-06-26, 70k→2026-06-11.

**But do NOT truncate the crawl by depth to save time.** Sequences run for weeks, so old leads are
still sending: in campaign 3570999, leads added **2026-06-30 are 94% still `INPROGRESS`**
(5% COMPLETED, 1% BLOCKED). Active-campaign membership does not decay with depth — 36/36 leads
sampled down to 60k deep were in an ACTIVE campaign. An 8k/10-day cutoff would miss most leads
still receiving email. If bounding the crawl, bound it **by `created_at` vs. the oldest active
campaign's start date** (~90 days), not by lead count.

### Send windows (all active campaigns, verified 2026-08-20)

All **70 ACTIVE** campaigns: `America/New_York`, **09:00–18:00**, Mon–Fri (one outlier 09:00–19:00),
`min_time_btwn_emails: 20`, `max_leads_per_day` 1000 (54 campaigns) / 2000 (14) / 1250 / 400.

Implication for any auto-pause automation: **pausing is only useful before or during 09:00–18:00 ET.**
A run after 18:00 can't prevent anything that day — it only cleans up retroactively. Schedule
pause runs at **09:00** (before the first send) and **13:30** (mid-window), not in the evening.

> [!important] **Two different windows — don't conflate them.**
> The `09:00–18:00` above is when **campaigns send email**, a per-campaign Smartlead setting.
> It is unrelated to the **response team's working hours**, which the reply-time KPI uses to
> compute business-hours-to-reply. Those are **09:00–18:00 ET** as of 2026-09-11 (history:
> 09:00–19:00 → 10:00–19:00 on 2026-08-27 → reverted to 09:00–18:00) and live in
> `OFFICE_OPEN`/`OFFICE_CLOSE` in the `smartlead-weekly-response-kpi` skill.
> The two windows now happen to share the same hours — that is a coincidence, not a link.
> Changing a send window must never be propagated into the KPI window, or vice versa.
> See [[wiki/tasks/done/2026-08-27-fix-reply-time-tracking-window]] and
> [[wiki/tasks/done/2026-09-11-revert-reply-time-window-to-9-18]].
