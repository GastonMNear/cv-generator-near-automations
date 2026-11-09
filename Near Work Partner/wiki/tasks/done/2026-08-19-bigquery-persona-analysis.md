---
type: task
title: "Re-run BigQuery persona analysis: HM vs No-HM by company size"
created: 2026-08-13
updated: 2026-08-24
priority: high
status: done
from-meeting: "[[wiki/meetings/2026-08-13-deliverability-root-cause]]"
related: ["[[wiki/tasks/2026-08-19-unblock-bigquery-billing]]", "[[wiki/tasks/2026-06-10-track-response-rate-by-persona]]"]
sources: ["[[bibliography/2026-08-13 - Deliverability Root Cause - Meeting]]", "[[bibliography/2026-08-10 - Marketing Stand Up - Meeting]]"]
---

# BigQuery persona analysis — HM vs No-HM

Two queries, one investigation:
1. **Verify the prior result** — Gaston does not believe the existing report's claim that the
   CEO/founder share stayed stable while No-HM volume grew from ~7,000 to ~17,000 leads. The math
   doesn't work unless many genuinely new companies were loaded. Run a fresh query targeting CEOs
   and founders specifically.
2. **Isolate HM vs No-HM performance** across all regions (US dominant; Canada and LATAM included so
   nothing is missed), split into **company-size buckets** to check the C-level proportion in each.

**Why:** This is the central root-cause question. Hiring managers held steady Jan–Jun (3.58% → 3.31%
positive) while non-hiring managers collapsed (1.46% → 0.53%) as that segment's volume more than
doubled. If the CEO/founder share actually fell, that explains August without needing a
deliverability story. Andres separately demanded the full funnel including response rates.

**Blocked on:** [[wiki/tasks/2026-08-19-unblock-bigquery-billing]] — the project is down.

> "Capaz corre uno nuevo específico buscando CEOs y founders para ver que no se haya equivocado."

**Source:** [[wiki/meetings/2026-08-13-deliverability-root-cause]] · [Fathom @46:19](https://fathom.video/calls/784480827?timestamp=2779), [@51:31](https://fathom.video/calls/784480827?timestamp=3091)

## Update 2026-08-21 — unblocked, and the premise was corrected

**BigQuery is working again**, so this is no longer blocked. Gaston attributed the fix to the deleted
tables rather than to the billing escalation — see the note on
[[wiki/tasks/2026-08-19-unblock-bigquery-billing]].

**Important correction to what this analysis is looking for.** The earlier signal that marketing,
engineering and sales personas were underperforming came from **blended** data. Split out:
- **Hiring-manager campaign** — those personas track the campaign benchmark. Not underperforming.
- **No-hiring-manager campaign** — severely underperforming. This is where the problem lives.

So the analysis should target the no-HM segment, and persona-specific copy belongs there. Pointing it
at the HM baseline would risk the only segment still performing.

Daniel is sending a revised prompt to drive this — the Monday deliverable is tracked separately in
[[wiki/tasks/2026-08-21-run-persona-prompt-and-hm-copy]].

**Source:** [[wiki/meetings/2026-08-21-weekly-check]] · [Fathom @40:07](https://fathom.video/calls/792826882?timestamp=2407) · BigQuery up [@42:00](https://fathom.video/calls/792826882?timestamp=2520)

## Update 2026-08-24 — done
Analysis run. **Top 3 high-volume, poor-performing personas on the Open Jobs baseline copy are
defined** — the deliverable Gaston named as done for the week.

Copywriting for those personas is the remaining work and is tracked separately in
[[wiki/tasks/2026-08-21-run-persona-prompt-and-hm-copy]] — it stays open.
