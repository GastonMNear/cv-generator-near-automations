---
name: lead-data-extractor
description: This skill extracts lead data from a Clay table given a lead email and a campaign name. It resolves the correct Clay table by matching the campaign name, then searches for the lead record and extracts 4 fields needed for call prep: job title, lead LinkedIn URL, employee count, and job post LinkedIn URL. Output is JSON. Use this skill when given a lead email and a campaign name and asked to pull their Clay data.
---

# Lead Data Extractor

Extracts 4 fields from a Clay table record for a given lead email:
- **job_title** — the lead's current job title
- **linkedin_url** — the lead's personal LinkedIn profile URL
- **employee_count** — the company's headcount
- **job_post_url** — the LinkedIn URL of the job they're hiring for

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
python .claude/skills/lead-data-extractor/scripts/extract_lead_data.py <lead_email> <table_id>
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

The script uses pattern matching to identify Clay field IDs. Patterns by priority:

| Field | Patterns to match (case-insensitive, substring) |
|---|---|
| Job Title | `title`, `job title`, `position`, `role` — must NOT contain `company` |
| Lead LinkedIn | `prospect linkedin`, `contact linkedin`, `linkedin url`, `linkedin profile`, `person linkedin` |
| Employee Count | `employee count`, `# employees`, `num employees`, `headcount`, `company size` |
| Job Post URL | `job post url`, `job post linkedin`, `linkedin job`, `opening url`, `posting url` |

If a field can't be resolved, the script reports which fields are available and exits with a non-zero code. In that case, display the available fields to the user and ask for the correct field name or ID.

## Error Handling

- **Lead not found**: Check email spelling, confirm the correct table, suggest partial search
- **Field not resolved**: Display all available fields (with IDs) so user can identify the right one
- **Clay auth failure**: The session cookie is short-lived — re-run after refreshing credentials
