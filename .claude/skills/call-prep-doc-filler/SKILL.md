---
name: call-prep-doc-filler
description: This skill fills an existing Google Doc call prep template with lead data extracted from Clay. Given a Google Doc URL and lead fields (job_title, linkedin_url, employee_count, job_post_url), it locates the fixed table in the doc and fills in the correct cells. The "Roles they're looking to hire for" field appends a new line with the job post URL rather than replacing existing content. Use this skill when you have lead data ready and need to fill it into a call prep Google Doc.
---

# Call Prep Doc Filler

Fills a fixed-structure Google Doc call prep template with lead data.

## Template Structure

The doc always contains the same table with these rows (label → value cell):

| Label | Action |
|---|---|
| Job Title | Replace with `job_title` |
| LinkedIn | Replace with `linkedin_url` |
| # Employees | Replace with `employee_count` |
| Roles they're looking to hire for | **Append** `\n{job_post_url}` to existing text |

"Roles" is special: whatever text already exists in that cell is preserved; the job post URL is added on a new line below it.

## Inputs

- `doc_url` — full Google Doc URL (e.g. `https://docs.google.com/document/d/{id}/edit`)
- `job_title` — lead's job title (may be null)
- `linkedin_url` — lead's personal LinkedIn URL (may be null)
- `employee_count` — company employee count as string (may be null)
- `job_post_url` — LinkedIn job post URL (may be null)

Skip filling a cell if its corresponding value is null — leave the cell as-is.

## Workflow

Run the filler script:
```bash
python .claude/skills/call-prep-doc-filler/scripts/fill_call_prep_doc.py \
  "<doc_url>" \
  "<job_title>" \
  "<linkedin_url>" \
  "<employee_count>" \
  "<job_post_url>"
```

Pass `""` (empty string) for any null values — the script skips empty values.

The script outputs a summary of which cells were filled and confirms success.

## How the Script Fills the Doc

1. Extract document ID from the URL
2. Refresh Google OAuth token (uses `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN`)
3. GET the document via `https://docs.googleapis.com/v1/documents/{docId}`
4. Walk `body.content` to find the first table
5. For each row, read the first cell's text (label) to identify which row to fill
6. Collect the value cell's index range for each matched row
7. Build `batchUpdate` requests, processed from **highest index to lowest** to avoid index shifting:
   - **Job Title, LinkedIn, # Employees**: clear existing text in value cell, insert new value
   - **Roles**: insert `\n{job_post_url}` at the end of the cell's last paragraph (before the final `\n`)
8. POST `batchUpdate` to `https://docs.googleapis.com/v1/documents/{docId}:batchUpdate`

## Label Matching

Labels are matched case-insensitively by keyword:

| Keyword | Field |
|---|---|
| `job title` | Job Title |
| `linkedin` | LinkedIn |
| `employee` | # Employees |
| `roles` | Roles they're looking to hire for |

## Error Handling

- **Auth failure**: Check that `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN` are set in `.env`
- **Table not found**: The script falls back to searching all structural elements — if still not found, confirm the doc URL is correct and the doc has a table
- **Cell not found**: Report which labels could not be matched and show what labels were found
