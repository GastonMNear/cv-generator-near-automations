# Run report

Read this during Step 7. The report is the only part of the run Gaston actually sees, so it carries
the whole burden of trust: it has to make the invisible work (what was skipped, what was merged,
what was guessed at) visible enough that he can catch a mistake.

## Format

```
FATHOM SYNC — 2026-08-19          3 meetings · 2 processed · 1 skipped

TASKS WRITTEN (4)

  Confident deadlines
  [1] Send Daniel the LinkedIn slides      due 2026-08-17   "te las mando el lunes"
  [2] Pause the Weekend campaign           due 2026-08-16   "antes de los tests"

  NEEDS YOUR CALL
  [3] Extend the email sequence            no deadline
      Daniel said "cuando puedas" — genuinely open-ended.
      → When do you want this by?

  [4] Document the deliverability protocol  deadline?
      You said "cuando vuelva de las pruebas" — I did NOT set a date.
      → Confirm?

UPDATED (1)
  [5] Correct LinkedIn Clay scoring — added Felix's 2 new comments (existing task,
      deadline moved Jul 24 → Aug 21)

WAITING ON OTHERS (1)
  [6] Daniel to approve campaign copy — blocks [1]

JUDGMENT CALLS — considered, not written (3)

  [J1] "Soft technical landing deploy"                    Gate 2 — no scope
       Daniel: "que lo vamos a hacer esta semana, ¿cierto?" — you: "Sí."  [Fathom @51:23]
       Confirmed for the week, but the call never says what shipping it means.
       → Want it? Tell me the deliverable.

  [J2] "Slack weekly metrics routine to Daniel"           Gate 1 — status question
       You: "I think the routine is done. I have to check."  [Fathom @16:41]
       Reads as uncertainty about what exists, not a commitment to build.
       → Is this outstanding work?

  [J3] "Send Sara the session-4 pack"                     possible duplicate
       Looks like the same deliverable as
       [[tasks/2026-09-02-send-sara-clay-enrichments]] — one Slack message, not two.
       → Merge into that task, or write separately?

SKIPPED (3)
  • "Vada & Near consultation" — sales call, not your workstream
  • "Help Scout & Near consultation" — sales call, not your workstream
  • "Weekly check" (2026-07-22) — already ingested (recording_id 166148624)

Vault: wiki/meetings/2026-08-14-weekly-check · 4 tasks · _index.md updated (fits budget)
```

## Rules

**Tasks that passed the gates are written before the report.** He chose auto-write, so for anything
that cleared Step 4 and Step 5 the report tells him what already happened — it is not a request for
permission, and he should never have to approve a clear commitment to get it onto the board.

The one exception is **Judgment Calls**: items that failed a gate or couldn't be told apart from an
existing task are deliberately left unwritten pending his answer. That isn't a retreat from
auto-write — it's the narrow slice where writing *is* the expensive error, and it stays narrow. If
you find most of a run's output sitting in Judgment Calls, the gates are miscalibrated; say so in
the report instead of quietly treating the whole run as provisional.

**Always list what was skipped, with the reason.** Silent filtering reads as "covered everything",
and Step 2 skips the large majority of meetings — if he can't see that 25 sales calls were dropped
on purpose, he can't catch the day the filter wrongly drops a real one. Group them if the list is
long (`• 25 sales consultations — sales team recorders`), but never omit the count.

**Say when a wave was processed.** If more than 3 transcripts qualified, state plainly that N
meetings remain unprocessed and that re-running will pick them up. This is the most dangerous
silent truncation in the pipeline.

**Flag budget pressure.** If `wiki/tasks/_index.md` is near its ~1000-token ceiling, say so — it's
a signal that completed work needs archiving to `tasks/done/`.

**Quote the actual phrase in Needs Your Call.** "No deadline" is not useful on its own; `"cuando
puedas"` tells him instantly whether it was genuinely open-ended or something he'd forgotten he
committed to. Keep the original language and gloss it if it isn't obvious.

**Number the items** so he can answer "1 is Friday, 3 is next week" without retyping titles. Number
judgment calls `J1, J2…` so they can't be confused with written tasks when he answers.

**Judgment Calls carries the weight of the raised bar.** Step 4's two gates and Step 5's dedupe
default all resolve toward *not writing* — which is only honest if every discard stays visible.
Each entry needs the **quote, the timestamp, and which gate it failed**, because that's what lets
him overturn the call without rewatching anything. A bare "didn't write 3 items" is worse than
useless: it tells him something was dropped and gives him no way to check it.

Two calibration signals worth watching across runs:
- **Consistently empty** → the gates are too loose and junk is passing again, not that the calls
  were clean. A real window of meetings produces borderline items.
- **He reverses most of them** → too tight, or the gates are misreading a whole category of his
  work. Note the pattern in Self-annealing rather than reversing the bar wholesale.

Keep each entry to ~3 lines. This section is a decision queue, not a second report — if it's longer
than TASKS WRITTEN, say so plainly and ask whether the bar is wrong.

## Handling his answers

When he answers a deadline question:

1. Patch `deadline:` in the task's frontmatter, and bump `updated:`
2. Patch the matching line in `wiki/tasks/_index.md`
3. Re-evaluate `priority` — a date under 3 days out makes it high
4. If the item had a `**Timing:**` line, leave it. It records what was actually said; the new
   `deadline:` records what he decided. Both are true, and the second doesn't erase the first.

**Do not rewrite task bodies** when patching a deadline. The body is provenance.

If he answers something like "drop that one" — move it to `tasks/done/` per `task-manager`'s MARK
DONE flow, or delete it if it was a mis-extraction, and note which in your confirmation so the
mistake is visible and the filter can learn from it.

### When he overturns a judgment call

"Write J1" / "J3 merges into the Sara task" — act immediately, in the same session. The evidence is
still in front of you; asking him to re-run the sync to recover an item you deliberately withheld
would make the whole Judgment Calls mechanism cost more than it saves.

- **"Write it"** — he usually supplies the missing piece in the same breath ("the deliverable is
  the Webflow page"). Write the task with his words as the scope and the original quote as
  provenance, and note in the body that the scope came from him post-meeting rather than from the
  transcript — otherwise a future reader will look for it in the call and not find it.
- **"Merge it"** — append `## Update YYYY-MM-DD` to the existing task per `dedupe.md`.
- **No answer** — it stays unwritten. Don't carry it forward into the next run's report; it's in
  this report and in the transcript, and re-surfacing the same discards every run rebuilds the
  noise problem in a different place.

**Feed reversals back into the gates.** One overturn is Gaston's call on one item. A *category* of
overturn — say, he keeps writing tasks you rejected for thin scope because he knows what they mean
— means a gate is misreading his work, and belongs in Self-annealing as a documented exception with
his reasoning, not as a quiet loosening of the rule.
