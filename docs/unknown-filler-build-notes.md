# Spec — Spreadsheet "Unknown" Filler

Validated build spec for a skill that fills `unknown` values in columns **I (Work Model)** and
**K (AI JD Verifier)** of a Google Sheet by reading the job post on LinkedIn.

Every rule here was verified against live data (col I on 5 rows, col K on 5 rows) and signed off.
**Column F (HM Bucket Label) is out of scope** — fixed upstream instead; its prompt lives in
[`hm-bucket-label-prompt.md`](hm-bucket-label-prompt.md).

> **Implemented as the `linkedin-scoring-agent` skill** (2026-08-06) —
> `.claude/skills/linkedin-scoring-agent/`. See §11 for what the build changed or learned.

---

## 1. Purpose

New leads land in the tab daily. An upstream API workflow populates I and K but sometimes gets blocked,
leaving `unknown`. The skill recovers the real value from LinkedIn and writes it back to the correct row.

| Col | Header | Source of truth | Reads |
|---|---|---|---|
| **I** | Work Model | the Remote/Hybrid/On-site **badge** | badge line only |
| **K** | AI JD Verifier | the job description **body text** | body prose, badge ignored |

One `get_job_details` call serves **both** columns — two independent readings of one payload.

Trigger: **manually invoked**, may become a scheduled routine later. Keep the entry point a single
non-interactive invocation so scheduling needs no refactor.

---

## 2. Target sheet

- **Spreadsheet ID**: `1nkf2qDx06lY14cXUUj_S7rFbUNsu_Xo547yqWAEwOEk` (title: `LinkedIn List | Open jobs`)
- **Tab**: `HMs list | No Email Found | Scoring System` — **resolve by gid `1674515397`**, 42 cols

⚠️ **Never match the tab by name.** Three tabs are near-identical (all 1059×42):

| gid | Title | |
|---|---|---|
| `1674515397` | `HMs list \| No Email Found \| Scoring System` | ✅ **use this** |
| `1818776469` | `Copy of HMs list \| …` | ❌ |
| `260901045` | `Priority ranking \| HMs list \| …` | ❌ |

15 tabs total; the rest are `[Old]` archives.

### Columns

| Letter | Idx0 | Header | Role |
|---|---|---|---|
| E | 4 | Prospect Title | — |
| F | 5 | HM Bucket Label | out of scope; **never write** |
| G | 6 | Imported Job Title | **identity check** |
| **I** | 8 | **Work Model** | **TARGET** |
| J | 9 | Near Fillability | — |
| **K** | 10 | **AI JD Verifier** | **TARGET** |
| **M** | 12 | **Job LinkedIn URL** | **fetch input** |
| **O** | 14 | **Company Name** | **identity check** |
| AB, AC | 27, 28 | Total Score, Priority | formula — **never write** |
| AI–AL | 34–37 | the four score columns | formula — **never write** |

**Re-verify letters against row 1 at runtime** — 42 columns leaves room for insertion.

### Gotchas

- **Col A is empty on every data row** → counting rows via col A returns 1. Use **col M or D** for extent.
- Tab name contains `|` and spaces → quote it in A1 ranges (`'HMs list | No Email Found | Scoring System'!I3`)
  and URL-encode the range in the request path.
- Some col M URLs are percent-encoded (`…engineer-%E2%80%93-pathology…`). **Regex the trailing digits**
  for the job ID; don't URL-parse the slug.
- Allowed values — `I`: `Remote` `Hybrid` `On-site` `unknown`. `K`: `Remote-friendly` `US-Specific`
  `Unknown`. Casing differs between columns but **comparisons are case-insensitive**, so casing is
  cosmetic. Write canonical casing; never "fix" legacy lowercase rows.
- **No data validation or dropdowns** on I or K — free text, so a new sentinel value needs no schema change.

---

## 3. Scoring formulas and write constraints

All six are **single spilled ARRAYFORMULAs in row 2**:

```
AB2 (Total Score)  =ARRAYFORMULA(IF(F2:F="", "", AI2:AI+AJ2:AJ+AK2:AK+AL2:AL))

AC2 (Priority)     =ARRAYFORMULA(IF(F2:F="", "",
                     IFS( K2:K="US-Specific", "Reject",
                          J2:J="Reject",      "Reject",
                          AB2:AB>=50, "High",
                          AB2:AB>=35, "Medium",
                          AB2:AB>=20, "Low",
                          TRUE, "Reject") ))

AI2 (HM seniority) IFS on F → Founder/CEO 15 · C-level 10 · VP/Head 10 · Director/Manager 7 ·
                              HR/Talent 0 · IC/low authority 0 · TRUE 0
AJ2 (Role Family)  IFS on H → Sales 15 · GTM/Marketing 15 · Engineering/Product/Data 15 ·
                              Finance/Accounting 10 · CS 5 · Admin/Support 5 · Ops 5 ·
                              Recruiting/Talent 5 · TRUE 0
AK2 (Role-fit)     IFS on J → Near-fillable 15 · Maybe-fillable 10 · TRUE 0
AL2 (Work Model)   IFS on I → Remote 15 · Hybrid 10 · On-site 5 · TRUE 0
```

Consequences:

1. **Write only to I and K.** Writing into a spilled ARRAYFORMULA range breaks it.
2. **Col I is scored. Col K is not** — K contributes zero points anywhere. Its only effect is
   `K="US-Specific" → Priority "Reject"`. So **K is the most consequential column in the sheet despite
   scoring nothing: one write can retire a lead.** (AK/Role-fit is driven by col J, not K.)
3. Every score column gates on `IF(F2:F="","")`, so a **blank** F blanks the whole score row. `unknown`
   in F is fine (scores 0 via `TRUE,0`). Blank F is an upstream data problem — **this skill takes no
   action on it and never writes F.**

---

## 4. Google Sheets auth

No Sheets MCP and no Drive connector is authorized. Use the OAuth creds already in `.env` (same ones
`call-prep-doc-filler` uses): `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN`.

Scopes are `auth/documents` + `auth/drive` — **there is no `auth/spreadsheets` scope, but Sheets API v4
accepts `auth/drive`**, so full read/write works. Do not conclude "no access" from the missing scope.

```
POST https://oauth2.googleapis.com/token
  grant_type=refresh_token, client_id, client_secret, refresh_token
→ access_token (1 h TTL)
```

A long batch can outlive the hour → **refresh proactively, don't wait for a 401.**

---

## 5. Run algorithm

### 5.1 Scan and plan (one read, no fetches)

Read `A2:M<last>`. Select rows where col I **or** col K, stripped and lowercased, `== 'unknown'`.
Keep each row's 1-based sheet number — that's the write target. **Skip rows already marked
`Human review`.**

Then derive per-row work, and let it drive exactly what gets parsed:

| Row state | Fetch | Parse badge? | Run JD classifier? |
|---|---|---|---|
| I unknown, K has a value | 1× | **yes** | **no — skip entirely** |
| K unknown, I has a value | 1× | no | **yes** |
| both unknown | 1× | yes | yes |
| neither | **none** | — | — |

The JD classifier is the expensive step (multi-thousand-token body read). Skipping it on I-only rows is
where most of the token saving lives.

**Dedupe the work list by job ID before fetching** so two rows sharing a URL cost one fetch.

### 5.2 Hard efficiency rules

- **`unknown` is the ONLY trigger.** Everything else is invisible to the skill.
- **Never re-derive, verify or "improve" a column that already holds a value** — not even when the
  fetched page plainly disagrees with it. No comparison, no discrepancy logging, no second look. Reading
  a value we won't change is wasted tokens and wasted account exposure. *(Observed: row 146 held `Remote`
  while the live badge read `On-site`. Correctly left alone.)*
- **One fetch per link, ever.** Cache the payload in memory keyed by job ID and serve both columns from
  it. The `Human review` sentinel enforces this across runs.

### 5.3 Pacing — protecting the LinkedIn account

`linkedin-scraper` drives Gaston's **real** logged-in account. A ban is the worst outcome available to
this skill, and outranks throughput in every trade-off.

- **Strictly sequential.** One row, one fetch at a time. **Never** parallel — not via `parallel()`, not
  background jobs, not two `mcporter` calls in one shell command. A single browser session backs it all.
- **Pause 2.0–5.0 s between rows**, drawn with **random jitter, not a constant** — a fixed gap produces a
  perfectly flat timing histogram, which is itself a machine fingerprint.
- Fetch takes 5–10 s warm (**~30 s cold start** while Chromium boots — a slow first call is not a hang),
  so real inter-request gaps land at 7–15 s. Budget ≈11.5 s/row → **~19 min per 100 rows.** Don't shorten it.
- **Run cap: default 40 rows**, overridable. Bounds a run to ~40 requests / ~8 min. Daily inflow is
  ~12 new rows (~6 new unknowns), so 40 stays ahead of the backlog. On hitting the cap, stop cleanly and
  report processed vs. remaining; untouched rows keep `unknown` and no sentinel is written.
- **Abort the entire run** on a challenge/CAPTCHA/"unusual activity" page, an auth wall or logged-out
  session, or **two consecutive failed fetches**. Never grind through errors — a run of failures is
  precisely what precedes a restriction. On abort keep every row already written, report the reason, stop.
- *Deliberately declined: a longer breather every ~25 rows. Jitter + run cap already bound exposure.*

### 5.4 Fetch

```bash
mcporter call 'linkedin-scraper.get_job_details(job_id: "4439299810")'
```

Job ID = trailing numeric segment of the col M URL; the slug is decorative:
`…/jobs/view/plaintiff-counsel-at-nybacs-4439299810` → `4439299810`.

Returns `{url, sections: {job_posting: "<text blob>"}, references: {…}}` — **not structured JSON**, parse
the text yourself.

### 5.5 Verify row identity BEFORE writing — the critical guard

Payload **line 1 = company**, **line 2 = job title**. Cross-check both against that row's **col O** and
**col G**. Exact string equality was sufficient on all 10 validated rows (including an `(A4AL)` suffix),
though normalization tolerance is worth keeping.

**On mismatch: write nothing at all, log the row, move on.** A mismatch means the URL is stale or rows
shifted, so the captured row number may now point at a *different lead* — writing anything (even the
sentinel) could stomp another row's good data. This is the one case that overrides the terminal-state
rule in §6: that rule governs *what value to write*; the identity check governs *whether we may write to
this row at all*.

### 5.6 Write, then verify

- **One single-cell range per value** (`I3`, `K3`, `I4`, …), never a block — a block write shifts if the
  row set isn't contiguous. Batch them:

```
POST /v4/spreadsheets/{id}/values:batchUpdate
{ "valueInputOption": "USER_ENTERED",
  "data": [ {"range": "'<tab>'!I3", "values": [["Remote"]]}, … ] }
```

- **Checkpoint as you go** — write in small batches rather than accumulating everything for one final
  write, so an interruption doesn't lose completed work.
- Afterwards read back the touched cells plus the recalculated score column, and confirm the unknown
  count moved by exactly the number of rows written.

### 5.7 The sheet is live — don't trust cached row numbers

Measured overnight: **192 → 204 data rows**, unknowns 86 → 92. Growth was append-only and the 5 rows
edited the previous day held their positions — **but a `Priority ranking` tab exists, implying sorting
happens somewhere in this workbook.** A long run gives someone time to sort or insert. Mitigation is the
§5.5 identity re-check immediately before each write.

---

## 6. Terminal state — the `Human review` sentinel

**Every row the skill touches ends in a terminal state: a real value, or `Human review`.** Never leave
`unknown` behind on a row that was attempted. `unknown` means "never attempted"; `Human review` means
"attempted, unresolved". Rationale: a row blocked once will likely block again, and re-fetching it daily
is pure account exposure for no gain.

| Situation | Write |
|---|---|
| Badge found in first ~10 lines | I ← `Remote` / `Hybrid` / `On-site` |
| Body read, classifier returned a verdict | K ← `Remote-friendly` / `US-Specific` |
| Page loaded but no badge present | I ← `Human review` |
| Body read but genuinely ambiguous | K ← `Human review` |
| Fetch errored / blocked / empty payload *(isolated failure)* | both target cols ← `Human review` |
| Job post deleted / expired | both target cols ← `Human review` |
| Col M empty or no extractable job ID | both target cols ← `Human review`, **no fetch attempted** |
| **Run aborted** (§5.3) — rows in flight | **leave `unknown`** — session-level problem, not the row's fault |
| **Row-identity mismatch** (§5.5) | **write nothing** |

**Zero-impact verified** against every formula: `I="Human review"` falls to `TRUE,0` → 0 points; K
contributes no points at all and `"Human review"` isn't `"US-Specific"` so it forces no Reject. Switching
a cell from `Unknown` to `Human review` therefore changes no score and no priority, while making the row
trivially filterable.

**Recovery path:** a human sets the cell back to `unknown` to requeue it — no code change needed. An
opt-in `--retry-human-review` mode could be added later, but must never be the default.

---

## 7. Column I — reading the badge

`sections.job_posting`, split on newlines with blanks stripped:

```
line 1  Company Name              ← identity check
line 2  Job Title                 ← identity check
line 3  Location · posted · applicants
line 4  Promoted by hirer · …             (SOMETIMES ABSENT)
        $165K/yr - $195K/yr               (SOMETIMES PRESENT)
        Remote | Hybrid | On-site         ← THE BADGE
        Full-time | Part-time | Contract
```

**Never parse by fixed line number** — the promo line and salary line are both optional and shift
everything below. Observed: NYBACS had no promo line; ACM Global's salary line sat *directly above* the
badge, so a fixed-index parser would have written `$165K/yr - $195K/yr` into Work Model.

**Method:** scan the first ~10 non-blank lines for an exact match against `{Remote, Hybrid, On-site}` —
LinkedIn emits precisely that casing. No match → `Human review`.

**Never infer the work model from description prose.** That is column K's job, using different logic, and
the two readings must stay independent.

---

## 8. Column K — the JD compliance gate

A hard-reject gate, **deliberately independent of the badge**: a post badged `Remote` can still bury a
licensing or presence requirement in the body. A `Remote` badge + `US-Specific` body is a valid and
common combination — 3 of 4 `Remote`-badged validation rows were `US-Specific`.

### 8.1 Body extraction

- **Starts** at the literal marker `About the job` (present in 5/5 payloads). Everything before it is
  header chrome — it holds the badge but no requirements.
- **Ends** at the first of: `Set alert for similar jobs`, `Put your best foot forward`,
  `Job search faster with Premium`, `Benefits found in job post`, `Featured benefits`.
- Observed lengths 2.3k–7.9k chars. **A short body is not a truncated fetch** — don't treat brevity as failure.
- **The disqualifier is often in the very last line.** Read the whole body; never classify from the first N chars.

### 8.2 Classifier prompt

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

### 8.3 Mapping output to the sheet

**The prompt's `Unknown` must never reach the sheet** — it always maps to `Human review` at write time.
This keeps the prompt reusable in the upstream API workflow (where `Unknown` is legitimate) while
loop-prevention lives in the skill.

| Prompt output | Written to K |
|---|---|
| `Remote-friendly` | `Remote-friendly` |
| `US-Specific` | `US-Specific` |
| `Unknown` | `Human review` |
| *(prompt never ran — fetch failed)* | `Human review`, or `unknown` if the run aborted (§6) |

### 8.4 Over-disqualifying is the failure mode that costs money

Over-disqualifying silently retires a viable lead and nothing downstream flags it. Under-disqualifying
merely means a human reads a JD that wasn't a fit. **Bias toward `Remote-friendly`.**

Three traps confirmed on live rows, all now guarded in the prompt:

1. **Work authorization was a missing category.** The original prompt had only licence (Cat 1) and
   presence (Cat 2); 2 of 5 rows failed on eligibility to work in the US, which is neither. → Category 3.
2. **A stated US hiring geography is not a blocker.** A US company advertising a US-remote role *is*
   Near's target customer — the whole pitch is converting that posting into a LatAm remote hire.
   Rejecting those would discard the most qualified part of the pipeline. The gate exists to catch
   candidates who *cannot* do the job, not employers who haven't yet considered hiring abroad.
3. **Pay-transparency and benefits boilerplate look like residency rules.** `CITY: Rochester` /
   `POSTAL CODE: 14624` under a `PAY RANGE` heading, and ADA "physical requirements" language, would each
   have flipped a genuinely `Remote-friendly` role.

---

## 9. Validated examples — use as regression fixtures

11 cells written across 8 rows, all reviewed and accepted.

**Col I** (badge reading, mechanical): row 3 NYBACS `Remote` · row 4 Johnson Group `Remote` ·
row 5 Glatfelter `Hybrid` · row 7 Exreprotein `On-site` · row 8 ACM Global `Remote` ·
row 9 Balance Ophthalmics `Remote`.

**Col K** (the judgment calls):

| Row | Company / Title | Badge | Verdict | Decisive evidence |
|---|---|---|---|---|
| 4 | Johnson Group — Account Director | `Remote` | **US-Specific** | *"Must be eligible to work in the USA"* (Cat 3). Its 12-state list contributes **nothing** |
| 8 | ACM Global Labs — Director of Cloud Software Eng. | `Remote` | **Remote-friendly** | `Location: Remote`; Microsoft/AWS certs are global; no licensure, no presence duty |
| 9 | Balance Ophthalmics — U.S. Strategic Account Manager | `unknown`→`Remote` | **US-Specific** | *"live procedure support"*, *"case coverage during initial device installations"*, *"travel up to ~50% within assigned territory"* (Cat 2) |
| 140 | Collaborative Fund Services — Fund Administrator | `Remote` | **Remote-friendly** | `Location: Remote (U.S.)` and *"Fully remote position within the United States"* are geography only — no licence, presence duty, or eligibility clause |
| 146 | A4AL — Legislative Intern (Volunteer) | `On-site` ᵃ | **US-Specific** | *"Under 52 U.S.C. § 30121 and 11 CFR 110.20, foreign nationals without legal authorization are prohibited from volunteering or employment with PACs"* (Cat 3) |

ᵃ Live badge. Col I already held `Remote` on this row, so col I was **not** written — the documented case
for §5.2 (never correct an existing value).

Rows **4 and 140 are the key pair**: both contain US state/country location language, and they land on
opposite verdicts purely because row 4 adds a work-authorization clause. Any change to the prompt must
keep both correct.

Row 9 proves the one-fetch-two-columns path — a single call resolved I and K.

**Snapshot when authored** (will drift; re-measure at runtime): 204 data rows; 100 need work — 36 I-only,
9 K-only, 55 both → **100 fetches, 64 classifier runs**, all job IDs present and distinct.

---

## 10. Invariant checklist

1. Resolve the tab by **gid `1674515397`**; verify column letters against row 1.
2. Write **only** to I and K. Never AB, AC, AI–AL, or F.
3. **`unknown` is the only trigger**; resolve only the unknown column(s); never audit existing values.
4. **One fetch per link, ever.** Cache by job ID; dedupe the work list.
5. **Strictly sequential**, 2.0–5.0 s jittered pause, 40-row default cap, abort on trouble.
6. **Identity-check col O + col G against payload lines 1–2 before every write.** Mismatch → write nothing.
7. Every touched row ends **terminal** — real value or `Human review`. Exceptions: identity mismatch
   (write nothing) and aborted runs (leave `unknown`).
8. Refresh the OAuth token proactively (1 h TTL).
9. Single-cell write ranges; checkpoint in small batches.
10. **Bias toward `Remote-friendly`** — over-disqualifying costs real leads and is invisible afterwards.

---

## 11. Implementation notes (added 2026-08-06 during the build)

Skill: `.claude/skills/linkedin-scoring-agent/` — `SKILL.md`, `scripts/plan_and_fetch.py`,
`scripts/write_results.py`, `references/classifier-fixtures.md`.

### 11.1 Architecture forced by the environment

**There is no `ANTHROPIC_API_KEY` in `.env` or the shell**, so the col K classifier cannot be a script
that calls an LLM. The agent running the skill *is* the classifier: phase 1 writes body text to disk,
the agent reads it and applies §8.2 as its own instructions. Three phases:

1. `plan_and_fetch.py` — auth, gid resolution, header re-verification, scan, dedupe, run cap,
   sequential jittered fetches, badge parse, body extraction, abort conditions → `manifest.json`.
2. **The agent** — reads only the bodies for rows needing K, classifies per job ID, writes
   `verdicts.json` (`{job_id: verdict}`) into the work directory.
3. `write_results.py` — re-verifies identity against the *current* sheet, writes single-cell ranges in
   batches of 20, reads back, reports the `unknown` delta per column.

Both scripts take `--dry-run`. Work directory defaults to `tmp/linkedin-scoring/<UTC ts>` (gitignored).
Keying verdicts by **job ID rather than row** falls out of the dedupe rule: two rows sharing a job post
share one verdict, so the classification can't be done twice.

### 11.2 Confirmed at runtime

- The §9 snapshot still holds exactly: **204 data rows, 100 needing work (36 I-only, 9 K-only,
  55 both), 100 distinct job IDs, 64 classifier runs.** No structural drift; headers E F G I J K M O all
  in place; gid `1674515397` resolves to the expected title.
- `unknown` counts on 2026-08-06: **I: 91, K: 64.**
- Identity checking is **exact on 3/3 rows of the first live batch** (`Glatfelter Insurance Group`,
  `Shoreline AI`, `INIT Innovations in Transportation, Inc.`), matching the 10/10 rate in §5.5. The
  scripts additionally accept a `loose` match (one side contained in the other, min 8 chars) so a
  suffix drift degrades to a write rather than a skip; anything else is `mismatch` → write nothing.
- Col K's legitimate value `Unknown` **is** the trigger, since comparisons are case-insensitive
  (row 5 held `Unknown` and was correctly queued). No special-casing needed.
- `mcporter call ... --output json` returns parseable JSON; `sections.job_posting` is found by walking
  the tree, which also tolerates a JSON-encoded MCP text block.

### 11.3 New: bodies end with a `…more` expander line

**Not in the original spec.** Both bodies in the first live batch ended with a literal `… more` line —
LinkedIn's description expander, left in the scraped text. It is **UI chrome, not truncation**: both
payloads still reached their natural footer (EEO statement, `Job Grade`, benefits block), which a
collapsed preview would not. `extract_body` now strips a trailing `…more` / `...see more`.

If a future body ends at `…more` *mid-sentence*, that would be real truncation and a different problem —
classify it `Unknown` (→ `Human review`) rather than guessing at the hidden tail.

### 11.4 New: raw payloads are kept

`payloads/<job_id>.txt` is saved for every successful fetch alongside the extracted body. The §5.2 rule
is "one fetch per link, **ever**", so without the raw text any later parsing question (a badge variant, a
new end-marker, a truncation worry) would cost a request that the rule forbids. The truncation question
in §11.3 could not be answered offline on the first run because of this gap.

### 11.5 Deviations from the spec, and why

- **Token refresh (§4).** Each script invocation takes its own fresh token rather than refreshing
  mid-run. A fetch phase is ~8 min at the 40-row cap, so it cannot outlive the 1 h TTL, and the write
  phase runs in seconds with a token minted at its start. This also survives the agent spending an hour
  classifying between phases, which a single long-lived token would not.
- **Extra write guard.** `write_results.py` skips any target cell that no longer reads `unknown` at
  write time. Implied by §5.2 rather than stated: between fetch and write a human may have filled the
  cell, and their value wins.
- **Abort marker scanning is restricted to failed payloads.** Words like "challenge" appear constantly
  in JD prose, so scanning a successful body for block signals would abort on healthy runs. A payload
  that yields ≥200 chars of `job_posting` is never scanned.
- **Two-failure abort is retroactive.** §6 marks an isolated failure `Human review` but leaves aborted
  rows `unknown`. The first of two consecutive failures is therefore held provisionally and converted to
  `leave_unknown` if the second failure fires the abort.

### 11.6 New: a concurrency lock (§5.3 gap)

**Not in the original spec, and the one hole the spec's pacing rules could not close.** Sequential
order, jitter and the run cap all bound a *single* process; nothing stopped a second
`plan_and_fetch.py` from running in another shell, and both would share the one browser session
backing Gaston's real account. Starting a duplicate run is exactly what an agent does after losing
track of an earlier one.

`plan_and_fetch.py` now takes an exclusive lock at `tmp/linkedin-scoring/.fetch.lock` before the fetch
loop, holding pid + start time, released via `atexit`. A lock younger than 30 min aborts the new run
before any fetch; older is treated as stale (a hard kill skips `atexit`) and cleared with a notice.
`--dry-run` never takes the lock, since it makes no calls. Verified: a simulated in-flight lock stopped
a live run with zero LinkedIn requests.

### 11.7 First live batch — 2026-08-06, 3 rows, all accepted

Extends the §9 fixtures. Identity exact on 3/3; 4 cells written; `unknown` I 91→89, K 64→62 (deltas
matched exactly); AB/AC recalculated correctly, so an I/K write does not disturb the row-2
ARRAYFORMULAs. A re-run of the write phase wrote **nothing** — the "cell no longer reads `unknown`"
guard makes the pipeline idempotent.

| Row | Company / Title | Badge → I | K verdict | Decisive evidence |
|---|---|---|---|---|
| 5 | Glatfelter Insurance — Fire & EMS Education Specialist | `Hybrid` (already held `Hybrid`, **not** written) | **US-Specific** | *"Instruct Emergency Vehicle Driver Training Course and related field safety programs"*; *"travel up to 50% of the time or more, often on weekends"*; remote only *"if candidate is near a major airport – Denver, Chicago or Atlanta"* (Cat 2) |
| 11 | Shoreline AI — Senior Vibration Analyst | `Remote` | *(already `Remote-friendly`, not re-read)* | n/a — the §5.2 skip-the-classifier path |
| 12 | INIT Innovations — BD Manager California/West Coast | `Remote` | **US-Specific** | *"Represent INIT at key industry events, conferences, and customer meetings"*; *"Travel up to 50% across North America and internationally"*; *"based in the Seattle area"* (Cat 2) |

Row 5 doubles as a free badge-parser check: it independently read `Hybrid`, matching the value already
in the cell, and correctly left it alone. Row 11 is the business case in miniature — filling col I moved
it from invisible to Priority `Medium` (35 pts).

Row 12 is worth remembering as a **near-miss on the geography rule**: it carries *"West Coast (U.S.),
preference will be given to applicants located in California"* and *"based in the Seattle area"*. Strike
both and the verdict is unchanged, because the in-person event/customer-meeting duties and 50% travel
carry it alone. A classifier that cited the geography language would be right for the wrong reason.

### 11.8 New: `--rows`, and the arithmetic of targeting High-priority upside

Added 2026-08-06 for a run asked to "increase High-priority leads". `plan_and_fetch.py --rows 97,72,96`
restricts a run to named sheet rows, so a batch can be picked by score upside instead of sheet order.
A job is kept whole when *any* of its rows is selected — two rows sharing one post share one fetch and
one verdict. Requested rows that need no work are reported and dropped.

**Before promising anyone more High leads, do this arithmetic.** Col I is worth at most **+15**
(`Remote`), and High needs `AB >= 50`. So **only rows already scoring 35–49 can be lifted to High by
this skill** — a `Low` row (20–34) can reach `Medium` at best, and `Reject` rows are gated by K/J ahead
of the score and cannot be rescued at all. Measured on the live sheet that day: of 85 rows with col I
`unknown`, **43 were Reject, 38 Low, and only 4 Medium** — i.e. the entire High-upside pool was 4 rows.
That ratio is the expected shape, not an anomaly; the backlog is mostly low-scoring rows.

A one-off read of `A2:AC` (cols AB/AC carry the computed score and priority) is the cheap way to rank
candidates — it costs one Sheets call and zero LinkedIn exposure.

### 11.9 Second live batch — 2026-08-06, 15 rows, score-targeted

15 rows / 15 distinct posts, identity exact on 15/15, 26 cells written, `unknown` I 85→70 and K 58→47
(both deltas exact). Yield: **1 new High** (row 97, 45 → 60), 10 rows Low → Medium, 3 → Reject.

Note the ceiling this demonstrates: 4 rows had High upside, and 3 of them were killed by their own K
verdict (rows 72 and 178 US-Specific; row 96 badged `Hybrid`, so +10 landed at 45). **The rows most
likely to reach High are sales/events/BD roles, and those are also the likeliest to be `US-Specific`** —
the two effects partly cancel, so plan for a low single-digit High yield per batch.

| Row | Company / Title | Badge → I | K verdict | Decisive evidence |
|---|---|---|---|---|
| 72 | The Wealthy Practitioner — Events Coordinator | `Remote` | **US-Specific** | *"Serve as the operational lead during live events"*; *"Manage onsite logistics and troubleshoot issues in real time"*; *"Willingness to travel several times per year"* (Cat 2) |
| 83 | BAZIC Products — Creative Marketing Specialist | `On-site` | **US-Specific** | *"Ability to work onsite in Monrovia, CA (no hybrid/remote options available)"* (Cat 2, explicit) |
| 178 | CV3 — Head, Growth Partnerships & Sales | `Remote` | **US-Specific** | *"You will be in the market—meeting customers… attending industry events"*; *"Represent CV3 at major US trade shows"*; *"Willingness to travel extensively"* (Cat 2) |

Two new geography near-misses that were correctly **not** rejected:

- **Row 27, Quantcast**: *"Although this role is remote, you must be based in WA."* A single-state
  residency rule is the same class as the §8.2 state-list example — geography only, nothing a LatAm
  candidate could never satisfy. `Remote-friendly`.
- **Row 96, Jewish Women's Archive**: office in Newton MA, hybrid schedule, *"Candidates in the Boston
  and New York City areas are preferred, though we are open to remote candidates."* The explicit
  remote opening is decisive; the CDO travel/representation duties are not framed as hard requirements.

Two calls worth flagging as lower-confidence, both resolved toward the §8.4 bias:

- **Row 70, SARACA — Industrial Software Engineer** → `Unknown` (written as `Human review`). Body is
  badged `Remote` and states the work supports *"a heavy industrial US defense contractor"* with
  *"Background and Meet and Greet: MANDATORY"*, but **never states** clearance, citizenship or work
  authorization. Defense work usually implies an ITAR US-person bar as a matter of law, yet the prompt
  rejects only on *stated* Category 1/2/3 requirements — so this is §8.2 step 3 ambiguity, not step 2.
  **A defense-contractor context with no explicit clause is the canonical `Unknown`.**
- **Row 84, Bradford Exchange — Senior Manager, Paid Social** → `Remote-friendly`. Carries `#LI-Hybrid`
  and describes a Chicago HQ, but the only hybrid language sits in a *benefits* paragraph about
  corporate staff generally. Per §8.4 a perk blurb is not a stated requirement.

### 11.10 Regression fixtures

`references/classifier-fixtures.md` holds the five §9 col-K cases as runnable bodies —
**reconstructions**, since the original payloads weren't retained and those rows now hold values. Each
carries the decisive quote wrapped in the boilerplate traps of §8.4. Pass condition is 5/5 with
fixtures 1 (row 4) and 4 (row 140) landing on *opposite* verdicts. Verified 5/5 on 2026-08-06.
