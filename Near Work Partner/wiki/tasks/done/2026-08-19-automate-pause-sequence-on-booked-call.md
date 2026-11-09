---
type: task
title: "Automate pausing email sequences when a cold call is booked"
created: 2026-08-19
updated: 2026-08-24
priority: high
status: done
from-meeting: "[[wiki/meetings/2026-08-19-weekly-metrics-optimization]]"
related: ["[[wiki/tools/smartlead]]"]
sources: ["[[bibliography/2026-08-19 - Weekly Metrics & Optimization - Meeting]]"]
---

# Auto-pause email sequences for booked cold-call leads

Build an automation that reads booked-call messages posted in the **Outbound Chosen** channel,
checks whether the lead has an email, and pauses any running Smartlead sequence for them.

**Why:** Once a call is booked it makes no sense to keep cold-emailing the lead. Ivan and Hector
post booked calls in the channel; currently pausing would be manual. Gaston framed it as either
checking each lead himself or automating the read — automating is the point. Done = booked calls
posted in the channel stop the matching sequence without manual work.

> "Porque Gasti va a revisar si ese man o va a activar alguna automatización para que lea ese
> mensaje y vaya y revise si hace parte de los que tienen email o no tienen email. Y si tienen
> email, pare la email sequence que esté corriendo en ese momento."

**Source:** [[wiki/meetings/2026-08-19-weekly-metrics-optimization]] · [Fathom @30:00](https://fathom.video/calls/787480435?timestamp=1800)


## Built 2026-08-20 — `booked-call-pause` skill

Automated end-to-end: HubSpot booking → one Smartlead crawl → match company → pause every
matched lead in every ACTIVE campaign → Slack report. Skill at
`.claude/skills/booked-call-pause/` (committed to main).

**Trigger changed from the original plan.** The meeting framed this as reading booked-call
messages out of the Outbound Chosen Slack channel. Built off **HubSpot meetings** instead —
bookings already land there via Chili Piper as structured objects with the company and email,
so there's no message parsing and nothing depends on someone remembering to post. Slack is
now the *output* channel, not the input.

**Why it matters more than expected:** verified on 22 real bookings — 15 leads matched at
7 companies, and **11 of the 15 were colleagues rather than the person who booked.** At Patch
Media (4 leads) and Scalix AI (3 leads) the booker wasn't in a campaign at all; only their
colleagues were. Pausing just the booked lead would have missed all of it.

**Live routines** (both `--live`, weekdays, created **disabled**):
- morning 09:03 ET — `trig_013MdhuD9nA5PrF7hJP5T11q`
- afternoon 13:27 ET — `trig_01UXrVZNP9GcChnc8sPM8kVh`

**BLOCKED on one thing:** `HUBSPOT_ACCESS_TOKEN` must be added to routine environment
`env_01DVzad9AipkSb49SRKPteVL`, then both routines enabled at
https://claude.ai/code/routines. Everything else is verified working.

## Update 2026-08-21 — confirmed live, one edge case to review

Gaston reported it working in the weekly check: runs twice a day, checks for new booked calls, finds
everyone from that company in the Smartlead campaigns and pauses them — **regardless of which
channel booked the call** (LinkedIn, cold calling, Google search), since it reads HubSpot rather
than a single channel's messages.

**Open edge case, assigned to Gaston.** Daniel questioned the blast radius of pausing at *company*
level: a company may have several hiring managers hiring for different open roles, and pausing all of
them would kill live outreach on unrelated positions. He concluded it is probably rare and not a
blocker, but asked Gaston to look at it.

Note this cuts against the finding that justified company-level scope in the first place — 11 of 15
matched leads were colleagues rather than the booker. The review should decide whether to scope by
company *and* open role rather than company alone.

> "maybe that's not going to be a big deal. But however, take a look at this, please." — "okay, I will."

**Source:** [[wiki/meetings/2026-08-21-weekly-check]] · [Fathom @35:37](https://fathom.video/calls/792826882?timestamp=2137) · live [@31:57](https://fathom.video/calls/792826882?timestamp=1917)

## Update 2026-08-24 — done
Closed by Gaston. The automation is live and running twice daily, and the company-level blast-radius
edge case Daniel raised on Aug 21 was reviewed and accepted — company-level scope stays. The
finding that 11 of 15 matched leads were colleagues rather than the booker is what justifies it.

Skill: `.claude/skills/booked-call-pause/`.
