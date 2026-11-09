---
type: tool
title: Clay — Reference
created: 2026-06-03
updated: 2026-07-10
tags: [tool, clay]
status: mature
related: ["[[tools/smartlead]]"]
---

# Clay

Lead enrichment and database tool. Used for sourcing, enriching, and managing leads across all campaigns.

## Access

- Workspace: HireWithNear (ID: 447061)
- Auth: Session cookie (`claysession`) — see clay-api skill for login flow
- API: `api.clay.com/v3` (internal, undocumented)

## Known Tables

See `.claude/skills/clay-api/references/known-tables.md` for pre-cached table IDs and field IDs.

Tables:
- US OJ No HM
- US OJ HMs
- LatAm OJ No HMs
- LatAm OJ HMs
- Canada OJ No HM
- Canada OJ HMs

## Common Operations

- Fetch lead by email → use `scripts/fetch_lead.py`
- Look up table/field IDs → see `clay-api` skill
- Bulk-fetch records → 3-step workflow in clay-api skill

## Quirks

- Session cookies expire after ~7 days — re-auth if getting 401s
- Passwords may contain `$` — use single quotes in curl
- Rate limits: retry with 30-60s backoff on 429/504


## Strategic Usage (Gaston)

Clay is the **lead intelligence layer** — where raw data becomes a qualified, segmented prospect list ready to push into sequences. It's part of the operating system for outbound, not just a database. See [[context/outbound-engine]].

- **DMU (Decision Making Unit) targeting** — who inside the account to reach.
- **Conditional routing formulas** — e.g. Baseline vs. Challenger split, HM vs. No-HM paths.
- **Firmographic filters** — e.g. 50+ employees, US businesses, currently hiring offshore (India/Philippines signal).
- **Exclusion lists** — CPG/DTC, AI-native companies.
- Dedicated workflows targeting **CPG/DTC brands needing AI/ML marketing talent**.
- **No-HM coverage**: when Clay/AI-researcher miss the right person, fall back to the **AI researcher** (by title/function) and **Apollo** (see [[tools/apollo]]).

**Cost discipline:** before enriching, check what's already enriched, what fields are missing, and whether extra credits are worth the expected opportunity value. Clay credits are tracked separately from inbox/domain/Smartlead costs.

## Open Jobs Workflow Model (July 2026)

**Experiment 5 - US Open Jobs No Hiring Managers / Candidate Lead vs. Routing CTA** is the current model workflow for Open Jobs builds. Use it as the reference pattern before creating or rebuilding US, Canada, LatAm, or Asia Open Jobs workflows.

Core architecture:
- **Source table** imports LinkedIn job posts through Clay's Find Jobs source.
- **Qualification waterfall** filters recruiting/staffing companies, bad-fit industries, employee count, HubSpot/client conflicts, and role fit before expensive downstream steps.
- **Company Table** receives the first occurrence of a company, enriches company-level data once, then feeds those fields back into each job-post row.
- **Contact finding** uses Clay first, AI researcher second, and Apollo fallback when the account is worth contacting.
- **Lead tabs** split one job post into one row per contact and can separate hypothesis arms such as Candidate Lead CTA vs. Routing CTA.
- **Routing** sends verified-email leads to Smartlead and qualified no-email leads to LinkedIn/no-email sheets.

### Company Table Pattern

Use this pattern for Open Jobs workflows whenever the same company can appear with multiple job posts.

1. Detect first company occurrence by company LinkedIn/domain in the job-post table.
2. Check Exclusion Lookup and company type before paying for enrichment.
3. Send only non-staffing/non-recruiting companies to the Company Table.
4. Enrich company description, industry, employee count, LatAm/headcount signals, and other firmographic fields once.
5. Look the company back up from the parent job-post table. Use a delay when processing large batches so the Company Table has time to finish enrichment.
6. Reuse Company Table fields across every job post from that company.

Why it matters: one company with five job posts should not trigger five company-level enrichments. The July 09 workflow walkthrough identified this as the most important Clay credit-efficiency improvement to replicate across Open Jobs.

### Source Setup Rules

- Keep regional workflows separate: US, Canada, LatAm, Asia.
- Keep HM and No-HM workflows separate unless there is a deliberate reason to combine them.
- Standard evergreen Open Jobs source uses daily recency (`1 day`) and a daily schedule.
- For a brand-new campaign, use a longer initial recency window only when volume requires it, commonly 7-14 days and occasionally 30 days for approved experiments.
- Standard Open Jobs uses **Full-Time** only.
- Standard remote Open Jobs uses `Remote` in the job-description filter.
- Hybrid roles should be a separate workflow/campaign because qualification and copy differ.
- Do not mix materially different campaign logic in one workflow just to save setup time.

### Qualification Gates

- **Recruiting/staffing suppression:** check Exclusion Lookup before AI classification. If AI finds a new staffing/recruiting company, write it back to Exclusion Lookup.
- **Company fit:** reject disqualified industries and companies outside the active employee-count range.
- **Employee count:** July 09 transcript confirms the referenced No-HM workflow allows companies with employee count >= 2 and <= 500.
- **HubSpot:** if the company does not exist in HubSpot, it can proceed. If it exists, reject companies with hires. If it has zero hires, allow only when the record has not been modified recently, roughly older than two months in the walkthrough.
- **Role qualification:** AI checks whether Near can credibly fill the role. This prompt should be reviewed and tightened; it may currently be too loose.
- **No-HM contact logic:** smaller companies lean CEO/founder/C-level; larger companies lean department heads, HR/talent, and role owners.

### Maintenance Rules

- Clay has a 50k row limit on tables and a 50k result/import limit on sources. If a source/table fills, new job posts stop importing.
- Review high-volume Open Jobs workflows weekly. US workflows may need more frequent checks than lower-volume regions.
- Prune old job-post rows by time window, not arbitrary row count.
- Company Tables also need row-count monitoring. When one approaches 50k, plan a sharding/lookup-order update before it blocks enrichment reuse.
- **New company table when the last one is full** (Gaston's Looms "Creating New Company Table in Clay" Part 1 / Part 2, Oct 26):
  1. Duplicate the latest company table (e.g. LATAM Company Table 2 → **Table 3**). In it, keep one Lookup Single Row per *previous* table (Company Identifier = Company Identifier), merge their results into one value, and dedupe, so only companies not already in an older table get enriched.
  2. In the Jobs table, add a new **Send table data** column → the new table. Send only Company Name, Domain, LinkedIn, Company Identifier, with the same run conditions as the old send column. Then **delete the old Send column** (the old table is full, so nothing lands there anyway).
  3. Add a new **Find in Company Table N** lookup. Its run condition = the previous find's condition + "not found in any earlier find".
  4. Add the new find to every **merged company formula column** (qualified for outreach, employees, industry, remote/LATAM countries…). Downstream steps then reference one merged variable whichever table the company came from.
- The **Send table data / "rows from…" feed is itself a source with a 50k cap**, separate from the destination table's row count. If the send column errors while the target table is well under 50k, delete that source and re-create the send column.
- Do not use Clay imports as the lead-sync path into BigQuery/reporting. Smartlead lead sync now belongs to Paz's SmartLead batch-fetch action. See [[tools/smartlead]].

## Fields Worth Preserving

- `LeadSource` — identifies whether a contact came from Clay, AI researcher, Apollo, or another source. Important for quality analysis once reporting includes the field.
- `Role Qualification` — AI output deciding whether the job is a realistic Near fit.
- `Company Type` / recruiting-company AI output — used with Exclusion Lookup to suppress staffing/recruiting competitors.
- `Normalized Company Name`, `Normalized Job Title`, `Hiring Country` — copy variables; prevent awkward legal names and raw job-title strings in email.
- `Job Description Analysis` — extracts role context, years of experience, and snippets used for personalization.
- `Compensation Guide` / role-match outputs — support LatAm compensation and savings claims. Do not let freeform AI invent salary claims.

## Backlog From July 09 Workflow Walkthrough

See [[tasks/2026-07-10-clay-reporting-workflow-improvements]].
