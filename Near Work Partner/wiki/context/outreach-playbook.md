---
type: context
title: Outreach Playbook
created: 2026-06-03
updated: 2026-07-10
tags: [context, outreach, playbook]
status: active
related: ["[[context/outbound-engine]]", "[[context/company]]", "[[context/cold-email-copywriting]]", "[[context/staffing-recruiting-cold-email-playbook]]", "[[tools/smartlead]]"]
---

# Outreach Playbook

How Near reaches prospects. Strategy and system live in [[context/outbound-engine]]; company claims/proof in [[context/company]].

## Target Personas

Driven by Open-Jobs / hiring signals (see [[context/outbound-engine]]):
- **Hiring Manager** when identified → contact directly.
- **No HM** → founders, C-levels, recruiters, talent/people leaders, department heads, role-specific decision makers.
- Buy-signal: **US companies hiring offshore talent (India / Philippines)** — strong fit for Near's nearshore pitch.
- Firmographic fit: US businesses, 50+ employees, currently hiring.
- Exclusions: CPG/DTC brands, AI-native companies (unless a dedicated AI-service angle).

## Channels & Sequencing

- **Email** = broad coverage, first touch. Variant-tested in Smartlead.
- **LinkedIn** + **cold calling** = layered touches for high-intent leads, ideally triggered **early (after email 1–2)** while the role is still open. See [[context/outbound-engine]].

## Active Campaigns / Experiments

- **Baseline vs. Challenger** A/B split in Smartlead, routing logic in Clay.
- **US Open Jobs +50** campaigns (copy + launch).
- **US Open Jobs <50** — baseline + direct-booking variants.
- AI-service campaigns for accounting & staffing firms (testing).
- Aniwa-inbox replication of a responsive on-site campaign (re-position toward remote).

## Messaging Frameworks

For detailed cold-email writing standards, examples, AI prompting rules, and QA checks, use [[context/cold-email-copywriting]]. For the broader staffing/recruiting copywriting playbook, use [[context/staffing-recruiting-cold-email-playbook]]. Read both before drafting or reviewing campaign copy.

### Value proposition
Strong English-speaking LatAm talent in aligned US time zones — faster (shortlist <5 days, hire <21 days) and 30–70% cheaper than US hires. Lead with the prospect's open role / hiring signal: who to contact, **why now** (role is open), what to say, how to measure.

### Proof / case studies
Reference similar clients or competitors in follow-ups: **AvantStay, Snap Diagnostics, Conversion Logix, Delve, R&d, Verbatim.**

### CTA framing
Assertive but low-friction booking language. Watch for offer confusion (e.g. remote vs. on-site roles) — make the message specific to the role and adjust the angle when the offer might confuse.

## Copy QA (reusable agent checks)

Before a sequence goes live, check rendered emails for: **unfilled placeholders**, grammar issues, **spintax inconsistencies**. Reusable agent prompts exist for this.

## What's Working

- Open-Jobs campaigns targeting actively-hiring companies = strongest motion.
- Case-study-driven follow-ups referencing named clients.

## Notes / Open Questions

- Best-of-both stack conclusion: **Clay layered on Smartlead** for firmographic segmentation; **Instantly** judged strongest Smartlead alternative on UX & variant management (not migrated). See [[tools/smartlead]].
