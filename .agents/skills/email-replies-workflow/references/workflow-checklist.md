# Workflow Execution Checklist

Use this checklist to validate each step of the email-replies-workflow execution. Check off each item as completed to ensure no steps are skipped.

## Pre-Execution Validation

Before starting the workflow, verify:

- [ ] User provided lead email address (contains `@`)
- [ ] User provided Clay table name or ID
- [ ] Environment variables loaded from `.env`
- [ ] Clay credentials available (`CLAY_USERNAME`, `CLAY_PASSWORD`)
- [ ] Google credentials available for CV generation:
  - [ ] `GOOGLE_CLIENT_ID`
  - [ ] `GOOGLE_CLIENT_SECRET`
  - [ ] `GOOGLE_REFRESH_TOKEN`
  - [ ] `GOOGLE_DRIVE_FOLDER_ID`
- [ ] OpenAI API key available (`OPENAI_API_KEY`)

**If any prerequisites missing:** Report error and list missing environment variables before proceeding.

---

## Step 1: Table Resolution

### 1.1 Parse User Input

- [ ] Email address extracted from user input
- [ ] Email format validated (contains `@` and valid format)
- [ ] Table name extracted from user input
- [ ] Table name cleaned (trimmed whitespace, normalized case)

### 1.2 Resolve Table Name to ID

**Option A: Known Tables Lookup**
- [ ] Read `known-tables.md` reference file
- [ ] Attempt exact match (case-insensitive)
- [ ] If no exact match: attempt partial match
- [ ] If match found: table ID extracted (format `t_[alphanumeric]`)
- [ ] If match found: log which table name matched

**Option B: API Fallback** (if Option A fails)
- [ ] Authenticate with Clay (see Step 2)
- [ ] Call `GET /workspaces/447061/tables`
- [ ] Search response for matching table name
- [ ] If found: extract table ID
- [ ] If not found: list available tables and report error

### 1.3 Validation

- [ ] Table ID confirmed (not null/empty)
- [ ] Table ID format validated (starts with `t_`)
- [ ] Table existence confirmed

**If validation fails:** Report error with suggestions for correct table name/ID.

---

## Step 2: Clay Authentication

### 2.1 Load Credentials

- [ ] `CLAY_USERNAME` loaded from `.env`
- [ ] `CLAY_PASSWORD` loaded from `.env`
- [ ] Credentials are not empty/null

### 2.2 Execute Login

- [ ] POST request to `https://api.clay.com/v3/auth/login`
- [ ] Request headers include `Content-Type: application/json`
- [ ] Request body contains email, password, source fields
- [ ] Response received (status code 200)
- [ ] `Set-Cookie` header present in response

### 2.3 Extract Session Cookie

- [ ] `Set-Cookie` header parsed
- [ ] Session cookie extracted (format: `claysession=...`)
- [ ] Cookie stored for subsequent requests
- [ ] Cookie format validated (starts with `claysession=`)

### 2.4 Test Authentication

- [ ] Test API call executed (e.g., `GET /me` or similar)
- [ ] Test call returns 200 (not 401)
- [ ] Authentication confirmed successful

**If authentication fails:**
- [ ] Check credentials are correct
- [ ] If 429/504: wait and retry
- [ ] Report specific error to user

---

## Step 3: Table Metadata Fetch

### 3.1 Fetch Table Metadata

- [ ] Call `GET /tables/{table_id}` with session cookie
- [ ] Response received successfully
- [ ] `table` object extracted from response
- [ ] `fields` array extracted (not empty)
- [ ] `views` array extracted (not empty)

### 3.2 Build Field Map

- [ ] Iterate through all fields
- [ ] Build map: `{field_id: field_name}`
- [ ] Field map contains at least 5 fields
- [ ] Log total field count

### 3.3 Extract View Information

- [ ] Default view identified (first view in array)
- [ ] View ID extracted
- [ ] View name logged (if available)

**If metadata fetch fails:**
- [ ] Verify table ID is correct
- [ ] Check session cookie is still valid
- [ ] Re-authenticate if necessary

---

## Step 4: Field Resolution

### 4.1 Resolve Email Field

- [ ] Read email patterns from `references/field-name-patterns.md`
- [ ] Iterate through fields with priority patterns
- [ ] Match found (case-insensitive partial match)
- [ ] Email field ID stored
- [ ] Email field name stored
- [ ] Log email field: "{name} ({id})"

**If email field not found:**
- [ ] List all text/formula fields
- [ ] Report error with field list
- [ ] Ask user to specify exact field name

### 4.2 Resolve LinkedIn Job URL Field

- [ ] Read LinkedIn URL patterns from `references/field-name-patterns.md`
- [ ] Apply exclusion patterns ("prospect", "person", "profile")
- [ ] Iterate through fields with priority patterns
- [ ] Match found (excluding prospect LinkedIn)
- [ ] LinkedIn URL field ID stored
- [ ] LinkedIn URL field name stored
- [ ] Log LinkedIn URL field: "{name} ({id})"

**If LinkedIn URL field not found:**
- [ ] List all URL/link fields (excluding prospect)
- [ ] Check if only prospect LinkedIn fields exist
- [ ] Report error with field list
- [ ] Ask user to specify exact field name

### 4.3 Resolve Name Field (Optional)

- [ ] Read name patterns from `references/field-name-patterns.md`
- [ ] Exclude company name fields
- [ ] Iterate through fields with priority patterns
- [ ] If match found: store name field ID and name
- [ ] If not found: log warning (name is optional)
- [ ] Log name field if found: "{name} ({id})"

### 4.4 Validation

- [ ] Email field ID is not null
- [ ] LinkedIn URL field ID is not null
- [ ] Fields are different (not the same field ID)

**Required fields identified:** email, LinkedIn job URL
**Optional fields identified:** name

---

## Step 5: Lead Record Search

### 5.1 Get Record IDs

- [ ] Call `GET /tables/{table_id}/views/{view_id}/records/ids`
- [ ] Response received successfully
- [ ] `results` array extracted
- [ ] Record IDs list stored
- [ ] Total record count logged
- [ ] Verify record count > 0

**If no records:**
- [ ] Report table is empty
- [ ] Cannot proceed without data

### 5.2 Batch Fetch and Search

- [ ] Batch size set to 100 records
- [ ] Target email normalized (lowercased)
- [ ] Loop through record IDs in batches

**For each batch:**
- [ ] Call `POST /tables/{table_id}/bulk-fetch-records`
- [ ] Request body contains batch of record IDs
- [ ] Response received successfully
- [ ] `results` array extracted
- [ ] Iterate through records in batch
- [ ] Check each record's email field value
- [ ] Case-insensitive email comparison
- [ ] Log batch progress: "Searched X/Y records..."

**When match found:**
- [ ] Record stored (break loop)
- [ ] Record ID logged
- [ ] Exit batch loop

### 5.3 Validation

- [ ] Lead record found (not null)
- [ ] Record has `cells` object
- [ ] Record ID exists

**If lead not found:**
- [ ] Report total records searched
- [ ] Suggest checking email spelling
- [ ] Suggest verifying correct table
- [ ] Report error with suggestions

---

## Step 6: LinkedIn URL Extraction

### 6.1 Extract URL from Record

- [ ] `cells` object extracted from record
- [ ] LinkedIn URL cell extracted using field ID
- [ ] URL value extracted from cell
- [ ] URL stored as string

### 6.2 Extract Name (Optional)

**If name field identified:**
- [ ] Name cell extracted using field ID
- [ ] Name value extracted from cell
- [ ] Candidate name stored (if not empty)
- [ ] Log candidate name

### 6.3 Validate LinkedIn URL

- [ ] URL is not null/empty
- [ ] URL is string type
- [ ] URL contains "linkedin.com/jobs/view/"

**If URL is invalid:**
- [ ] Check if it's a prospect LinkedIn URL ("linkedin.com/in/")
- [ ] Report error: wrong URL type (prospect vs job)
- [ ] Report error: URL format invalid
- [ ] Cannot proceed without valid job URL

### 6.4 Log Extracted Data

- [ ] Log LinkedIn URL
- [ ] Log candidate name (if available)

**Extracted data validated:** LinkedIn job URL confirmed

---

## Step 7: Job Details Extraction

### 7.1 Invoke linkedin-job-extractor Skill

- [ ] Use `Skill` tool with skill name "linkedin-job-extractor"
- [ ] Pass LinkedIn URL as argument
- [ ] Skill invocation successful

**Alternative (if Skill tool unavailable):**
- [ ] Use `WebFetch` tool directly
- [ ] Pass LinkedIn URL and extraction prompt
- [ ] Response received

### 7.2 Parse Job Details

- [ ] Company name extracted
- [ ] Job title extracted
- [ ] Job description extracted (complete, not truncated)
- [ ] All fields are not empty/null

### 7.3 Validation

- [ ] Company name is string
- [ ] Job title is string
- [ ] Job description is string (length > 100 characters)
- [ ] Log company name
- [ ] Log job title
- [ ] Log description length

**If extraction fails:**
- [ ] Try alternate URL format (add query params)
- [ ] Try with/without trailing slash
- [ ] If all attempts fail: ask user for manual job description
- [ ] Option: proceed with manual input

**Job details confirmed:** company, title, description extracted

---

## Step 8: CV Generation

### 8.1 Invoke latam-cv-generator Skill

- [ ] Use `Skill` tool with skill name "latam-cv-generator"
- [ ] Pass job title as argument
- [ ] Pass job description as argument
- [ ] Skill invocation successful

### 8.2 Monitor CV Generation Process

The latam-cv-generator skill will automatically:
- [ ] Load prompt template and reference data
- [ ] Generate LATAM CV (Argentina, Colombia, Mexico, or Brazil)
- [ ] Run expert review with GPT-4o
- [ ] Create Google Doc in specified Drive folder
- [ ] Return Google Doc URL

**Note:** These steps are handled by the skill internally.

### 8.3 Capture Output

- [ ] Google Doc URL received
- [ ] Review feedback received (optional)
- [ ] Generated candidate name received
- [ ] Generated candidate location received

### 8.4 Validation

- [ ] Google Doc URL is not empty
- [ ] URL format validated (contains "docs.google.com/document")
- [ ] URL is accessible (can be opened)

**If CV generation fails:**
- [ ] Check `OPENAI_API_KEY` is valid
- [ ] Check Google credentials are valid
- [ ] Check `GOOGLE_DRIVE_FOLDER_ID` exists
- [ ] Review error logs from skill
- [ ] Report specific error to user
- [ ] Suggest checking environment variables

**CV generated successfully:** Google Doc URL confirmed

---

## Step 9: Format Results

### 9.1 Compile Workflow Results

- [ ] Lead information compiled:
  - [ ] Email address
  - [ ] Name (if available)
  - [ ] Source table name and ID
- [ ] Job details compiled:
  - [ ] Company name
  - [ ] Job title
  - [ ] LinkedIn URL
- [ ] CV details compiled:
  - [ ] Generated candidate name
  - [ ] Generated candidate location
  - [ ] Google Doc URL
- [ ] Review feedback compiled (if available)

### 9.2 Format Output

- [ ] Output formatted with clear sections
- [ ] Sections: Lead Information, Job Details, Generated CV, Expert Review, Workflow Summary
- [ ] All fields populated (or "Not available" if missing)
- [ ] Google Doc URL prominently displayed
- [ ] Success checkmarks included for completed steps

### 9.3 Present to User

- [ ] Formatted output returned to user
- [ ] Output is readable and well-structured
- [ ] Google Doc URL is clickable/copyable
- [ ] Next steps clear (CV ready to send)

---

## Post-Execution Validation

After workflow completion:

- [ ] All 9 steps completed successfully
- [ ] No critical errors occurred
- [ ] Google Doc created and accessible
- [ ] Google Doc URL shared with user
- [ ] Workflow duration logged (optional)
- [ ] Temporary files cleaned up (if any)

### Success Metrics

✅ **Workflow Successful If:**
- Lead found in Clay table
- LinkedIn job URL extracted and valid
- Job details extracted from LinkedIn
- CV generated with expert review
- Google Doc created successfully
- Google Doc URL returned to user

❌ **Workflow Failed If:**
- Lead email not found in table
- LinkedIn URL missing or invalid
- LinkedIn extraction failed completely
- CV generation failed
- Google Doc creation failed

### Error Recovery

**For non-critical errors:**
- [ ] Log warning
- [ ] Continue workflow with degraded functionality
- [ ] Note limitations in output

**For critical errors:**
- [ ] Stop workflow
- [ ] Report specific error with context
- [ ] Provide recovery suggestions
- [ ] Ask user for clarification or manual input

---

## Troubleshooting Quick Reference

| Issue | Checklist Item | Recovery Action |
|-------|----------------|-----------------|
| Table not found | Step 1.2 | Try API fallback, list available tables |
| Auth fails | Step 2.2 | Check credentials, retry if rate limited |
| Field not found | Step 4.1-4.2 | List candidate fields, ask user |
| Lead not found | Step 5.3 | Report search completed, suggest checks |
| URL empty | Step 6.3 | Report missing URL, cannot proceed |
| LinkedIn fails | Step 7.1 | Retry with alternates, ask for manual input |
| CV gen fails | Step 8.4 | Check credentials, review error logs |

---

## Performance Tracking

**Optional:** Track timing for each major step:

- [ ] Step 1 (Table Resolution): ___ seconds
- [ ] Step 2 (Authentication): ___ seconds
- [ ] Step 3 (Metadata Fetch): ___ seconds
- [ ] Step 4 (Field Resolution): ___ seconds
- [ ] Step 5 (Record Search): ___ seconds
- [ ] Step 6 (URL Extraction): ___ seconds
- [ ] Step 7 (Job Extraction): ___ seconds
- [ ] Step 8 (CV Generation): ___ seconds
- [ ] Step 9 (Format Results): ___ seconds

**Total Workflow Duration:** ___ seconds

**Expected Duration:** 30-60 seconds (varies with table size)

---

## Summary

**Checklist Usage:**
- Use this checklist every time the email-replies-workflow skill is invoked
- Check off items systematically as you progress
- Do not skip validation steps
- Report clear errors when validation fails
- Ensure all required steps complete before marking workflow successful

**Remember:**
- Email and LinkedIn URL fields are **required** (fail if not found)
- Name field is **optional** (warn if not found, continue)
- Always exclude prospect LinkedIn URLs when searching for job URLs
- Validate URLs before invoking extraction skills
- Report specific, actionable errors with recovery suggestions
