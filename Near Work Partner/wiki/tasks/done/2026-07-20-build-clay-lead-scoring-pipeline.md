---
type: task
title: "Build Clay lead scoring / qualification pipeline"
created: 2026-07-20
updated: 2026-08-19
priority: high
status: done
from-meeting: "[[wiki/meetings/2026-07-20-clay-lead-scoring-pipeline]]"
related: ["[[wiki/tools/clay]]"]
sources: ["[[bibliography/2026-07-20 - Clay Lead Scoring Pipeline - Meeting]]"]
---

# Build Clay lead scoring / qualification pipeline

Design + build the pipeline agreed with Daniel on 2026-07-20. Confirm exact Clay field names before building (transcript was low-fidelity).

## Sub-steps
- [ ] Add `LinkedIn ICP type` field — C-level / hiring manager vs. non-hiring manager.
- [ ] Score non-hiring-managers via `contact seniority bucket`; keep hiring-manager as its own flag.
- [ ] Derive work model (remote / hybrid / on-site) from the Clay job description as an input; default ambiguous → `unknown`. Add a `remote-convertible flag`.
- [ ] Build near-fillable / maybe-fillable / reject classification against the historical filled-roles list (~150–250 roles).
- [ ] Write the priority formula (high / med / low) combining seniority bucket + role family + role fit score + near-fillable score, plus a `reason` column.
- [ ] Set up the human-check loop: export scored leads to a spreadsheet → manual review → feed corrections back into Clay.
- [ ] Define outreach owner + channel (email / phone / LinkedIn) and sequencing per priority tier.
