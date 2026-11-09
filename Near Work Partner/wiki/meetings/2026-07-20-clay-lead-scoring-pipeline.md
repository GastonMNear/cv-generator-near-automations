---
type: meeting
title: "Clay Lead Scoring Pipeline"
created: 2026-07-20
updated: 2026-07-20
attendees: ["Gaston Murillo — GTM Engineer / Outbound", "Daniel A."]
meeting-type: internal
recording_id: unresolved   # not found in Fathom for 2026-07-20 — see Full Transcript note
duration-min: 35
tags: [type/meeting, meeting-type/internal]
status: mature
related: ["[[wiki/tools/clay]]", "[[wiki/tools/linkedin]]"]
sources: ["[[bibliography/2026-07-20 - Clay Lead Scoring Pipeline - Meeting]]"]
---

# Clay Lead Scoring Pipeline

> [!warning] Low-fidelity transcript
> Auto-transcription was heavily garbled (Spanglish + noise). Field names below are reconstructed intent, not verbatim. Confirm exact naming against Clay before building.

## TLDR
- Designing a **lead scoring / qualification pipeline in Clay** to classify LinkedIn (and email) leads and assign an outreach priority before they enter a campaign.
- Agreed on segmentation via a **LinkedIn ICP type** (C-level / hiring manager vs. non-hiring manager) plus a **contact seniority bucket** for normalization.
- **Work model** (remote / hybrid / on-site) is derived from the Clay job description as an *input* — not a hard label; ambiguous cases default to `unknown` → human check. Add a **remote-convertible flag**.
- **Role fit** matches each role against Near's historically filled roles (~150–250) → **near-fillable / maybe-fillable / reject**.
- Output is a **priority score (high / med / low)** combining seniority, role family, role fit, and near-fillable score, with a **reason column**; then a **human-check step** via spreadsheet export before campaigns.

## Key Decisions
- Split contacts by **LinkedIn ICP type**: C-level / hiring manager vs. non-hiring manager. Keep hiring-manager as its own flag; score non-hiring-managers via **contact seniority bucket**.
- **Work model is an input, not a label**: derive remote/hybrid/on-site from the job description in Clay; when unclear → `unknown` and send to human check. Add a **remote-convertible flag**.
- Classify roles as **near-fillable / maybe-fillable / reject** by matching against the historical filled-roles list. "Maybe-fillable" = roles similar to ones filled before but not exactly.
- Priority score = **formula** over seniority bucket + role family + role fit score + near-fillable score, with a **reason column** explaining the score.
- Keep a **human-check gate**: export scored leads to a spreadsheet for manual review, then feed corrections back into Clay.

## Action Items
- [ ] Build the Clay lead scoring / qualification pipeline (see task) — *Gaston*
- [ ] Polish Felix and pull top-5 findings — *Gaston*

## Open Questions
- Exact Clay field names + formula weights for the priority score (transcript too garbled to lock).
- How corrections from the human-check spreadsheet flow back into Clay (new column vs. re-run formula).
- Outreach owner + channel routing (email / phone / LinkedIn) per priority tier — discussed but not finalized.

## Full Transcript
Partial / low-fidelity. Original garbled auto-transcript retained in chat history; not stored here due to poor quality.
