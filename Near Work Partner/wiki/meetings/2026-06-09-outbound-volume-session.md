---
type: meeting
title: "Outbound Volume Session"
created: 2026-06-09
updated: 2026-06-11
attendees:
  - "Gaston Murillo — GTM Engineer / SalesOps"
  - "Michael Girdley — Investor/Advisor"
  - "Andres Bahamon — Head of Sales / Operations"
  - "Daniel Ardila — Campaign Strategy"
  - "Franco — AI Services Lead"
meeting-type: internal
duration-min: 56
recording_id: 153626817
fathom-url: "https://fathom.video/calls/703319526"
tags: [type/meeting, meeting-type/internal]
status: mature
related: []
sources: ["[[bibliography/2026-06-09 - Outbound Volume Session - Meeting]]"]
---

# Outbound Volume Session

## TLDR
- **Nearshore vs. Offshore email experiment** (~2,000 leads, 4 calls) is performing at ~70% of baseline — team aligned to keep running and gather more data; under-50 segment volume is low but per-lead conversion looks fine.
- **Persona-level tracking gap identified**: data exists in Smartlead but nobody is looking at reply/booking rate per persona weekly — agreed this needs to be built into reporting.
- **Experiment concurrency cap set at 3** (current manual capacity); Gaston estimates 2-week build-out for agent infra (make.com → Claude Code + campaign iteration agent) before capacity increases.
- **Michael's benchmark**: 330 emails/day → 2 booked calls/day using persona-segmented campaigns + OpenClaw agent for attribution via TidyCal → SmartLead → Close CRM cron job.
- **Gaston OOO weeks of Jun 16 & Jun 23** — Paz (Clay-fluent) and Hector (admin onboarded) being lined up for coverage; Andres to coordinate with Franco & Hayden.

## Key Decisions
- Continue running Nearshore vs. Offshore campaign; do not kill yet — too early with small numbers.
- 3 simultaneous experiments = safe ceiling at current (pre-agent) capacity.
- Everyone to come to next call (Tue Jun 16, noon CT) with narrow single-variable experiment proposals.
- Michael will share his experiment-proposal template as a format example.
- Migrate reporting from make.com → Claude Code routines (target: before Gaston's OOO or ~2 weeks).
- Splitting monolithic Clay workflow into per-segment tables will enable independent experiment iteration without cross-contamination.

## Action Items
- [ ] Add persona-level tracking to SmartLead/Clay reporting — *Gaston* — (maps to [[tasks/2026-06-10-track-response-rate-by-persona]])
- [ ] Propose narrow experiment ideas for Jun 16 call — *Gaston / all* — due: 2026-06-13 (maps to [[tasks/2026-06-10-propose-narrow-campaign-experiments]])
- [ ] Onboard Hector on Clay + lead scraping before OOO — *Gaston* — due: 2026-06-13 (see [[tasks/2026-06-11-onboard-hector-clay-lead-scraping]])
- [ ] Talk to Paz today re: OOO coverage scope — *Gaston* — (maps to [[tasks/2026-06-10-ooo-coverage-plan]])
- [ ] Draft experiment proposal format + share with team — *Michael* — before Jun 16
- [ ] Post Slack update when dashboard refreshed — *Andres* — due: 2026-06-10 EOD
- [ ] Send calendar invite: Tue Jun 16 noon CT — *Michael*
- [ ] Coordinate Franco & Hayden on Gaston OOO backup resources — *Andres*

## Context
- **CRM data cleanup (Andres)**: referral sources now clean (organic/referral program/founder network/employee referral); headcount buckets (1-10, 11-50, 50+) live in dashboard; final piece = re-qualifying "unqualified due to pricing" deals (Carlos reviewing calls, done by EOD Jun 9; full dashboard refresh Jun 10).
- **Experiment strategy history (Daniel)**: prior tests — VP Sales case study (9k emails, ~2 calls) and low/medium-seniority roles — underperformed broad Open Jobs. Pivoted to strong candidate-led message. Team now has capacity to revisit persona-segmented experiments.
- **Michael's OpenClaw setup**: Claude Code for analysis + OpenClaw (agentic, API-connected) on hardened Mac Mini at home, accessible only via Slack. Full API access to SmartLead, TidyCal (forced attribution dropdown), and Close CRM. Cron job matches bookings to campaigns daily. AI-written email copy consistently outperforms Michael's own.
- **SmartLead AI assistant**: in-app chatbot has near-full account access — can bulk-change send delays, check blacklist risk, etc. Worth exploring for Near's setup.
- **LinkedIn**: new SDR "Michael" onboarded Jun 8, shadowing Sam, warming up LinkedIn accounts. Hiring still open for another SDR.

## Open Questions
- Will Paz have enough bandwidth to cover AI services attribution + outbound ops during Gaston's OOO?
- What are the 2 specific experiment ideas Michael wants to bring to the Jun 16 call?
- When exactly does the make.com → Claude Code migration need to be done vs. Gaston's OOO start?

## Full Transcript
See Fathom: https://fathom.video/share/uPNVSHoE435fvgDb11wN7begSCiEzCuM
