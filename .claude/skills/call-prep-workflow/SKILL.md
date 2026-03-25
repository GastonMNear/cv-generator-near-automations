---
name: call-prep-workflow
description: This skill orchestrates the full call prep workflow when a new meeting is booked. Given a Google Doc URL, a lead email, and a campaign name, it automatically fetches the lead's data from Clay and fills the call prep doc. Use this skill when a call is booked and you need to prepare the call doc for a lead — provide the doc URL, lead email, and campaign name.
---

# Call Prep Workflow

Fills a call prep Google Doc with lead data pulled from Clay — in one step.

## Inputs

| Input | Description |
|---|---|
| `doc_url` | The Google Doc URL (already an open/copy of the template) |
| `lead_email` | The lead's email address |
| `campaign_name` | The Smartlead campaign name — used to identify the right Clay table |

## Workflow

### Step 1 — Extract Lead Data from Clay

Use the **lead-data-extractor** skill:
- Resolve the Clay table ID from `campaign_name` (check known-tables.md first, then search Clay API)
- Run `extract_lead_data.py <lead_email> <table_id>`
- Capture the JSON output: `job_title`, `linkedin_url`, `employee_count`, `job_post_url`

If the script exits with an error, diagnose and fix before continuing. Common issues:
- Auth failure → re-check `.env` credentials
- Lead not found → verify the email and table name

### Step 2 — Validate Extracted Fields

Check which of the 4 fields were successfully extracted. Report any missing fields to the user, but continue with the available data.

Example output if something is missing:
```
⚠ employee_count not found in Clay — will leave that cell blank
⚠ job_post_url not found — "Roles" row will not be updated
```

### Step 3 — Fill the Call Prep Doc

Use the **call-prep-doc-filler** skill:
- Run `fill_call_prep_doc.py` with the doc URL and the 4 fields (pass `""` for any missing ones)
- Confirm success or report any errors

### Step 4 — Report Results

Summarise what was done:
```
✓ Call prep doc filled for <lead_email>
  Table used: <table_name> (<table_id>)
  Doc: <doc_url>

  Filled:
    Job Title:      <value>
    LinkedIn:       <value>
    # Employees:    <value>
    Roles (appended): <value>

  Missing: [list any fields not found in Clay]
```

## Quick Reference — Script Commands

```bash
# Step 1: Extract from Clay
python .claude/skills/lead-data-extractor/scripts/extract_lead_data.py \
  "lead@example.com" "t_tableId"

# Step 3: Fill the doc
python .claude/skills/call-prep-doc-filler/scripts/fill_call_prep_doc.py \
  "https://docs.google.com/document/d/DOCID/edit" \
  "VP of Engineering" \
  "https://www.linkedin.com/in/john-doe" \
  "500-1000" \
  "https://www.linkedin.com/jobs/view/1234567"
```

## Required Environment Variables

```
CLAY_USERNAME
CLAY_PASSWORD
GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET
GOOGLE_REFRESH_TOKEN
```

All should be in the `.env` file at the project root.
