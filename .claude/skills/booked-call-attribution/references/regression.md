# Regression: automated filter vs the hand-built roster

`docs/booked-call-attribution-handoff.md` describes an 8-week run where **Gaston
supplied the company list per week by hand** out of HubSpot. This skill derives that
list automatically (`hs_activity_type` present + contact tagged `Email Outreach`).
Running the automated filter over the same 8 weeks, 2026-09-01:

| Week (Mon) | Automated | Manual roster | Δ |
|---|---|---|---|
| 2026-07-06 | 10 | 10 | — |
| 2026-07-13 | 5 | 5 | — |
| 2026-07-20 | 12 | 12 | — |
| 2026-07-27 | 11 | 10 | **+Cash Margin Partners** |
| 2026-08-03 | 6 | 5 | **+Krece** |
| 2026-08-10 | 8 | 7 | **+Cash Margin Partners** (2nd booking) |
| 2026-08-17 | 11 | 12 | **−From The Future** |
| 2026-08-24 | 12 | 13 | **−Cactus Audio** |
| **Total** | **75** | **74** | 3 added, 2 removed |

Five weeks match exactly. Every difference is explained:

**+Krece (08-03)** — this is the open discrepancy the handoff flagged and left
unanswered: *"Samuel Gedaly's Krece booking (created 08-05) falls in the Aug 3–9
week, which Gaston supplied as 5 companies without Krece. That week may actually be 6
calls."* The automated filter independently confirms it: **that week is 6 calls.**

**+Cash Margin Partners (07-28 and 08-14)** — John Valenti, tagged `Email Outreach`,
with a Chili Piper booking in each week. Absent from the manual roster both times.
Two bookings by the same contact in different weeks is a real pattern here (Krece did
it too, five days apart across two weeks).

**−From The Future (08-17)** — contact `neil@ftf.co` is tagged **`Friend`**, not
`Email Outreach`, so the rule excludes it. Note the manual roster also recorded a
different person for it (Lance Hollander vs HubSpot's Neil Bar-or). If the tag is
wrong, the fix belongs in HubSpot; the skill will pick it up on the next run. This is
a *decision*, so it is not review-flagged — only untagged contacts are.

**−Cactus Audio (08-24)** — the 2026-08-24 record is `sync: Near & Cactus`, with no
`hs_activity_type`. That account first booked **2025-12-12**. Same shape as Astrozon
(booked 07-22, then two candidate interviews on 08-27) and Greenwich Metals (booked
04-16, then a kickoff on 08-28).

> [!note] **Superseded 2026-09-01.** Gaston counts Cactus Audio as one of the 13 —
> `sync: Near & Cactus` was a real sales call, whereas the Astrozon and Greenwich
> records are a candidate interview and a kickoff. No API field separates those, so
> the skill no longer drops any of them: all three are **written to the sheet marked
> `REVIEW – …`**, carrying the meeting title and the original booking date, and held
> out of the headline until he keeps or deletes each one. A company silently missing
> from the week is the worse failure — it reads as 12 calls when the truth was 13.
> Cactus Audio lands as `REVIEW – UNRESOLVED` with blank reply columns, since
> `adam@cactusaudio.com` genuinely returns `{}` from Smartlead.

Both removals are also the two rows the handoff itself marks as **not API-derived**
(jmfbuilders and Cactus Audio came from Gaston's inbox, not from any endpoint).

## Reproducing

```bash
./scripts/run.sh 2026-08-24 --dry-run     # expect 12 bookings, 1 review flag
```

The bucket assertions to pin (from `results-2026-07-06_2026-08-30.csv`):

| Lead | First reply (ET) | Bucket in the 08-24 week |
|---|---|---|
| `egan@sanabenefits.com` | Tue 2026-08-25 10:09 | SAME |
| `harshita@grade.capital` | Mon 2026-08-24 09:05 | SAME |
| `anthony.spallone@arcticgrey.com` | Mon 2026-08-24 20:09 | SAME (UTC says 08-25) |
| `gunnar@hypeproxies.io` | Fri 2026-08-21 11:19 | PREV (`last_reply_at` 08-27 would say SAME) |
| `yasha@mercatodibellina.com` | Wed 2026-07-15 16:27 | PREV (6-week nurture) |

**Category tags mutate**, so a re-run of an old week is not guaranteed to reproduce
forever — `Meeting Booked` decays into `CV Sent - Opp Lost` and similar. Decay is
slow (all 49 leads from 8 weeks back still carried the tag on 2026-09-01), but freeze
each week once computed rather than silently recomputing history. `write_to_sheet.py`
enforces this: appending a week already present is refused without `--force`.

## First live run — 2026-09-01, week 2026-08-24 → 08-30

Written to the sheet (rows 7–21) and posted to Slack.

**12 counted** — 7 SAME (58.3%) / 5 PREV (41.7%), 0 unresolved.
**3 flagged `REVIEW`** — Cactus Audio, Astrozon LLC, Greenwich Metals.

All six hand-verified first-reply timestamps reproduced to the minute, including the
three traps: Artic Grey's UTC/ET date flip (`8/24 20:09 ET`, not 8/25), HypeProxies
where `last_reply_at` would have said SAME (`8/21`, not 8/27), and USAD's six-week
nurture (`7/15`). Four rows resolved to a different address than HubSpot recorded —
Artic Grey (booked from a `…zendesk.com` helpdesk address), USAD, Dance With Me, and
HypeProxies (booked by Awan Ali, measured on colleague Gunnar Catlett).
