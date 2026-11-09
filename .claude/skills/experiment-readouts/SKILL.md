---
name: experiment-readouts
description: >
  Builds the weekly cold-email experiment readouts: one Google Doc per live experiment
  (EXP-008A, 008B, 009, 011, 012, 013…) in the format of Andrés's EXP-008 readout (TLDR +
  DECISION, what we test, performance table + chart vs benchmark, progress to the 3,600-lead
  threshold, main insight, recommendation, sources), from live Smartlead numbers, plus a short
  exec Slack draft linking them. Use this whenever Gaston asks for "the experiment readouts",
  "the readouts", "readout for EXP-0xx", "how are the experiments doing", "should we stop /
  call EXP-0xx", whether a test hit threshold, or a positive-rate comparison against the No-HM
  or HM benchmark, even if he doesn't say "readout". Not the per-campaign Monday review
  (`outbound-campaign-review`), the huddle deck (`weekly-volume-session`) or the off-week
  update (`offweek-outbound-update`). Docs go in Gaston's Drive only after he OKs the
  decisions; never post to Slack.
---

# Experiment readouts

Weekly, one Google Doc per live experiment, for Gaston and the execs (Andrés, Franco,
Michael). Format comes from Andrés's EXP-008 first readout
(`1hogCUOXHccrKSCGTqOljQ3I-LsWi8vSJliJoj-jgG2I`); the Oct 13 set is the latest reference
(Drive folder "Experiment Readouts 2026-10-13", log `Near Work Partner/logs/experiment-readouts/2026-10-13.md`).

The docs are reading material for decision makers, so they carry results and decisions,
not tracking problems. Data issues still matter: they go to Gaston separately (step 5).

## Workflow

1. **Confirm which experiments are live.** `references/experiments.json` maps each
   experiment to its Smartlead parent campaigns, benchmark and threshold. Before pulling,
   check the vault for changes since the last log in `logs/experiment-readouts/`
   (`wiki/hot.md`, meetings and tasks since then: launches, stops, new arms, renamed
   campaigns). Tell Gaston the list you'll run and ask about anything you're unsure of
   (e.g. whether HireBase or Apollo should get a readout). Update the JSON when the list
   changes; it's the only place the campaign map lives.

2. **Pull the numbers.** From the repo root:
   ```
   python3 .claude/skills/experiment-readouts/scripts/pull_stats.py --out <scratch>/stats.json
   ```
   ~5–15 min (the benchmark campaign is large; run it in the background). It prints a
   one-line summary per arm and benchmark and writes the full detail: received per step,
   positives per step, reply categories per step, positive leads with domain, new Email 1
   in the last 7 days, last Email 1 date, campaign status. Definitions are in the script
   docstring and repeated in the Sources line below.

3. **Compare with last week.** Read the previous log. For each experiment note what moved
   (new positives, bookings, progress), and whether any count *dropped*: categories are
   current, so a re-tagged lead disappears. Name the drop, don't paper over it.

4. **Analyze each experiment.**
   - Positive and booked rate vs its benchmark, per arm. **No-HM tests compare to the historic
     US OJ No-HM baseline** (`us_oj_nohm_historic`, all baseline / Candidate-led / Routing CTA
     campaigns, A+B, since Nov 2025), not a same-period cohort (Gaston, Oct 29). Mention once
     that recent sends (Jun 30+) run lower (0.52% / 0.10% on Oct 29). CEO tests compare to all
     US HM campaigns (`us_oj_hm_all`). Comparisons across personas are **directional**: say so.
     A persona test also shows its persona's own baseline when experiments.json has a
     `secondary_benchmark` (EXP-013: HR / Talent in No-HM, 0.42% / 0.06%). Beating that is the win,
     even below the overall No-HM baseline (Gaston, Oct 29).
   - For step tests (008A Email 2–3, 008B Email 4–7) read the focus steps: positives and
     the DNC / Not Interested they drew.
   - Progress to threshold and weeks to go at the current `new_e1_last_7d` pace.
   - A decision per experiment: keep running / call it / stop. Decisions follow earlier
     ones: a checkpoint set last week is checked this week.
   - Sanity checks (these feed step 5, not the doc): several positives at one domain
     (008B, Oct 19: 3 of 6 at us-ignite.org); an arm with `new_e1_last_7d` 0 or an old
     `last_e1` (stalled Clay feed); a persona leaking into the wrong experiment (use
     `/campaigns/{id}/leads` → `custom_fields.prospect_title`, not `open_role_title`);
     for 011, whether the CEO's company also had a positive HM.
   - `Not Qualified` is a real positive (an interested reply we chose not to book; Gaston,
     Oct 23). The Oct 6 and Oct 13 readouts did **not** count it, so the No-HM pre-split
     benchmark reads 38 positives (0.65%) now vs 26 (0.44%) then, with 12 Not Qualified
     making up the gap. When comparing with a log from before Oct 23, use
     `positives_excl_not_qualified`, and say once in the doc that the definition changed.

5. **Show Gaston before building.** One message: per experiment, the headline numbers,
   what changed since last week and the proposed decision; then, separately, the data
   issues you found. He rewrites decisions (Oct 13: EXP-012's became "keep one more week
   until the heads-of-department experiment replaces it"), so don't upload until he OKs them.

6. **Build the Docs.** Write `<scratch>/spec.json` (shape below), then:
   ```
   python3 .claude/skills/experiment-readouts/scripts/build_docs.py <scratch>/spec.json --html-dir <scratch>/html
   ```
   Open one HTML to check it, then re-run with `--upload`. It creates
   "My Drive / Experiment Readouts <date>" and prints each Doc link. To revise Docs already
   uploaded, add `"doc_id"` to each doc in the spec: `--upload` then overwrites it in place
   and the link stays the same.

7. **Draft the exec Slack message** (Gaston posts it) in the format of
   [references/slack-examples.md](references/slack-examples.md): one short, sharp line per test
   with its key insight and decision, plus its Doc link. Numbers only when there's a big change
   (a stop or a call). Describe the test in words rather than leaning on the experiment
   number (Andrés, Oct 5).

8. **Log it.** Write `Near Work Partner/logs/experiment-readouts/<date>.md` with the same
   frontmatter and sections as the 2026-10-13 file: method line, Drive folder + Doc ids,
   team message, per-experiment readout text, data issues. Add a line to
   `logs/session-log.md`. Put new API quirks or experiment facts in
   `references/experiments.json` or `wiki/tools/smartlead.md` → "Experiment readout notes".

## Doc structure

Every Doc has these sections in this order. **No data-quality / execution-audit section**:
Gaston cut it (Oct 14) because tracking problems are his to fix, not reading material.

- Header: `Near Outbound | EXP-0xx`, `WEEKLY READOUT | <what it tests, short>`,
  reporting date, "Data: cumulative since launch".
- **TLDR**: `DECISION: <IN CAPS>` then 2–4 sentences: result vs benchmark, what moved
  this week, when the next call is.
- **1. What we are testing**: the variable, the arms, primary metric (positive reply rate),
  threshold.
- **2. Performance**: table `Segment/Arm | Contacted | Actual replies | Positive replies |
  Positive share | Booked calls`, cells as `32, 1.36%`; a Total row when there are several
  arms, and the benchmark row last (both bold). Chart of positive rate per arm with the
  benchmark as the reference line. One or two sentences under it. For step tests, add or
  swap in a per-step table (`Step | Received | Positive replies | Other replies`).
- **3. Progress to threshold**: `Segment | Contacted | Progress to 3,600 | New leads, last
  7 days | Status` (status like "Crosses 3,600 next week", "~14 weeks to go").
- **4. Main insight**: the one thing the reader should take away, in plain words.
- **5. Recommendation**: bullets: what to do now and what decides the next call.
- **Sources**: `Smartlead | /campaigns/{id}/statistics for the experiment campaigns, their
  subsequences and the benchmark campaigns | Pulled <date>`; `Vault experiment notes |
  3,600-leads-per-arm threshold, positive replies as primary metric (Aug 18) | Reviewed <date>`;
  `Definitions | Actual replies exclude Out of Office, bounces and uncategorized. Positive =
  current Smartlead category is positive (incl. subsequences), credited to the step of the
  first reply. Booked = Smartlead "Meeting Booked" tag, not HubSpot.`

Rates: two decimals with `%` (`0.39%`), positive share one decimal. Numbers with thousands
separators (`3,075`).

## Spec shape

```json
{"date": "2026-10-27", "date_label": "Oct 27, 2026",
 "docs": [{"id": "EXP-012", "subtitle": "No-HM Copy by Role Group (Engineering, Sales/GTM, Marketing)",
   "decision": "Keep running", "tldr": "...",
   "sections": [
     {"heading": "1. What we are testing", "paragraphs": ["..."]},
     {"heading": "2. Performance",
      "table": {"columns": ["Segment", "Contacted", "Actual replies", "Positive replies", "Positive share", "Booked calls"],
                "rows": [["Engineering", "2,345", "32, 1.36%", "8, 0.34%", "25.0%", "1, 0.04%"]],
                "bold_rows": [3, 4]},
      "chart": {"title": "Positive reply rate", "unit": "%",
                "bars": [{"label": "Engineering", "value": 0.34}],
                "reference": {"label": "Benchmark", "value": 0.44}},
      "paragraphs": ["..."]},
     {"heading": "5. Recommendation", "bullets": ["..."]}],
   "sources": ["Smartlead | ... | Pulled Oct 27, 2026"]}]}
```
Optional per doc: `"kind"` (default `WEEKLY READOUT`; use `FINAL READOUT` for a stop/call).
