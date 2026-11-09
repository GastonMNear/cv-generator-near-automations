---
type: context
title: Outbound Engine
created: 2026-06-10
updated: 2026-07-10
tags: [context, outbound, strategy]
status: active
related: ["[[context/my-role]]", "[[context/outreach-playbook]]", "[[tools/clay]]", "[[tools/smartlead]]", "[[tools/apollo]]", "[[tools/linkedin]]"]
---

# Outbound Engine

Near's outbound is one connected machine, not separate activities. It decides **which opportunities to pursue, how to reach them, how much it costs, and how to scale without wasting capacity or lowering quality.** Gaston helps design and run it. See [[context/my-role]].

## Channel Model

| Channel | Role | Owner |
|---|---|---|
| **Email** | Broad-coverage layer — touches almost every opportunity first, captures high intent, feeds the other channels | Gaston (owns/heavily involved) |
| **LinkedIn** | Additional touchpoint for the best opportunities (hiring-now / clear intent) | Samuel (daily execution); Gaston (strategy, Clay lists) |
| **Cold calling** | Additional touchpoint for prioritized high-intent leads | Gaston supports lead-prioritization logic |

**Cross-channel sequencing (target state):** don't wait for a full email sequence to finish before handing to calling/LinkedIn. Trigger calls and LinkedIn touches **earlier — after email 1 or 2 — while the job opening is still fresh.** Same high-intent opportunity touched across channels at the right time.

## Campaign Architecture

Strongest motion = **Open Jobs campaigns** targeting companies actively hiring. Split by:
- **Region** — US / LatAm / Canada (see Clay tables in [[tools/clay]]).
- **Hiring Manager present or not:**
  - **HM identified** → target that person directly.
  - **No HM** → workflow must identify relevant contacts: founders, C-levels, recruiters, talent leaders, department heads, role-specific decision makers.

Other signals/segments: US companies hiring offshore (India/Philippines focus) as a buy-signal for Near's nearshore value prop; firmographic filters (e.g. 50+ employees, US); exclusion lists (CPG/DTC, AI-native companies). AI-service campaigns being tested for accounting & staffing firms.

### Active A/B test
**Baseline vs. Challenger** sequence variants in Smartlead, with routing logic built in Clay. Also US Open Jobs <50 baseline + direct-booking variants. See [[context/outreach-playbook]].

## Contact Coverage Problem (Apollo + AI research)

Clay and the AI researcher don't always find the right person at a company. Two fillers:
- **Apollo** — coverage-expansion layer; finds contacts when Clay/AI researcher don't. Goal: more open-job opportunities Near can actually contact. **Estimated impact: ~3,000 additional leads/month.** See [[tools/apollo]].
- **AI researcher** — identifies relevant people by job title/function for No-HM and open-jobs campaigns.

Economics gate every enrichment: what's already enriched, what fields are missing, what extra credits cost, and whether scraping/enriching a lead is worth it given expected opportunity value.

## Clay Workflow Operating Model

The July 09 Clay workflow walkthrough made **Experiment 5 - US Open Jobs No Hiring Managers / Candidate Lead vs. Routing CTA** the current model workflow for Open Jobs builds. See [[tools/clay]] and [[meetings/2026-07-09-clay-workflow-walkthrough]].

Durable rules:
- Use Company Table enrichment so company-level enrichment happens once per company, then feeds back into each job-post row.
- Keep Open Jobs workflows separated by region and HM vs No-HM to control 50k Clay limits and keep contact logic clean.
- Preserve `LeadSource` so reporting can compare quality by contact-finding layer: Clay, AI researcher, Apollo, or other.
- Qualified no-email leads are not dead leads. Route them to LinkedIn/no-email lists rather than Smartlead.
- Review role-qualification and company-type prompts periodically because bad filters either waste sends or suppress real opportunities.

## Lead Prioritization → Calling

Email volume > call capacity, so not every email lead gets called. Priority order:
1. **Hiring managers** first.
2. **High-potential No-HM leads** — C-levels in smaller companies, recruiting people in larger companies.

Gaston defines the logic for which leads move email → calling and when.

## Outbound Command Center

Central reporting hub so the team compares channels and aligns strategy (email / LinkedIn / calling). Tracks: campaigns, active experiments, monthly & weekly metrics, email capacity, calls booked, reply rate, positive replies, bounce rate, leads added, new leads contacted, total leads contacted, LinkedIn connection requests / acceptance / replies / calls-booked-per-account, account-health flags. Goal isn't more volume — it's understanding **which campaigns produce booked calls efficiently** and which are worth scaling.

### Reporting Sync

As of July 2026, do **not** use Clay imports to BigQuery for Smartlead lead sync. Use **Paz's SmartLead batch-fetch action**:
- fetch Smartlead leads in batches,
- upload missing leads,
- update leads that changed.

Confirm the latest batch completed before treating BigQuery/Command Center data as fresh. Add/verify `LeadSource` in this sync so the team can analyze reply, call-booked, qualified-call, and closed/won outcomes by contact source.

## Costs (tracked separately)

Clay credits · inbox costs · domain costs · Smartlead sending costs — each behaves differently. Roll up to **cost per lead** and **cost per call booked**. Capacity is expanded only when added volume will reach high-intent opportunities.

## Reply Handling

Worked with Hector on reply handling. Focus: make the reply workflow **scalable** so volume grows without losing quality. Includes AI-generated resumes in reply workflows.

## Current / Recent Projects

- Expanding **Apollo** coverage for open jobs.
- Improving the open-jobs outbound engine.
- Replicating the Experiment 5 Company Table pattern across Open Jobs workflows to reduce Clay credit waste.
- Adding `LeadSource` into reporting through Paz's SmartLead batch-fetch action.
- Reviewing Clay prompts for Role Qualification and Company Type / recruiting-company suppression.
- Running/optimizing Smartlead campaigns; incorporating new inbox capacity (e.g. **Aniwa inboxes** — connect to Smartlead, replicate a responsive on-site campaign, then re-position since Near's offer is usually remote vs. those on-site roles).
- Testing AI-service campaigns for accounting & staffing firms.
- Tracking **Unify** job-change alerts. See [[tools/unify]].
- Building a scalable **LinkedIn expansion** motion using Clay lists. See [[tools/linkedin]].
- Supporting cold calling with LinkedIn touches.
- Improving the Outbound Command Center for cross-channel review.
