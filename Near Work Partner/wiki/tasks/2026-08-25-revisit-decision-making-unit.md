---
type: task
title: "Revisit the Decision Making Unit for No-HM, and test HR as a target"
created: 2026-08-25
updated: 2026-10-13
priority: high
status: open
from-meeting: "[[wiki/meetings/2026-08-25-kpi-deck-prep]]"
related: ["[[wiki/tasks/2026-08-24-review-conversion-improvement-strategy]]", "[[wiki/tools/clay]]"]
sources: ["[[bibliography/2026-08-25 - KPI Deck Prep - Meeting]]"]
---

# Revisit the DMU — are we even writing to the right roles?

Re-examine which roles the No-HM playbook targets, and run a BigQuery analysis of how **HR / Talent**
profiles actually perform.

**Why — Gaston's hypothesis, and it's the alternative explanation to Daniel's.** The No-HM playbook
chases *functional owners*. But in companies over ~50 (and certainly over ~150) the hiring process is
typically owned by **HR**, a profile the team does not systematically target — **only 8.2% of No-HM
leads are HR/Talent** (validated Jan–Aug 13). If that's right, the No-HM problem is partly *who we
write to*, not only *what we write*. Daniel's routing fix and this can both be true.

**What's needed:**
- Confirm whether the "HR is the second-best target" finding was **blended or hiring-manager-only** —
  Daniel wasn't sure and said he'd check.
- Performance of the **50–199 employee band** (10% of No-HM leads) — positive reply rates. Daniel
  owns completing that table.
- Whether writing HR *directly* beats writing the Head of Engineering in larger companies.

**Loose end:** there was a **Decision Making Unit** document defining role targeting and neither
Gaston nor Daniel could remember where it lives. It's referenced as a concept in
[[wiki/context/my-role]] and [[wiki/tools/clay]] but has no page of its own. Worth finding or
rebuilding as a vault page.

> "capaz que no es un tema del copywriting, es un tema también de a quién estamos targeteando"

## Update 2026-09-02 — Daniel gave the exact cut, and it's scheduled for Friday
Daniel converted this from an open hypothesis into a **specific query** and Gaston put it on **Fri
Sep 4**.

**The analysis:** in the Hiring Managers campaign, filter to companies **under 50 employees**, count
how many contacts are **HR people**, and check whether those HR contacts **are booking calls**.

**The inference rule Daniel stated:** if HR at sub-50 companies books calls, then *"the title doesn't
have nothing to do [with it] — the important thing is that they have the money."* i.e. **budget
ownership, not function**, is the qualifier — which would mean the current practice of
**deprioritising HR by company size** is wrong and should be dropped.

Note this inverts the original framing above: that hypothesis was *HR matters more in **large**
companies* (where HR owns hiring). Daniel's test is at the **small** end, where HR shouldn't matter on
a functional theory — so a positive result there is the stronger evidence. **Both cuts are worth
running.**

**Source:** Huddle 2026-09-01 (Daniel + Gaston), ~[03:10]–[04:20]

---

## Update 2026-09-28

**Implementation half done.** The DMU rework on the No-HM Clay workflows was Gaston's #1 build for Sep 22–23 and is **✅ per his Sep 28 status**. Current ~1.7 contacts/opportunity, target ~2–2.3, no cap on Head of Dept / HR / CEO found [@07:30](https://fathom.video/calls/831201936?timestamp=450). **What's left is the analysis question** (do HR contacts at sub-50 companies book?). Close or rescope.

*From fathom-task-sync run 9 (Sep 14–25 meetings) + Gaston's Sep 28 status.*

## Update 2026-10-05

**Rescoped Sep 30. The HR-at-sub-50 analysis is superseded.** Daniel's #1 ask for the week of Oct 5: *"trabajes en la solución para encontrar la persona correcta en los Decision Making [Units] y no solamente encontrar más personas"* (work on finding the RIGHT person, not just more people). Gaston: *"Clarísimo."* [@52:19](https://fathom.video/calls/844117752?timestamp=3139). The approach discussed is **three separate role searches**, which takes ~4 Clay columns to ~12 and **hits the table column limit**. The Clay ticket asking for more columns hadn't been sent; Gaston said he'd send it right after the call ([@22:22](https://fathom.video/calls/844117752?timestamp=1342)). Sep 29: the RB2B DMU is live and scheduled, but sends weren't verified ([@12:54](https://fathom.video/calls/840247722?timestamp=774)). **No done-condition was stated.** See the run report for what "designed" should mean. Segmentation structure goes to a Daniel/Andrés (maybe Franco) workshop before Clay. Related: [[tasks/2026-09-29-run-daniel-rb2b-dmu-prompts-in-clay]].

*From fathom-task-sync run 10 (Sep 28 – Oct 1 meetings).*

## Status 2026-10-05 (Gaston)

**Pending.** Still open. **Daniel, who set the "right person" rescope, has left Near**, so who now signs off on the design is unconfirmed.

## Update 2026-10-13

**Oct 5 (Andrés, [@26:57](https://fathom.video/calls/849739413?timestamp=1617)) set the target structure:** for each open job with no HM, 3 branches (CEO/founder; head(s) of HR; top 1–2 people in the hiring department), each with distinct copy. The CEO gets the baseline. Next step: [[wiki/tasks/2026-10-05-claude-3-branch-no-hm-targeting]].
