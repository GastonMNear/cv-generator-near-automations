---
name: booked-call-attribution
description: >
  Weekly report answering "of the calls booked this week, how many came from emails we
  sent this week versus contacts who replied in an earlier week and only booked now?"
  Pulls the week's booked calls from HubSpot, keeps only the ones whose source is
  'Email Outreach', matches each booker to their Smartlead lead, finds that person's
  FIRST reply ever, buckets them same-week vs previous-week pipeline, appends the
  detail to the Outbound metrics Google Sheet and posts a headline to Slack. Use this
  whenever asked about booked-call attribution, same-week vs previous-week pipeline,
  "where did this week's calls come from", whether new sending or the reply backlog is
  driving bookings, the weekly booked-calls report, or when run as a scheduled Claude
  routine. Also use it to backfill or re-run any single past week.
---

# Booked-Call Pipeline Attribution

Gaston reports this weekly. The business question underneath it is whether **new
sending drives bookings, or whether we are harvesting an ageing backlog of warm
replies** — two very different stories about the health of outbound, and they look
identical if you only count calls booked.

## The rule

For each call booked in the target week, find the person who booked, then find **the
first time that person ever replied to us**:

| First reply | Bucket | Reads as |
|---|---|---|
| inside the target week | `SAME` | new sending produced this call |
| before the target week | `PREV` | replied earlier, booked now |

There is no "two weeks ago" bucket — anything before the week start is one bucket.

Three details decide real rows, so they are worth stating rather than assuming:

- **Weeks start Monday 00:00 America/New_York.** Three of the 74 rows in the
  regression baseline first replied on a weekend inside those 14 hours before their
  week opened (TheMCTTeam Sun 08-16 10:30, jmfbuilders Sat 08-15 01:05, Rex Sat
  07-04). A Sunday-start week moves all three.
- **API timestamps are UTC; convert to ET before comparing.** Artic Grey replied
  2026-08-25 00:09 UTC = **Aug 24 20:09 ET** — a different calendar day. Getting
  this backwards flips rows.
- **A call belongs to the week it was *booked*, not the week it happens.**
  `hs_createdate` on the meeting, never `hs_meeting_start_time`. jmfbuilders booked
  08-20 for a call held 08-25 and counts in the 08-17 week. Whether the call was
  actually held is irrelevant here — no filtering on outcome, no-shows, or
  cancellations. Both halves of this metric are reply/booking events; nothing
  downstream of the booking matters.

Off-hours first replies are normal and must not be "corrected" — several leads are
overseas (Maxim Group 05:03, AstroZon 02:42, AfterShip 06:23 ET).

## Pipeline

```
1. fetch_booked_calls.py   HubSpot: week's bookings, Email Outreach only   ~5 requests, 4 s
2. attribute.py            direct /leads/?email= probe for every booker     ~12 requests, 10 s
     └─ scan_booked_leads.py   only if something didn't resolve            ~1,400 requests, ~7 min
3. attribute.py (cont.)    first reply per lead -> SAME / PREV             ~3 requests per lead
4. write_to_sheet.py       append the per-call detail + weekly summary
5. post_to_slack.py        headline + link to the sheet
```

`run.sh` chains all of it and is what a routine should call.

### Why the scan is conditional

The Smartlead campaign-statistics scan is the dominant cost and it is **flat** — the
same ~7 minutes whether you are attributing 5 bookings or 50. Its job is *identity
resolution*: when the address HubSpot recorded is not the address we emailed, the
only way back to the lead is to search a population, and the ~318 people currently
tagged `Meeting Booked` is a far less ambiguous population than all ~215k leads.

But HubSpot hands us the booker's exact email, so most bookings resolve with a single
`/leads/?email=` call. `attribute.py` therefore probes directly first and runs the
scan only if something is left over (8 of 12 resolved directly in the reference
week — so it usually still runs, but a clean week costs seconds instead of minutes).
Force it either way with `--scan-mode always|never`.

## Usage

```bash
./scripts/run.sh                    # previous full Mon-Sun week, posts to Slack
./scripts/run.sh 2026-08-24         # the week containing that date (backfill)
./scripts/run.sh --dry-run          # compute everything, print the Slack message, post nothing
```

Individual steps, if you need to inspect something mid-pipeline:

```bash
python3 scripts/fetch_booked_calls.py 2026-08-24 --out bookings.json
python3 scripts/attribute.py --bookings bookings.json --out attribution.json
python3 scripts/post_to_slack.py --attribution attribution.json --dry-run
```

## What lands where

**Slack** (`#outbound auto-pause reports`, `C0BRJAFNUG5`) gets the headline only:
totals, the same/prev split with counts *and* percentage, unresolved rows, the review
flags, and a link to the sheet. Per-lead detail deliberately stays in the sheet,
where it can be sorted and kept.

**Google Sheets** gets one row per booked call in tab
`Email Lead-Conversion-Timing-Analysis`, each week's block ending in a `Totals`
row of live formulas that recalculate as rows are adjudicated, blocks separated by a blank row with an `x` on
each block's first row. Columns are resolved **by header name**, so the tab can be
reordered without touching the code. Use `--replace` to correct a week already
written. See `references/sheet-layout.md`.

### Two things the report always says out loud

**Percentages are of what could be attributed**, not of the raw total. An unresolved
booking is missing information, not evidence of an old lead, so it never silently
lands in a bucket.

**At 5-13 calls a week the percentage is mostly noise.** In the eight-week baseline
the two best-looking weeks (80%, 86%) were the two smallest (5 and 7 calls) — one
booking moves them 14-20 points. Lead with pooled multi-week figures; treat the
weekly series as directional. If you build a chart, encode call volume in bar length
so a thin bar cannot be misread as a strong week, and state the Mon-00:00-ET
boundary on it.

## Filtering to Email Outreach

The source lives on the **contact**, in `meeting_source__standardized_`. Match it
**exactly** to `Email Outreach`. The live vocabulary is wider than the property's
declared enum options (Email Outreach, LinkedIn Outreach, Google Search, Google Ad,
LLM, Friend, Girdley, Atlas, Deel…), so enumerating the others will go stale.

**Do not read the source from the meeting body instead.** "How did you hear about
Near?" is free text the prospect typed; real Email Outreach bookings answered it
with "They outreached", "Cold reach out!", and "cold email from Franco Pereyra". The
CRM property is the only consistent signal.

## Edge policy — nothing is skipped, but only real bookings are counted

**A company must never silently vanish from the sheet.** A missing row reads as "we
booked 12 calls" when the truth was 13, and there is no way to notice it from the
report. So every Email Outreach meeting in the week is written as a row; the ones
that are not confirmed bookings are marked and held out of the headline.

**Counted** — contact tagged exactly `Email Outreach`, meeting is a real Chili Piper
booking (`hs_activity_type` present). These get `SAME` / `PREV` / `UNRESOLVED` and
drive the percentages.

**Dropped as delivery** — a non-booking meeting whose title marks it as post-sale
work. No property separates these from a real call: lifecycle stage does not (Sana
Benefits, a genuine booking, is `customer` like the rest) and the deals are shared.
The title is the only signal, and in this account it is regular:

| Title | What it is |
|---|---|
| `Charlie Wilkins + Sajid // Account Manager` | candidate interview |
| `Vello + Near // Weekly Sync` | client sync |
| `Kickoff call - Hire with Near + Erica Ferreira` | post-sale kickoff |

`DELIVERY_MARKERS` in `fetch_booked_calls.py` holds the patterns. Because this is a
heuristic over free text it **drops** rather than silently counting, and every
exclusion is named in Slack so a wrong drop is visible.

**Written but flagged `REVIEW – …`** — what survives that filter: an `Email Outreach`
contact with a non-booking meeting in the sales-conversation shape (`sync: Near &
Cactus`, `Follow-up | Near`, `30 min with Chris`) and no counted booking that week.
Each carries the meeting title and, where one exists, the date the account
*originally* booked. Gaston keeps or deletes. Contacts who already have a counted
booking that week are excluded — those are calendar-synced duplicates, and including
them would double-count Purpose, Zaelab, Nerife and HypeProxies.

**Reported but not written** — a booking whose contact has *no source tag at all*.
That exclusion is a CRM data gap rather than a decision, so it goes in Slack only. A
contact tagged `Friend` or `Google Search` **is** a decision and is simply excluded:
From The Future is tagged `Friend`; if that is wrong, it is wrong in HubSpot.

**`UNRESOLVED` is not a skip.** A counted booking with no Smartlead match still gets
its row, with the reply columns left blank to fill in by hand. Cactus Audio is the
standing example — `adam@cactusaudio.com` returns `{}` from `/leads/?email=`, so it
is genuinely absent from Smartlead, not a matching failure.

## Secrets

| Var | For | Status |
|---|---|---|
| `HUBSPOT_ACCESS_TOKEN` | the bookings (private-app token, `pat-na1-…`) | in repo `.env` |
| `SMARTLEAD_API_KEY` | lead lookup + message history | in repo `.env` |
| `SLACK_BOT_TOKEN` | `chat.postMessage` (bot `email_kpi_bot`) | in repo `.env` |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` / `GOOGLE_REFRESH_TOKEN` | the Sheets write (the `drive` scope on this token covers Sheets) | in repo `.env` |
| `BOOKED_ATTRIBUTION_SLACK_CHANNEL_ID` | *optional* override | defaults to `C0BRJAFNUG5` |

`.env` contains a value with an unescaped `$3`, so any shell wrapper must **not** use
`set -u` when sourcing it or it aborts.

## Cloud routine (live)

| | |
|---|---|
| Name | Booked-Call Attribution (weekly, Mon 10:34 ET) |
| ID | `trig_01SvtFNc2CUF47VFGwPsUy7T` |
| Cron | `34 14 * * 1` (UTC) = **Mon 10:34 ET** |
| Environment | `env_01DVzad9AipkSb49SRKPteVL` — "Slack Bot + SL + Drive + HS" |
| Repo | `GastonMNear/cv-generator-near-automations` (main) |
| Model | `claude-sonnet-5` |
| Tools | `Bash`, `Read`, `Grep`, `Glob` |

https://claude.ai/code/routines/trig_01SvtFNc2CUF47VFGwPsUy7T

The prompt runs `run.sh` with **no date argument** — that targets the previous full
Mon–Sun week, which is what a Monday run wants. It also tells the run to let the
~8-minute Smartlead scan finish rather than retry it, and to report rather than work
around the "week already in the sheet" guard.

Note the Response-Time KPI routines run from a **different repo**
(`GastonMNear/smartlead-weekly-response-kpi`), which is why that skill is not tracked
here. This skill and the auto-pause skill both live in this repo.

## Running it as a routine

Weekly, **Monday morning ET**. Point the routine at this skill with a minimal prompt
(`run the booked-call-attribution skill for the previous week`) and keep the logic
here, not in the prompt.

**Pick a slot that does not collide.** Smartlead's 200 req/min ceiling is
account-wide and already shared:

| Existing run | Local time | Cost |
|---|---|---|
| reply-time KPI (daily + weekly) | ~08:00 ET | moderate |
| booked-call-pause morning | 09:03 ET | ~207 requests |
| booked-call-pause afternoon | 13:27 ET | ~207 requests |

**~10:30 ET Monday** is clear of all three and leaves the ~7-minute scan room to run.

Cloud routine runs get a **fresh checkout**, so this skill and its scripts must stay
committed and no run may depend on local state. The routine's environment needs all
three hosts on its network allowlist — a missing host fails as a blocked-domain
error, which reads nothing like an auth error:

```
api.hubapi.com          # bookings + contact associations
server.smartlead.ai     # lead lookup, message history, campaign statistics
slack.com               # chat.postMessage
sheets.googleapis.com   # the sheet write
oauth2.googleapis.com   # refreshing the Google token
```

## Traps

Every one of these cost real time. `references/api-notes.md` has the verified
endpoint shapes; these are the ones that produce a *confidently wrong* answer.

**`last_reply_at` is the last reply, not the first.** The single most tempting wrong
field in this job. It would mis-bucket Hype Proxies (last 08-27, first 08-21) and
USAD (last 08-26, first 07-15).

**The lookback must be unbounded.** USAD first replied 07-15 and booked in the 08-24
week — six weeks. Any "look back two weeks" optimisation silently reclassifies long
nurtures as same-week.

**Take the first reply across *every* campaign the lead is in.** Leads are routinely
in two (20 of 49 in the reference batch), and the first reply can sit in a campaign
that does not hold the Meeting Booked tag.

**Never strip the last dot-segment as a "TLD".** That turned `grade.capital` into
`grade` and silently lost the booking. New gTLDs are common here: `.capital .app .io
.ai .shop .health .sh .co .us .ca`. Match the full domain.

**Never substring-match a short company name.** Measured on this book: `usad` hits 25
unrelated leads, `cactus` 23, `sana` 93, `purpose` 61, `rex` matches `cognitrex.com`.
Require equality on a registrable domain or a full name. An honest `UNRESOLVED` beats
a confident wrong match.

**The booking address is often not the Smartlead address.** Confirmed: USAD books as
`Yasha@usadistributions.com`, is in Smartlead as `yasha@mercatodibellina.com`; RISE
Research `yash@riseresearch.com` vs `yash@riseglobaleducation.com`; Rex
`design@rexarch.com` vs `mahmad@rexmediausa.com`. Founders with several ventures book
under whichever entity is hiring, and HubSpot and Smartlead disagree on surnames.
Never conclude "not in Smartlead" from a domain miss alone — check the person.

**Booking addresses can be helpdesk hosts.** Artic Grey books from
`anthony.spallone@arcticgreyltd.zendesk.com`. Keying on `zendesk.com` would join
every company routing support through the same vendor, so helpdesk hosts are in
`JUNK_DOMAINS` alongside LinkedIn and the free mailboxes.

**`company_name` in Smartlead is often a shortened brand and sometimes just wrong.**
`Sana` for Sana Benefits, `Grade` for GRADE CAPITAL, `MCT` for TheMCTTeam. City of
Yellowknife (`bsleem@yellowknife.ca`) is filed as "Western Arctic Moving"; Mubite is
filed as "Pionex". **Trust the domain over the name.**

**Category tags mutate.** Re-running an old week later gives different counts as
leads get re-categorized (`Meeting Booked` → `CV Sent - Opp Lost`). Decay is slow
(all 49 leads from 8 weeks back still carried the tag), but historical re-runs are
not guaranteed reproducible. **Freeze each week's result once computed; do not
silently recompute history.**

**A resolved lead that has lost the Meeting Booked tag** is a signal the identity
match is wrong. `attribute.py` records `booked_tag` per row as a self-check.

## Regression baseline

`docs/booked-call-attribution/results-2026-07-06_2026-08-30.csv` — 74 hand-verified
rows over 8 weeks, pooled **42 same-week (57%) / 32 prev-week (43%)**. Useful
single-lead assertions:

| Lead | First reply (ET) | Tests |
|---|---|---|
| `egan@sanabenefits.com` | Tue 2026-08-25 10:09 | happy path, hand-verified by Gaston |
| `yasha@mercatodibellina.com` | Wed 2026-07-15 16:27 | 6-week nurture + address mismatch |
| `gunnar@hypeproxies.io` | Fri 2026-08-21 11:19 | 2 campaigns; `last_reply_at` would be wrong |
| `harshita@grade.capital` | Mon 2026-08-24 09:05 | new-gTLD domain, near the boundary |
| `anthony.spallone@arcticgrey.com` | Mon 2026-08-24 20:09 | UTC date ≠ ET date |
| `ngideon@themctteam.com` | Sun 2026-08-16 10:30 | weekend, 14 h before week open |

Two rows in that CSV are **not** API-derived and must not be asserted against
Smartlead: jmfbuilders and Cactus Audio (both supplied by Gaston from his inbox).

`references/regression.md` records how this skill's automated filter compares to
that hand-built roster, including the three bookings the manual list missed.

## Self-annealing

On failure: read the error, fix the script, re-run against the baseline week
(`./scripts/run.sh 2026-08-24 --dry-run` should give 12 bookings), and update the
traps above with whatever changed.

On success, cache what you learned at runtime: new source values seen in
`meeting_source__standardized_`, new address-mismatch pairs, new junk domains, and
any endpoint shape that shifted. Keep `Near Work Partner/wiki/tools/smartlead.md`
in sync — it is the maintained copy of the API facts, not a fork.
