---
type: task
title: "Unblock BigQuery billing via Andrés and Paz"
created: 2026-08-19
updated: 2026-08-24
priority: high
status: done
from-meeting: "[[wiki/meetings/2026-08-19-weekly-metrics-optimization]]"
related: ["[[wiki/tasks/2026-08-19-bigquery-persona-analysis]]", "[[wiki/tasks/2026-08-18-email-scorecard-missing-metrics]]"]
sources: ["[[bibliography/2026-08-19 - Weekly Metrics & Optimization - Meeting]]", "[[bibliography/2026-08-18 - KPI Deck Prep - Meeting]]"]
---

# Unblock BigQuery billing

Message Andrés directly to push Paz on updating the BigQuery payment information. Gaston has no
access to do it himself.

**Why:** BigQuery being down blocks real work — the net-new-open-jobs metric was still missing from
the email scorecard going into the Aug 18 leadership meeting because of it, and the persona-level
analysis can't run either. Paz has not answered Daniel's Slack follow-ups, so escalating via Andrés
is the workaround. If Andrés doesn't respond, escalate in the marketing update. Done = BigQuery
queries running again.

**Timing:** "ahora le escribo" — Gaston said he'd write immediately on Aug 19.

> "O pues le escribo andrés por interno, le digo, Marica, necesito que me ayudes a pujar a Paz.
> Eh, dale, bueno, ahora le escribo."

**Source:** [[wiki/meetings/2026-08-19-weekly-metrics-optimization]] · [Fathom @56:43](https://fathom.video/calls/787480435?timestamp=3403)

## Update 2026-08-21 — queries running again, but did this actually close?

BigQuery is working again as of the Aug 21 weekly check, and the persona analysis is unblocked.

**Left open deliberately.** Gaston attributed the fix to the **deleted tables** issue, not to the
payment information being updated — so it is not established that Paz/Andrés ever resolved the
billing. If the payment info is still stale, this will resurface. **Confirm the billing state before
marking this done.**

**Source:** [[wiki/meetings/2026-08-21-weekly-check]] · [Fathom @42:00](https://fathom.video/calls/792826882?timestamp=2520)

## Update 2026-08-24 — done
BigQuery is working and the persona queries ran, so the escalation has served its purpose. Gaston
attributed the recovery to the deleted tables rather than to a billing fix; closing on the outcome
rather than the mechanism. If queries fail again on billing, reopen.
