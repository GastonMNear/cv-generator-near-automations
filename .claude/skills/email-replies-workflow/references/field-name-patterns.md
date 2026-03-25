# Clay Field Name Patterns

This reference documents common field naming patterns across HireWithNear Clay tables to enable dynamic field resolution in the email-replies-workflow skill.

## Purpose

Clay tables use field IDs (e.g., `f_4z7XTwVeBRvA`) rather than field names in API responses. Field names vary across tables, making hardcoded field mappings brittle. This reference provides pattern-based matching strategies to dynamically identify fields regardless of schema variations.

## Email Field Patterns

Search for these patterns (case-insensitive) to identify email fields.

### Priority Order

1. **"validated email"** - Most reliable, typically contains verified email addresses
2. **"email one"** - Primary email field in most tables
3. **"email"** - Generic email field name
4. **"contact email"** - Alternative naming convention
5. **"work email"** - Business email field
6. **"personal email"** - Personal email field

### Pattern Matching Strategy

```python
EMAIL_PATTERNS = [
    "validated email",  # Priority 1
    "email one",        # Priority 2
    "email",            # Priority 3
    "contact email",    # Priority 4
    "work email"        # Priority 5
]

for f in fields:
    name_lower = f["name"].lower()
    for pattern in EMAIL_PATTERNS:
        if pattern in name_lower:
            email_field_id = f["id"]
            break
```

**Matching Rules:**
- **Exact match preferred:** "Email" matches "Email"
- **Partial match acceptable:** "email" matches "Primary Email", "Email One", "Contact Email"
- **Case insensitive:** "EMAIL" matches "email"
- **Stop on first match:** Use first pattern found in priority order

### Field Type Validation

Email fields typically have these types:
- `type`: `"text"` or `"formula"`
- `dataType`: `"text"` or `"email"` (if present)

If multiple fields match the pattern, prefer fields with explicit email dataType.

### Examples

| Field Name | Field ID | Matches Pattern |
|------------|----------|-----------------|
| Validated Email | f_SUTHMU5bi2XD | ✓ "validated email" (Priority 1) |
| Email One | f_dWUgCoGRG2RD | ✓ "email one" (Priority 2) |
| Primary Email | f_abc123 | ✓ "email" (Priority 3) |
| Contact Email | f_def456 | ✓ "contact email" (Priority 4) |

## LinkedIn Job URL Field Patterns

Search for these patterns (case-insensitive) to identify LinkedIn job posting URL fields.

### Priority Order

1. **"job post url"** - Explicit job posting URL
2. **"job url"** - Clear job URL field
3. **"linkedin job"** - LinkedIn-specific job field
4. **"opening url"** - Job opening URL
5. **"posting url"** - Alternative job posting URL

### CRITICAL: Exclude Patterns

**NEVER use these patterns** - they indicate prospect/person LinkedIn profiles, NOT job postings:

- **"prospect"** - Lead's personal LinkedIn profile
- **"person"** - Individual's LinkedIn profile
- **"profile"** - Personal LinkedIn profile
- **"linkedin url"** (without "job") - Often refers to prospect LinkedIn

### Pattern Matching Strategy

```python
LINKEDIN_JOB_PATTERNS = [
    "job post url",   # Priority 1
    "job url",        # Priority 2
    "linkedin job",   # Priority 3
    "opening url",    # Priority 4
    "posting url"     # Priority 5
]

EXCLUDE_PATTERNS = ["prospect", "person", "profile"]

for f in fields:
    name_lower = f["name"].lower()

    # MUST NOT contain exclude patterns
    if any(exclude in name_lower for exclude in EXCLUDE_PATTERNS):
        continue  # Skip this field

    # Check for job URL patterns
    for pattern in LINKEDIN_JOB_PATTERNS:
        if pattern in name_lower:
            linkedin_field_id = f["id"]
            break
```

**Matching Rules:**
- **Must contain job-related keyword:** "job", "post", "opening", "posting"
- **Must NOT contain exclude keywords:** "prospect", "person", "profile"
- **Partial match acceptable:** "job url" matches "LinkedIn Job URL", "Job Post URL"
- **Case insensitive**
- **URL validation:** Value must contain "linkedin.com/jobs/view/"

### Field Type Validation

LinkedIn URL fields typically have these types:
- `type`: `"text"`, `"formula"`, or `"url"`
- `dataType`: `"text"` or `"url"` (if present)

### Examples

| Field Name | Field ID | Match Result | Reason |
|------------|----------|--------------|--------|
| Job Post URL | f_xyz789 | ✓ Match (Priority 1) | Contains "job post url" |
| LinkedIn Job URL | f_abc123 | ✓ Match (Priority 3) | Contains "linkedin job" |
| Opening URL | f_def456 | ✓ Match (Priority 4) | Contains "opening url" |
| Prospect Linkedin URL | f_4z7XTwVeBRvA | ✗ Excluded | Contains "prospect" (exclude pattern) |
| Person LinkedIn | f_ghi789 | ✗ Excluded | Contains "person" (exclude pattern) |
| LinkedIn Profile | f_jkl012 | ✗ Excluded | Contains "profile" (exclude pattern) |

### Common Mistake: Using Prospect LinkedIn URLs

**Problem:** Prospect LinkedIn URLs point to the lead's personal profile (linkedin.com/in/johndoe), not the job posting.

**Example:**
```
Correct:   Job Post URL → https://www.linkedin.com/jobs/view/12345678/
Incorrect: Prospect Linkedin URL → https://www.linkedin.com/in/johndoe/
```

**Solution:** Always exclude fields with "prospect", "person", or "profile" in the name.

## Name Field Patterns

Search for these patterns (case-insensitive) to identify full name fields.

### Priority Order

1. **"full name cleaned"** - Cleaned/formatted version, most reliable
2. **"full name"** - Standard full name field
3. **"name"** - Generic name field
4. **"contact name"** - Alternative naming

### Exclusion Rule

**Exclude fields containing "company"** - these are company names, not person names.

### Pattern Matching Strategy

```python
NAME_PATTERNS = [
    "full name cleaned",  # Priority 1
    "full name",          # Priority 2
    "name",               # Priority 3
    "contact name"        # Priority 4
]

for f in fields:
    name_lower = f["name"].lower()

    # Exclude company name fields
    if "company" in name_lower:
        continue

    for pattern in NAME_PATTERNS:
        if pattern in name_lower:
            name_field_id = f["id"]
            break
```

**Note:** Name field is **optional** in the workflow - don't fail if not found.

### Field Type Validation

Name fields typically have:
- `type`: `"text"` or `"formula"`
- `dataType`: `"text"`

### Examples

| Field Name | Field ID | Match Result | Reason |
|------------|----------|--------------|--------|
| Full Name cleaned | f_rOj3SQqDVF8U | ✓ Match (Priority 1) | Contains "full name cleaned" |
| Full Name | f_abc123 | ✓ Match (Priority 2) | Contains "full name" |
| Contact Name | f_def456 | ✓ Match (Priority 4) | Contains "contact name" |
| Company Name | f_xyz789 | ✗ Excluded | Contains "company" |
| Account Name | f_ghi012 | ✗ No Match | Doesn't match patterns |

## Employee Count Field Patterns

Search for these patterns (case-insensitive) to identify the LinkedIn employee count field.

### Priority Order

1. **"employee count"** - Explicit employee count field
2. **"# employees"** - Numeric format (e.g., "# Employees (LinkedIn)")
3. **"num employees"** - Abbreviated numeric form
4. **"headcount"** - Alternative headcount field
5. **"company size"** - Company size reference
6. **"employees"** - Generic employees field
7. **"staff"** - Alternative staff count

### Pattern Matching Strategy

```python
EMPLOYEE_COUNT_PATTERNS = [
    "employee count",  # Priority 1
    "# employees",     # Priority 2
    "num employees",   # Priority 3
    "headcount",       # Priority 4
    "company size",    # Priority 5
    "employees",       # Priority 6
    "staff",           # Priority 7
]

for f in fields:
    name_lower = f["name"].lower()
    for pattern in EMPLOYEE_COUNT_PATTERNS:
        if pattern in name_lower:
            employee_count_field_id = f["id"]
            break
```

**Note:** Employee count is **optional** — don't fail the workflow if not found. Display "Not available" in the output.

### Examples

| Field Name | Match Result | Reason |
|------------|--------------|--------|
| # Employees (LinkedIn) | ✓ Match (Priority 2) | Contains "# employees" |
| Employee Count | ✓ Match (Priority 1) | Contains "employee count" |
| Company Headcount | ✓ Match (Priority 4) | Contains "headcount" |
| Company Size | ✓ Match (Priority 5) | Contains "company size" |
| Staff Count | ✓ Match (Priority 7) | Contains "staff" |

## Company Name Field Patterns

Search for these patterns (case-insensitive) to identify company name fields (optional).

### Priority Order

1. **"company name"** - Explicit company name
2. **"account name"** - Common CRM field name
3. **"company"** - Generic company field
4. **"organization"** - Alternative naming

### Pattern Matching Strategy

```python
COMPANY_PATTERNS = [
    "company name",  # Priority 1
    "account name",  # Priority 2
    "company",       # Priority 3
    "organization"   # Priority 4
]
```

**Note:** Company field is **optional** - extracted from LinkedIn job details instead.

## Ambiguity Resolution

When multiple fields match the same pattern, apply these tiebreakers:

### Tiebreaker Priority

1. **Exact match over partial match**
   - "Email" exactly matches "Email"
   - Prefer over "Primary Email" partial match

2. **Higher priority pattern**
   - "Validated Email" (Priority 1) beats "Email One" (Priority 2)

3. **Non-extracted fields preferred**
   - If field has `isExtractedField: true`, it may be stale
   - Prefer original data over extracted data

4. **Sortable fields preferred**
   - If field has `isSortable: true`, indicates primary data column
   - Prefer sortable over non-sortable

5. **Field description context**
   - Check field `description` for context clues
   - Example: "Primary contact email" vs "Secondary email"

6. **Ask user if still ambiguous**
   - List all matching fields with names and IDs
   - Ask user to specify exact field name
   - Store user's choice for this table

### Example: Ambiguity Resolution

**Scenario:** Table has both "Email" and "Email (Validated)"

```python
# Both match "email" pattern
field1 = {"id": "f_abc", "name": "Email", "isSortable": True}
field2 = {"id": "f_def", "name": "Email (Validated)", "isSortable": False}

# Apply tiebreakers:
# 1. Check priority pattern match
#    - "Email (Validated)" contains "validated" → Priority 1
#    - "Email" → Priority 3
# Winner: f_def ("Email (Validated)")
```

**Scenario:** Table has "Job URL" and "Job Posting URL"

```python
# Both match job URL patterns
field1 = {"id": "f_xyz", "name": "Job URL"}
field2 = {"id": "f_uvw", "name": "Job Posting URL"}

# Apply tiebreakers:
# 1. Check priority pattern match
#    - "Job Posting URL" contains "job post" → Priority 1
#    - "Job URL" contains "job url" → Priority 2
# Winner: f_uvw ("Job Posting URL")
```

## URL Validation

After identifying a LinkedIn job URL field, validate the extracted URL:

### Valid URL Format

```
https://www.linkedin.com/jobs/view/[job_id]/
https://linkedin.com/jobs/view/[job_id]
```

### Invalid Formats

```
❌ https://www.linkedin.com/in/johndoe/  (prospect profile)
❌ https://linkedin.com/company/acme     (company page)
❌ empty string or null
❌ non-LinkedIn URL
```

### Validation Code

```python
def validate_linkedin_job_url(url):
    if not url or not isinstance(url, str):
        return False, "URL is empty or invalid type"

    if "linkedin.com/jobs/view/" not in url:
        if "linkedin.com/in/" in url:
            return False, "This is a prospect LinkedIn profile, not a job posting"
        else:
            return False, "URL does not match expected format: linkedin.com/jobs/view/[id]"

    return True, "Valid LinkedIn job URL"
```

## Field Discovery Strategy

When field resolution fails, use this strategy to discover correct fields:

### Step 1: List Candidate Fields

```python
# For email fields
email_candidates = [
    f for f in fields
    if f.get("type") in ["text", "formula"]
    and ("email" in f["name"].lower() or "contact" in f["name"].lower())
]

# For URL fields (excluding prospect LinkedIn)
url_candidates = [
    f for f in fields
    if ("url" in f["name"].lower() or "link" in f["name"].lower())
    and not any(exclude in f["name"].lower() for exclude in ["prospect", "person", "profile"])
]
```

### Step 2: Present to User

```
Could not automatically identify the email field. Candidates found:

1. Email One (f_dWUgCoGRG2RD)
2. Validated Email (f_SUTHMU5bi2XD)
3. Contact Email (f_abc123)

Please specify which field contains the lead's email address.
```

### Step 3: Store Learning

Once user specifies correct field, consider updating:
- This reference file with new pattern
- Table-specific field mapping (if pattern is table-specific)

## Pattern Update Process

When new field patterns are discovered:

1. **Identify the pattern:** What naming convention does the field use?
2. **Check generalizability:** Does this pattern apply to other tables?
3. **Update priority list:** Where does this pattern fit in priority order?
4. **Document examples:** Add examples showing when pattern matches
5. **Test across tables:** Verify pattern works on multiple tables

**Example Update:**
```
Discovered field: "Primary Contact Email"
Pattern: "contact email" (already in Priority 4)
Action: No update needed - existing pattern covers this case
```

**Example Update 2:**
```
Discovered field: "Job Opening Link"
Pattern: "opening" is generic but combined with "job" + "link"
Action: Add "opening link" to LINKEDIN_JOB_PATTERNS Priority 5
```

## Known Field Mappings (Reference)

For quick reference, here are known field IDs for key tables:

### US Open Jobs - No Hiring Manager (t_0t59d2y3ZuD4396Kz5B)

| Field Name | Field ID | Type |
|------------|----------|------|
| Email One | f_dWUgCoGRG2RD | Email |
| Validated Email | f_SUTHMU5bi2XD | Email |
| Prospect Linkedin URl | f_4z7XTwVeBRvA | URL (prospect, NOT job) |
| Full Name cleaned | f_rOj3SQqDVF8U | Name |

**Note:** This table does NOT have a direct "Job Post URL" field. The job URL may be in a different field or need to be derived from other data.

### Additional Tables

Field mappings for other tables (LatAm, Canada, US HMs) should be discovered dynamically using the patterns above. As mappings are discovered, they can be added here for reference.

## Summary

**Key Takeaways:**
1. Use **pattern-based matching** with priority order, not hardcoded field IDs
2. **Always exclude** "prospect", "person", "profile" when searching for job URLs
3. **Validate URLs** to ensure they point to job postings, not profiles
4. **Apply tiebreakers** when multiple fields match the same pattern
5. **Ask the user** if field resolution remains ambiguous
6. **Update this reference** when new patterns are discovered
