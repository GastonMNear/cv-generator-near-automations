---
type: task
title: "Mine the JustCall report for job-title exclusion keywords, apply to both cold-call campaigns"
created: 2026-08-31
updated: 2026-09-01
priority: high
status: open
from-meeting: "[[wiki/meetings/2026-08-31-cold-calling-lists]]"
related: ["[[wiki/tasks/2026-08-31-load-no-hm-ceos-to-parallel-dialer]]", "[[wiki/tasks/2026-08-24-justcall-metrics-via-api]]"]
sources: ["[[bibliography/2026-08-31 - Listas Cold Calling - Meeting]]"]
---

# Fix the on-site problem with better title exclusions

Download the **JustCall report** plus the **1,000+ lead Hiring Managers list**, focusing on the leads
Ivan dispositioned **"Hiring Manager not eligible"** (~95% of which were on-site roles). Feed them to
ChatGPT and get back **additional job-title keywords** to add to Clay's title exclusions. Apply the
new exclusions to **both** cold-calling campaigns.

**Why:** **18 of ~40 conversations** last week died because the role was **on-site**. That's the single
biggest source of wasted dials, and it makes Ivan look like he's underperforming when the list is the
problem.

**Titles are the only lever available.** The chain of constraints, worth keeping written down:
- **Clay's source cannot access job-description text at all** — so "exclude on-site roles" cannot be
  filtered on the description.
- **AI cannot read LinkedIn's own remote/on-site tag** — LinkedIn blocks it.
- Therefore job titles carry the signal, and exclusion keywords are the mechanism.

**Held as fallback only:** the "has Near ever placed this role?" AI qualification filter. Explicitly
deferred — *"de última instancia"* — because it risks over-restricting a list Ivan needs volume from.

**Done =** new exclusion keywords live in Clay on **both** campaigns, and the on-site share of Ivan's
"not eligible" dispositions drops.

**Timing:** Started same-day (*"ahora me estoy descargando el reporte"*), no completion date given.
**Needs a date from Gaston** if it didn't finish Aug 31.

> "Me voy a descargar la lista esta de mil y pico de leads, se la voy a pasar a ChatGPT... dame otras
> palabras que yo debo excluir"

**Validation depends on Ivan** hitting 800 dials/day — without that volume there's no way to tell
whether the new exclusions worked or last week was just a bad sample.

**Source:** [[wiki/meetings/2026-08-31-cold-calling-lists]] · [Fathom @28:55](https://fathom.video/calls/805161647?timestamp=1735)
