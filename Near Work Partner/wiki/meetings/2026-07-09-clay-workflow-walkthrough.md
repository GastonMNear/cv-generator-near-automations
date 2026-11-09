---
type: meeting
title: "Clay Workflow Walkthrough — Experiment 5"
created: 2026-07-10
updated: 2026-07-10
attendees:
  - "Gaston Murillo — GTM Engineer / SalesOps"
  - "Daniel Ardila — Campaign Strategy"
meeting-type: internal
duration-min: 113
recording_id: 162303039
fathom-url: "https://fathom.video/calls/741333840"
tags: [type/meeting, meeting-type/internal, outbound, clay]
status: active
related: ["[[tools/clay]]", "[[tools/smartlead]]", "[[tools/linkedin]]", "[[context/outbound-engine]]"]
sources: ["[[bibliography/2026-07-09 - Clay Workflow Walkthrough - Meeting]]"]
---

# Clay Workflow Walkthrough — Experiment 5

## TLDR

- **Experiment 5 - US Open Jobs No Hiring Managers / Candidate Lead vs. Routing CTA** is the best current Open Jobs workflow model and should be used as the reference for future Open Jobs rebuilds.
- The main architecture improvement is the **Company Table pattern**: enrich company-level data once, then reuse it across multiple job-post rows from the same company.
- Qualified no-email leads should route to the **No Hiring Managers List - No Email Found** sheet for LinkedIn instead of being discarded or pushed to Smartlead.
- Reporting needs `LeadSource` so the team can compare contact quality by source: Clay, AI researcher, Apollo, or other.
- Several optimization ideas were identified: replicate Company Table logic, tighten role/company prompts, test 7-day sending, explore hybrid-role workflows, and investigate replied-then-ghosted calling handoff.

## Key Decisions

- Treat Experiment 5 as the current model for Open Jobs workflow design.
- Replicate Company Table logic across Open Jobs workflows to reduce duplicate Clay credit usage.
- Keep regional Open Jobs workflows separate and keep HM vs No-HM separate to control 50k row/source limits and maintain clean contact logic.
- Continue using run conditions to avoid enrichment and AI steps on disqualified rows.
- Do not send no-email leads to Smartlead. Route qualified no-email leads to LinkedIn/no-email lists.
- Preserve `LeadSource` in lead tables and reporting sync.

## Workflow Notes

### Clay Source

- Find Jobs source imports new job postings from LinkedIn through Clay.
- Evergreen Open Jobs sources should run daily with a short recency window, typically 1 day.
- New campaigns may use a longer initial recency window, usually 7-14 days and sometimes 30 days for approved experiments.
- Standard Open Jobs source filters include region, Full-Time employment type, Remote job-description keyword, job-title exclusions, HM/no-HM setting, posting date, and source result cap.
- Hybrid roles, C-level roles, and niche clinical/psychology roles should be separate workflows if tested because qualification and copy need different logic.

### Qualification Waterfall

- Check Exclusion Lookup before running AI company-type classification.
- If AI identifies a staffing/recruiting company, write it back to Exclusion Lookup.
- Use Company Table enrichment for company description, industry, employee count, LatAm/headcount signals, and related fields.
- Employee-count rule in the referenced No-HM workflow: company must have at least 2 and no more than 500 employees.
- HubSpot rule in the walkthrough: companies not found in HubSpot can proceed; companies with hires are rejected; companies with zero hires can proceed only if last modified is older than roughly two months.
- Role Qualification prompt decides whether Near can credibly fill the role and needs review/tightening.

### Contact Finding

- Find Contacts at Company is the first contact layer.
- AI researcher searches website/team/about pages and LinkedIn when Clay does not find enough relevant people.
- Apollo is the fallback layer when the company is worth contacting but Clay/AI coverage is incomplete.
- `LeadSource` should identify which layer found each contact.
- No-HM contact logic changes by company size: smaller companies lean CEO/founder/C-level; larger companies lean HR/talent, department heads, and role owners.

### Lead Tabs and Routing

- Parent job-post table sends qualified leads into lead tabs, one row per contact.
- Experiment 5 splits lead tabs by hypothesis/CTA: Candidate Lead CTA vs Routing CTA.
- The split uses a roughly 50/50 randomizer; results should be close but not perfectly equal.
- Lead tabs clean names, find work emails, generate Email 1/2/3 copy, and add verified-email leads to the correct Smartlead campaign.
- If work email is missing but the lead passed filters, route to LinkedIn/no-email sheet.

## Action Items

- [ ] Replicate Company Table logic across Open Jobs workflows.
- [ ] Ask Paz to include `LeadSource` in the Smartlead batch-fetch/reporting sync.
- [ ] Review and tighten the Role Qualification prompt.
- [ ] Review the Company Type / recruiting-company prompt and job-title exclusion list.
- [ ] Investigate Smartlead webhook or batch process for replied-then-ghosted leads into Calling Sequences.
- [ ] Validate required fields for LinkedIn/Meta lookalike audiences.
- [ ] Implement/report 7-day sending test on roughly 10% of Candidate Lead volume.
- [ ] Improve Email 2 and Email 3 personalization using available Clay fields.

## Open Questions

- What is the canonical link and run log location for Paz's SmartLead batch-fetch action?
- Does Paz's current sync already include `LeadSource`?
- What is the exact Smartlead schedule and decision rule for the 7-day send test?
- Which excluded roles should stay globally excluded vs move into separate small experiments?
- Can replied-then-ghosted leads be routed into Calling Sequences without creating noisy or unsafe handoffs?

## Source

Fathom: https://fathom.video/share/YzZcxdVX-oG1D5AvTjPzDcKWDCmp9UCy
