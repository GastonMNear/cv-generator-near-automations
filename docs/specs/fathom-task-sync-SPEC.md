# BUILD SPEC — `fathom-task-sync` skill

**For:** the agent building this skill
**Repo:** `/Users/gastonmurillo/Documents/Near Automations/Near-AI-Agent`
**Vault:** `Near Work Partner/`
**Written:** 2026-08-19
**Status:** approved to build — nothing has been built yet

---

## 0. TL;DR of the task

Build a **new** skill at `.claude/skills/fathom-task-sync/SKILL.md` that:

1. Pulls Gaston's recent meetings from the **Fathom MCP** (already authenticated).
2. Fetches the **full transcript** of each and reasons over it *with the vault's business
   context loaded* — deliberately NOT trusting Fathom's own action-item extractor.
3. Writes real tasks into `Near Work Partner/wiki/tasks/`, deduped against existing tasks.
4. Prints a **report** of what it wrote, and **asks Gaston about deadlines it could not
   determine**.

Then make **two small edits** to the existing `meeting-ingest` skill (§9).

Do **not** merge this into `task-manager`. Rationale in §1.

---

## 1. Why a new skill, not an edit to `task-manager`

Gaston initially asked whether this could just edit `task-manager`. Recommendation was a
separate skill, and he asked for the reasoning to be included here so the builder doesn't
re-litigate it.

| | `task-manager` (exists, 186 lines) | `fathom-task-sync` (new) |
|---|---|---|
| Trigger | "add a task", "what's due", "mark X done" | "sync my meetings", "pull today's calls", daily run |
| Shape | Interactive CRUD, one task at a time | Batch pipeline: fetch → reason → dedupe → write → report |
| Input | Gaston's words | Fathom transcripts |
| Failure mode | Wrong single edit | Duplicate/noisy tasks at volume |

Merging them would roughly double `task-manager` and blend two trigger patterns, causing
misfires (a "what's due?" question should never hit the Fathom API). They share the *task file
format*, which is already documented in `task-manager` + `WIKI.md` — reuse that by reference,
not by copy-paste.

**Exception, already done:** the "ask about a task" feature (`EXPLAIN`) was added to
`task-manager` on 2026-08-19. Do not duplicate it. Read it — it defines the progressive
disclosure pattern this skill must stay compatible with.

---

## 2. Required reading before writing a line

| File | Why |
|---|---|
| `Near Work Partner/WIKI.md` | Schema, frontmatter, naming, **context budget contract** |
| `Near Work Partner/CLAUDE.md` | Vault behavioral rules + hard rules on transcripts/deadlines |
| `.claude/skills/task-manager/SKILL.md` | Task file format, `_index.md` format, `EXPLAIN` op |
| `.claude/skills/meeting-ingest/SKILL.md` | Meeting-note pipeline this skill delegates to |
| `.claude/skills/obsidian-wiki/SKILL.md` | Vault read/write discipline |
| `CLAUDE.md` (repo root) | Design principles, self-annealing rules |
| `Near Work Partner/wiki/context/team.md` | Who's who — needed for owner attribution |

**Follow `skill-creator` conventions.** Supporting files (`references/`, `scripts/`) live
alongside `SKILL.md` and load on demand — see `clay-api`, `linkedin-scoring-agent` for the
established pattern.

---

## 3. Verified environment facts (do not re-research)

### Fathom MCP — CONNECTED and working

Verified live on 2026-08-19. Authenticated as
`Gaston Murillo <gaston.murillo@hirewithnear.com>` via `get_identity`.

Available tools (all read-only):

```
mcp__claude_ai_Fathom__get_identity            → {name, email}
mcp__claude_ai_Fathom__list_meetings           → recording_id, title, url, recorded_by, invitees
mcp__claude_ai_Fathom__get_meeting_transcript  → full transcript w/ timestamped deep links
mcp__claude_ai_Fathom__get_meeting_summary     → Fathom's AI summary
mcp__claude_ai_Fathom__search_meetings         → keyword search (recorded_by REQUIRED)
mcp__claude_ai_Fathom__get_recording_by_url    → resolve a share/call URL → recording_id
mcp__claude_ai_Fathom__get_recording_by_call_id
mcp__claude_ai_Fathom__find_person
mcp__claude_ai_Fathom__list_teams
```

**`list_meetings` params:** `created_after`, `created_before` (ISO 8601), `recorded_by`
(array of emails), `teams`, `include_summary`, `include_action_items`, `max_pages` (1–20,
~10 results/page), `cursor`.

**`get_meeting_transcript` params:** `recording_id` (int, required), `url` (string — **pass
it**, it's what produces clickable `[MM:SS](url?timestamp=N)` deep links in the output).

### CRITICAL GOTCHA — two different IDs

The number in a Fathom URL is **not** the `recording_id`. Verified example:

```
title: "Weekly check" (2026-07-24)
recording_id: 167111420
url:          https://fathom.video/calls/758127739   ← different number
```

Always take `recording_id` from `list_meetings` / `get_recording_by_url`. Never parse it out
of a URL. Store **both** in meeting frontmatter.

### Rate limits (Fathom API, applies through MCP)

- Global **60 req/60s**; **heavy** requests (transcripts, summaries) **30/60s**, degradable
  to **5/60s** under load.
- The MCP tool description says: **fetch at most 3 transcripts per query — they are large.**
  Respect this. Batch/paginate; don't fan out 20 transcript calls.
- Pagination is opaque cursor-based (`next_cursor` → pass as `cursor`).

### What is NOT available

- **No `FATHOM_API_KEY` in `.env`.** MCP is the only path today. If unattended/cron use is
  ever needed, note that MCP OAuth tokens expire and cannot be re-authed headlessly — a
  direct API key (`https://api.fathom.ai/external/v1`, header `X-Api-Key`, available on all
  plans) would be the fallback. **Out of scope for v1 — do not build it.**
- No Monday/Notion/ClickUp credentials anywhere. **Vault-only. Do not add a board tool.**

---

## 4. Design decisions already made (do not revisit)

| # | Decision | Rationale |
|---|---|---|
| D1 | **Reason over the full transcript**, don't use Fathom's `include_action_items` as the source of truth | Fathom's extractor misses commitments phrased conversationally ("yeah I'll take that"), and has no business context. Gaston explicitly asked for transcript-level reasoning. May fetch Fathom's list as a **cross-check** to catch misses — but the vault-aware pass decides. |
| D2 | **Vault-only output.** No Monday/Notion/Sheets. | Board would be a second source of truth beside 21 existing vault tasks. Accepted tradeoff: **not shareable with teammates.** |
| D3 | **Never store transcripts in the vault.** | ~8–10k tokens of low-density filler per 45-min call. Store `recording_id` + `fathom-url`; refetch live when needed. This is a hard rule in `WIKI.md` + vault `CLAUDE.md`. |
| D4 | **Never invent a deadline.** | A guessed date in `deadline:` looks authoritative and silently misleads. No stated date → omit the key, record the phrasing in the body, **ask Gaston in the report**. |
| D5 | **Auto-write everything** (Gaston's choice), but deadlines are the exception per D4. | He wants the board populated without gating on approval. |
| D6 | **Gaston's tasks + "waiting on" items.** | Others' items only when they **block** him → separate lane. Pure others'-business items are captured in the meeting note, not as tasks. |
| D7 | **Delegate meeting-note creation to `meeting-ingest`.** | It already does bibliography + note + index + hot.md + log. Duplicating it means two places to fix. |
| D8 | **Quote budget: 2 lines max** of verbatim transcript per task. | Keeps tasks ≤250 tok. Link the Fathom timestamp for more. |

---

## 5. The pipeline

```
STEP 0  Load context (cheapest-first, per WIKI.md tier model)
        wiki/hot.md → wiki/index.md → wiki/tasks/_index.md
        → wiki/context/team.md, my-role.md
        Budget: ~3k tokens. This is what makes tasks business-aware.

STEP 1  Discover meetings
        get_identity() once → confirm email
        list_meetings(created_after=<since>, recorded_by=[gaston's email])
        Default window: since last run (see §8 state), else last 24h.
        NOTE: recorded_by filters to meetings Gaston RECORDED. Calls recorded by
        teammates that he attended will be missed — if he wants those, omit
        recorded_by and filter on calendar_invitees instead. Ask if ambiguous.

STEP 2  Filter before spending transcript calls  ← IMPORTANT, rate limits
        Skip: sales/consultation calls not involving Gaston's own workstream,
        meetings already ingested (check wiki/meetings/ for recording_id),
        recordings < ~5 min.
        Use title + attendees + (optionally) get_meeting_summary — summaries are
        cheaper than transcripts — to decide which deserve a full transcript.
        Cap at 3 transcripts per batch; if more qualify, process in waves and
        SAY SO in the report. Never silently truncate.

STEP 3  Fetch transcript
        get_meeting_transcript(recording_id, url)   ← pass url for deep links

STEP 4  Extract tasks (the core reasoning step — see §6)

STEP 5  Dedupe against existing tasks (see §7)

STEP 6  Write
        a) Meeting note → delegate to `meeting-ingest` (D7).
           MUST add recording_id + fathom-url to frontmatter.
        b) Task files → wiki/tasks/YYYY-MM-DD-{slug}.md, format per task-manager
        c) Update wiki/tasks/_index.md (one line per task, keep ≤1000 tok)
        d) Update wiki/index.md Meetings section (decision-grade line, ≤40 tok)
        e) Overwrite wiki/hot.md
        f) Prepend logs/ingest-log.md

STEP 7  Report to Gaston + ask deadline questions (see §8)
```

---

## 6. Task extraction — what "business-aware" means

This is the step that justifies a skill over a dumb script. With the vault loaded, the agent
should produce tasks that a stranger reading the transcript could not.

**Extract as a task when:**
- Gaston explicitly commits ("I'll do X", "I'll have that by Wednesday")
- Someone assigns him something and he doesn't decline
- A decision creates unavoidable work for him
- He says he'll follow up / send / check / build something

**Do NOT extract:**
- Hypotheticals ("we could maybe look at...") with no commitment
- Work explicitly assigned to someone else (→ "waiting on" only if it blocks him)
- Things already done during the call
- Vague aspirations with no actionable verb

**Owner attribution.** Use `wiki/context/team.md`:
Samuel (LinkedIn execution) · Hector (reply handling) · Franco (reporting) ·
Hayden, Camila (outreach) · Daniel, Andres (campaign decisions) · Felix (Girdley-side).
Gaston's email: `gaston.murillo@hirewithnear.com`.

**Task body must answer "what did I mean by this?"** — this is the feature Gaston explicitly
asked for. Required shape:

```markdown
# {Task title}

{1-3 lines: what it is and why it matters — the business context, not a transcript restatement.}

**Why:** {who asked, what it unblocks, what "done" looks like}
**Timing:** {verbatim phrase if no hard date — e.g. "when you get a chance"}

> {≤2 lines of verbatim quote — MAX}

**Source:** [[wiki/meetings/YYYY-MM-DD-slug]] · [Fathom @12:34](https://fathom.video/calls/N?timestamp=754)
```

Keep the whole file **≤250 tokens**.

### Priority inference (from `task-manager`)
`urgent`/`ASAP`/`today`/`tomorrow` or deadline <3 days → **high** ·
`whenever`/`no rush` → **low** · default → **medium**

### Deadlines — the D4 rule, restated because it matters
- Explicit date/day ("by Thursday", "before Friday the 24th") → set `deadline:`, resolve
  relative days against the **meeting date**, not today's date.
- Vague ("soon", "when you get a chance", "next sprint") → **omit `deadline:`**, put the
  phrase in `**Timing:**`, and **add it to the report's Needs-Your-Call section**.
- Never interpolate. "First thing when I'm back" is not a date unless his return date is known.

---

## 7. Deduping — the hard part

Runs daily; a recurring weekly meeting will re-discuss the same items. Naive string matching
will both duplicate and miss.

**Layer 1 — cheap, exact.** Key on `recording_id` — if a meeting's note already exists with
that `recording_id`, it's fully processed. Skip.

**Layer 2 — semantic, against open tasks.** Read `wiki/tasks/_index.md` (~870 tok, already
loaded in Step 0). For each candidate task, decide:

| Case | Action |
|---|---|
| Same work, already open | **Update** existing: append a `## Update YYYY-MM-DD` note, refresh `deadline`/`priority` if changed. Do NOT create a twin. |
| Same work, in `tasks/done/` | Create new **only** if genuinely recurring. Otherwise flag in report. |
| Related but distinct | Create new, add `related: ["[[existing]]"]` |
| Genuinely new | Create |

Real example of what Layer 2 must catch: a new call saying "fix the LinkedIn scoring per
Felix's notes" is the **same task** as the existing
`wiki/tasks/2026-07-22-correct-linkedin-clay-scoring-per-felix.md` — update it, don't duplicate.

**When unsure → create it and flag it in the report.** A flagged duplicate is cheap to merge;
a silently-dropped task is invisible. This is the one place to favor false positives, and it is
a deliberate exception to the repo's general "conservative actions" principle (which is about
*external* side effects — vault writes are cheap and reversible).

---

## 8. Output report + deadline Q&A

Print after every run. Exact shape Gaston asked for:

```
FATHOM SYNC — 2026-08-19          3 meetings · 2 processed · 1 skipped

TASKS WRITTEN (4)

  Confident deadlines
  [1] Launch Experiment 008           due 2026-08-21   "before Thursday"
  [2] Correct LinkedIn Clay scoring   due 2026-08-21   "same deadline"

  NEEDS YOUR CALL
  [3] Extend the email sequence       no deadline
      Daniel said "when you get a chance" — genuinely open-ended.
      → When do you want this by?

  [4] Purchase Clay credits           deadline?
      You said "first thing when I'm back" — I did NOT set a date.
      → Confirm?

UPDATED (1)
  [5] Correct LinkedIn scoring — added Felix's 2 new comments (existing task)

WAITING ON OTHERS (1)
  [6] Daniel to finalize copy for next experiment — blocks [1]

SKIPPED (1)
  • "Vada & Near consultation" — sales call, not Gaston's workstream

Vault: wiki/meetings/2026-08-19-weekly-check · 4 tasks · _index.md updated
```

**Rules for the report**
- Tasks are written **before** the report. Nothing is gated on Gaston answering (D5).
- After he answers, patch `deadline:` in frontmatter + the `_index.md` line. Do not rewrite bodies.
- **Always list what was skipped and why.** Silent filtering reads as "covered everything".
- If more than 3 transcripts qualified, say explicitly that it processed a wave and more remain.

### Run state
Store the last-run timestamp so `created_after` is correct. Suggested:
`Near Work Partner/logs/fathom-sync-state.json` → `{"last_run": "...", "last_recording_ids": [...]}`
Never store transcript content there. If missing, default to last 24h and say so.

---

## 9. Required edits to `meeting-ingest` (2 small changes)

**(a) Add `recording_id` + `fathom-url` to the meeting-note frontmatter template.** Currently
absent — without it every transcript refetch costs an extra `list_meetings` search. Template
in §Step 5 of that skill should become:

```yaml
recording_id: 166148624
fathom-url: "https://fathom.video/calls/756981297"
```

**(b) Update its Mode 1 (Fathom MCP) section.** It currently says to call
`mcp__claude_ai_Fathom__authenticate`, **which is not a real tool** and will fail. Replace with
the real flow: `get_identity` → `list_meetings` → `get_meeting_transcript(recording_id, url)`.

Also confirm its "Full Transcript" section keeps storing a **link, not the transcript** (it
already does — preserve that).

---

## 10. Constraints — non-negotiable

1. **Never store a transcript in the vault** (D3).
2. **Never invent a deadline** (D4).
3. **≤3 transcripts per batch**; report when more remain.
4. **Task files ≤250 tok; `wiki/tasks/_index.md` ≤1000 tok; `wiki/index.md` ≤2000 tok.**
5. **No `tags:` in task frontmatter**; omit empty `related`/`sources` keys entirely
   (trimmed across all 33 task files on 2026-08-19 — don't undo it).
6. **Never read `wiki/tasks/done/`** except to check for recurrence in dedupe Layer 2.
7. **Surgical writes** — append/update; never rewrite a note wholesale. `hot.md` is the one
   file that IS fully overwritten (per `WIKI.md`).
8. **No new external services or credentials.**
9. **Do not create or overwrite other skills without asking** (repo `CLAUDE.md`).

---

## 11. Acceptance criteria

Per repo `CLAUDE.md` §5 (Goal-Driven Execution) — verify, don't assume:

- [ ] Runs against a **real** Fathom meeting end-to-end
- [ ] Meeting note created with correct `recording_id` + `fathom-url`; **no transcript stored**
- [ ] Tasks created with `**Why:**` populated well enough that `task-manager`'s `EXPLAIN` can
      answer "what did I mean by this?" without fetching the transcript
- [ ] A vague-timing item produces **no** `deadline:` key and **does** appear in Needs-Your-Call
- [ ] Re-running on the same meeting creates **zero** duplicates
- [ ] A restated existing task **updates** rather than duplicating
- [ ] Report lists written / updated / waiting-on / skipped
- [ ] Answering a deadline question patches frontmatter **and** `_index.md`
- [ ] `wiki/tasks/_index.md` still ≤1000 tok afterward
- [ ] No broken wikilinks (verify with a link scan)

**Dry-run first.** Show Gaston the exact note + tasks + report for one real meeting **before**
writing to the live vault. He has 21 open tasks and 4 meeting notes that must not be corrupted.
Back up `Near Work Partner/wiki/` before the first real write.

---

## 12. Known open items

- **`2026-07-20-clay-lead-scoring-pipeline.md` has `recording_id: unresolved`** — no matching
  Fathom recording found for that date. Left explicit rather than guessed. If the builder
  identifies it, fill it in.
- **`recorded_by` scoping** (§Step 1) — v1 filters to meetings Gaston recorded. Confirm with
  him whether teammate-recorded calls he attended should be included.
- **Cron/unattended** is explicitly **out of scope for v1**. Build it invocable-by-hand first,
  prove it on real meetings, then discuss scheduling. MCP OAuth cannot re-auth headlessly.
- **`wiki/context/` is ~10.9k tokens** — the largest directory in the vault, bigger than all
  meetings and tasks combined. Not this skill's problem, but Step 0 should load `team.md` and
  `my-role.md` **selectively**, never the whole folder.
