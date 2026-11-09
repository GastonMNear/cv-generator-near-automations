---
type: tool
title: LinkedIn — Outreach Reference
created: 2026-06-10
updated: 2026-07-10
tags: [tool, linkedin, outreach]
status: active
related: ["[[context/outbound-engine]]", "[[context/team]]", "[[tools/clay]]"]
---

# LinkedIn

Outreach + lead-gen channel. **Samuel** owns daily execution (connection requests, DMs, follow-ups, replies). Gaston's role is strategic: connect LinkedIn to the broader engine, supply Clay lists, design the expansion plan.

## Expansion Motion (pilot)

Goal: a **scalable, repeatable** model where one operator safely manages multiple LinkedIn accounts and generates extra booked calls **without hurting the existing baseline**. Pilot question: stay manual, go semi-automated, or hybrid? Uses high-intent Clay lead lists to cut manual work.

## Account Safety (core constraint)

- **Fake / AI-generated accounts are risky** — safer path is existing **warmed accounts** with strong profile quality.
- Restrictions/bans would hurt the company — scale carefully, protect account health, reply quality, and message consistency.

## Cross-Channel Role

- Selected high-intent **cold-call leads** can get a LinkedIn connection request as a supporting touch.
- Touches should fire **early** (alongside email 1–2), not only after the email sequence ends. See [[context/outbound-engine]].

## Clay No-Email Routing

Qualified leads without a found work email should not be discarded.

Current rule:
- If a lead passes ICP, company, role, and contact qualification but `Work Email` is missing, do not push it to Smartlead.
- Route it from Clay to the shared **No Hiring Managers List - No Email Found** Google Sheet through a run-conditioned export.
- Use these leads for LinkedIn outreach/list building because they already consumed enrichment and are still high-intent.

Future use cases to validate:
- Calling, if phone enrichment is added or if these leads are routed into Calling Sequences.
- Paid-media/lookalike audiences, but only after confirming required fields for LinkedIn/Meta audience matching.
- Additional email enrichment attempts if a better provider/workflow is approved.

## Metrics

Connection requests sent · acceptance rate · replies · positive replies · calls booked per account · account-health / restriction flags.

Also track whether LinkedIn leads came from no-email Clay routing, direct LinkedIn list builds, or another source. This matters for comparing incremental value by channel/source.
