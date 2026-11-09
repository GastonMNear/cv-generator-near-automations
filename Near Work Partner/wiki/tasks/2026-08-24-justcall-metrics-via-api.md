---
type: task
title: "Pull JustCall cold-call metrics via API into the Outbound Metrics sheet"
created: 2026-08-24
updated: 2026-10-19
priority: medium
status: open
from-meeting: "[[wiki/meetings/2026-08-24-priority-alignment-huddle]]"
related: ["[[wiki/tasks/2026-08-21-justcall-api-move-reset-leads]]"]
sources: ["[[bibliography/2026-08-24 - Priority Alignment & Cold Call Huddle - Meeting]]"]
---

# Automate the JustCall metrics pull — **last of Daniel's 5 priorities**

Investigate what the JustCall API can return and feed the cold-calling section of the Outbound
Metrics dashboard from it instead of Ivan typing numbers in daily.

**Why:** Ivan hadn't filled the sheet since ~Jul 14, and that data feeds Daniel's weekly report.
Automating removes the dependency. Daniel wants it modelled on the email funnel: **leads pulled,
leads called, and first / second / third / fourth attempt counts** — he believes the attempt
breakdown is available in JustCall.

**Known constraint — this is why it's manual today.** The API's **dial counts are reliable**, but
connection and conversation metrics were not: JustCall **overstated its connection rate** and the
counts of how many people were actually reached and spoken to. That's what drove the earlier decision
to track by hand. So: automate dials confidently, and validate anything connection-related against
Ivan's own numbers before trusting it.

**Interim:** Ivan fills the daily sheet at the **general level only** — no per-campaign split until
this lands.

**Timing:** Daniel wants it soon ("lo antes posible") but ranked it **last of the five**, behind the
copy and campaign work that generates calls directly.

> "el problema que teníamos con la API de JustCall es que... sobreestimaba su connection rate"

## Update 2026-10-19 — rescoped, now Paz's

**Oct 16 ([@06:14](https://fathom.video/calls/863650212?timestamp=374)):** Andrés asked to automate the cold-calling report so it no longer depends on Ivan's daily manual entry. **Paz owns it now**: a CallTools API import with a per-campaign breakdown (general = sum), probably a Claude routine, *"sin deadline"*. Booked/qualified calls may come from the Command Center import. **Gaston's remaining parts:** give Paz CallTools admin/API access (promised same-day, see the run 12 report), and [[wiki/tasks/2026-10-16-replace-cold-calling-sheet-campaigns]]. Keep the old caveat: validate connection metrics against Ivan's numbers. **Close-or-move candidate:** this is now a waiting-on item for Paz.
*From fathom-task-sync run 12.*
