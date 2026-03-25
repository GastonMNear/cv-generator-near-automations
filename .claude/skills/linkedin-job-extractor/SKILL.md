---
name: linkedin-job-extractor
description: >
  Extracts structured job post details (company name, job title, full description) from a
  LinkedIn job URL (linkedin.com/jobs/view/...). Always use this skill whenever a LinkedIn
  jobs URL appears in the conversation and job details are needed — whether the user explicitly
  asks for extraction or the URL is part of a larger workflow like CV generation. Also trigger
  this skill when called programmatically by email-replies-workflow as Step 2 of the CV pipeline.
---

# LinkedIn Job Post Extractor

Extract company name, job title, and full job description from a LinkedIn job post URL.

> **Programmatic use:** This skill is invoked as Step 2 of the `email-replies-workflow`. When called from that workflow, output is captured internally — do not present intermediate results to the user.

## Accepted Input

A LinkedIn job post URL in any of these formats:
- `https://www.linkedin.com/jobs/view/{job_id}/`
- `https://linkedin.com/jobs/view/{job_id}`
- `https://www.linkedin.com/jobs/view/{job_id}?...` (with query params)

Validate the URL contains `linkedin.com/jobs/view/` before proceeding. If the URL does not match this pattern, inform the user and ask for a corrected URL.

## Extraction Workflow

### Step 1: Fetch the Job Page

Use the **WebFetch** tool to retrieve the LinkedIn job posting page. Pass the URL and use the following prompt:

```
Extract ALL of the following from this LinkedIn job posting:

1. COMPANY NAME: The name of the company that posted the job
2. JOB TITLE: The exact title of the position
3. FULL JOB DESCRIPTION: The COMPLETE text of the job posting including ALL of these sections if present:
   - About the job / Job description
   - About the company / About us
   - Responsibilities / What you'll do
   - Requirements / Qualifications
   - Experience required
   - Skills
   - Benefits / Perks
   - Any other sections in the posting

Return the FULL unabridged text for the job description - do not summarize or truncate.
Format the output as:
COMPANY: [company name]
TITLE: [job title]
JD_START
[full job description text here]
JD_END
```

### Step 2: Handle Fetch Failures

If WebFetch returns an error, incomplete content, or a login wall:

1. **Try appending `?trk=public_jobs_topcard-title` to the URL** — this sometimes forces the public view.
2. **Try the guest job view URL pattern**: replace `www.linkedin.com/jobs/view/{id}` with `www.linkedin.com/jobs/view/{id}/` (ensure trailing slash).
3. If all attempts fail, report to the user that the job post could not be accessed and suggest they paste the job description text directly.

### Step 3: Format the Output

Present the extracted data in this exact markdown format:

```markdown
## Job Post Details

**Company:** [Company Name]

**Title:** [Job Title]

### Job Description

[Full JD text preserving all sections, line breaks, and bullet points from the original posting]
```

## Important Notes

- LinkedIn job posts are mostly public, but some may require authentication — the public fetch works for the majority of postings.
- Preserve the full job description text verbatim. Do NOT summarize, shorten, or paraphrase any part of it.
- If the page content is truncated or partial, explicitly tell the user that the extraction may be incomplete.
- Some job posts include an "Easy Apply" or "Apply" section — exclude application buttons/links from the JD output.
