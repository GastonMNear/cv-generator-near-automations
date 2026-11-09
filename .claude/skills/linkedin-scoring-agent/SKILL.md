---
name: linkedin-scoring-agent
description: >
  Fills `unknown` cells in columns I (Work Model) and K (AI JD Verifier) of the
  "LinkedIn List | Open jobs" prospecting sheet by reading each lead's LinkedIn job post,
  so stalled leads re-enter the outreach ranking. Use this skill whenever Gaston mentions
  the scoring sheet, the HMs list, unknown / missing Work Model or AI JD Verifier values,
  "fill the unknowns", backfilling the job-post backlog, US-Specific vs Remote-friendly
  classification, rows that aren't getting scored or prioritised, or an upstream Clay/API
  workflow that got blocked and left unknowns behind — even when he names neither this skill
  nor the columns. Drives LinkedIn through the `agent-reach` skill, so its
  references/career.md is required reading before any fetch. Writes only columns I and K,
  only to rows that currently read `unknown`, and never more than 40 job posts per run.
---

# LinkedIn Scoring Agent

Recovers leads that the upstream API workflow left as `unknown` in two columns of Gaston's
outbound prospecting sheet. Both columns feed the ranking the outreach team works from, so an
`unknown` row is invisible — a real lead sitting unworked.

| Col | Header | Read from | Effect on the lead |
|---|---|---|---|
| **I** | Work Model | the Remote/Hybrid/On-site **badge** | scores 15 / 10 / 5 points |
| **K** | AI JD Verifier | the job description **body prose** | `US-Specific` → Priority `Reject` |

One `get_job_details` call serves both columns — two independent readings of one payload. The badge
never informs K, and the body never informs I; that independence is the point (a `Remote`-badged post
routinely buries a licensing or work-authorization blocker in its body).

**Understand the asymmetry before you classify anything.** Writing `US-Specific` retires a lead, and
nothing downstream ever flags a mistake. Writing `Remote-friendly` on a bad lead merely costs a human
one JD read. Near's entire sales motion is convincing a US employer with a US-remote posting to hire
in LatAm — so **a stated US hiring geography is a sales objection, not a disqualifier.** Bias toward
`Remote-friendly`; that is a commercial decision, not timidity.

Full spec, formulas and validated fixtures: [`docs/unknown-filler-build-notes.md`](../../../docs/unknown-filler-build-notes.md).

## Rules that outrank everything else

1. **Only `unknown` triggers work.** Never re-derive, verify or "improve" a cell that already holds a
   value — not even when the fetched page plainly disagrees with it. Reading a value we won't change is
   wasted tokens and wasted account exposure.
2. **Write only I and K**, only on the tab with **gid `1674515397`**. Columns F, AB, AC and AI–AL are
   spilled ARRAYFORMULAs or out of scope; writing them breaks the sheet.
3. **Never parallelize LinkedIn.** One fetch at a time, in sheet order — `linkedin-scraper` drives
   Gaston's real logged-in account and a restriction is the worst outcome available here. Never two
   `mcporter` calls in one shell command, never a background job, never `parallel()`, and **never a
   second `plan_and_fetch.py` while one is running** (a lock enforces this, but don't rely on it —
   two runs share one browser session, which defeats every pacing rule at once).
4. **One fetch per job link, ever.** The scripts dedupe and cache; do not "just re-check" a post.
5. **Show Gaston the first real batch before running a larger one.** A full run can retire many leads.

## Preflight

1. **Invoke the `agent-reach` skill** (`/agent-reach`, or the Skill tool) and read its
   [`references/career.md`](../agent-reach/references/career.md). It owns the LinkedIn channel —
   `get_job_details` signature and response shape, badge-line layout, session handling, cold-start
   timing, account-risk rules — and this skill deliberately does not duplicate any of it. Go through
   agent-reach even though `plan_and_fetch.py` issues the actual `mcporter` call: you need its rules in
   context to judge a failure, and its command reference is the only sanctioned way to reach LinkedIn
   here. **Never invent your own LinkedIn access path** — no direct scraping, no Jina fallback on
   `linkedin.com/jobs`, no substitute tool.
2. Announce the channel, per agent-reach's standing rules: *"using agent-reach, LinkedIn via
   linkedin-scraper"*.
3. Confirm the backend is alive — `mcporter list` should show **linkedin-scraper (19 tools)**. If it is
   offline, stop; a missing session is a login problem, not something to retry through.
4. Confirm no other fetch run is active. `plan_and_fetch.py` enforces this with a lock, but if you are
   holding a work directory from an earlier run in this session, finish or abandon it rather than
   starting a second.
5. Run the dry-run below and compare it against what you expect. The sheet grows daily, so row numbers
   and counts **will** have drifted from the spec's snapshot — that is normal, re-measure rather than
   trusting it. A *structural* difference (renamed column, missing gid, moved tab) is different: the
   scripts stop with `STRUCTURAL:` and you should raise it with Gaston instead of adapting silently.

## Phase 1 — plan and fetch

```bash
# Always start here. Zero LinkedIn calls, zero writes.
python3 .claude/skills/linkedin-scoring-agent/scripts/plan_and_fetch.py --dry-run

# Live. Default cap is 40 fetches; use a small --limit for the first batch of a session.
python3 .claude/skills/linkedin-scoring-agent/scripts/plan_and_fetch.py --limit 3
```

Flags: `--dry-run`, `--limit N` (default 40), `--workdir PATH` (default
`tmp/linkedin-scoring/<UTC timestamp>`, gitignored — **never commit fetched payloads**), and
`--rows 97,72,96` to restrict a run to named sheet rows instead of sheet order.

**When Gaston asks for more High-priority leads, use `--rows` and do the arithmetic first.** Col I is
worth at most +15 and High needs `AB >= 50`, so **only rows already scoring 35–49 can be lifted to
High** — Low rows top out at Medium and Reject rows can't be rescued. Read `A2:AC` once (AB = score,
AC = priority) to rank candidates; that pool is typically only a handful of rows. See build-notes §11.8.

The script owns everything deterministic: OAuth, tab resolution by gid, header re-verification, the
scan, dedupe by job ID, the run cap, strictly sequential fetches with a random 2.0–5.0 s pause between
them, badge parsing, body extraction, and the abort conditions. It writes `manifest.json` after every
single fetch and keeps every raw payload in `payloads/`, so a crash between phases loses nothing and no
re-parse ever costs a second fetch.

It deliberately does **not** classify. Read the manifest, not the raw payloads — only bodies for rows
needing K ever reach your context, which is what keeps a 40-row run affordable.

Expect ~11.5 s per row (5–10 s warm fetch plus jitter; **~30 s on the first call while Chromium boots —
a slow first call is not a hang**). Roughly 8 minutes for a full 40-row run. Do not shorten the pacing.

**It aborts the whole run** on a challenge/CAPTCHA/"unusual activity"/logged-out response, or on two
consecutive failed fetches. On abort, rows already resolved keep their values but the rows in flight
stay `unknown` — a session-level problem is not the row's fault, and those rows deserve a clean retry.
If a run aborts, investigate the LinkedIn session before running again; do not immediately retry.

### Manifest fields you need

| Field | Meaning |
|---|---|
| `row` | 1-based sheet row — the write target |
| `needs` | `["I"]`, `["K"]` or both — which columns are still `unknown` |
| `identity_ok` | payload company/title matched col O/col G. **`false` → nothing gets written** |
| `badge` | `Remote` / `Hybrid` / `On-site`, or `null` if no badge line existed |
| `body_file` | body text path, present only when the row needs K |
| `writes` | cell values already decided mechanically (col I, and error/no-body rows) |
| `status` (top level) | `complete`, `cap-reached` or `aborted` |

## Phase 2 — you are the classifier

There is **no `ANTHROPIC_API_KEY` in this environment**, so column K cannot be a script that calls an
LLM. You do the classification yourself: read each body file the manifest points at and apply the
prompt below as your own instructions. That is by design, not a workaround — it also means you can
notice when a body is genuinely ambiguous instead of forcing a verdict.

Read each `body_file` **in full**. The disqualifier is often in the very last line, and a short body
(2.3k chars is normal) is not a truncated fetch. Classify per job ID, not per row — two rows sharing a
job post share one verdict.

Bodies normally end at a footer (EEO statement, benefits, pay range); the script strips LinkedIn's
trailing `…more` expander. If a body instead stops **mid-sentence**, that is genuine truncation — verdict
`Unknown`, and don't guess at the hidden tail. The raw payload is in `payloads/<job_id>.txt` if you need
to check something without spending another fetch.

### The JD Compliance Scan prompt

```
# JD Compliance Scan

Hard-reject gate. Decide whether a Latin America–based candidate — not physically in the US, holding
no US state licensure — could realistically qualify for and perform this role.

IGNORE any Remote/Hybrid/On-site badge. It is scored separately and is frequently inaccurate.
Judge ONLY the job description body text below.

CATEGORY 1 — a US-specific license/certification as the ONLY qualifying path.
  e.g. US life insurance licence, US real estate licence, state professional licensure, US CPA,
  US bar admission.
  - Mandatory with no alternative stated                → disqualifying
  - Explicit alternative present ("CPA or equivalent
    experience", "license preferred, not required")     → NOT disqualifying
  - Do NOT reject on the word "license" alone. Reject only when a US credential is the sole stated
    way to qualify.

CATEGORY 2 — physical-presence requirements the candidate could not perform from abroad.
  e.g. commute to a specific office, in-person meetings or events as a core duty, on-site
  responsibilities, hands-on/live support at a customer site, recurring required travel to US
  locations, covering a territory in person.

CATEGORY 3 — US work authorization, citizenship or legal-eligibility requirements.
  e.g. "must be eligible to work in the USA", "must be authorized to work in the US without
  sponsorship", "US citizenship required", security clearance, or a statute barring foreign
  nationals from the work (e.g. 52 U.S.C. § 30121 / 11 CFR 110.20 for PACs).

NOT disqualifying — never reject on any of these alone. Bias toward Remote-friendly; only a HARD
requirement the candidate could never satisfy counts:
  - *** A STATED US HIRING GEOGRAPHY IS NOT A DISQUALIFIER. *** "Remote (U.S.)", "Remote — US only",
    "Fully remote position within the United States", "located in one of the following states:
    TN, GA, AL…" — these describe where the employer is advertising, not something the candidate is
    incapable of meeting. Such an employer may well be open to a remote LatAm hire. Flag US-Specific
    only when a Category 1/2/3 blocker is ALSO present.
  - a pay-transparency disclosure naming the employer's city/postal code under a PAY RANGE or
    COMPENSATION heading (that is the employer's location, not a residency requirement)
  - US-style benefits — 401(k), medical/dental/vision, PTO, FLSA/exempt, W-2. These describe how the
    employer pays US staff; they are NOT a location requirement.
  - ADA/accommodation boilerplate about "physical requirements"
  - an EEO / equal-opportunity statement
  - a globally available certification (Microsoft, AWS, PMP, CFA) or a plain degree requirement
  - the company merely being US-based, or the location field naming a US city
  - conditional in-person duties that apply only to candidates already living in a given area
    ("DMV-based interns may be asked to…")

The test is always: "is there something here a LatAm-based remote candidate could NEVER satisfy?"
A licence they cannot hold, a place they must physically be, or a legal status they cannot have.
A company's stated preference for US-based hiring is a sales objection, not a disqualifier.

WORKED CONTRAST — the same state list, opposite verdicts:

  "Remote. Candidates must be located in TN, GA, AL, FL, NC or SC."
      → Remote-friendly. A geography preference and nothing else.

  "Remote. Must be eligible to work in the USA and located in TN, GA, AL, FL, NC or SC."
      → US-Specific, resting ENTIRELY on "eligible to work in the USA" (Category 3).
        The state list adds nothing and would not disqualify on its own.

  Shortcut: strike the geography clause and re-read. If nothing disqualifying remains → Remote-friendly.

Decision procedure — stop at the first match:
  1. Body text missing or unreadable → Unknown  (never default to Remote-friendly on an unread body)
  2. A Category 1/2/3 disqualifier with no valid alternative path → US-Specific
     Do not over-disqualify.
  3. Requirements still genuinely ambiguous after a careful read → Unknown
  4. No disqualifier found → Remote-friendly

Output exactly one of: Remote-friendly | US-Specific | Unknown
No other text.

--- JOB DESCRIPTION BODY ---
{job_posting_text}
```

### Recording verdicts

Write `verdicts.json` in the work directory, keyed by **job ID**:

```json
{
  "4443941231": "Remote-friendly",
  "4443959491": "US-Specific",
  "4442232139": "Unknown"
}
```

`Unknown` is a legitimate verdict here and maps to `Human review` at write time — that keeps this prompt
reusable in the upstream API workflow while loop-prevention stays in the skill. Never invent a verdict
to avoid it, and never write `Unknown` into the sheet yourself.

For each `US-Specific` verdict, note the decisive quote — Gaston reviews those, and a verdict you can't
quote evidence for is a verdict you should reconsider.

Before trusting a run, sanity-check yourself against
[`references/classifier-fixtures.md`](references/classifier-fixtures.md): five cases with known verdicts,
including the row 4 / row 140 pair that carries near-identical US location language and lands on
opposite verdicts. Anything that collapses that pair is wrong.

## Phase 3 — write and verify

```bash
python3 .claude/skills/linkedin-scoring-agent/scripts/write_results.py --workdir <dir> --dry-run
python3 .claude/skills/linkedin-scoring-agent/scripts/write_results.py --workdir <dir>
```

Always dry-run first and read the cell list — it is the last checkpoint before touching Gaston's
production prospecting list. The script re-resolves the tab, re-verifies the headers, re-checks each
row's identity against the **current** sheet contents (rows can be sorted or inserted between phases),
skips any target cell that no longer reads `unknown`, writes single-cell ranges in batches of 20, then
reads everything back and reports the `unknown` count delta per column. It refuses to run at all if any
fetched body lacks a verdict.

### Terminal states

Every row the skill touches ends terminal: a real value, or `Human review`. `unknown` means "never
attempted"; `Human review` means "attempted, unresolved". A row blocked once will block again, and
re-fetching it daily is pure account exposure for no gain. `Human review` scores 0 and forces no Reject,
so it changes no score and no priority — it just makes the row filterable.

| Situation | Write |
|---|---|
| Badge found | I ← `Remote` / `Hybrid` / `On-site` |
| Classifier returned a verdict | K ← `Remote-friendly` / `US-Specific` |
| Page loaded, no badge line | I ← `Human review` |
| Body ambiguous, or no `About the job` section | K ← `Human review` |
| Fetch errored / post deleted *(isolated failure)* | both needed cols ← `Human review` |
| Col M empty or no extractable job ID | both needed cols ← `Human review`, no fetch attempted |
| **Run aborted** — rows in flight | **leave `unknown`** (session problem, not the row's fault) |
| **Row-identity mismatch** | **write nothing at all** — the row number may now point at another lead |

Recovery path: a human sets a cell back to `unknown` to requeue it. There is deliberately no
`--retry-human-review` mode.

## Reporting to Gaston

Report: rows processed, cells written per column, the `unknown` delta, every `US-Specific` verdict with
its decisive quote, every row left `Human review` or skipped and why, and how many rows remain for the
next run. Log the run in the vault per `obsidian-wiki` conventions if the session touched the vault.

Surface doubt rather than smoothing it over — a `US-Specific` you were unsure about is exactly the thing
worth naming, because nothing downstream will catch it.

## Self-annealing

If runtime contradicts or extends the spec, update
[`docs/unknown-filler-build-notes.md`](../../../docs/unknown-filler-build-notes.md) in the same session,
and this skill if the procedure changed. Things worth capturing: a new body end-marker, an abort signal
the scripts didn't recognise, a badge variant, a JD pattern that fooled the classifier, or `mcporter`
output-shape changes. Do not silently patch around a structural sheet change — raise it.
