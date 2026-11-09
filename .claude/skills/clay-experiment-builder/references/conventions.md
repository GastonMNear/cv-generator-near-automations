# Conventions: how Near's Clay outbound workflows are built

Use these to infer defaults. Anything marked **ask** needs Gaston. When a run proves a
convention wrong or finds a new one, propose an edit here (SKILL.md §9).

## Contents
1. Families (what they are, how to add one)
2. Family: US OJ No-HM experiment (EXP012 / EXP014 line)
3. Cross-family rules (apply to every family)
4. Smartlead conventions (variable contract, cloning, inbox rule)
5. Audit checklist (every family)

## 1. Families

A **family** is a workflow shape: which tables exist and in what roles, the key columns and
their field IDs, how arms are split, naming, defaults, and the Smartlead pattern. Duplicated
workbooks keep field IDs, so one family entry serves every copy of it.

**Matching:** from `cb.audit`: table roles (jobs = has a `v3-action`/webhook source, companies,
leads), column names (`Lead Title Search`, `Find in Companies Table`, `A/B Output`,
`Cold Email Creation`, `Add Lead to Campaign`), and the field IDs below. Most present → same
family. Several missing or renamed → **not** this family: ask (SKILL.md §Workflow families).

**Adding a family** (proposed at the end of the first run on it, applied after OK), using the
same headings as §2: anatomy, field IDs (verified), naming, defaults (with who decided and
when), Smartlead pattern, family-specific audit checks, known harmless leftovers.

Other workflows in `clay-daily-control/references/active-workflows.md` (US HMs EXP006,
Coworkers, HubSpot cold accounts, Apollo EXP010, HireBase, LatAm/Canada/Asia No-HM and HM,
EXP013 HR leaders) have **no family entry yet**.

## 2. Family: US OJ No-HM experiment (EXP012 / EXP014 line)

Verified on EXP014 Engineering, Sales/GTM and Marketing (2026-11-06).
Instances: see `clay-api/references/known-tables.md` §1g, §1g-2, §1g-3.

### 2.1 Anatomy
```
Find jobs source (segment job-title keywords, US, full-time, last 3–4 days, often scheduled daily)
  └─ Jobs "Remote Jobs, US, Recent"                  AUTO_RUN normally OFF while building
       Previously Found Recruiting Company? ×2  → Exclusion Lookup t_2w6YPVuSrbj7
       Already in HM workflow?                   → HM jobs table
       Lookup Company in this workflow → First Occurrence of Company?
       companyType (AI: Recruiting / Other) → Write to Exclusion Lookup (if Recruiting)
       Send To Companies Table (route, first occurrence + "Other")
       Find in Companies Table (lookup on companyIdentifier) → "(merge)" formulas read
          record["<column name>"]: Qualified? / Description / Industry / Employee Count /
          Country Count / 3 Remote / 3 Latam / Company Domain / Hq Country, A/B Output
       Open Role Persona → Lead Title Search (AI, comma list) → MoltSets Titles (formula, ≤2-word titles)
       JD / pay: Job Description, Job Compensation, Lookup Multiple Rows (comp guide
          t_0theva5JjGp7cXT3z4A) → Estimated Latam Pay Range, Role Match, Role Qualification
       Contact chain, stop at first hit: Find Contacts (Clay) → Relevant Employees (AI)
          → Find people by job title (Apollo) → MoltSets Lead Search
       Routes: [Baseline] / [Challenger] Send Clay | AI | Apollo | Apollo (2) Leads
          condition: A/B Output === '<arm>' && snippet && person && pay/no-JD && role qualified
  └─ Companies "<Segment> | Companies Table"         AUTO_RUN ON, dedupes on companyIdentifier (keep oldest)
       Enrich Company, Headcount by Country, Qualified for Outreach?, A/B Output (50/50)
  └─ Leads [Baseline…] / Leads [Challenger…]         one table per arm, identical schemas
       Email waterfall → Work Email; MoltSets fallbacks → Final Work Email
       HR Classification (HR leads → EXP013), Name Analysis, Email Overview
       Cold Email Creation (JSON subject_line + email_one) → Email 2 draft → Email 3 draft
       Add Lead to Campaign (Smartlead), condition: Subject && Email One && Two && three
```
**Where the segment lives:** only in the jobs source's job-title keywords, the Lead Title
Search prompt, and the challenger Email 1 prompt's slot examples. Email copy itself is
segment-neutral (EXP012 used identical email prompts in every segment).

### 2.2 Field IDs (same in every copy; verify cheaply each run)
| Column | Field ID |
|---|---|
| Leads: Cold Email Creation | `f_zhSirppXa2dV` |
| Leads: Email One / Subject Line | `f_dWUgCoGRG2RD` / `f_VX8hfWJ28i7g` |
| Leads: Email 2 draft / Email Two | `f_7DNge2NPZWUm` / `f_v8Q9RiHtiQTY` |
| Leads: Email 3 draft / email_three | `f_gEaUqxfuTyrQ` / `f_MWiMXxrgUCeC` |
| Leads: Email Overview / Final Work Email | `f_najVDpzDZU5i` / `f_0tnzx7d5m7PoG8pfywt` |
| Leads: Add Lead to Campaign | `f_q97azby9qkPE` |
| Leads: source field "Rows from: …" (read via `?.parent?.[name]`) | `f_0tdyrtbYupMAJFX4pPY` |
| Jobs: Lead Title Search / A/B Output | `f_0t5mo6xyqJ4tcApKWbm` / `f_0tk4zudGw2j3pgBX3Ex` |
| Jobs: Find in Companies Table | `f_0thesu2VpqS8bGWiEJP` |
| Companies: Qualified for Outreach? / companyIdentifier / source field | `f_0thet2wFVpWUoSZrmP9` / `f_0thesmlVvKCVHVySti2` / `f_0thesmkDJoRCzeoNux8` |

Every companies table in this line (EXP012 and EXP014, all segments) shares these IDs.
Columns created later (new routes, `A/B Output` added to a reused table) get new IDs: read
them from the audit.

### 2.3 Naming (infer; show in the plan)
| Thing | Pattern |
|---|---|
| Workbook | `[EXP0xx] - US Open Jobs \| No HMs \| <Segment> Segment` (+ ` + <extra>`) |
| Baseline leads table | keep the source's name |
| Challenger leads table | `Leads [Challenger] - US OJ No HMs \| <short angle>` |
| Companies table | `<Segment> \| Companies Table` |
| Challenger routes | `[Challenger] Send Clay \| AI \| Apollo \| Apollo (2) Leads` |
| Smartlead | `[EXP0xx] - Baseline \| US OJ No HM Priority Segments \| <Segment> dept \| B Inboxes` / `[EXP0xx] - Challenger1 \| …` |

Another region, HM workflows or a non-standard name: **ask**.

### 2.4 Defaults
| Decision | Default | Source |
|---|---|---|
| What differs between arms | Only Email 1 (Cold Email Creation) | one-variable tests |
| Email 2 / 3 | Byte-identical to baseline | same |
| A/B split | 50/50 `"Baseline"` / `"Challenger"`, only when `Qualified for Outreach?` | Gaston, 2026-11-06 |
| Challenger table | UI duplicate of the baseline leads table, renamed | Gaston |
| Lead title search | Department heads at every size; + Founder/Cofounder/CEO/COO < 150 employees; + HR/talent leaders ≥ 300 | Gaston, 2026-11-06 |
| Lead title search structure | No-'of' rule, permutations, dept-heads list by sub-function, seniority example in the segment | EXP014 Sales/Mkt |
| Deprecated models | gpt-4o / gpt-4o-mini → `gpt-5.4-mini`, both arms | |
| Email-draft model | The baseline arm's Claude model (haiku-4-5 on EXP014) | |
| Pay in copy | Midpoint → yearly (hourly ×2,080, monthly ×12), round to 1,000; missing US → market estimate; missing LatAm → US × 0.7 | Gaston, 2026-11-06 |
| Companies table | The segment's existing enriched table (EXP012 `<Segment> \| Companies Table`), else the source's; never create silently | Gaston, 2026-11-06 |
| Jobs source schedule | Keep whatever the duplicate inherited (daily 07:00 Bogota on EXP014) | Gaston, 2026-11-06 |
| Smartlead template | The source experiment's own arm campaigns by ID (EXP014: `4341415` / `4341416`) | |
| Subsequences / OOO | Gaston, in the Smartlead UI | API limits |

### 2.5 Family-specific audit checks
- Jobs source keywords + excludes fit the segment; days 3–4; US; schedule noted.
- Lead title search fits the segment; `MoltSets Titles` still derives from it.
- Exclusion Lookup write → `t_2w6YPVuSrbj7`. Pay lookup → `t_0theva5JjGp7cXT3z4A`.
- Intentional cross-workflow routes on leads tables: `Send to CC <50 NO HM Workflow`,
  `Send HR Lead to EXP013` (label `HR`). OK.
- Known harmless leftovers: refs to deleted fields in `conditionalRunFormulaPrompt` / optional
  paths / examples of First Occurrence of Company?, Normalized Company Name, Relevant Employees
  Array, Cold Email Creation (`f_SUTHMU5bi2XD`); a "Rows from: Leads … Engineering" source with
  0 records on the leads tables.

## 3. Cross-family rules

- **Duplicates keep field IDs** (workbooks and tables). Diff a copy against its source by field
  ID; expect only table pointers + the segment text.
- **A duplicated workbook makes its own empty copies** of every table, including the companies
  table, and points everything at them. If Gaston moves an existing table in, the links still
  point at the empty copy until re-wired.
- **Lookups expose `record` by column name.** Re-pointing a lookup to a table with the same
  column names needs no formula remap; only missing column names matter (`cb.schemaDiffByName`,
  `cb.keysReadFrom`).
- **Routes can't change destination.** Create a new one (§Create a route).
- **Credits are shared** across the workspace: prove "no runs" with run status, not credits.
- **Count reach from Smartlead.** Clay's add-lead SUCCESS includes leads skipped as already in
  another campaign (70–93% on EXP014's first runs).

## 4. Smartlead conventions

### Variable contract (US OJ No-HM line; check per family)
Copy: `​{{subject_line}}` / `{{email_one}}` + `%signature%` → +2 days `{{email_two}}` → +4 days
`{{email_three}}` + `%signature%` → +1 day manual "Send Lead to Justcall".
Clay `Add Lead to Campaign` sends `custom_fields` with exactly: `subject_line` (Subject Line + " "),
`email_one` (Email One + " "), `email_two` (Email Two + " "), `email_three`, plus reporting fields
`job_url, industry, lead_source, employee_count, prospect_title, open_role_title, lead_email_source,
company_linkedin_url, normalized_company_name`. Top level: `email` = Final Work Email, names,
`linkedin_profile`, `location`, `company_name`, `company_url`. Each arm's `email_one`/`subject_line`
come from **that arm's** Cold Email Creation, so both campaigns are identical apart from the name.

### Cloning
Template = the source experiment's arm campaigns **by ID** (names can hide U+00A0). ACTIVE is fine
(read only). Clone each arm from its own source arm. Expected residuals: OOO off (UI) and
`ignore_ss_mailbox_sending_limit` null.

### Inbox rule (verify every run)
The clone copies the source's exact inbox list (336 accounts on 2026-11-06, called "B Inboxes",
0 tagged `A`, 0 `[Don't use]`). **Don't assume A/B is a clean rest rotation:** on 2026-11-06,
262 of the "A inboxes" campaigns' 296 inboxes were in this same set, and 32 parent campaigns used
all 336 (`scripts/inbox_load.py`). Report the load; if a request implies a different inbox group,
**ask**.

## 5. Audit checklist (OK / ⚠ + reason for each)

1. `cb.audit(...).warnings`: every line explained or fixed (missing table, empty companies table
   vs a fuller one, a same-named table in another workbook, jobs source already pulling).
   `cb.audit(...).external` matches the family's intended shared links (§2.5).
2. Auto-run per table (off on any table whose action columns you'll touch; on where it must stay on).
3. Broken refs (`refScan`): LIVE = fix or ask; optional-path-only / prose-only = report as harmless.
4. Every route → an existing table in this workbook; challenger routes → challenger table;
   labels match the A/B formula.
5. A/B formula in every table the jobs A/B reads from; 50/50; labels match.
6. Lookups → the intended table (not an empty duplicate); filter field exists there; every
   `record["…"]` key the jobs table reads exists there (`keysReadFrom` + `schemaDiffByName`).
7. Reused tables (`cb.reuseCheck`): enrichment fully run, `AUTO_RUN_MODE: keep_existing` (no
   re-enrichment), own outbound links listed, other workflows still feeding it listed.
8. Arm diff: only the column(s) under test differ; Email 2/3 identical; baseline Email 1 untouched.
9. Models: none deprecated; arms equal.
10. Prompts: every nullable `{{field}}` in `optionalPathsInInputs`.
11. Segment text: no leftover department words in prompts (case-sensitive acronyms, whitelist
    intended words).
12. Diff vs source workbook: only pointers + segment text.
13. Smartlead: each arm's campaign is its own, DRAFTED until Gate D, variable contract holds.
14. Leftovers (orphan duplicate tables, stale sources, stale dates): report, don't fix.
15. Family-specific checks (§2.5 for this family).
