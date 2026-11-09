# Handoff Brief — build the "unknown filler" skill

Context and instructions for the agent authoring this skill. The technical spec is a **separate
document**; this file deliberately does not repeat it.

**Read [`unknown-filler-build-notes.md`](unknown-filler-build-notes.md) first and treat it as
authoritative.** It is a validated spec, not a draft: every rule in it was tested against live rows and
signed off by Gaston. Where it states a rule, implement it as written rather than re-deriving it.

---

## 1. Your task

Build a production skill in this repo that fills `unknown` values in two columns of a live Google Sheet
by reading the corresponding LinkedIn job post. The spec document defines the sheet, the columns, the
algorithm, the classifier prompt, the safety rules and the validated test cases.

You are **authorized to create this skill** — the repo's usual "don't create skills without asking" rule
has been satisfied by Gaston explicitly requesting it.

## 2. Why this exists (business context, not in the spec)

HireWithNear ("Near") places **remote Latin American talent into US companies**. The sheet is an outbound
prospecting list of hiring managers with open roles, scored and ranked so the outreach team knows whom to
contact first.

The two target columns feed that ranking:

- **Work Model** — a remote or hybrid posting is a warmer prospect than an on-site one, so it earns points.
- **AI JD Verifier** — a hard-reject gate. If the role genuinely *cannot* be filled by someone based in
  LatAm, the lead is worthless no matter how good its score, and it gets rejected outright.

An upstream API workflow fills both, but gets blocked often enough to leave a large `unknown` backlog.
Those rows are effectively invisible to the ranking, so real leads sit unworked. This skill recovers them.

Two consequences worth internalising, because they shape every judgment call:

1. **Marking a role US-Specific retires a lead.** It is the most consequential write in the sheet and
   nothing downstream flags a mistake. The spec's instruction to bias toward `Remote-friendly` is a
   commercial decision, not timidity.
2. **A US company advertising a US-remote role is the target customer, not an excluded one.** The entire
   sales motion is convincing exactly that employer to hire in LatAm. This is why a stated US hiring
   geography is explicitly *not* a disqualifier — a rule that is counter-intuitive enough that a fresh
   agent tends to get it backwards. The spec has a worked contrast for it; honour it.

## 3. Repo conventions you must follow

- Read `CLAUDE.md` at the repo root before starting. Its design principles govern this work —
  particularly **accuracy over speed**, **conservative actions on anything external-facing**, and
  **surgical changes**.
- Skills live at `.claude/skills/<name>/SKILL.md`, with optional `scripts/` and `references/`
  subdirectories loaded on demand. Frontmatter is `name` + `description` (see
  `.claude/skills/clay-api/SKILL.md` for the house style — the description should be written so the skill
  auto-triggers on relevant requests, not just on an explicit slash command).
- **Register the new skill in the "Available Skills" table** in `CLAUDE.md` — and note that `CLAUDE.md`
  and `AGENTS.md` are kept **byte-identical**. Edit both or the convention breaks.
- LinkedIn access goes through the existing `agent-reach` skill →
  `mcporter call 'linkedin-scraper.<tool>(…)'`. Its
  `references/career.md` already documents `get_job_details` response shape, badge-line parsing, session
  handling and rate/account risk. **Reference it; do not duplicate it** into your new skill.
- Self-annealing is expected: if you learn something at runtime that contradicts or extends the spec,
  update the spec document in the same session.

## 4. Environment constraints (verified — these change the architecture)

- **`python3` is 3.9.6.** No `match` statements, no 3.10+ syntax, and **no backslashes inside f-string
  expressions** (this bites when building A1 ranges — it is a real error, encountered during validation).
- **There is no `ANTHROPIC_API_KEY` in `.env` or the shell.** You therefore **cannot** implement the JD
  classifier as a script that calls an LLM API. Classification must be performed by **you, the agent
  running the skill**, reading the body text and applying the spec's prompt as your own instructions.
  Design the skill around that constraint — it is the single biggest architectural fact here.
- Google Sheets credentials are in `.env` at the repo root; see the spec's auth section for the scope
  subtlety, which is easy to misread as "no access".
- `mcporter` is on PATH. `mcporter list` should show `linkedin-scraper` with 19 tools before you rely on it.

## 5. Recommended architecture

A three-phase design that puts deterministic work in code and judgment in the agent:

1. **`plan_and_fetch.py`** — authenticate, scan the sheet, build and dedupe the work list, apply the run
   cap, then fetch sequentially with the required jittered pacing and abort conditions. For each row:
   run the identity check, parse the badge deterministically (no judgment needed), extract the body, and
   write it to a scratch work directory. Emit a JSON manifest: row number, job ID, identity-check result,
   badge verdict, path to the body file, and which columns this row still needs.
2. **You** — read the manifest, read body files only for rows needing column K, classify each per the
   spec's prompt, and record verdicts back into the manifest.
3. **`write_results.py`** — re-verify identity, write single-cell ranges, verify, and report.

Why this split:

- All the account-safety behaviour (sequential order, jitter, cap, abort) lives in code, where it cannot
  be forgotten mid-run under context pressure.
- Badge reading is mechanical and needs no model.
- Only K bodies enter your context. The spec's 40-row cap conveniently doubles as a context bound —
  ~40 bodies at ~5k chars is manageable, whereas the full backlog would not be.
- A crash between phases loses nothing: the manifest and bodies are already on disk.

You may deviate if you see something better, but keep those four properties.

Use the session scratchpad (or `tmp/`) for the work directory — **never** commit fetched payloads.

## 6. Deliverables

1. `.claude/skills/<name>/SKILL.md` — when to use it, inputs/flags, the run procedure, the classifier
   prompt, and the safety rules. Name it something an agent would match on naturally (e.g.
   `sheet-unknown-filler`).
2. The supporting scripts.
3. A `--dry-run` mode: scan and report the work plan (row counts, per-column breakdown, planned fetches)
   with **zero** LinkedIn calls and **zero** writes. This is how the skill gets verified without cost.
4. `CLAUDE.md` + `AGENTS.md` updated with the skill registered.
5. Spec document updated if you learned anything new.

## 7. How to verify without burning LinkedIn calls or corrupting data

- **Start with `--dry-run`** and confirm the work plan matches a manual read of the sheet.
- **Test the classifier against the spec's validated examples.** Five rows with known-correct verdicts and
  the decisive evidence quoted. Rows 4 and 140 are the critical pair — they contain similar US location
  language and land on *opposite* verdicts. A prompt or implementation that gets both right is very likely
  correct; one that collapses them is wrong.
- **Then run a genuinely small live batch** (2–3 rows) and present the results to Gaston before running
  anything larger. He has asked to review the first real batch, since a full run could retire many leads.
- Recount `unknown` values before and after; the delta must equal the number of rows written.

## 8. Do not

- Parallelize LinkedIn calls, or fetch the same link twice. Account safety outranks throughput absolutely.
- Touch any tab other than the one named in the spec, or any column other than I and K.
- Re-read, verify or "improve" cells that already hold a value, even when the fetched page disagrees.
- Drain the whole backlog as a "test".
- Implement anything for column F. It is out of scope by decision, and its prompt is a separate artifact.

## 9. If reality disagrees with the spec

The sheet is live and grows daily, so row numbers, counts and the backlog figures in the spec **will**
have drifted — re-measure at runtime rather than trusting the snapshot. That kind of drift is expected.

But if you find a *structural* difference — a renamed column, a changed formula, a tab that moved — stop
and raise it rather than adapting silently. The spec's facts were verified; a contradiction means
something changed underneath, and guessing risks writing wrong data into Gaston's production prospecting
list.
