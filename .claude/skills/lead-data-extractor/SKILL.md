---
name: lead-data-extractor
description: >
  Extracts lead data from a Clay table for the call-prep workflow. Given a lead email and
  campaign name, resolves the correct Clay table and extracts 4 fields: job_title (lead's
  current title), linkedin_url (personal profile), employee_count, and job_post_url. Output
  is JSON. Always use this skill when given a lead email and campaign name and need to pull
  data for a call prep document — it feeds directly into the call-prep-doc-filler skill.
  Trigger this skill any time someone provides a lead email + campaign/table name and needs
  call prep data, even if they don't explicitly say "extract lead data".
---

# Lead Data Extractor

> **Workflow note:** This skill is for the **call-prep workflow** (lead email + campaign → call prep doc). The CV generation workflow (`email-replies-workflow`) uses `temp/fetch_lead.py` instead, which has all 6 table field IDs pre-cached and returns `name`, `linkedin_url` (job URL), and `employee_count`. Use this skill for call prep; use `fetch_lead.py` for CV generation.

Extracts 4 fields from a Clay table record for a given lead email:
- **job_title** — the lead's current job title (personal title, not the open role)
- **linkedin_url** — the lead's personal LinkedIn profile URL (`linkedin.com/in/...`)
- **employee_count** — the company's headcount
- **job_post_url** — the LinkedIn URL of the job they're hiring for (`linkedin.com/jobs/view/...`)

## Inputs

- `lead_email` — the lead's email address
- `campaign_name` — the Smartlead campaign name; used to identify the right Clay table

## Workflow

### Step 1 — Resolve the Clay Table

Match `campaign_name` against the known table list in `.claude/skills/clay-api/references/known-tables.md` (case-insensitive substring match against name and all aliases).

If no match, call the Clay API to list all tables:
```
GET https://api.clay.com/v3/workspaces/447061/tables
```
Score each table by name similarity to `campaign_name` and pick the best match.

If ambiguous (multiple close matches), list the candidates and ask the user to confirm.

### Step 2 — Run the extraction script

Once the table ID is resolved, run:
```bash
PYTHONUTF8=1 python .claude/skills/lead-data-extractor/scripts/extract_lead_data.py <lead_email> <table_id>
```

The script outputs JSON like:
```json
{
  "success": true,
  "lead_email": "john@example.com",
  "table_id": "t_xxx",
  "record_id": "r_xxx",
  "job_title": "VP of Engineering",
  "linkedin_url": "https://www.linkedin.com/in/john-doe",
  "employee_count": "500-1000",
  "job_post_url": "https://www.linkedin.com/jobs/view/1234567",
  "fields_found": { ... }
}
```

### Step 3 — Handle Missing Fields

If any field is `null` in the output, report clearly which ones are missing and continue with what's available. Do not fail the whole workflow if optional fields (employee_count, job_post_url) are absent — still pass the available data downstream.

## Field Resolution Patterns

The script uses **priority-based pattern matching** to identify Clay field IDs — it finds the field matching the highest-priority pattern first, then falls through lower priorities if not found.

| Field | Priority patterns (highest → lowest) |
|---|---|
| Email | `work email`, `validated email`, `find work email`, `contact email`, `email` — must NOT match `email one` or similar draft-copy fields |
| Job Title | `job title`, `title`, `position`, `role` — must NOT contain `company` or `url` |
| Lead LinkedIn | `prospect linkedin`, `contact linkedin`, `person linkedin`, `linkedin url`, `linkedin profile` |
| Employee Count | `employee count`, `# employees`, `num employees`, `headcount`, `company size`, `employees` |
| Job Post URL | `job post url`, `job post linkedin`, `linkedin job`, `opening url`, `posting url`, `job url`, `job link` — must NOT match `prospect`, `person`, `profile`, `company linkedin` |

**Known-tables optimization**: For tables in `.claude/skills/clay-api/references/known-tables.md`, the correct field IDs are pre-cached. The script will still auto-discover them via pattern matching, but if a field fails to resolve, cross-reference with known-tables.md to confirm the correct field name.

**View ID selection**: The script prefers a view named "Default View" when available. Some tables have "Errored Rows" as the first view (e.g., US HMs, Canada HMs) — these only contain ~100-400 records. "Default View" contains the full dataset.

If a field can't be resolved, the script reports which fields are available and exits with a non-zero code. In that case, display the available fields to the user and ask for the correct field name or ID.

## Error Handling

- **Lead not found**: Check email spelling, confirm the correct table, suggest partial search
- **Field not resolved**: Display all available fields (with IDs) so user can identify the right one
- **Clay auth failure**: The session cookie is short-lived — re-run after refreshing credentials
