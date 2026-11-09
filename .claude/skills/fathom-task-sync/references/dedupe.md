# Deduping

Read this during Step 5. This is the step most likely to quietly corrupt the vault, because both
failure modes are invisible at write time: a duplicate looks like a new task, and a wrong merge
looks like a clean run.

## Layer 1 — exact, cheap

Key on `recording_id`. If a meeting note in `wiki/meetings/` already carries it, that meeting is
fully processed. Skip it and count it as skipped in the report.

```bash
rg -l "recording_id: 173602241" "Near Work Partner/wiki/meetings/"
```

This is why `recording_id` in frontmatter is non-negotiable — without it, re-running the sync
re-ingests everything. Note `2026-07-20-clay-lead-scoring-pipeline.md` has
`recording_id: unresolved` (no matching Fathom recording was found for that date); treat it as
processed, and if you ever identify the real ID, fill it in.

## Layer 2 — semantic, against open tasks

Baseline is `wiki/tasks/_index.md`, already loaded in Step 0 (its sections are time horizons —
This Week / Next Week / Backlog — not priorities). For each candidate task:

**Match on the deliverable line** Gate 2 made you write — the action plus done-condition — not on
the title. Titles collide when the work differs and diverge when it doesn't; the deliverable is the
thing that's actually the same or not.

| Case | Action |
|---|---|
| Same deliverable, already open | **Update** the existing file — append `## Update YYYY-MM-DD`, refresh `deadline` / `priority` if they changed. Never create a twin. |
| Same deliverable, in `tasks/done/` | Create new **only** if genuinely recurring (a weekly report is; "fix the scoring" is not). Otherwise surface in the report and let Gaston decide. |
| Different deliverable, related topic | Create new, and add `related: ["[[existing]]"]` both ways if it helps |
| Genuinely new | Create |
| **Can't tell** | **Don't write it.** Surface it in Judgment Calls against the task it might duplicate. |

### Index lines are titles, not scope

This is the trap. `wiki/tasks/_index.md` gives you one line per task — enough to spot a *candidate*
match, not enough to confirm one. Two tasks can share a title and mean different work; two can have
different titles and mean the same work.

**So: when a candidate looks like it might match, open that one task file** (~250 tok) and compare
bodies before deciding. Reading one or two task files is far cheaper than either failure mode. Do
not open all 22 — just the plausible matches.

Real example this must catch: a new call saying *"fix the LinkedIn scoring per Felix's notes"* is
the **same task** as the existing
`wiki/tasks/2026-07-22-correct-linkedin-clay-scoring-per-felix.md`. Update it. A naive string match
on "LinkedIn scoring" would also collide with
`2026-07-20-build-clay-lead-scoring-pipeline.md`, which is genuinely different work (build the
pipeline vs. correct its scoring) — those two are `related:`, not duplicates.

### The update shape

Append; never rewrite. The original body is provenance — it records what he meant *then*.

```markdown
## Update 2026-08-19

Restated in [[wiki/meetings/2026-08-19-weekly-check]]: Felix added 2 further comments on the
seniority weighting. Deadline moved to Aug 21.

> "también hay que revisar el peso de seniority"

[Fathom @23:14](https://fathom.video/calls/N?timestamp=1394)
```

Also update `updated:` in frontmatter, and the `_index.md` line if priority or deadline changed.

## Adjacent meetings restate the same items

Recurring meetings in the same week are often *adjacent, not duplicate* — they cover the same
ground for different audiences. Verified example: the **Aug 18 KPI deck prep** builds the deck for
a leadership call, while the **Aug 19 weekly** is the outbound team's own review. Items genuinely
restate across them (scorecard metrics, Experiment 009, the reply backlog).

When processing a multi-meeting batch, dedupe **across the batch**, not just against the vault —
otherwise two meetings from the same week produce twin tasks that neither Layer 1 nor a
vault-only Layer 2 would catch. Merge the restatement into one task and note both meetings in
`sources:`.

## When unsure, don't write — surface it

If you cannot tell whether it's the same work, **leave it unwritten and put it in the report's
Judgment Calls section**, named against the task it might duplicate, with quote and timestamp.

**This reverses what this file said until 2026-09-11, and the old rule was not a mistake — it
expired.** It read: *"create it and flag it; a flagged duplicate takes seconds to merge, a
silently-dropped task is invisible forever."* True of a near-empty vault, where the board had room
and a miss was the costly error. At **~44 open tasks** the arithmetic flipped: duplicates are what
make the board unscannable, and merging them is not seconds of work once there are several. Nothing
is actually lost by waiting — the item is in the report with its evidence, and the transcript stays
refetchable via `recording_id` indefinitely. Gaston says "write it" and the next run does.

Re-read that reasoning rather than the verdict. If the board is ever deliberately cleared back down,
the bias should move again — what stays constant is that the default protects whichever resource is
scarce, and right now that's Gaston's attention, not vault coverage.

> [!warning] **The Sara case — detection worked, the verdict didn't.** On Sep 8 the run identified
> its own duplicate in the body it was writing: *"this is the **second** outstanding 'send Sara
> materials' item, alongside [[2026-09-02-send-sara-clay-enrichments]]. Worth sending together in
> one Slack message."* It set `related:`, then created the file anyway — "create and flag" said so.
> Both now carry the same Sep 11 update block, and the two Slack messages were always going to be
> one.
>
> **Writing prose that explains how your new task relates to an existing one *is* the duplicate
> finding.** At that point you've already done the comparison. Update the existing task, or surface
> it. Don't narrate the overlap into a second file.

## Do not read `tasks/done/` routinely

`WIKI.md` forbids it except to check for recurrence in Layer 2. When you do need it, check for the
specific slug rather than crawling the folder:

```bash
ls "Near Work Partner/wiki/tasks/done/" | rg "linkedin.*scoring"
```
