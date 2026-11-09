---
type: task
title: "Confirm whether spam-test emails consume sending capacity"
created: 2026-08-13
updated: 2026-08-24
priority: high
status: done
from-meeting: "[[wiki/meetings/2026-08-13-deliverability-root-cause]]"
related: ["[[wiki/tasks/2026-08-13-run-spam-tests-all-inboxes]]"]
sources: ["[[bibliography/2026-08-13 - Deliverability Root Cause - Meeting]]"]
---

# Do spam tests eat sending capacity?

Before scaling the spam tests: confirm whether test emails count against the inboxes' daily sending
capacity (15 sends/inbox configured, real capacity 15–20), whether per-day test volume can be capped
at ~2 per inbox, and whether Smartlead limits simultaneously active tests.

**Why:** Gating question — one test email every 17 minutes would burn a large share of capacity that
should be going to leads. Daniel wants a hard cap of ~2 test emails per inbox per day. Gaston flagged
this himself as the thing to settle "antes de avanzar con esto". Done = answer known and cap applied.

> "lo otro que tengo que averiguar antes de avanzar con esto es si los mails que se mandan como test
> cuentan dentro de nuestra capacidad de envío"

**Source:** [[wiki/meetings/2026-08-13-deliverability-root-cause]] · [Fathom @20:28](https://fathom.video/calls/784480827?timestamp=1228)

## Update 2026-08-24 — done
Gaston confirmed the gating question is settled and the cap applied. Spam tests run **5 concurrent
max**, which keeps them clear of the lead-sending capacity. Unblocks
[[wiki/tasks/2026-08-13-run-spam-tests-all-inboxes]].
