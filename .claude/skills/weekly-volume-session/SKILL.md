---
name: weekly-volume-session
description: >
  Builds the "Near Weekly Outbound Volume Session" Google Slides deck for the next
  bi-weekly Tuesday outbound huddle (every 2 weeks since 2026-10-13). It duplicates the
  last session's deck into the volume session folder, renames it
  MM-DD_Near_Weekly_Outbound_Volume_Session, and refreshes every metric for the two
  weeks before the session: booked calls by channel, qualified call rate, weekly metrics by
  channel, quarterly cost / value by channel, the email overview, email capacity by
  campaign group, to-dos, plus clearing headlines and issues. Sources are the Command
  Center, the Outbound metrics sheet and the Near CAC dashboard. Use this whenever
  Gaston asks to prep, build, duplicate or update the weekly huddle / volume session /
  outbound meeting deck, "do the slides for Tuesday", "prep the next volume session",
  refresh the KPI scorecard, or
  update any of those metrics in the deck, even if he doesn't name the deck. Also use it
  to draft the deck's Headlines and Issues to discuss once Gaston has added his context
  (it asks him first, never invents the story). Not the off-week Slack update
  (`offweek-outbound-update`).
---

# Weekly Outbound Volume Session deck

Every other Tuesday Gaston runs the outbound huddle off a Google Slides deck (bi-weekly
since 2026-10-13; in off-weeks there's a written update instead). Each session's deck is
a copy of the previous one, with the numbers refreshed. The metrics stay weekly: the deck
shows the last two full weeks, not a two-week total. The work has two phases:

1. **Metrics** (scripted): copy the deck and refresh every number.
2. **Narrative** (drafted with Gaston): after he adds his context to the channel
   slides, draft the Headlines and Issues to discuss from the whole deck.

The agent never writes "what we learned", "this week" or notes boxes. Those are
Gaston's.

**The design rule:** never change shapes, charts, colors, fonts, sizes or layout. Only
replace text inside the boxes and cells that already exist. The scripts enforce this.
They write new text so it inherits the existing style, and they copy font size and
family from a sibling cell so the numbers look consistent. The only geometry they
touch is the capacity bar split, which Gaston asked for. If a slide seems to need a
real design change (a new column, a new row type, a moved box), stop and ask. Gaston
approved one exception on 2026-10-13 (adding Q3 columns to the value table). That
does not make it a general rule.

## Dates

- **Session date** = the Tuesday of the meeting, **14 days after the last session**
  (2026-10-13 → 2026-10-27 → 2026-11-10). If Gaston doesn't give a date, take the last
  deck's date + 14 and confirm it with him. `duplicate_deck.py` warns if the gap isn't 14
  days (a skipped or moved session).
- **Reporting week** ("last week") = the last full Monday–Sunday week before the session:
  for a Tuesday, session − 8 days to session − 2 days. Session Oct 27 → Oct 19–25.
  Written `Oct 19–25`, or `Sep 28–Oct 4` across months. Slide 4 headers use upper case:
  `OCT 19–25`.
- **Previous week** = the week before that (Oct 12–18). It was an off-week with no deck,
  so it is **fetched from the sheets** like the reporting week. Never copy it from the
  last deck: that deck's "last week" (Oct 5–11) is two weeks older than this one.
- `fetch_metrics.py --session-date` works out both weeks, prints them, and warns if the
  reporting week isn't over yet (partial numbers). Check the printed weeks before going on.

## Workflow

Scripts live in `scripts/`. Run them from the repo root with `SK=.claude/skills/weekly-volume-session/scripts` (they find `.env` on their own).
Put scratch files in the session scratchpad.

1. **Duplicate:** `python3 $SK/duplicate_deck.py --session-date YYYY-MM-DD`
   copies the newest deck in the volume session folder (`1ANO1rNmzojy4zOKj3x2Z49Oed1ysp0iR`)
   under the new name. If that name already exists, it prints the existing deck instead
   of making a second copy. If it prints a `warning` about the gap, ask Gaston before
   going on. Share the link with Gaston right away.
2. **Sheets:** `python3 $SK/fetch_metrics.py --session-date YYYY-MM-DD --out metrics.json`
   pulls booked calls, email metrics, reply speed, cold-calling dials and per-campaign
   sends for **both** weeks (the previous week sits under `"prev"`). Read its `warnings`;
   the ones starting `Previous week:` are about the older week.
3. **Dashboard:** open the dashboard in the browser and add to metrics.json (details in
   the Sources table below):
   ```json
   "dashboard": {
     "qualified_rate": {"email": "33%", "linkedin": "24%", "cold_calling": "29%"},
     "quarters": {
       "Q1": {"email": {"cpqc": "$636", "v90": "$9.3k"}, "linkedin": {...}, "cold_calling": {...}},
       "Q2": {...}, "Q3": {...}
     }
   }
   ```
   Fill every quarter the value table has a column for. Format the 90-day value as
   `$9.3k` and write `-` where the dashboard shows `-`.
4. **Dry run:** `python3 $SK/update_deck.py --deck <new id> --metrics metrics.json`
   prints every change as old → new, plus warnings. Check that the numbers make sense
   (a week with 0 sends or a total that halved deserves a second look).
5. **Apply:** the same command with `--apply`. It refuses to run on a deck that already
   shows the target week, because a second run would copy the cleared to-dos onto slide 2
   and empty Headlines and Issues again.
6. **Verify visually:** `python3 $SK/thumbnails.py --deck <id> --out-dir <scratch>`.
   Look at the to-dos, KPI scorecard, Email overview and capacity slides. Text overflowing a cell, a box that moved, or mixed
   font sizes all mean something went wrong.
7. **Report** to Gaston: the deck link, the numbers written, and every warning (source
   mismatches, blank cells, unassigned sends, new quarters). Log the run in
   `Near Work Partner/logs/session-log.md`. Then stop. Phase 2 starts when he says his
   context is in.

## Phase 2: Headlines and Issues to discuss

Gaston fills in the channel slides himself: email notes, learned and this-week boxes,
the cold calling slide, the LinkedIn slides and the experiments table. Headlines are a
summary of *his* story, so the order matters:

1. **Ask before writing**, unless he already told you. Ask him:
   - Is his context in on the email, cold calling and LinkedIn slides?
   - Has he written any headline himself? His headlines stay word for word. On
     2026-10-13 he wrote the LinkedIn one.
   - What does he want to raise in Issues to discuss? He usually brings this, often
     as a pasted note.
   - Anything that must be mentioned (e.g. "mention the cold calling numbers issue")?
2. **Read the whole deck again** (`get_presentation` and dump every shape and table).
   Gaston edits and reorders slides between phases, so don't rely on what you read in
   phase 1.
3. **Check the numbers you're about to quote** against the slides. If two slides
   disagree (a mislabeled week header, a blank KPI cell that another slide has), don't
   pick one silently. List it for Gaston and fix it only when he says so.
4. **Draft, then write** with `write_box.py` (dry run first). It only writes into empty
   boxes, so a headline Gaston typed is never overwritten.

**Headlines (Headlines slide, 4 boxes, top to bottom).** One line per box,
`Label: sentence`, matching Gaston's own style (`Linkedin: Sam is back on pace…`).
- Default order: **Booked calls** (total and mix, vs the prior week and the 30+ target),
  **Email**, **Cold calling**, **LinkedIn**. Keep any headline Gaston already wrote in its box.
- Each headline gives the result, then the reason or the next step. Quote 1–3 numbers
  from the deck, and use an arrow for changes (`45 → 60`). At most 2 lines at 15pt.
- Base the "why" on Gaston's context boxes (notes, what we learned, this week). Don't
  add explanations he didn't give.
- Write: `--style-from <the box Gaston wrote>`. If he wrote none, use the same box in
  the last session's deck: `--style-deck <last deck id>`.

**Issues to discuss (one body box).** Format agreed on 2026-10-13. The title is bold;
the labels are bold and the rest is plain, 12pt:
```
<Issue in a few words, with the key number>
Today: <the situation, with numbers from the deck>
Proposal: <what Gaston suggests>
Fallback: <plan B, if he gave one>
Decision needed: <the question the meeting must answer>
```
For two issues, separate them with a line of `— — —` as in older decks. Write with
`--title-style-from --bold-labels --style-from g3f9d2510f4c_0_14 --style-deck <a deck
where that box has text>`. Clear, simple and sharp: Gaston edits after, so keep it short.

## Sources: where every number comes from

| Deck field | Source |
|---|---|
| Booked calls by channel (slide 4 mix + total, weekly metrics "Email calls booked" / "CC booked calls", slide 9 "Calls booked") | **Command Center** › `Weekly Data`, rows 61 (email), 62 (LinkedIn), 63 (cold calling), column = week start in row 2. **Always use the Command Center** for email booked, even when the Outbound sheet's "Calls Booked" differs. |
| Emails sent, capacity, reply rate, positive replies | **Outbound metrics** › `Email Campaign Metrics (Weekly)`, column = week start in row 3; rows "Email Capacity" (10), "Emails sent" (11), "Reply Rate" (14), "Positive replies" (15) |
| Per-campaign sends (slide 12 groups) | Same tab, under "Breakdown by campaign" (row 24+). Each campaign block has its own "Emails sent" row |
| Median reply time, reply speed | **Outbound metrics** › `Email Time-to-reply tracker`, column = week start in row 2; rows 10 (median, `0:08` = 8 min), 7 (<5 min), 8 (<10 min) |
| Cold calling dials | **Outbound metrics** › `Cold Calling (Weekly)`, column = week start in row 3, row 10 "Dials" |
| Qualified call rate | [CAC dashboard › Outbound Scoreboard](https://near-cac-dashboard.vercel.app/outbound-scoreboard/), section "3. Matured qualified rate", table column "Qualified rate". Deck order is Email \| LinkedIn \| Cold Calling, but the dashboard lists Cold Calling first. |
| Value table: cost / qualified call | [CAC dashboard › Summary](https://near-cac-dashboard.vercel.app/) with **Quarterly** selected (the default), "Cost per Qualified Call by channel". Use rows **Email Outreach**, **LinkedIn Outreach** (not organic "LinkedIn") and **Cold Calling**. |
| Value table: 90-day value | Same page, "90-day Customer Value by channel (avg per paying customer)", same three rows |
| Last full month · cost / qualified call | **Not updated weekly.** Leave it as is. See "Open items". |

`get_page_text` works on the dashboard once its tables have loaded. Charts don't
expose data, but every number above is also in a table.

## What changes on each slide

Gaston reorders slides from week to week. On 2026-10-13 he deleted the copy workshop
and moved Issues to discuss next to the email slides. The scripts find elements by
objectId, so the order doesn't matter to them. Refer to slides by **title** when talking
to Gaston; the numbers below are the 10-13 deck's.

| # (10-13) | Slide | Phase 1 action |
|---|---|---|
| 1 | Intro | Subtitle → session date (`October 13, 2026`) |
| 2 | To-dos from last week | Replace with the last deck's "To-dos for this week" rows **verbatim** (task, owner, due, where we are). Adds table rows if needed. |
| 3 | Headlines | Empty the 4 headline boxes and keep the boxes. Phase 2 fills them. |
| 4 | KPI scorecard | Booked-calls total + `Prior week: <previous-week total from the Command Center>`, mix + its date label, qualified rate. Weekly metrics: both week columns from the sheets. Value table: refresh every quarter column. |
| 5–8 | LinkedIn slides, IDS | **Skip** (Gaston / the LinkedIn team fill these) |
| 9 | Email overview | Both week columns (headers and numbers) from the sheets. Leave the text boxes (tests, learned, this week, notes) alone. |
| 10 | Email experiments | Skip (Gaston) |
| 11 | How we used email capacity | Subtitle (dates · capacity · sent · unused), caption cleared, group emails + share (share = group ÷ **total sent**, not capacity), bar split + labels (open jobs = everything except "Other sends", other, unused; all ÷ **capacity**) |
| 12 | Issues to discuss | Empty the body box. Phase 2 fills it. |
| 13 | Cold calling overview | Skip. Gaston fills it, including the new week's column. |
| 14 | To-dos for this week | Empty all rows (keep the rows) so the meeting can fill them |
| 15 | Rate this huddle | Skip |

## Email groups (slide 12)

`references/campaign-groups.json` maps each Smartlead campaign name to a group:
Open Jobs, EXP-008A/B, EXP-009, Fresh Apollo, EXP-012, EXP-013, Other sends. A group
can hold several campaigns (EXP-012 = its Sales/GTM, Marketing and Engineering
campaigns, summed). Names are matched with runs of spaces collapsed, because the sheet
and the map have disagreed on spacing before. If a campaign that sent email isn't in the
map, `update_deck.py` stops and lists it. Ask Gaston which group it belongs to, add it to
the JSON, and re-run. New experiments start every few weeks, so expect this.

**A group with sends but no table row** also stops the run. Adding a row is a design
change: ask Gaston first. On 2026-10-23 EXP-012 and EXP-013 became groups. The table
already filled the slide (265–501pt, footer at 508pt), so 2 more rows don't fit at the
current height. Gaston decides how the slide makes room. For the 10-27 deck he OK'd a
one-off fix: 2 rows added, and the columns rebalanced (Group/Emails/Share narrower,
"What it means" wider, same table size) so every row fits on one line. Not a rule:
the next layout change needs his OK again.

**Unassigned sends:** total "Emails sent" is usually higher than the sum of the
campaign rows (by 2,041 on Oct 5–11). Until we know where those come from, they go to
**Open Jobs**. It's an open item, not settled.

## Formats (match the deck)

- Emails sent: `17.9k` (one decimal, lower-case k, `20k` rather than `20.0k`).
  Slide 12 group emails: `11.3K`, `2.25K`, `423`.
- Percentages: one decimal (`63.3%`). Reply speed: `56.1% <10m` and `8.8% <5m` on two lines.
- Median: `8 min`. Booked mix: `6  |  5 |  0` (keeps the original spacing).
- A metric whose source is empty is left **blank**: never guess and never carry last
  week's value forward. Say it in the report.

## Open items (check each run, update this list)

- **Cold calling dials:** `Cold Calling (Weekly)` stopped at Aug 24 as of 2026-10-13.
  By 2026-10-23 it had Oct 12–18 (4,205) and Oct 19–25 (3,806 so far), but Oct 5–11
  read 0 while the 10-13 deck showed 5,496. A blank or 0 leaves the KPI cell blank with a
  warning. Both dials cells are now fetched, so a hand-typed number in the last deck is
  not carried over. In phase 2, if a cell is blank and Gaston has filled the Cold calling
  overview slide, offer to copy its dials into the KPI cell. Also check that the cold
  calling table's week headers are right: on 10-13 both read `Sep 28–Oct4`.
- **Last full month cost / qualified call:** at the end of October, **ask Gaston** for
  the right number and where it comes from. Then add it to the Sources table and the
  scripts. Until then, leave the box alone.
- **Q3 is on the value table** since 2026-10-13. When Q4 data appears, the dry run
  will warn "Dashboard has [Q4]". Ask Gaston whether to add or swap columns. Don't
  add them on your own.
- **Unassigned email sends** → Open Jobs, as above. Find the source (likely campaigns
  missing from the breakdown, such as EXP012, whose rows read 0).
- **Booked calls arrive late:** on 2026-10-13 Gaston updated the Command Center during
  the day. Oct 5–11 went from 6|5|0 to 10|7|0, and Sep 28–Oct 4 cold calling went from 1 to 0,
  which made the prior week 22 instead of 23. Since both weeks are fetched at build time,
  late updates made before the build are picked up. When Gaston says the sheets were
  updated after the build, run `fetch_metrics.py` with the same `--session-date`. Compare every number with the
  slides (slide 4: total, `Prior week`, mix, weekly metrics both columns; slide 9: both
  week columns), and fix only the cells that differ with `set_cell`/`set_shape`. Never
  re-run `update_deck.py --force` for this: it would copy the cleared to-dos onto
  slide 2 and empty Headlines and Issues again.

## Gotchas

- The Slides API was enabled on GCP project 1005567143564 on 2026-10-13. A 403
  "Slides API has not been used" means it was switched off.
- `batchUpdate` is atomic: one bad request and nothing applies. Example: styling an
  empty cell fails with "object has no text". `set_cell` only styles cells it writes text into.
- `insertTableColumns` shrinks the other columns to keep the table width the same. Set
  column widths afterwards.
- Old decks had stray 10pt cells. `update_deck.py` restyles data cells from the
  Target / Goal column (or the row label), which fixes drift without changing the design.
