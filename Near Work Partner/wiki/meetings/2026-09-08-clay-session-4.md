---
type: meeting
title: "Clay Session #4 — CEOs 11–200 Workflow Walkthrough"
created: 2026-09-08
updated: 2026-09-11
attendees: ["Gaston Murillo — trainer", "Sara Sofia Calderon Henriquez — trainee"]
meeting-type: internal
duration-min: 81
recording_id: 181044814
fathom-url: "https://fathom.video/calls/815488849"
tags: [type/meeting, meeting-type/internal, topic/clay, topic/training]
status: mature
related: ["[[wiki/meetings/2026-09-02-clay-session-3]]"]
sources: ["[[bibliography/2026-09-08 - Clay Session 4 - Meeting]]"]
---

# Clay Session #4 — CEOs 11–200 Workflow Walkthrough

> [!note] **Summary-only ingest.** Training content with one unambiguous Gaston-owned deliverable —
> no transcript spend. Fetch live via `recording_id` if verbatim wording is ever needed.

## TLDR
- Fourth Clay training session with Sara, walking the **CEOs 11–200 workflow** end to end as a
  worked example of production-grade Clay logic rather than teaching features in isolation.
- **The central technique is `clay.getCellStatus` for step chaining** — a step runs only when the
  previous one returned `success no data`. This is what prevents parallel execution and wasted credits.
- **Cascading lead-finding fallback: Clay → AI → Apollo**, each firing only if the prior found nothing.
  Maximises coverage per company without paying for redundant enrichment.
- **Company tables and lead tables stay separate** — qualify and enrich at company level, then export
  individual leads via `Send Table Data` with *"send row for each item in a list"*.
- Homework set: Sara builds a simple workflow from scratch, then rebuilds CEOs 11–200 from the
  template plus an Apollo CSV.

## Key Decisions
- **Helper columns are the standard pattern for complex logic** — consolidate multi-condition checks
  (`CanContact`, `Qualified`, `Random A/B Output`) into a single column, so downstream run conditions
  are one simple reference instead of a long compound expression.
- **HubSpot suppression is encoded in `CanContact`:** no open deals, no recent hires, and no contact
  in the last 2 months.
- **Qualification criteria for this workflow:** employee count 11–200, excluding defense and space
  manufacturing, non-profit, and recruiting.
- **Exclusion lookup runs before any AI step** so disqualified companies (e.g. recruiting agencies)
  never consume AI credits.
- **A/B routing happens at company level** — a random helper column assigns qualified companies to one
  of three test groups (Paralysis FOMO, Hidden Cost, Proof First) before leads are exported.

## Workflow Reference — CEOs 11–200

**Company table:**
1. Apollo CSV import (companies using AI) → formula extracts base domain from website URL
2. `merge` column unifies the Apollo domain and the AI-found domain into one variable
3. `Exclusion Lookup` marks disqualified companies before AI spend
4. AI step classifies company type (*Staffing Company* / *Other*)
5. `CanContact` helper column → HubSpot activity check
6. `Qualified` helper column → industry + size gate

**Cascading lead discovery** (each step gated on the previous returning nothing):
1. `Find Contacts at Company` (Clay enrichment) — CEO/Founder title filters, limit 2 leads.
   Run condition: company is `Qualified`.
2. `Relevant Employees` (AI step) — run condition: step 1 contact status is `success no data`.
3. `Find People at Company` (Apollo) — run condition: step 2 succeeded but found no employees.

**Lead table:**
- AI step cleans lead names (*"Peter Kjome, CPA"* → *"Peter Kjome"*)
- `Find Work Email` runs a waterfall across providers (Leadmagic, FindEmail, …), advancing only on failure
- `Add Lead to Campaign` pushes to Smartlead using the resolved work email

## Action Items
- **Gaston** — email Sara the session recordings, the CEOs 11–200 template, an Apollo CSV and a simple
  build exercise → [[wiki/tasks/2026-09-08-send-sara-clay-training-materials]]
- **Sara** — build a simple Clay workflow from scratch, then CEOs 11–200 from the template
- **Both** — review the exercise and walk the OpenJobs workflows in the next session

## Open Questions
- No date was set for the next session in the summary; the OpenJobs review is agreed but unscheduled.

**Source:** [Fathom recording](https://fathom.video/calls/815488849) · `recording_id: 181044814`
