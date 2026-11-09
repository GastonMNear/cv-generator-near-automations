---
name: fathom-task-sync
description: >
  Syncs Gaston's recent Fathom meetings into the Near Work Partner vault — pulls transcripts,
  reasons over them with vault business context loaded, writes deduped tasks into wiki/tasks/,
  delegates the meeting note to meeting-ingest, and reports what it wrote plus any deadlines it
  could not determine. Use this skill whenever Gaston says "sync my meetings", "pull my calls",
  "catch me up on this week's meetings", "what did I commit to", "process my Fathom meetings",
  "any tasks from yesterday's calls", or asks for the vault to be brought up to date after a run
  of meetings. Also use it when he mentions falling behind on meeting follow-ups or wants to know
  what came out of a specific recent call. This is the batch pipeline — for a single pasted
  transcript use meeting-ingest, and for one-at-a-time task CRUD use task-manager.
---

# fathom-task-sync

Batch pipeline: Fathom meetings → business-aware tasks in the vault → report.

The value here is not transcription — Fathom already does that. It is that this runs **with the
vault loaded**, so it produces tasks a stranger reading the transcript could not write: it knows
who Samuel is, that "the scoring thing" is an existing open task, and that a restated commitment
is an update rather than a new item.

## What this skill owns vs. delegates

| Concern | Owner |
|---|---|
| Which meetings matter, transcript budget | **this skill** |
| Task extraction + dedupe + deadline discipline | **this skill** |
| The run report | **this skill** |
| Meeting note, bibliography, index/hot/log updates | `meeting-ingest` |
| Task file format, `_index.md` format, EXPLAIN | `task-manager` (read it for format) |
| Vault read/write discipline | `obsidian-wiki` |

Don't reimplement a delegate's job. If a task file's shape is unclear, read `task-manager` rather
than guessing — it and `WIKI.md` are the contract, and drifting from them is how the vault rots.

---

## Step 0 — Load context (~3k tokens, cheapest-first)

This is what makes the output business-aware. Read in this order, and stop early only if the run
is scoped to one already-known meeting:

1. `wiki/hot.md` — what happened recently
2. `wiki/tasks/_index.md` — **the dedupe baseline.** Every open task, one line each.
3. `wiki/meetings/_index.md` — which meetings are already ingested
4. `wiki/context/team.md` — who's who, for owner attribution
5. `wiki/context/my-role.md` — what counts as Gaston's workstream

Read `wiki/context/` **selectively** — it is ~10.9k tokens, larger than all meetings and tasks
combined. `team.md` and `my-role.md` only.

---

## Step 1 — Discover meetings

```
get_identity()                    → confirm gaston.murillo@hirewithnear.com
list_meetings(created_after=<since>, include_action_items=true, max_pages=3)
```

**Do not pass `recorded_by`.** Gaston attends calls that teammates record — the Aug 17 Marketing
Stand Up was recorded by Micaela, and filtering to his own recordings would silently drop it.
Filter on `calendar_invitees` containing his email instead, plus recorder identity.

> [!warning] **Corrected 2026-09-01 — Gaston DOES have a recorder account.** An earlier run
> concluded he had none (because `search_meetings` with `recorded_by:
> ["gaston.murillo@hirewithnear.com"]` returns *"No user found for the provided recorded_by email"*)
> and recorded that his 1:1s were "structurally absent from Fathom". **That was wrong.** The Sep 1
> run found three meetings `recorded by Gaston Murillo` — `178357794`, `178722833`, `178414004` —
> including his Daniel 1:1 and his Hector 1:1. **`list_meetings` without a `recorded_by` filter
> surfaces his own recordings fine**, which is what this skill already does.
>
> What remains true: **`search_meetings` requires `recorded_by` and errors on his email**, so it is
> useless for discovery here — use `list_meetings` + cursor paging. And the Aug 24 / Aug 25 notes
> carry `recording_id: null` because they were pasted transcripts; those two can never be backfilled.
>
> **Lesson worth keeping:** a failure in one endpoint was generalised into a claim about the account,
> and that wrong claim then shaped two runs' reports ("no *recorded* internal meetings"). When an API
> says no, scope the conclusion to that call.

`include_action_items=true` is worth it here: it is far cheaper than a transcript and gives a
useful pre-filter signal (a meeting with action items assigned to Gaston almost certainly deserves
a transcript). Treat it as a **cross-check, not the source of truth** — see Step 4.

**Window:** read `logs/fathom-sync-state.json` for `last_run`. If missing, default to the last 24h
and **say so in the report** — a silently-narrow window looks like "nothing happened".

> [!warning] **Don't trust the state file's window alone — cross-check the vault.** On the Sep 11 run
> `fathom-sync-state.json` still recorded the Aug 27–Sep 1 window, while `hot.md` and
> `logs/ingest-log.md` both showed a completed Sep 2–7 run. A run had written its notes and log but
> not its state file. **Grep the actual `recording_id`s out of `wiki/meetings/*.md` and diff against
> what `list_meetings` returns** — that is the only authoritative record of what is ingested. Costs
> one Bash call and prevents re-ingesting a whole window:
> `grep -h "^recording_id:" wiki/meetings/*.md | sort -u`

---

## Step 2 — Filter before spending transcript calls

This step matters more than it looks. In a real sample of 30 meetings since Jul 22, **25 were sales
consultations** recorded by the sales team. Skipping them is most of the job — without this filter
the 3-transcript budget gets burned on calls that contain zero tasks for Gaston.

**Skip:**
- **Sales/consultation calls.** Reliable pattern: title matches `* & Near – Complimentary remote
  recruiting consultation`, or `{Company} <> Near`, and the recorder is sales
  (**Laura Temponi Soares, Pedro Vasconcelos, Gianluca Vendramini, Camila Bagnati, Carlos Barrera**).
  These are the sales team's workstream, not Gaston's. In the Aug 10-19 run this filter alone
  removed ~40 of 72 discovered meetings. Also skip **client/candidate calls** that don't match
  those title patterns but are still sales-side: `{Company} + Near`, `{Company} // Near`,
  `sync: Near & {Company}`, `Carlos + {Name} | AE Near`, `Meet with {Name} at Near`. In the
  Aug 24-27 run, 33 of 34 discovered meetings were removed by this filter — a normal result,
  not a sign the window is wrong. The Aug 27-Sep 1 run removed **35 of 41**. Expect the sales team
  to account for **~85-97% of every window**; that ratio holding is the filter working, not a
  discovery failure.
- **Already ingested** — a meeting note already carries that `recording_id` (dedupe Layer 1).
- **Internal calls with no Gaston-owned commitments.** Some qualify on every other signal but
  contain nothing for him — a rescheduled sync, a stand-up he only listened to. Check
  `include_action_items` from Step 1 first: if nothing is his and the title suggests a status
  round-up, skip it and **say so in the report with the reason**. Three meetings were correctly
  skipped this way in the Aug 10-19 run (Aug 13 Marketing Stand-Up `173064693`, Aug 13 impromptu
  `173049799`, Aug 11 Weekly Metrics `172309498` — rescheduled, no items).
- **Recordings under ~5 minutes** — rarely carry commitments.
- **Company-wide all-hands and delivery-side calls.** New in the Sep 1 run: `Biweekly Near Meeting`
  (75 invitees, sole action item belonged to Franco) and `Near + Ascend // Weekly Sync` (client
  delivery / PIP work). Gaston is an invitee on both but owns nothing in either. Distinguish from
  stand-ups by invitee count and by whether the agenda touches campaigns, Clay, or reporting.

**Onboarding and training sessions qualify — they are not "internal noise."** The Sep 8–11 window was
**6 of 7 qualifying meetings spent onboarding one new hire**, and it produced the highest-severity
finding the vault has recorded (production API credentials pasted into Slack) plus the numbers
explaining a missed weekly target. A session where Gaston *teaches* a system is where the system's
undocumented rules get spoken aloud — lookup keys, routing tiers, framing rules, tribal workarounds.
**Treat a long training call as high-value, not low.**

> [!warning] **Never filter on title alone — check the recorder.** The single most valuable call of
> the Sep 1 run was titled **"Impromptu Google Meet Meeting"** with no invitee list; it was the
> 69-minute leadership deck build with Daniel, and it produced 8 tasks including the RB2B webhook
> discovery. **A generic or empty title on a meeting `recorded by Gaston Murillo` is a strong
> process signal, not a weak one** — he records his own working sessions and Google Meet names them
> badly. Treat `recorded by Gaston Murillo` as near-automatic qualification.

**Process:** internal team calls where Gaston is an invitee — weekly checks, stand-ups, alignment
calls, 1:1s with Daniel/Samuel/Hector/Felix, anything about campaigns, Clay, LinkedIn, reporting,
or deliverability.

**Unsure?** `get_meeting_summary(recording_id)` is much cheaper than a transcript — use it to
decide. If it's still ambiguous, process it; a skipped real task is invisible, a wasted summary
call is not.

### Transcript volume — the real constraint, and how to beat it

The nominal guidance is 3 transcripts per query (heavy-request limit 30/60s, degradable to 5/60s).
But the binding constraint in practice is **context, not rate**: transcripts in the Aug 2026 window
ran 61k chars / 143-227 lines and **exceed the MCP response token cap** — they save to a file and
must be read in ~25-line chunks.

**So don't read transcripts into your own context.** Delegate each one to a subagent that reads the
file and returns only structured JSON (tasks, owners, quotes, timestamps). The raw Spanish text
never enters the orchestrating context, and a 6-meeting batch becomes feasible — this is what made
the Aug 10-19 run work against a nominal 3-transcript cap.

**Verified again 2026-09-01:** three transcripts (49 min, 69 min, 13 min) were delegated to three
parallel subagents and all returned structured JSON. Two came back **in full, inline** — no file
chunking needed — so the "always exceeds the cap" note is not universal; a ~49-min Spanish call fit.
Delegation is still the right default because it keeps the raw text out of the orchestrating context
regardless. Give each subagent the **vault dedupe candidates and the meeting date** in its prompt:
that is what lets it flag `possible_duplicate_of` and resolve relative deadlines itself, and both
came back correct without a second pass.

**Give each subagent the Step 4 gates too — they are the only ones who read the actual words.** A
subagent that returns every mention forces you to filter on its summaries, and by then the evidence
you'd need to reject something (the exact phrasing, who spoke, whether anyone accepted) is gone.
Ask each one to apply both gates itself and return its rejects separately, so a discard is still
backed by a quote you can put in the report. Required per candidate:

```json
{
  "deliverable": "one line: physical action + how you'd know it's done, from the transcript only",
  "ownership_evidence": "the quote where Gaston took it, or someone assigned it to him",
  "speaker": "who said it", "timestamp": "MM:SS",
  "possible_duplicate_of": "vault task slug, or null",
  "gate_failed": "ownership | concreteness | same-day | null",
  "reject_reason": "one line, when gate_failed is set"
}
```

If a subagent can't fill `deliverable` or `ownership_evidence` from the transcript, that *is* the
gate failure — it should return the item with `gate_failed` set rather than inferring a plausible
scope. Instruct it explicitly not to help: an eager subagent writing "presumably this means
deploying the landing page" produces exactly the task this skill is trying to stop making.

**Verified again 2026-09-11: six transcripts in two waves of three, all returned structured JSON.**
Totals ran 20–145 min including a 2.4-hour session. Space the waves, but 6 is demonstrably fine.

Stay mindful of the rate limit when fanning out (space the calls), but treat 3 as a *default*, not
a ceiling. If you do stop short of what qualified, **say explicitly in the report that a wave was
processed and N remain**. Silent truncation reads as "covered everything", which is the one thing
the report must never imply.

---

## Step 3 — Fetch transcript

```
get_meeting_transcript(recording_id, url)     ← pass url, always
```

`url` is what produces clickable `[MM:SS](url?timestamp=N)` deep links. Those links are how a task
written today stays answerable in three months — they're the citation, so a task without one costs
a future `list_meetings` search.

> [!warning] The number in `https://fathom.video/calls/<n>` is **not** the `recording_id`.
> Verified: "Weekly check" is `recording_id: 173602241` but lives at `/calls/783947351`.
> Never parse an ID out of a URL. Take it from `list_meetings`, and store **both** in frontmatter.

**Meetings are often conducted in Spanish.** Reason over the Spanish transcript directly, but write
**all vault content in English** — that's what every existing note uses, and mixing languages breaks
search. A verbatim quote may stay in Spanish; add a short English gloss if the meaning isn't obvious.

**Fathom's diarization is unreliable on long calls.** Speaker labels drift inside long merged turns
— observed on the Aug 13 and Aug 18 recordings, and on **3 of 6** Sep 8–11 transcripts. On the
2.4-hour Sep 9 call labels **inverted wholesale after ~1:37**, attributing Gaston's own teaching to
the trainee. In a training call the tell is reliable: **whoever is explaining the system owns it.** Do not attribute a commitment on the label alone:
ground ownership in *content* and in who owns the system being discussed. If Ivan owns JustCall
config, a JustCall commitment is his even when the label says otherwise.

---

## Step 4 — Extract tasks

Read `references/extraction.md` for the full rules, the required task body shape, and worked
examples. The short version:

### Two gates — a candidate becomes a file only if it passes both

The board was at **~44 open tasks** when these gates were written (2026-09-11) — you saw the current
count in Step 0's `_index.md`. At that size a junk task costs more than a missed one: the transcript
stays refetchable forever via `recording_id`, so a dropped item is recoverable, while a bad task is
removable only by hand and quietly erodes trust in the whole board. Both gates exist to protect that
board. Apply them to every candidate, including ones Fathom's `action_items` handed you.

**Gate 1 — Ownership. Someone has to have actually put this on Gaston.**

He said he'd do it, or someone assigned it to him and he didn't decline. That's the whole test.

Topic adjacency is **not** ownership. "Gaston owns campaigns, this is about a campaign, therefore
it's his" is the inference that fills the board with work nobody gave him — he attends calls to
decide, advise, and listen, and most of what's discussed in them belongs to someone else or to
no one. If you cannot point at the moment of assignment or commitment in the transcript, it does
not pass, however clearly it sits in his domain.

Watch for three shapes that mimic commitment:
- **Agreement that something should happen** — "sí", "dale", "exacto" confirming a plan is not the
  same as taking the work. Ask who would do it, and whether anyone said so.
- **Open questions about status** — *"I think the routine is done, I have to check"* is a thing to
  find out, not a thing to do. It belongs in the meeting note's Open Questions.
- **Work the team agreed on with no named owner** — real, but unassigned. Meeting note, and raise
  it in the report if it looks like it will fall to him by default.

**Gate 2 — Concreteness. Write the action and the done-condition in one line, from the transcript alone.**

If you can't, the transcript didn't contain a task — it contained a mention. Concretely: name the
physical action ("send X to Y", "rename the table", "load the CEO list into the dialer") and how
you'd know it was finished, using only what was actually said. No inference about what it probably
means.

The reliable tell that you've failed this gate is hedging in your own draft. If the body you're
writing says *"scope is thin in the transcript"*, or *"if the scope isn't obvious, the deck slide is
the reference"*, or *"check first — this may already exist"* — stop. That prose is the task telling
you it isn't one yet. A real example the old rules let through: **"Ship the soft technical landing
deploy"**, whose entire evidence was Daniel asking *"we're doing it this week, right?"* and Gaston
answering *"Sí."* Nobody in that exchange said what shipping it involves. It is a deck line item,
not a task, and three weeks later Gaston can't act on it either.

This gate also protects dedupe. A vaguely-scoped task is an **unmatchable** task: the next meeting
that touches the same topic can't recognise it as the same work, so a twin gets written. Most of
the duplicate problem starts here, not in Step 5.

**Also discard:**
- **Same-day / in-call actions** — things he does during the call or right after it ("ahora yo le
  contesto", "let me Slack him now"). By the time he reads the report it's done or moot, and it
  lands as noise. If it's genuinely multi-day work that merely *starts* with a message, that's a
  task — write the work, not the message.
- Hypotheticals with no commitment, things completed during the call, vague aspirations with no
  actionable verb.
- Work explicitly owned by someone else → the **waiting-on** lane, and only if it blocks him.

**When a candidate fails either gate, it is not silently dropped** — it goes to the report's
*Judgment Calls* section with the quote, timestamp, and which gate it failed, so Gaston can say
"actually, write that one." See Step 7.

> [!warning] **An action item can be narrower than the event it describes.** On Sep 9 Fathom logged
> *"Delete SmartLead credentials from Slack after Lila changes password."* The transcript showed the
> session also pasted the **entire `.env` bundle — Smartlead API key, Google Docs and Clay
> credentials** — into Slack. Acting on the summary alone would have rotated one password and left
> three live API keys exposed. **When an item implies a security, access or data-exposure event,
> read the surrounding transcript to size the real scope before writing the task.**

**Use Fathom's `action_items` as a cross-check, never as the source.** Its extractor misses
conversational commitments ("yeah, I'll take that") and has no business context. After your own
pass, compare against its list — anything it caught that you missed deserves a second look, and
anything you caught that it missed is usually the reason this skill exists. Its `assigned to` field
is a genuinely useful signal for owner attribution and for the waiting-on lane.

**Never invent a deadline.** Explicit date → set `deadline:`, resolving relative days ("by
Thursday") against the **meeting date**, not today's. Vague ("soon", "when you get a chance") →
omit the key, put the phrase in `**Timing:**`, and raise it in the report's Needs-Your-Call
section. A guessed date looks authoritative and silently misleads — that's worse than an absent one.

---

## Step 5 — Dedupe

Runs often; recurring meetings re-discuss the same items. Read `references/dedupe.md` for the
decision table. The core of it:

**Layer 1 (exact):** `recording_id` already in a meeting note → fully processed, skip.

**Layer 2 (semantic): compare deliverables, not titles.** Gate 2 made you state each candidate's
action and done-condition in one line. That line — not the title — is what you match against the
vault, because two tasks worded differently can produce the identical deliverable, and two sharing
a title can mean different work.

Baseline is `wiki/tasks/_index.md` from Step 0. Its lines are titles, so they can only surface a
*candidate* match. Whenever one looks plausible, **open that task file** (~250 tok) and compare
deliverables before deciding. Reading one or two files is far cheaper than either failure mode.

Same deliverable already open → **update** it (append `## Update YYYY-MM-DD`), don't create a twin.
Genuinely different deliverable → create, and link via `related:`.

**When you can't tell whether it's the same work, don't write it — surface it in the report.**

This reverses what this skill said before, and the reason matters, because the old rule was correct
when it was written. With a near-empty vault a missed task was the expensive failure and a
duplicate was a two-second merge, so "create and flag" was right. At ~44 open tasks the cost has
inverted: duplicates are what make the board unreadable, and nothing is actually lost by waiting —
the item appears in the report with its quote and timestamp, and the transcript is refetchable via
`recording_id` indefinitely. Gaston says "write it" and the next run does.

> [!warning] **The failure this fixes was a verdict, not a miss.** The Sep 8 run correctly spotted
> that its Sara task duplicated an open one — the body it wrote says *"this is the **second**
> outstanding 'send Sara materials' item... Worth sending together in one Slack message"* — linked
> it via `related:`, and then created the file anyway, because "when unsure, create and flag" told
> it to. Both files now carry the same update block. **If you find yourself writing prose that
> explains how a new task relates to an existing one, you have already decided it's a duplicate.**
> Update the existing task, or surface it — don't narrate the overlap into a second file.

**Dedupe across the batch, not just against the vault.** Two meetings in one window routinely
restate the same item; merge them into one task with both meetings in `sources:`.

---

## Step 6 — Write

**a) Meeting note FIRST → delegate to `meeting-ingest`.** It owns bibliography + note + index +
hot.md + log. Pass it the transcript and require `recording_id` + `fathom-url` in the frontmatter.

Write the note **before** the task files, even though tasks feel like the point. The note's
`recording_id` is what dedupe Layer 1 keys on — if a run writes tasks and then dies before the note
lands, the meeting looks unprocessed and the next run duplicates every task. Note first means a
crash costs you a re-run, not a cleanup.

**b) Task files** → `wiki/tasks/YYYY-MM-DD-{slug}.md`, format per `task-manager`. Body shape and
budgets are in `references/extraction.md`.

**c) `wiki/tasks/_index.md`** — one line per task. **The sections are time horizons, not priorities**
(restructured 2026-08-19): `## This Week (<dates>)` · `## Next Week (<dates>)` · `## Backlog`. The
old High/Medium/Low split stopped carrying information once the backlog was cleared — don't
reintroduce it. `priority:` still lives in each task's frontmatter; the index sorts by *when*.

File a new task under the horizon its deadline implies, and mark blocking relationships inline —
`| **blocks Ivan**`, `| blocked on BigQuery`, `| gates the above` — since that is what makes the
index readable without opening files. Keep it **≤1000 tokens**; if it's near the ceiling, say so in
the report rather than letting it sprawl.

**d) `wiki/index.md`** — decision-grade Meetings line (≤40 tok). `"discussed deadlines"` is
useless; `"4 deliverables due Jul 24; Clay credits → Aug 1"` is not.

**e) `wiki/hot.md`** — the one file that is fully overwritten, per `WIKI.md`.

**f) `logs/ingest-log.md`** — prepend, newest at top.

**g) `logs/fathom-sync-state.json`** — `{"last_run": "<ISO>", "last_recording_ids": [...]}`.
Never put transcript content here.

**Never store a transcript in the vault** — not in the note, not in the log, not in the state file.
Store `recording_id` + `fathom-url` and refetch live. A 45-min call is ~8-10k tokens of
low-density filler; the TLDR replaces it. Hard rule in `WIKI.md` and the vault's `CLAUDE.md`.

---

## Step 7 — Report

Tasks that **passed both gates** are written before the report — those aren't gated on Gaston
answering. Only judgment calls wait. Full format and rules in `references/report-format.md`.

Every run reports: what was **written**, **updated**, **waiting on others**, **skipped with
reasons**, and **judgment calls** — candidates that failed a Step 4 gate or were too close to an
existing task to call, each with its quote and timestamp.

**The Judgment Calls section is what makes the raised bar safe.** Gates 1 and 2 and the Step 5
default all resolve toward *not writing*, which is only defensible if the decision stays visible.
Listing each discard with the evidence lets Gaston overturn it in a sentence — and a section that's
consistently empty across runs means the gates are set too loose, not that the calls were clean.

When he answers a deadline question, patch `deadline:` in the task frontmatter **and** its
`_index.md` line. Don't rewrite the body — the body is provenance.

---

## First run on a live vault

Gaston has 22 open tasks and 4 meeting notes that must not be corrupted. On the first real run, or
any run touching many meetings at once, **show him the exact note + tasks + report for one meeting
before writing**, and back up `Near Work Partner/wiki/` first. After it's proven, run it directly —
the auto-write default is deliberate (he wants the board populated without gating on approval).

## Self-annealing

After each run, cache what you learned: a new sales-call title pattern for Step 2, a teammate not
yet in `team.md`, a recurring meeting whose items always restate. Update this skill or the relevant
reference file in the same session — a filter that has to be rediscovered every run isn't a filter.

**Watch the gates specifically.** They were tightened 2026-09-11 after the board reached ~44 open
tasks, and they are the part of this skill most likely to be wrong in either direction:

- **Gaston reverses the same *kind* of judgment call repeatedly** → a gate is misreading a category
  of his work. Record the exception and his reasoning here; don't just start writing that category
  again silently.
- **Judgment Calls is empty run after run** → the gates aren't biting. Real windows produce
  borderline items; a clean sheet usually means the old permissive reading crept back.
- **Duplicates still appear despite Step 5** → check whether the twins' Gate 2 lines were crisp. A
  vague deliverable is unmatchable, so recurring duplicates are usually an extraction failure
  surfacing one step late, not a dedupe failure.

**Revisit the bias if the board size changes materially.** The don't-write default is calibrated to
a full board, and `dedupe.md` explains the arithmetic. If the vault is ever cleared back to a dozen
open tasks, the cost of a miss rises again and the default deserves rechecking — the principle is
that the default protects the scarce resource, which today is Gaston's attention.

**Sales-recorder roster (Step 2 filter), current as of 2026-09-11:** Laura Temponi Soares, Pedro
Vasconcelos, Gianluca Vendramini, Camila Bagnati, Carlos Barrera, **Fred Delvaux** (added — he
recorded ~10 consultations in the Sep 8–11 window and appeared in no earlier roster).

**Ratio check:** sales/client calls were **49 of 58** discovered meetings (~85%) in the Sep 8–11
window, consistent with the 85–97% expectation. That ratio holding is the filter working.

**Run 9 (2026-09-28, Sep 11–25):** 125 of 138 were sales/client (~91%). New sales-side title shapes, all
from rostered recorders: `Kickoff call - Hire with Near …`, `Intro Call: {Co} & Hire With Near`,
`Follow up: {Co} & Near`, `sync - Near ({Name})`, `Meeting with {Name}`, and bare `{Name} and {Name}`
(Fred). `max_pages=20` returned all 138 in one call with no cursor. The output exceeds the token cap and saves to a
file, so **grep it rather than reading it**. Filtering on recorder roster + excluding the consultation title
isolated the 11 internal meetings in one pass.

**When Gaston supplies a status update mid-run, give it to every subagent** and add an
`already_done_per_gaston` flag to the candidate schema. On run 9 that caught **9 of 16** accepted candidates
as already finished. Without it they would have been written as open tasks the day he'd reported them done.

**A targeted run must not move the sweep window.** Run 8 (single URL) overwrote `fathom-sync-state.json`, so
`last_run` pointed at Sep 14 while the last *sweep* ended Sep 11. Derive the window from the last sweep's
`window_covered`, and keep diffing `recording_id`s against the vault.

**Run 10 (2026-10-05, Sep 25 – Oct 2):** 59 of 66 were sales/client (~89%). `Mock call` (Carlos Barrera) is AE
training, so it's sales-side. **Both "Impromptu Google Meet Meeting" recordings by Gaston were again among the most
valuable calls**: the Oct 6 deck handoff and the Lila CNAME session. **Subagents can write the meeting note +
bibliography themselves** if the brief points them at an existing note to copy. That kept the orchestrator to task
dedupe and index work, and all 6 came back clean. Put the shared rules in one scratchpad brief file and keep each
agent prompt to the meeting-specific details. **Watch for self-set dates that have already passed:** the run
happens days after the meetings, so "hoy" commitments (CallTools API Sep 30, playbook video Oct 1) are overdue by
the time the report lands. Report them as "done?" rather than writing them as new deadlines.

**Run 10 judgment calls:** Gaston overturned 2 of 4 (J1, J4). **J1 is the pattern to watch.** It was rejected as
same-day because he said *"voy a mandarles en este momento"*, but it had **not** been sent five days later, and it
blocks a high-priority task (the DMU). **When a same-day promise gates another open task, still reject it, but
list it at the top of Judgment Calls and point out what it blocks.** J4 merged into an existing task instead of
becoming a new file, because the existing task's decision was already settled and only the build was left.

**Run 11 (2026-10-13, Oct 2–13):** 52 of 60 were sales/client (~87%). **Gaston now titles his own recordings**
("EXP013 building session", "Clay Session - Workflow maintenance", "Ale - Gasti Sync"), so the "Impromptu"
signal is weaker, but `recorded by Gaston Murillo` still qualified every internal call. **When Gaston pastes a
weekly focus message, treat its items as owner-confirmed tasks.** Gate 1 is satisfied by his own list. Still
apply Gate 2, and ask about vague lines like "[Update] - volume session next steps" instead of writing them.
**Several "send X the doc" promises to different people on the same day were grouped into one checklist task**
rather than three files. The goal was less board noise without losing any of them.
**Run 11 judgment calls:** Gaston rejected all 6 ("don't add any as tasks"), including meeting-only follow-ups, standing
habits (weekly close-out to Andrés), and unscoped ideas (an AI daily Clay check, defining Alexia's scope). That suggests
the gates are set right for these categories. **Viktor is an AI agent**, not a teammate. Don't attribute human tasks
to him.

**Run 12 (2026-10-19, Oct 13–19):** 41 of 45 were sales/client (~91%). The **Oct 13 Outbound volume session was
recorded by Carlos Barrera**, a rostered sales recorder. **Don't let the recorder filter drop the huddle.** Check
the title and invitees (Gaston + leadership) before skipping a rostered recorder's call. **Fathom attributed 2
items to Gaston that the transcript doesn't support:** a group decision ("switch huddle to bi-weekly") and Lila's
own "reconnect from my Claude" (a diarization drift). Re-check every `assigned to Gaston` item, especially in
1:1s with a single other speaker. **A ✅ in Gaston's focus message can be contradicted by a later meeting**
(Viktor test workflow, ✅ Oct 13 → "ahí quedó" Oct 16). Have subagents flag contradictions with prior ✅s, not
just duplicates. `bibliography/_index.md` hasn't been updated since Aug 25, and no run maintains it.
**Run 12 judgment calls:** Gaston rejected all 6, the second run in a row with 100% rejections. Same-day promises (even
ones that gate other work), group decisions Fathom assigned to him, calendar events, and "sounds good" to a
"we" proposal all correctly stay out. Gates look right for these categories. **Status recaps arrive right after
the report:** he closed 6 items and cleared 2 waiting-on lines in two messages. A "✅" on a focus item can mean
"my part is done, now on someone else" (Chili Piper → Paz). Archive the task and move the remainder to waiting-on;
don't keep it open as his.
**Waiting-on lane = only what blocks Gaston (Gaston, Oct 19).** He removed every Carlos and Felix line because
"they don't depend on me". Don't log teammates' own action items there just because they came up in his
meetings. Keep a line only if Gaston's next step waits on it.

**Run 13 (2026-10-23, Oct 19–23):** 40 of 45 were sales/client (~89%), plus the Biweekly all-hands. All 4 internal
calls were Gaston's own recordings or ones he had an item in. **A short window can still carry a manager-set deadline
that has already passed** (HireBase readout, EOD Oct 22, ingested Oct 23). Write it with the real date and flag it
"sent?" rather than dropping it. **Two meetings describing one deliverable from different angles** (Andrés: "net new
by Oct 22", stand-up: "overlap over the 2-week trial") were merged into one task with both in `sources:`. **"Charly" /
"Charlie" in transcripts = Carlos Barrera** (manages the AEs).


**Run 14 (2026-11-03, Oct 23 – Nov 3):** 78 of 83 were sales/client (~94%). **Kickoff calls recorded by Fred or
Gianluca** (`Kickoff call - Hire with Near + {Name}`, `Near Kick-Off Call`, `Kick-Off Call - Hire with Near between …`)
are delivery-side. Skip them. **A meeting already ingested by a targeted run sits inside the sweep window** (Oct 29
volume session). The recording_id grep caught it, which is why that grep is mandatory. **Two Fathom MCP servers can be
present.** `mcp__fathom__*` disconnected mid-run, but `mcp__c931b28c-…__get_meeting_transcript` kept working. Name
both in the subagent brief so a disconnect doesn't stall a wave. **Lila 1:1s mostly produce Lila's work and
waiting-on changes, not Gaston's tasks.** Expect 0–1 new tasks from them, plus waiting-on edits.

**Run 15 (2026-11-09, Nov 3–9):** 29 of 30 were sales/client (~97%), and the 30th was the Nov 3 Lila 1:1 that
run 14 had already ingested. **An empty window is a valid result.** No internal meetings were recorded Nov 4–9
(Andrés was still OOO; Gaston confirmed he returned Nov 9 and no 1:1 had happened yet). Don't go looking for something to write. Update the
state file and log, and tell Gaston which recurring meetings you expected but didn't find. Then he can say whether
they happened unrecorded. **Delivery-side `Near Sync + {Client}` calls** (Fred, with recruiters) are client work.
Skip them.
