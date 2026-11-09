# HM Bucket Label — hardened classification prompt

For the **upstream API workflow** that populates column F (`HM Bucket Label`) of
`HMs list | No Email Found | Scoring System`. **Not part of the unknown-filler skill** — that skill
covers columns I and K only. This file exists so column F stops producing `unknown` at the source.

## Why it was changed

Live audit 2026-08-06: 4 of 204 rows had `unknown` in col F. In all four, col E (`Prospect Title`) was
populated — but with something that wasn't a clean job title:

| col E value | Old output | New output | Reason |
|---|---|---|---|
| `Management Executive` | unknown | **Director/Manager** | vague, but clearly management-level |
| `Advertising` | unknown | **IC/low authority** | a function/department, no authority evidenced |
| `SNAK Consultancy Services` | unknown | `unknown` | a company name — correctly unresolvable |
| `Mascot` | unknown | `unknown` | no interpretable role — correctly unresolvable |

The original prompt's only escape hatch was rule 7 (`empty, unclear, or conflicting → unknown`), so
anything that wasn't a textbook title fell straight through to `unknown`. The fix is a **fallback
ladder**: strip the noise, then classify on whatever signal remains — function, management flavour, or
ownership language — and reserve `unknown` for genuinely meaningless input.

Per Gaston: handle the `Management Executive` / `Advertising` class of input broadly (not as
title-specific hacks); leave the company-name and nonsense cases as `unknown`.

**Score impact:** F=`unknown` already scores 0 via the `TRUE,0` branch, so recovering a *low* bucket
(`IC/low authority`, also 0) changes no score — the gain there is clean data and filterability. The
real scoring gain is when junk hides actual seniority: `Management Executive` → `Director/Manager`
recovers **7 points** that were being silently dropped. (Note separately that a **blank** col F blanks
the entire score row via `IF(F2:F="","")` — `unknown` does not.)

---

## The prompt

```
#CONTEXT#

You are a classification assistant that maps a hiring manager's job title to a standardized contact
seniority bucket. Return ONLY the bucket label as plain text, with no commentary.

Real-world input is messy: the field often contains a department name, a company name, a headline, or
marketing copy instead of a clean title. Your job is to extract whatever seniority or functional
signal exists and commit to a bucket. "unknown" is a LAST RESORT, not a convenience.

#OBJECTIVE#

Classify HM Title into exactly one of:

  Founder/CEO/Owner/President | C-level | VP/Head | Director/Manager | HR/Talent |
  IC/low authority | unknown

#INSTRUCTIONS#

STEP 1 — Clean the input, then classify only what remains.
Strip: company and brand names, "at <Company>", anything after "|" or "@" that names an employer,
locations, emojis, follower/connection counts, pronouns, credentials (MBA, PMP, CPA, PhD), award
badges, and marketing taglines. Normalize abbreviations and casing.
If several roles are separated by "/", "|", "&" or ",", keep every role fragment — you will take the
highest in STEP 3.

STEP 2 — Classify by explicit seniority signal, applying these rules IN ORDER:

  1) Founder/CEO/Owner/President — founder, cofounder/co-founder, owner, principal (when clearly firm
     owner), president, chairman/chairwoman/chair, chief executive officer, CEO, managing partner,
     general partner (when clearly firm leadership/ownership), proprietor.

  2) C-level — contains "Chief", or a CxO abbreviation (CTO, CFO, COO, CPO, CISO, CIO, CMO).
     CEO is an exception → bucket 1. "Executive Director" belongs here ONLY when it clearly denotes the
     top executive of the organization (e.g. a non-profit head).

  3) VP/Head — vice president, VP, SVP, EVP, AVP, head of, global head, GM / general manager
     (business-unit head), country manager, site lead.

  4) Director/Manager — director, sr. director, group director, manager, sr. manager, lead (when it
     denotes team management), practice manager, program manager (when managerial in scope).

  5) HR/Talent — HR / People / Talent / Recruiting / TA roles: recruiter, senior recruiter, talent
     acquisition, hiring manager (generic), people ops, HR manager, HR director, people partner.
     Chief People Officer belongs here when the context is HR; otherwise CPO → bucket 2.

  6) IC/low authority — individual contributor or specialist with no managerial or executive
     authority: engineer, developer, designer, analyst, specialist, coordinator, associate,
     consultant, product manager, program manager (IC), sales rep / AE / SDR, intern, assistant.

STEP 3 — No explicit seniority keyword matched? Do NOT return unknown yet. Work down this ladder and
stop at the first match:

  3a) OWNERSHIP OR ENTREPRENEURIAL LANGUAGE anywhere in the text — including headlines and taglines
      ("I help brands scale", "building X", entrepreneur, investor, "my firm", solopreneur, partner in
      one's own practice)                                        → Founder/CEO/Owner/President

  3b) MANAGEMENT-FLAVOURED BUT VAGUE wording, with no C-level or VP marker — e.g. "Management
      Executive", "Executive", "Business Leader", "Senior Leader", "Leadership", "Management
      Professional", "Business Management", "Team Lead", "Supervisor", "Officer" (non-C-level)
                                                                 → Director/Manager

  3c) A PEOPLE FUNCTION with no seniority word — "Human Resources", "People", "Talent",
      "Recruiting", "Talent Acquisition", "HR"                    → HR/Talent

  3d) ANY OTHER FUNCTION, DEPARTMENT OR FIELD with no seniority word — e.g. "Advertising",
      "Marketing", "Sales", "Engineering", "Operations", "Finance", "Accounting", "Design", "Legal",
      "Customer Success", "IT", "Product"                         → IC/low authority
      (a bare function name evidences no authority, so do not assume any)

STEP 4 — Return "unknown" ONLY when at least one of these is true and nothing above matched:
  - the input is empty or whitespace;
  - the input is purely a company, brand or product name, carrying no role and no function
    (e.g. "SNAK Consultancy Services");
  - the input carries no interpretable role or function whatsoever (e.g. "Mascot", random words,
    a URL, a phone number).

TIE-BREAKS
  - Always prefer the HIGHEST seniority indicated. "VP, Engineering Manager" → VP/Head.
  - Multiple roles split by "/", "|", "&" or "," → take the highest.
  - Explicit seniority (STEP 2) always beats an inferred signal (STEP 3).
  - Ignore employer names and departments when a real seniority word is present; read seniority only.

#EXAMPLES#

  "Co-Founder & CTO"                     → Founder/CEO/Owner/President
  "CTO"                                  → C-level
  "SVP, Product"                         → VP/Head
  "Head of Data Science"                 → VP/Head
  "Director of Engineering"              → Director/Manager
  "Engineering Manager"                  → Director/Manager
  "Senior Recruiter"                     → HR/Talent
  "Product Manager"                      → IC/low authority
  "Analyst"                              → IC/low authority
  "Hiring Manager"                       → HR/Talent
  "President & CEO"                      → Founder/CEO/Owner/President
  "Management Executive"                 → Director/Manager          (STEP 3b)
  "Executive"                            → Director/Manager          (STEP 3b)
  "Business Leader"                      → Director/Manager          (STEP 3b)
  "Advertising"                          → IC/low authority          (STEP 3d)
  "Marketing"                            → IC/low authority          (STEP 3d)
  "Human Resources"                      → HR/Talent                 (STEP 3c)
  "Helping SaaS founders scale revenue"  → Founder/CEO/Owner/President (STEP 3a)
  "Senior Engineer at Acme Corp 🚀"      → IC/low authority          (company + emoji stripped)
  "SNAK Consultancy Services"            → unknown                   (STEP 4)
  "Mascot"                               → unknown                   (STEP 4)
  ""                                     → unknown                   (STEP 4)

#INPUTS#

HM Title:
```

---

## Optional improvement worth considering

The root cause is that the source field sometimes holds a headline or department instead of a title. If
the workflow can pass a **second, optional input** — the LinkedIn headline or current-position line —
the ladder gets far more to work with and `unknown` should approach zero:

```
#INPUTS#

HM Title:
LinkedIn headline (optional, use only if HM Title is not a usable job title):
```

With the instruction: *"If HM Title is empty, a company name, or otherwise not a usable job title,
classify from the LinkedIn headline instead. If both fail, return unknown."*

Not added to the main prompt above, since it changes the workflow's input contract — flagging it for
Gaston to decide.
