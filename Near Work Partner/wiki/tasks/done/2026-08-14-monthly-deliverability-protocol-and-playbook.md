---
type: task
title: "Define the monthly deliverability review protocol and update the email playbook"
created: 2026-08-14
updated: 2026-08-24
priority: high
status: done
from-meeting: "[[wiki/meetings/2026-08-14-weekly-check]]"
related: ["[[wiki/tasks/2026-08-14-pause-weekend-campaign-for-deliverability-tests]]", "[[wiki/tasks/2026-08-14-research-spam-vs-primary-benchmarks]]", "[[wiki/context/outreach-playbook]]"]
sources: ["[[bibliography/2026-08-14 - Weekly Check - Meeting]]"]
---

# Monthly deliverability review protocol + email playbook update

Turn the one-off Smartlead inbox tests into a standing monthly check, and write it into the email
playbook so deliverability failure is caught rather than discovered months later.

**Why:** Daniel flagged the gap: the team needs to *know* deliverability isn't failing rather than
infer it after performance drops. August's may have run undetected for weeks. Plan: rerun the
existing tests one weekend a month, updating dates rather than rebuilding. Done = protocol
documented and folded into the email playbook as a standing function.

**Timing:** "probablemente un fin de semana todos los meses" — a recurring cadence, but no start
date or delivery date was given. Not scheduled.

> "Tenemos que crear un protocolo de revisión de eso... y actualizar el playbook de email."

**Source:** [[wiki/meetings/2026-08-14-weekly-check]] · [Fathom @18:53](https://fathom.video/calls/783947351?timestamp=1133)

## Update 2026-08-13/19
Cadence firmed up in the Aug 13 session: **run the tests periodically (end of month) rather than
continuously**, capped at ~2 test emails per inbox per day, on the retiring inbox group. Execution is
being delegated to Héctor (10–20 tests/day) — see
[[wiki/tasks/2026-08-13-train-hector-spam-tests]].

Still no start or delivery date for writing the protocol into the playbook. The operational pieces
now live in [[wiki/tasks/2026-08-13-run-spam-tests-all-inboxes]] and
[[wiki/tasks/2026-08-13-confirm-spam-tests-consume-capacity]]; this task remains the documentation.

## Update 2026-08-24 — done
Protocol defined and the email playbook updated. Deliverability is now a standing monthly check
rather than something discovered after performance drops — the gap Daniel flagged on Aug 14 is
closed.
