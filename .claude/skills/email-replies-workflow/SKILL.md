---
name: email-replies-workflow
description: >
  Orchestrates the complete CV generation workflow from Clay lead data. Always use this
  skill when given a lead email address and a Clay table name (or campaign name that maps
  to a table) — it automatically fetches lead data via temp/fetch_lead.py, extracts LinkedIn
  job details, and generates a tailored LATAM CV as a Google Doc. Trigger this skill any time
  someone says "generate CV for [email]", "process lead [email]", or provides an email with
  a Clay table context, even if they don't explicitly ask for "the workflow".
---

# Email Replies Workflow

## Overview

This skill provides end-to-end orchestration of the CV generation workflow for leads in Clay tables. When given a lead's email address and the Clay table name, the skill automatically:

1. Runs `temp/fetch_lead.py --email EMAIL --table ALIAS` → returns name, linkedin_url, employee_count (all 6 tables pre-cached, no metadata API calls needed)
2. Invokes the linkedin-job-extractor skill to get company name, job title, and full job description
3. Invokes the latam-cv-generator skill to create a tailored LATAM CV as a Google Doc
4. Returns the Google Doc URL and company employee count

This workflow eliminates manual data gathering and coordinates three specialized skills (clay-api, linkedin-job-extractor, latam-cv-generator) into a seamless automation.

## When to Use This Skill

Use this skill when:
- Processing email replies from Smartlead campaigns
- User provides a lead email address and Clay table name
- Need to generate a CV for a specific lead in a Clay table
- Want to automate the complete workflow from Clay data to Google Doc

**Example triggers:**
- "Process lead john@example.com from US Open Jobs - No Hiring Manager"
- "Generate CV for jane.doe@company.com from LatAm OJ - HMs"
- "Create CV for the lead bob@test.com in Canada Open Jobs"

## Prerequisites

### Required Environment Variables

The workflow requires the following environment variables in `.env`:

**Clay API:**
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

This skill orchestrates three existing skills:
- **clay-api** - For Clay table data access
- **linkedin-job-extractor** - For LinkedIn job post extraction
- **latam-cv-generator** - For CV generation and Google Doc creation

### Clay Workspace

The workflow assumes access to **HireWithNear workspace** (ID: 447061) with the following known tables:
- US Open Jobs - No Hiring Manager (`t_0t59d2y3ZuD4396Kz5B`)
- US Open Jobs - Hiring Managers (`t_0t5pvx3g4o5WfysopqA`)
- LatAm Open Jobs - No HMs (`t_aNvk4jWMNeG7`)
- LatAm Open Jobs - Hiring Managers (`t_0t6ghvgCsvvvqAus4bp`)
- Canada Open Jobs - No HM (`t_0taasak5KAa5zbTmTJd`)
- Canada Open Jobs - HMs (`t_0t746txPqz5sjFMtut2`)

## User Input Requirements

The user must provide:
1. **Lead Email Address** - The email address of the lead to process
2. **Clay Table Name** - The name or ID of the Clay table containing the lead

**Input Format Examples:**
- "Process lead john@example.com from US Open Jobs - No Hiring Manager"
- "john.doe@company.com in LatAm OJ - HMs"
- "email: jane@test.com, table: Canada Open Jobs"

Extract the email and table name from natural language input.

**If inputs are missing:** Ask for them in plain text only — do NOT use AskUserQuestion (the 6-table list exceeds the 4-option maximum and will throw a validation error).

## Workflow Steps

**IMPORTANT — Run all steps end-to-end without stopping.** This is a fully automated pipeline. Do not output intermediate results (LinkedIn job details, lead info) to the user mid-workflow. Each step feeds directly into the next. Only output to the user once Step 4 (final summary) is reached. If you find yourself about to present job details or lead data before the Google Doc is created, stop and proceed to the next step instead.

### Step 1: Fetch Lead Data from Clay

**Objective:** Resolve the table, authenticate, search for the lead, and extract linkedin_url + employee_count — all in one command.

**⚡ Use the universal fetch script** — do NOT write inline auth/search code. The script has all 6 tables' field IDs pre-cached.

**Table aliases** (case-insensitive partial match):

| User says | Alias to pass |
|-----------|---------------|
| US Open Jobs - No HM | `us no hm` |
| US Open Jobs - HMs | `us hms` |
| LatAm Open Jobs - No HMs | `latam no hm` |
| LatAm Open Jobs - HMs | `latam hms` |
| Canada Open Jobs - No HM | `canada no hm` |
| Canada Open Jobs - HMs | `canada hms` |

**Command:**
```bash
PYTHONUTF8=1 python temp/fetch_lead.py --email {lead_email} --table "{table_alias}"
```

**Output (JSON printed to stdout):**
```json
{
  "email": "craig.t@blackretebuilders.com",
  "name": "Craig Thomas",
  "linkedin_url": "https://www.linkedin.com/jobs/view/estimator-at-blackrete-builders-inc-4064769752",
  "employee_count": 34
}
```

Parse `name`, `linkedin_url`, `employee_count` from this JSON output.

**Error: lead not found** → script exits with code 1. Check email spelling and confirm correct table.

**Error: table not recognised** → script prints known table list. Adjust alias.

**LinkedIn URL validation** — after extracting, verify:
- Must contain `linkedin.com/jobs/view/` — if it contains `linkedin.com/in/` instead, that's a prospect profile URL (wrong field); report and stop.
- LinkedIn job URLs may be slug format (e.g., `.../jobs/view/estimator-at-company-4064769752`) — this is valid, WebFetch handles it fine.

**Output:** `lead_name`, `linkedin_url`, `company_employee_count`

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

**Important:** `company_name` comes from the `linkedin-job-extractor` output in Step 2. It must be passed here so the Google Doc is named correctly.

**Important:**
- The skill ALWAYS returns a Google Doc URL, not markdown text
- Expert review is mandatory and runs automatically
- The Google Doc is created in the folder specified by `GOOGLE_DRIVE_FOLDER_ID`

**If CV generation fails:** check `OPENAI_API_KEY`, Google OAuth credentials (`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN`), and `GOOGLE_DRIVE_FOLDER_ID`. If Google Doc creation fails, report the error — do NOT return CV markdown as a fallback.

**Output:** `google_doc_url`, `review_feedback`, `generated_candidate_name`, `generated_candidate_location`

### Step 4: Format and Return Results

**Objective:** Present comprehensive workflow results to the user.

**Implementation:**

Format the final output with all relevant information. The output must always include the Google Doc URL (not the CV content) and end with the company's LinkedIn employee count from Clay:

```
✅ CV Generation Workflow Complete!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 LEAD INFORMATION

Email: {lead_email}
Name: {candidate_name or "Not specified"}
Source Table: {table_name}

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

✓ Lead found in Clay table
✓ LinkedIn job details extracted
✓ LATAM CV generated and reviewed
✓ Google Doc created successfully

The CV is ready to send to {lead_email}!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👥 # Employees (LinkedIn): {company_employee_count or "Not available"}
```

**Important:** The employee count comes from the Clay table record fetched in Step 1. Always display it at the end of the output even if the value is "Not available". Do not skip this field.

**Output:** Formatted results string for user

## Error Handling

### Table Resolution Errors

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

### Authentication Errors

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
2. Suggest:
   - Check email spelling
   - Verify lead is in correct table
   - Try searching by partial email (domain only)
3. Ask user to confirm email and table
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

### Example 1: Canada HMs (verified working 2026-03-16)

**User Input:**
```
craig.t@blackretebuilders.com
Canada Open Jobs - HMs
```

**Step 1 command:**
```bash
PYTHONUTF8=1 python temp/fetch_lead.py --email craig.t@blackretebuilders.com --table "canada hms"
```
**Step 1 output:**
```json
{"email": "craig.t@blackretebuilders.com", "name": "Craig Thomas",
 "linkedin_url": "https://www.linkedin.com/jobs/view/estimator-at-blackrete-builders-inc-4064769752",
 "employee_count": 34}
```
Steps 2–4 → Google Doc created, CV delivered.

### Example 2: US Campaign, No Hiring Manager

**User Input:**
```
Process lead john.doe@techcorp.com from US Open Jobs - No Hiring Manager
```

**Step 1 command:**
```bash
PYTHONUTF8=1 python temp/fetch_lead.py --email john.doe@techcorp.com --table "us no hm"
```

### Example 3: LatAm HMs

**User Input:**
```
Generate CV for maria.garcia@startup.io from LatAm OJ - HMs
```

**Step 1 command:**
```bash
PYTHONUTF8=1 python temp/fetch_lead.py --email maria.garcia@startup.io --table "latam hms"
```
Note: LatAm HMs field IDs are assumed from US/Canada HMs schema — verify on first run and update known-tables.md if wrong.

## Performance Notes

- **Total execution time:** 30-60 seconds (depends on table size and API response times)
- **Clay API rate limits:** Respect rate limits, retry with backoff if rate limited
- **Batch size:** 10,000 records per batch (tested maximum — reduces scan from 100+ calls to 1-3 calls)
- **Session reuse:** Always authenticate fresh — session cookies expire quickly
