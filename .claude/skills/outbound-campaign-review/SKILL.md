---
name: outbound-campaign-review
description: >
  Monday-morning review of per-campaign cold-email performance for the last full Mon–Sun
  week, from the Outbound metrics sheet › 'Email Campaign Metrics (Weekly)'. Ranks active
  campaigns by total calls and by performance (calls per 1k emails sent), separates real
  changes from noise, finds campaigns that stopped booking or started again, sizes which
  fix would add ≥1 call/week, and tracks each insight week over week in the vault
  (wiki/outbound/campaign-insights.md + logs/campaign-reviews/). Use this whenever Gaston
  asks "which campaign booked the most", "best / worst campaign", "which campaigns
  stopped booking", "what should we improve", campaign performance, the Monday metrics
  check, what to tell Andrés about outbound performance, or why a campaign's results
  moved, even if he doesn't name the skill. Read-only on the sheet. Not the huddle deck
  (`weekly-volume-session`) or the off-week Slack update (`offweek-outbound-update`).
---

# Outbound campaign review (Monday)

Gaston must walk into the week knowing which email campaigns make calls, which stopped,
and where one fix buys the most calls. It feeds what he tells Andrés (VP Marketing), and
**Andrés's rule** applies: explain a result by its quantified impact, not by listing what
was done. Each run answers the standing questions and then **thinks past them**: the best
insight is often one nobody asked for.

## Dates & windows (agreed 2026-10-27)

- **Reporting week** = the last full Mon–Sun before today (run Mon Oct 26 or Tue Oct 27
  → Oct 19–25, sheet column BN). Gaston can name another week: `--week-start`.
- **recent** = last 4 weeks incl. the reporting week · **base** = the 8 weeks before ·
  **life** = since the campaign first sent. Judge on recent vs base. The single week is
  context and is never a verdict by itself (1–3 calls/campaign/week is noise-level).

## Workflow

1. **Numbers.** From the repo root:
   `python3 .claude/skills/outbound-campaign-review/scripts/campaign_metrics.py --out <scratch>/cm.json`
   It prints one line per **active** campaign (emails sent > 0 in the reporting week) and
   writes the full JSON. Columns: `wk s/c` and `4w s/c` (sent/calls), calls per 1k emails
   (recent, base, life), `p_low` / `p_hi`, `upside` (calls/wk if the campaign hit its peer
   rate), `since` (weeks since its last call). Then the went-dark list and the warnings.
   If it warns the week isn't over, stop: the numbers are partial.
2. **Memory.** Read `Near Work Partner/wiki/outbound/campaign-insights.md` (watchlist +
   change log) and the newest `logs/campaign-reviews/*.md`. Each open thread must get a
   verdict this run.
3. **Causes.** Look for what changed since the last review, so a move can be explained
   instead of guessed: `wiki/hot.md`, meetings since the last review (TLDRs only),
   `logs/smartlead-campaign-log.md`, `logs/experiment-readouts/`. Typical causes: copy
   or sequence change, list/source change (Apollo, HireBase, Clay filter), inbox or
   deliverability issue (bounce rate), follow-up subsequence broken/fixed, lead supply
   ran out, a campaign launched or paused.
4. **Analyze** using "How to think" below. Answer every standing question, then add what
   else the data says.
5. **Write** the weekly log, rewrite the living page (formats below), and give Gaston the
   brief in chat. If a cause is a guess, it gets labeled a hypothesis, and the brief asks
   Gaston to confirm it.

## Sheet structure

- `Email Campaign Metrics (Weekly)` (gid 654422282). Row 3 = week start (`10/19/2026`),
  one column per week since 8/4/2025. Rows 9–22 = totals. From row 24 (`Breakdown by
  campaign`) every campaign is a block: an `x` row with the name in B, then the 12
  column-B metrics (Calls Booked, Emails sent, Booking Rate, Replies, Reply Rate, Positive
  replies, Positive Reply Rate, Emails Bounced, Bounce rate, Leads added, New leads
  contacted, Total leads contacted). ~79 blocks, most of them dead. Old campaigns are
  filtered out by sent > 0 in the reporting week.
- Sheet's `Booking Rate` = calls ÷ emails sent. `Reply Rate` = replies ÷ leads contacted.
  We use **calls per 1k sent** (Gaston, 2026-10-27).
- **Calls source:** campaign rankings use the campaign rows. The **official email total
  is the Command Center** (`Weekly Data` row 61). They disagree often (Oct 19–25: CC 11 vs
  sheet 13), so state the gap in one line and don't reconcile it.
- **Unassigned sends:** total sent > the sum of campaign rows (Oct 19–25: 1,604). This is a
  known open item, so mention it only if it grows.
- Subsequences (hard follow-ups) are not separate blocks: calls count for the parent.

## How to think

**Signal vs noise first.** For each moved campaign ask: if the base rate still held, how
likely is the recent count? `p_low` < 0.10 = a real drop, `p_hi` < 0.10 = a real gain,
anything else = "within normal variance". Say so plainly; "random fluctuation" is a valid
and useful answer. Expected calls < 2 in the window = too little volume to judge. Say
"too early" and name the volume that would settle it (≈ 2000 ÷ peer calls/1k emails).

**Volume ≠ performance.** Rank both ways. A high-volume campaign with a low rate can be
the biggest call source *and* the biggest improvement lever. A small high-rate campaign
is a scaling question (is there more lead supply?), not a copy question.

**Decompose the funnel before naming a cause.** Calls/1k = (positives/1k) ×
(calls/positive). A drop with steady positives is a conversion/follow-up problem (reply
handling, booking link, hard follow-up). A drop in positives is a list or copy problem.
Bounce rate up = deliverability. Leads added ≈ 0 with falling sends = lead supply.

**Lag.** Calls often book 1–3 weeks after the reply (`booked-call-attribution`: ~half
come from earlier weeks). A campaign that just lost volume can keep booking for a while,
and a new one books late. Don't call a 2-week-old campaign a failure.

**Peers.** Groups: HM / No-HM / Other (CEOs, RB2B, coworkers, clients). The script's peer
rate is pooled over 12 weeks. Region (US / LATAM / Canada / Asia) and experiment arms
(EXP-008 A vs B, EXP-006 baseline vs challenger) are the sharper comparisons. Use them.

**Size the fix.** Calls/wk gained = weekly sends × (target − own calls/1k) ÷ 1000.
Targets to try: peer rate, own base or life rate, best comparable campaign. The volume
lever: +1 call/wk needs 1000 ÷ own rate extra sends/wk, which only works if leads exist.
Answer "≥1 call/week" with the math shown, and pick the cheapest credible lever.

**Allocation.** Are sends going where calls/1k is highest? Say if the top-rate campaigns
are lead-limited while low-rate ones hold most of the volume. That's usually the
headline for Andrés.

**Concentration.** The share of calls from the top 1–2 campaigns. A single campaign
carrying most of the calls is a risk worth naming.

## Standing questions (answer every week, then go beyond)

1. **Most calls:** the top campaign by total calls (recent window; give week and life
   too).
2. **Typically books but didn't:** life or base calls/1k ≥ peer rate, 0 calls this week
   and/or `since` ≥ 2. Then the verdict: real (p_low) or variance.
3. **Best by total vs best by performance:** both, with their volumes. Flag a high-rate,
   low-volume campaign.
4. **Used to perform, not lately:** base ≫ recent with p_low < 0.10, or a long `since`.
   Also the went-dark list (stopped sending: paused, or out of leads?).
5. **Improve for ≥1 call/wk:** the campaign + lever + math.
6. **What changed vs last review:** every watchlist thread gets a verdict: resolved,
   still open, or reversed (e.g. "Canada HMs: 0 for 3 wks → booked 1 this week; volume
   too low to call it fixed").
7. **Beyond:** anything else the numbers or the vault show: an experiment ready for a
   verdict, a funnel break, deliverability, lead-supply limits, allocation, new campaigns
   to watch.

## Output

**Chat brief** (what Gaston reads Monday): ≤12 bullets. Answers first, one line each,
numbers inline (`US HMs: 12 calls / 4.9k sent = 2.5/1k, vs 1.3 base, real gain p=0.02`).
Then `Watch:` for open threads and `Ask:` for causes he needs to confirm. No tables, IDs or
vault links. If he wants something Andrés-ready, the same points in his voice, ≤5 bullets.

**Weekly log** → `Near Work Partner/logs/campaign-reviews/<reporting Monday>.md`.
Immutable after the run (Gaston's corrections go in the living page and the next log).
Keep it ≤400 words:
```
---
type: log
title: Campaign review, wk Oct 19–25
date: 2026-10-27
week: 2026-10-19
source: campaign_metrics.py (Outbound sheet col BN; CC email calls 11 vs sheet 13)
---
## Answers
1–7 as above, one or two lines each, with numbers.
## Insights
Beyond-the-questions findings, sharpest first.
## Hypotheses to confirm
Each cause not yet confirmed by Gaston.
```

**Living page** → `Near Work Partner/wiki/outbound/campaign-insights.md`. **Rewritten
every run, never appended.** Hard caps keep it under ~600 tokens:
- `## Standing`: ≤6 lines (volume leader, performance leader, biggest lever,
  concentration, data caveat).
- `## Watchlist`: open threads only, ≤8. One line each:
  `Thread — opened <date> — <latest evidence> — next check`. Close a thread when it's
  resolved or 4 runs pass with no change.
- `## Resolved`: closed threads from the last 4 runs only, one line each with the
  outcome. Older ones are dropped (the logs keep them).
- `## Campaign change log`: dated causes that explain moves (copy change, list source,
  paused, subsequence fixed), ≤3 lines per campaign. Delete a campaign's lines once it has
  been dark for 8+ weeks.

Also: one line at the top of `wiki/hot.md`'s `Last Updated` and a line in
`logs/session-log.md`. Index only the living page (`wiki/index.md` → Outbound).

## Self-annealing

- New campaign whose peer group is wrong → fix `peer_group()` in the script.
- Gaston corrects a cause or a verdict → put it in the change log, and if it was a
  reasoning error, add the rule to "How to think".
- Sheet layout changes (row 3 header, block shape) → fix the script, note the date here.
