---
name: latam-cv-generator
description: >
  Generates realistic, human CVs for strong LATAM candidates (Argentina, Colombia, Mexico,
  Brazil) based on job descriptions and automatically creates them as Google Docs. Always use
  this skill when given a job title and job description and asked to create a CV for a LATAM
  candidate — whether triggered interactively or as Step 3 of the email-replies-workflow CV
  pipeline. The skill ensures authenticity with real universities, large companies, natural
  career progressions, and cultural appropriateness while avoiding AI-generated patterns.
  Output is always a Google Doc URL saved to the configured Drive folder.
---

# LATAM CV Generator

Generate realistic, human CVs for strong LATAM candidates that match specific job requirements.

## Purpose

This skill creates authentic CVs for candidates from Argentina, Colombia, Mexico, or Brazil that appear human-written and pass scrutiny from hiring managers. The CVs feature real educational institutions, verified large employers (>1,000 employees), natural career progressions, and appropriate cultural context for LATAM professionals.

## When to Use This Skill

Invoke this skill when:
- Given a job title and full job description from a LinkedIn posting
- Asked to create or generate a CV for a LATAM candidate
- Part of the automation workflow after extracting job details
- Need a CV that matches specific job requirements while maintaining authenticity

## How to Use This Skill

### Step 1: Extract Job Information

Before invoking this skill, ensure the following information is available:
- **Job Title:** The exact position title from the job posting
- **Job Description:** The complete job description including responsibilities, requirements, qualifications, and experience needed
- **Company Name:** The name of the company that posted the job (used in the Google Doc title)

If this information is not provided, use the `linkedin-job-extractor` skill first to extract it from a LinkedIn URL. That skill returns all three fields.

### Step 2: Load the Prompt Template

Read the CV generation prompt from `references/prompt-template.md`. This file contains the complete 6-part prompt structure (Role, Task, Context, Reasoning, Output Format, Stop Condition) with all requirements embedded.

### Step 3: Load Reference Data

Before generating the CV, load the following reference files to inform the generation:

1. **Universities:** Read `references/latam-universities.md` to access real university names organized by country (Argentina, Colombia, Mexico, Brazil)

2. **Companies:** Read `references/latam-companies.md` to access verified large companies (>1,000 employees) operating in LATAM, organized by industry

3. **Job Title Mappings:** Read `references/job-title-mappings.md` to identify common title alternatives when the target job title is uncommon or specialized

### Step 4: Analyze the Job Requirements

Before generating, analyze the job posting to determine:

1. **Seniority Level:** Entry, Junior, Mid-level, Senior, or Lead/Principal
2. **Industry:** The specific industry or sector of the role
3. **Key Skills:** Technical and soft skills mentioned in the description
4. **Experience Requirements:** Years of experience and specific domain expertise
5. **Title Commonality:** Whether the job title is common or requires mapping to an alternative for the candidate's current role

### Step 5: Generate the CV Using AI

Use an AI model (Claude Opus 4.6 or GPT-4) with the complete prompt from `references/prompt-template.md` as the system instructions. Provide the job title and job description as input.

The prompt template includes all necessary constraints:
- LATAM country selection (Argentina, Colombia, Mexico, Brazil)
- Real university validation
- Large company requirement (>1,000 employees)
- Career progression logic
- Experience seniority matching
- First job realism (part-time, unrelated, during university)
- Minor gaps for authenticity
- Always output CV in English
- Output format specification

### Step 6: Validate the Generated CV

After generation, verify the CV meets all requirements:

**Required Validations:**
- [ ] Candidate is from Argentina, Colombia, Mexico, or Brazil
- [ ] University is from the appropriate country (cross-reference with universities list)
- [ ] Current employer is a large company (>1,000 employees, from companies list) in the same industry as the target role
- [ ] Current role seniority is **one level below** the target position (not equal — this job is a step up)
- [ ] Current job title uses the most common, generic naming convention for that level
- [ ] Career progression is logical and natural (coherent advancement)
- [ ] First job is part-time, during university final year, unrelated to BOTH the current field AND the target industry
- [ ] No connection to target company or subsidiaries
- [ ] Career history spans multiple industries — maximum 2 roles in the target industry
- [ ] Professional summary is generic and broad — NOT targeted at this specific job opening
- [ ] Candidate is 8/10 fit: strong but has 1-2 minor gaps in skills or experience
- [ ] Name and surname are varied (not repetitive from previous generations)
- [ ] CV does NOT include: employee counts, industry descriptions, remote/timezone mentions, comments about first job context, US citizenship/work authorization, or the words "bilingual", "native English", or "native speaker"
- [ ] Role durations are natural and varied — no round numbers, no tenures that exactly match JD experience requirements
- [ ] For senior candidates (4+ roles): at least one job transition has a 1–3 month gap in the middle of the career history
- [ ] If multi-year industry experience required, one prior industry role is included; otherwise current role is the only one

**If Validation Fails:**
Regenerate the CV with explicit corrections for the failed validation points.

### Step 7: Expert Recruiter Review (MANDATORY)

**IMPORTANT:** Always review the CV with an expert recruiter AI before creating the final Google Doc. This ensures the CV appears human and realistic.

After validating the CV against the checklist, send it to OpenAI GPT-4o for expert review:

```python
from pathlib import Path
import sys

# Add script directory to path
script_dir = Path(".claude/skills/latam-cv-generator/scripts")
sys.path.insert(0, str(script_dir))

from review_cv import review_cv_with_expert

# After generating and validating CV markdown
cv_markdown = """[Generated CV content here]"""

# Send to expert recruiter for review
print("Sending CV to expert recruiter for review...")
review_result = review_cv_with_expert(cv_markdown)

# Check results
if review_result['needs_changes']:
    print(f"\nExpert Review: Changes were made")
    print(f"Issues found: {', '.join(review_result['issues_found'])}")
    print(f"Changes: {', '.join(review_result['changes_made'])}")
else:
    print("\nExpert Review: CV looks good - no changes needed")

# Use the reviewed CV (either original or edited)
final_cv_markdown = review_result['final_cv']
```

**What the Review Checks:**
1. **Realism & Authenticity** - Natural career progression, real companies/universities
2. **Cultural Appropriateness** - Correct degree names, location formats for country
3. **Professional Quality** - Achievement-oriented bullets, concise summary
4. **AI-Generated Patterns** - Flags overly perfect alignment, buzzwords, unrealistic jumps

**Review Output:**
```python
{
    "needs_changes": False,  # True if changes were made
    "issues_found": [],      # List of issues spotted
    "changes_made": [],      # List of changes made
    "final_cv": "..."        # Final CV markdown (original or edited)
}
```

**Important Notes:**
- The reviewer only makes **minimal changes** if necessary
- It will NOT change names, dates, companies, or structure
- If CV is already good, returns the exact original
- Uses GPT-4o model for high-quality review
- Completely isolated - no context about how CV was generated

### Step 8: Create Google Doc (MANDATORY)

**IMPORTANT:** Always create a Google Doc automatically after the expert review. Use the **reviewed CV** (from Step 7), not the original. Do not just return markdown - the final output must be a Google Doc URL.

After the expert review, convert the final CV to a Google Doc using the bundled script:

```python
from pathlib import Path
import sys
import re

# Add script directory to path
script_dir = Path(".claude/skills/latam-cv-generator/scripts")
sys.path.insert(0, str(script_dir))

from create_google_doc import create_cv_google_doc

# Use the REVIEWED CV from Step 7, not the original
final_cv_markdown = review_result['final_cv']

# Extract candidate first name (first word of the first line: "# Full Name")
candidate_full_name = final_cv_markdown.split('\n')[0].replace('# ', '').strip()
candidate_first_name = candidate_full_name.split()[0]

# Extract candidate's current job title (first ### heading under Work Experience)
work_exp_match = re.search(r'## Work Experience\s+### (.+)', final_cv_markdown)
current_job_title = work_exp_match.group(1).strip() if work_exp_match else "Professional"

# Build title: {First Name} - {Current job title} - {Company Name}
# company_name must be passed in from the caller (from linkedin-job-extractor output)
doc_title = f"{candidate_first_name} - {current_job_title} - {company_name}"

# Create Google Doc
doc_url = create_cv_google_doc(
    cv_markdown=final_cv_markdown,
    title=doc_title
)

print(f"CV created successfully!")
print(f"Google Doc: {doc_url}")

# Clean up: Delete temporary markdown files after successful upload
import os
temp_files = [".temp/generated_cv.md", ".temp/reviewed_cv.md"]
for temp_file in temp_files:
    if os.path.exists(temp_file):
        os.remove(temp_file)
        print(f"Temporary file {temp_file} deleted.")
```

**What the Script Does:**
1. Authenticates with Google using credentials from `.env`
2. Creates a new Google Doc with proper formatting (headings, bold, bullets)
3. Converts markdown CV to Google Docs rich text format
4. Moves the document to the folder specified by `GOOGLE_DRIVE_FOLDER_ID`
5. Returns the shareable Google Doc URL
6. **Deletes both temporary markdown files** (`generated_cv.md` and `reviewed_cv.md`) from `.temp/` folder after successful upload

**Expected Output Format:**

```
CV created successfully!
Google Doc: https://docs.google.com/document/d/[DOCUMENT_ID]/edit
```

### Step 9: Return Google Doc URL with Review Feedback

**CRITICAL: The final output MUST be the Google Doc URL only. NEVER return the CV content as markdown text or paste the CV in the reply. If Google Doc creation fails, report the error — do NOT fall back to returning CV markdown.**

Present the final output to the user, including the expert review feedback:

**Template:**
```
✅ CV Generated Successfully!

**Candidate:** [Full Name]
**Location:** [City, Country]
**Target Role:** [Job Title from JD]
**Current Role:** [Candidate's Current Title]
**Experience:** [X] years
**Doc Title:** [First Name] - [Current Title] - [Company Name]

📄 **Google Doc:** [URL]

**Expert Review:**
[If changes were made:]
- Changes Made: Yes
- Issues Found: [list issues from review_result['issues_found']]
- Changes Applied: [list changes from review_result['changes_made']]

[If no changes:]
- Expert Review: No changes needed - CV looks realistic and professional
```

**Example with changes:**
```
✅ CV Generated Successfully!

**Candidate:** Matías Fernández Rojas
**Location:** Buenos Aires, Argentina
**Target Role:** ML Engineer, AI & Financial Intelligence
**Current Role:** Software Engineer
**Experience:** 2.5 years

📄 **Google Doc:** https://docs.google.com/document/d/1jeul7yNjTrxi6BSifhBRJMsZALdue6EUeW5I-0-_06A/edit

**Expert Review:**
- Changes Made: Yes
- Issues Found: Job responsibilities were too perfectly aligned with target role, buzzword-heavy language in professional summary
- Changes Applied: Toned down some responsibilities to be more realistic, simplified professional summary language
```

**Example with no changes:**
```
✅ CV Generated Successfully!

**Candidate:** Matías Fernández Rojas
**Location:** Buenos Aires, Argentina
**Target Role:** ML Engineer, AI & Financial Intelligence
**Current Role:** Software Engineer
**Experience:** 2.5 years

📄 **Google Doc:** https://docs.google.com/document/d/1jeul7yNjTrxi6BSifhBRJMsZALdue6EUeW5I-0-_06A/edit

**Expert Review:**
- Expert Review: No changes needed - CV looks realistic and professional
```

**What NOT to do:**
- Do NOT paste the CV markdown content as the reply
- Do NOT send the CV text as the output
- Do NOT return markdown fallback if Google Doc creation fails — report the error instead

## Important Notes

### Career Progression Rules

**Natural Advancement:** Each role must represent a believable next step. Examples:
- Junior Analyst → Analyst → Senior Analyst → Lead Analyst
- Software Engineer → Senior Software Engineer → Tech Lead
- Marketing Coordinator → Marketing Manager → Senior Marketing Manager

**Avoid Large Jumps:** Do not skip multiple levels (e.g., Analyst → Director)

### Experience Duration Guidelines

- **First job (part-time):** 6-12 months during final year of university
- **Second job (first full-time):** 1-2 years
- **Mid-career roles:** 2-3 years each
- **Current role:** 1.5-3 years (longer tenures acceptable for senior roles)
- **Total career length:** Should align with age implied by graduation date (typically 23-25 years old at graduation)

### Company Selection Strategy

**Current Employer (must be large company >1k employees):**
1. Must be in the **same industry** as the target job
2. Select multinationals or well-known local companies
3. Geographic coherence with candidate's location

**Previous Employers — Vary the Industries:**
- Deliberately choose companies from **different industries** than the target role
- This creates a realistic, varied career background — most real candidates change sectors
- Mix of large and medium-sized companies
- Geographic coherence with candidate's location
- Only add a prior same-industry role if the JD explicitly requires multi-year industry experience

### Language Specifications

- **Spanish-speaking countries (Argentina, Colombia, Mexico):** Spanish (Native), English (Advanced / Excellent proficiency / Professional proficiency — depending on role requirements)
- **Brazil:** Portuguese (Native), English (Advanced / Excellent proficiency), Spanish (Intermediate/Basic) if relevant
- **Never use:** "Bilingual", "Native English", "Native speaker", or any phrasing implying English is the candidate's first language — in ANY part of the CV (languages section, professional summary, anywhere)

### Quality Indicators

A high-quality generated CV should:
1. Pass as human-written (no formulaic AI patterns)
2. Demonstrate natural career growth without unexplained gaps or jumps
3. Match 70-85% of job requirements (intentional minor gaps)
4. Use realistic contact information format for the country
5. Include LinkedIn URL in format: linkedin.com/in/[firstname-lastname-3digits]
6. Show cultural awareness (location formats, degree names, etc.)

## Integration with Automation Workflow

This skill fits into the broader automation system:

1. **Smartlead** monitors email replies and identifies campaigns
2. **Clay** retrieves lead and company data including LinkedIn job URLs
3. **linkedin-job-extractor** skill extracts job title and description
4. **latam-cv-generator** skill (this skill) creates tailored CV, reviews it, and converts to Google Doc
5. **Output:** Google Doc URL in the configured Drive folder

**Complete Flow:**
```
Smartlead reply → Clay data → LinkedIn job URL → Job details → CV generation → Expert review (GPT-4o) → Google Doc creation → Google Doc URL
```

**Expected Output:**
- **Format:** Google Doc URL (not markdown text)
- **Location:** Saved in Google Drive folder ID from `.env` (`GOOGLE_DRIVE_FOLDER_ID`)
- **Title:** `{Candidate First Name} - {Candidate Current Title} - {Company Name}`

When invoked programmatically, pass:
- `job_title` (string): The position title
- `job_description` (string): The complete job description text
- `company_name` (string): The company that posted the job (from `linkedin-job-extractor` output) — used in the Google Doc title

**Returns:**
- `google_doc_url` (string): The shareable URL of the created Google Doc
- **Doc title format:** `{Candidate First Name} - {Candidate Current Title} - {Company Name}`

## Troubleshooting

### CV Content Issues

**Issue:** Generated CV includes company employee counts or descriptions
**Solution:** Regenerate with explicit instruction to exclude these in the prompt

**Issue:** Candidate appears overqualified (current role too senior)
**Solution:** Regenerate with instruction to reduce current role seniority by one level

**Issue:** University or company doesn't exist or isn't in correct country
**Solution:** Cross-reference with bundled references and regenerate with correct options

**Issue:** Career progression has unrealistic jumps
**Solution:** Regenerate with explicit intermediate roles to fill progression gaps

**Issue:** First job appears related to current career path
**Solution:** Regenerate specifying the first job must be in retail, food service, administrative support, or other entry-level unrelated field

### Expert Review Issues

**Issue:** Review fails with OpenAI API error
**Solution:** Verify `OPENAI_API_KEY` in `.env` is valid and has sufficient credits. Check OpenAI status at status.openai.com.

**Issue:** Review returns malformed JSON
**Solution:** The script includes fallback handling - it will return the original CV if review fails. Check error logs for details.

**Issue:** Review changes too much of the CV
**Solution:** The reviewer is instructed to make minimal changes only. If it's overly aggressive, this indicates the original CV had significant AI-generated patterns that needed fixing.

**Issue:** Review always says "no changes needed"
**Solution:** This is actually good! It means your CVs are already passing the human realism test.

### Google Doc Creation Issues

**Issue:** Google Doc creation fails with authentication error
**Solution:** Verify `.env` contains valid `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `GOOGLE_REFRESH_TOKEN`. If tokens are expired, run `google_auth_setup.py` to refresh.

**Issue:** Document created but not moved to folder
**Solution:** Verify `GOOGLE_DRIVE_FOLDER_ID` in `.env` is correct and the Google account has write access to that folder.

**Issue:** Script fails with "Invalid requests" error
**Solution:** Ensure the CV markdown is properly formatted. The script expects standard markdown with # for name, ## for sections, ### for subsections.

**Issue:** CV returned as markdown text instead of Google Doc URL
**Solution:** Ensure Step 8 (Create Google Doc) was executed after Step 7 (Expert Review). The skill must always create a Google Doc - returning markdown alone is not sufficient.
