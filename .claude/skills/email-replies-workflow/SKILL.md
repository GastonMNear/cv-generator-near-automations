---
name: email-replies-workflow
description: >
  Orchestrates the complete CV generation workflow for a lead. Always use this skill when
  given a lead email address and asked to generate a CV, process a lead, or send a sample
  profile — it fetches the lead from Smartlead via scripts/fetch_lead_smartlead.py (one call,
  no table name needed), extracts the job post details, and generates a tailored LATAM CV as
  a Google Doc. Trigger this skill any time someone says "generate CV for [email]", "process
  lead [email]", or pastes a lead email, even if they don't explicitly ask for "the workflow"
  and even if they don't name a campaign or Clay table. Falls back to Clay only when the lead
  is absent from Smartlead.
---

# Email Replies Workflow

## Overview

End-to-end orchestration of the CV generation workflow for a lead who replied to a campaign.
**All you need is the lead's email address** — Smartlead is queried by email directly, so no
campaign or table name is required:

1. Runs `scripts/fetch_lead_smartlead.py --email EMAIL` → name, company, job URL,
   employee count, and the campaign the lead belongs to, in a single API call
2. Invokes the linkedin-job-extractor skill to get company name, job title, and full description
3. Invokes the latam-cv-generator skill to create a tailored LATAM CV as a Google Doc
4. Returns the Google Doc URL and company employee count

Smartlead is the source of truth because it is the system that actually sent the campaign — the
lead is keyed by email, so there is nothing to resolve. This replaced a Clay-based Step 1 that
had to guess the right table from a campaign name and then linearly scan up to ~33k records.
Clay remains available as a fallback for the rare lead Smartlead does not have, and for filling
in a missing employee count (see Step 1b).

## When to Use This Skill

Use this skill when:
- Processing email replies from Smartlead campaigns
- The user provides a lead email address and wants a CV / sample profile
- The user names a campaign or Clay table alongside the email — that context is no longer
  needed for the lookup, but it does not change how the workflow runs

**Example triggers:**
- "Generate CV for john@example.com"
- "Process lead jane.doe@company.com"
- "Create CV for the lead bob@test.com in Canada Open Jobs" *(table name simply ignored)*

## Prerequisites

### Required Environment Variables

The workflow requires the following environment variables in `.env`:

**Smartlead API (primary lead source):**
- `SMARTLEAD_API_KEY` - Smartlead API key

**Clay API (fallback only):**
- `CLAY_USERNAME` - Clay account email
- `CLAY_PASSWORD` - Clay account password

**OpenAI (for CV review):**
- `OPENAI_API_KEY` - OpenAI API key
- `OPENAI_MODEL` - Model name (default: gpt-4o)

**Google Drive (for CV document creation):**
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth client secret
- `GOOGLE_REFRESH_TOKEN` - Google OAuth refresh token
- `GOOGLE_DRIVE_FOLDER_ID` - Target folder ID for storing CVs

### Skill Dependencies

This skill orchestrates:
- **linkedin-job-extractor** - For job post extraction
- **latam-cv-generator** - For CV generation and Google Doc creation
- **clay-api** - Fallback lead lookup only, when Smartlead has no record

### Clay Fallback Tables

Only relevant if Smartlead has no record for the lead. The workspace is **HireWithNear**
(ID 447061); `scripts/fetch_lead.py` has every table ID and field ID pre-cached and walks
ordered fallback chains itself, so pass it an alias and let it do the resolution. Run
`python3 scripts/fetch_lead.py --help` to see the current alias list rather than duplicating
it here — it drifts as campaigns are added.

## User Input Requirements

The user must provide **one thing: the lead's email address.**

Smartlead is queried by email, so a campaign or table name is not needed. If the user supplies
one anyway ("john@acme.com from US Open Jobs - No HM"), just note it as context and proceed —
do not try to translate it into a table alias unless you end up in the Clay fallback.

**If the email is missing:** ask for it in plain text.

## Workflow Steps

**IMPORTANT — Run all steps end-to-end without stopping.** This is a fully automated pipeline. Do not output intermediate results (LinkedIn job details, lead info) to the user mid-workflow. Each step feeds directly into the next. Only output to the user once Step 4 (final summary) is reached. If you find yourself about to present job details or lead data before the Google Doc is created, stop and proceed to the next step instead.

### Step 1: Fetch Lead Data from Smartlead

**Objective:** Get the lead's name, company, job post URL, and employee count in one call.

**Command:**
```bash
PYTHONUTF8=1 python3 scripts/fetch_lead_smartlead.py --email {lead_email}
```

**Output (JSON on stdout):**
```json
{
  "source": "smartlead",
  "email": "awollmann@horvath-partners.com",
  "name": "Anna Wollmann",
  "company_name": "Horváth USA",
  "company_name_raw": "Horváth USA",
  "company_name_normalized": "Horváth",
  "job_title_hint": "(Senior) Consulting Manager (f/m/d) Finance Transformation",
  "linkedin_url": "https://www.linkedin.com/jobs/view/4462903121/",
  "employee_count": 9,
  "prospect_linkedin": "https://de.linkedin.com/in/anna-wollmann-4681a5189",
  "campaigns": ["[EXP010] Apollo Open Jobs HMs | B inboxes"]
}
```

Parse `name`, `linkedin_url`, `employee_count` — these feed the rest of the pipeline. The
`campaigns` array tells you which campaign the lead replied to, which is useful for the final
summary and removes any need to ask the user.

**Reading the fields with the right amount of trust:**

- `linkedin_url` — the job post; the field the pipeline depends on. Sourced from Smartlead's
  **`job_url`**, which is the canonical field. A minority of leads still carry the URL only in the
  legacy `job_linkedin_url` (verified: `awollmann@horvath-partners.com`, `michael.hsu@curogram.com`),
  so the script falls through to that when `job_url` is null. The two are never both populated, so
  a null in either one is not a miss.
- `employee_count` — `null` on many older leads; newer leads carry it. This is normal, not a
  failure: report it as unavailable in the final output and carry on (see below).
- `company_name` — already resolved for you. Smartlead stores two company names,
  `company_name` and `normalized_company_name`; at least one is always populated but either can
  be empty on its own, so the script takes whichever exists and prefers the **longer** of the two
  when both do. `normalized_company_name` is shortened for email copy and drops meaningful words
  ("Mach33" for "Mach33 Media", "Entry" for "Entry Capital"), so the longer form is nearly always
  the better one. Both raw values are returned as `company_name_raw` and
  `company_name_normalized` if you need to see what was stored.
  Even so, treat the result as provisional: Step 2 reads the company name off the job posting,
  which is the public, correct name — **prefer Step 2's value** for the Google Doc title and fall
  back to `company_name` only when the posting yields nothing.
- `job_title_hint` — written for email copy, so often lowercase or abbreviated ("estimators",
  "founding AE"). Use it to sanity-check that the job URL points at the role the campaign was
  about; do **not** pass it to the CV generator as the target title. Step 2's extracted title is
  the real one.
- `prospect_linkedin` — the lead's own profile. Never a job post; it exists only as context.

**Exit codes and what to do:**

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Lead found | Proceed to Step 2 |
| 1 | Not in Smartlead | Go to **Step 1b** (Clay fallback) |
| 2 | Key rejected (401) or blocked (403) | Report it — the script explains which; do not retry blindly |
| 3 | Transient failure after retries | Retry once, then fall back to Step 1b |

**A note on 403s:** Smartlead sits behind Cloudflare, which blocks Python's default urllib
User-Agent with `403 Forbidden / error code: 1010`. This masquerades as rate limiting but is
permanent — backoff never clears it, while the same URL via curl works. The script already sends
a real User-Agent. If you ever write a fresh Smartlead request inline, set that header too;
otherwise you will waste minutes retrying a block that will never lift. Genuine throttling shows
up as 429 with `x-ratelimit-*` headers (limit is 200 per window).

**Full field reference:** `references/smartlead-lead-api.md` documents every custom field, its
reliability across campaign families, the failure modes above, and the verified company-name
clipping table. Read it if a field is missing or a value looks wrong.

### Step 1b: Clay Fallback (only if Smartlead returned exit code 1)

Smartlead holds every lead that was actually mailed, so a miss usually means the address is a
variant rather than that the lead is absent. Try, in order:

1. **Re-query Smartlead with likely variants.** Clay-vs-Smartlead mismatches are usually
   `firstname@` vs `firstname.lastname@`. One extra lookup is far cheaper than a Clay scan.
2. **Fall back to Clay** with the campaign the user mentioned, if any:
   ```bash
   PYTHONUTF8=1 python3 scripts/fetch_lead.py --email {lead_email} --table "{table_alias}"
   ```
   Prefer pasting the campaign name verbatim over hand-translating it to an alias — the resolver
   keys on the distinguishing word and routes full campaign names correctly.
3. **Scan Clay by domain** if that also misses:
   ```bash
   PYTHONUTF8=1 python3 scripts/find_by_domain.py --needle {domain_word} --table "{table_alias}"
   ```
   If exactly one person at that domain matches on first name, treat it as the same lead, re-run
   with the corrected address, and tell the user which email was actually used. If several
   distinct people come back, ask which one they meant.

If the user named no campaign and Smartlead has nothing, say so and ask which campaign the lead
came from rather than scanning every Clay table.

**Missing employee count is expected, not an error.** Older leads often lack it; newer ones have
it. When it is null, say so plainly in the Step 4 output alongside the CV and finish the workflow
normally. Do not fall back to Clay for it, re-run the lookup, or hold up the CV — the count is
supplementary context, and a clear "not available" is more useful to the reader than a delay.

**Job URL validation** — before Step 2, check the URL:
- A `linkedin.com/in/` URL is a *profile*, not a job post — the wrong field was read. Report and stop.
- LinkedIn slug URLs (`.../jobs/view/estimator-at-blackrete-builders-inc-4064769752`) are valid;
  WebFetch handles them.
- Non-LinkedIn job URLs (Greenhouse, Lever, Ashby, a careers page) are **valid, not errors** —
  the norm for Apollo/EXP010 leads. Pass them to Step 2 like any other posting. Only
  `linkedin.com/in/` and an empty value are failures.
- **Stale LinkedIn job posts:** a closed posting does not 404 — LinkedIn silently serves a generic
  jobs *search-results* page, so WebFetch "succeeds" while returning nothing usable. When Step 2
  reports a search-results page instead of a posting, go straight to the guest API
  (`https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}`), which still returns the
  archived posting. Verified: `zainab@clickstalentagency.com` (job `4458701353`) served an
  unrelated search page twice; the guest API returned the full posting. Do not treat this as an
  extraction failure or ask the user to paste the JD.

**Output:** `lead_name`, `linkedin_url`, `company_employee_count`, `campaign_name`

### Step 2: Extract Job Details from LinkedIn

**Objective:** Use the linkedin-job-extractor skill to get job title and description.

**Implementation:**

Invoke the `linkedin-job-extractor` skill using the Skill tool:

```
Use the Skill tool:
- skill: "linkedin-job-extractor"
- args: linkedin_url

The skill will use WebFetch to extract:
- Company name
- Job title
- Full job description (complete, unabridged)

Capture the output in structured format:
{
    "company": "Company Name",
    "title": "Job Title",
    "description": "Full job description text..."
}
```

**If LinkedIn extraction fails:**
1. Retry with `?trk=public_jobs_topcard-title` appended to the URL
2. Retry with/without trailing slash
3. If all attempts fail: use AskUserQuestion to ask the user to paste the job description manually

**Output:** `company_name`, `job_title`, `job_description`

These three values are **authoritative over anything Smartlead returned.** The posting carries
the company's real public name and the role's actual title, whereas Smartlead's copies were
written for email personalization and are often clipped or informal. If the extracted title and
Smartlead's `job_title_hint` describe clearly different roles, the URL may point at the wrong
posting — worth a sentence to the user in the final summary, but not a reason to stop.

> **Do not present these results to the user.** This is an internal step. Once you have `company_name`, `job_title`, and `job_description`, immediately proceed to Step 3.

### Step 3: Generate LATAM CV and Create Google Doc

**Objective:** Use the latam-cv-generator skill to create a tailored CV as a Google Doc.

**Implementation:**

Invoke the `latam-cv-generator` skill using the Skill tool:

```
Use the Skill tool:
- skill: "latam-cv-generator"
- args: f"--job-title \"{job_title}\" --job-description \"{job_description}\" --company-name \"{company_name}\""

The skill will:
1. Load prompt template and reference data
2. Generate realistic LATAM CV (Argentina, Colombia, Mexico, or Brazil)
3. Run expert review with GPT-4o (scripts/review_cv.py)
4. Create Google Doc titled: "{Candidate First Name} - {Candidate Current Title} - {company_name}"
5. Return Google Doc URL

Capture the output which includes:
- Google Doc URL (primary output)
- Expert review feedback
- Candidate information (name, location)
```

**Important:** `company_name` and `job_title` come from the Step 2 extraction, not from
Smartlead — Smartlead's versions are clipped/informal and would produce a badly named Google Doc
and a CV aimed at a vague title. Fall back to Smartlead's values only if Step 2 produced none.

**Important:**
- The skill ALWAYS returns a Google Doc URL, not markdown text
- Expert review is mandatory and runs automatically
- The Google Doc is created in the folder specified by `GOOGLE_DRIVE_FOLDER_ID`

**If CV generation fails:** check `OPENAI_API_KEY`, Google OAuth credentials (`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN`), and `GOOGLE_DRIVE_FOLDER_ID`. If Google Doc creation fails, report the error — do NOT return CV markdown as a fallback.

**Output:** `google_doc_url`, `review_feedback`, `generated_candidate_name`, `generated_candidate_location`

### Step 4: Format and Return Results

**Objective:** Present comprehensive workflow results to the user.

**Implementation:**

Format the final output with all relevant information. The output must always include the Google Doc URL (not the CV content) and end with the company's LinkedIn employee count from Smartlead:

```
✅ CV Generation Workflow Complete!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 LEAD INFORMATION

Email: {lead_email}
Name: {candidate_name or "Not specified"}
Campaign: {campaign_name or "Not specified"}
Source: {"Smartlead" or "Clay (fallback)"}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💼 JOB DETAILS

Company: {company_name}
Position: {job_title}
LinkedIn URL: {linkedin_url}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 GENERATED CV

Candidate Name: {generated_candidate_name}
Location: {generated_candidate_location}

📄 Google Doc: {google_doc_url}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 EXPERT REVIEW

{review_feedback}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ WORKFLOW SUMMARY

✓ Lead found in Smartlead
✓ Job post details extracted
✓ LATAM CV generated and reviewed
✓ Google Doc created successfully

The CV is ready to send to {lead_email}!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👥 # Employees (LinkedIn): {company_employee_count or "Not available (not stored for this lead)"}
```

**Important:** The employee count comes from Smartlead's `employee_count` in Step 1, which is
null for many older leads. Always display the line — when the value is missing, state that
explicitly rather than omitting the field. The reader looks for this number, so a visible "not
available" answers the question, whereas a missing line reads as an oversight and prompts a
follow-up. A null count never blocks or delays delivering the CV.

**Output:** Formatted results string for user

## Error Handling

### Lead Lookup Errors

**Error:** Smartlead returns 401 Invalid API Key
```
Recovery:
1. SMARTLEAD_API_KEY in .env has been rotated — ask the user for a current key
2. Do not fall back to Clay silently; the user should know the key is stale
```

**Error:** Smartlead returns 403 (Cloudflare error 1010)
```
Recovery:
1. This is a blocked User-Agent, NOT rate limiting — retrying will never clear it
2. Ensure the request sends a real User-Agent header (the bundled script does)
3. Verify with: curl -s "https://server.smartlead.ai/api/v1/leads/?email=...&api_key=..."
   curl works where bare urllib fails, which confirms the diagnosis
```

**Error:** Smartlead has no record for the email
```
Recovery: see Step 1b — try address variants first, then the Clay fallback chain,
then the Clay domain scan. Ask which campaign the lead came from if nothing is known.
```

### Table Resolution Errors (Clay fallback only)

**Error:** Table name not found
```
Recovery:
1. List known tables from known-tables.md
2. Try API search as fallback
3. Suggest exact matches based on similarity
4. If still not found: ask user for exact table ID
```

**Error:** Invalid table ID format
```
Recovery:
1. Validate table ID starts with "t_"
2. Ask user to confirm table ID
```

### Clay Authentication Errors (fallback path only)

**Error:** Clay login fails (401)
```
Recovery:
1. Check CLAY_USERNAME and CLAY_PASSWORD in .env
2. Verify credentials are correct
3. Try authenticating via web browser to confirm credentials work
```

**Error:** Clay rate limited (429) or timeout (504)
```
Recovery:
1. Wait 60 seconds
2. Retry authentication
3. If persistent: contact Clay support
```

### Field Resolution Errors

**Error:** Email field not found
```
Recovery:
1. List all text/formula fields in table
2. Ask user to specify exact email field name
3. Update references/field-name-patterns.md with new pattern
```

**Error:** LinkedIn URL field not found
```
Recovery:
1. List all URL/text fields
2. Check if only prospect LinkedIn fields exist (wrong field type)
3. Ask user to specify exact job URL field name
4. Warn if no job URL fields found
```

**Error:** Multiple ambiguous fields match
```
Recovery:
1. List all matching fields with IDs
2. Ask user to select correct field by name or ID
3. Consider adding field to known-tables.md for future reference
```

### Lead Search Errors

**Error:** Lead email not found in table
```
Recovery:
1. Report total records searched
2. Run scripts/find_by_domain.py to reveal the stored address variant
3. Ask user to confirm email and campaign
```

**Error:** Multiple records with same email
```
Recovery:
1. Use most recently updated record (by updatedAt timestamp)
2. Log warning about duplicate records
3. Report which record was selected
```

### LinkedIn URL Errors

**Error:** LinkedIn URL field is empty
```
Recovery:
1. Report missing URL
2. Cannot proceed without job URL
3. Ask if URL is stored in different field
```

**Error:** Invalid LinkedIn URL format
```
Recovery:
1. Check if it's a prospect LinkedIn URL (linkedin.com/in/)
2. Report error and ask for job URL field
3. Validate URL contains "linkedin.com/jobs/view/"
```

**Error:** LinkedIn extraction fails (WebFetch error)
```
Recovery:
1. Retry with alternate URL patterns:
   - Add ?trk=public_jobs_topcard-title
   - Try with/without trailing slash
2. If all retries fail: ask user to paste job description manually
3. Proceed with manual input
```

### CV Generation Errors

**Error:** latam-cv-generator skill fails
```
Recovery:
1. Check OPENAI_API_KEY is valid
2. Check Google credentials are valid
3. Verify GOOGLE_DRIVE_FOLDER_ID exists
4. Review error logs from skill
5. Suggest manual CV generation as fallback
```

**Error:** Expert review fails (GPT-4o error)
```
Recovery:
1. The review_cv.py script has fallback logic
2. Returns original CV if review fails
3. Log warning but continue to Google Doc creation
4. Check OpenAI API status and credits
```

**Error:** Google Doc creation fails
```
Recovery:
1. Verify Google OAuth credentials
2. Check GOOGLE_DRIVE_FOLDER_ID exists and is accessible
3. Suggest running google_auth_setup.py to refresh tokens
4. Report the error to the user — do NOT return CV markdown as output
5. Ask user to resolve credentials and retry
```

## Example Usage

All examples below were verified against the live Smartlead API on 2026-09-09.

### Example 1: The only input needed is an email

**User Input:**
```
Generate CV for awollmann@horvath-partners.com
```

**Step 1 command:**
```bash
PYTHONUTF8=1 python3 scripts/fetch_lead_smartlead.py --email awollmann@horvath-partners.com
```
**Step 1 output (abridged):**
```json
{"name": "Anna Wollmann", "company_name": "Horváth USA",
 "job_title_hint": "(Senior) Consulting Manager (f/m/d) Finance Transformation",
 "linkedin_url": "https://www.linkedin.com/jobs/view/4462903121/",
 "employee_count": 9,
 "campaigns": ["[EXP010] Apollo Open Jobs HMs | B inboxes"]}
```
Note the campaign came back *from* the lead — the user never had to name it. Steps 2–4 proceed
normally.

### Example 2: Employee count is null

```bash
PYTHONUTF8=1 python3 scripts/fetch_lead_smartlead.py --email michael.hsu@curogram.com
```
Returns Michael Hsu / Curogram with a valid job URL but `employee_count: null` and
`job_title_hint: null`. Both are optional — the workflow continues and reports the count as
"Not available". Worth noting that this lead previously required a Clay domain scan to find at
all; Smartlead resolves it directly by email.

### Example 3: Clipped company name — trust the job post

```bash
PYTHONUTF8=1 python3 scripts/fetch_lead_smartlead.py --email craig.t@blackretebuilders.com
```
Smartlead reports `company_name: "Blackrete"`, but the job URL slug reads
`estimator-at-blackrete-builders-inc-4064769752`. Step 2 extracts "Blackrete Builders Inc",
which is what the Google Doc should be named. Same pattern for `benjamin@covenantgolfsociety.com`
("Covenant Golf" → "The Covenant Golf Society") and `dante@entrycapital.com.br`
("Entry" → "Entry Capital").

## Performance Notes

- **Step 1 is now a single sub-second API call** — no auth handshake, no table resolution, no
  record scanning. The Clay path it replaced took 2–3 minutes on large tables (LatAm HMs is
  ~33k records).
- **Total execution time** is dominated by job extraction and CV generation, not lead lookup.
- **Rate limits:** 200 requests per window, reported in `x-ratelimit-limit` /
  `x-ratelimit-remaining` / `x-ratelimit-reset`. Normal workflow use is nowhere near this.
- **403 ≠ rate limit.** See the Cloudflare User-Agent note in Step 1 before adding any backoff.
- **Clay fallback** retains its old characteristics: fresh auth per run, 10,000-record batches,
  ordered fallback chains.
