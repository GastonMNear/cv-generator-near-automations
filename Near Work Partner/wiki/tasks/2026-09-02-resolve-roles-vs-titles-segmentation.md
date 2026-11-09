---
type: task
title: "Settle whether No-HM segments by role hired or by recipient title"
created: 2026-09-02
updated: 2026-10-05
priority: medium
status: open
from-meeting: "[[wiki/meetings/2026-09-02-cold-call-reporting]]"
related: ["[[wiki/tasks/2026-09-02-edit-no-hm-routing-ceo-under-50]]", "[[wiki/tasks/2026-08-25-revisit-decision-making-unit]]"]
---

# Roles vs person-titles — the segmentation question under everything else

Should No-HM campaigns be segmented by the **role being hired** or by the **title of the person
receiving the email**? Gaston built it by role; both converged in-call on titles being more logical.

**Why it matters:** it determines the routing rule in
[[wiki/tasks/2026-09-02-edit-no-hm-routing-ceo-under-50]], and **settling it on titles would reopen
that rule**. It also connects to the decision-making-unit work in
[[wiki/tasks/2026-08-25-revisit-decision-making-unit]] — the recurring finding is that the CEO at a
small company is the economic buyer regardless of which role is open.

> Daniel: "la lógica para mí es que sea por titles, o sea, por titles de la persona que recibe el mail"
> — and later, "estoy cada vez más seguro que deberíamos hacerlo por las personas"

**Blocked on Daniel** reviewing the outbound strategy doc to see how No-HM was originally designed. He
said he'd do it three separate times in the call. He also asked whether to kill the running campaign in
the meantime and answered his own question: **no, let it run.**

**A hard constraint on any title-based approach:** roughly **1,000 hiring-manager records have no
title**, possibly never exported from an older base. Title-based segmentation can't cover them until
that's fixed.

**Timing:** No date. Deferred pending Daniel's doc review.

**Source:** [[wiki/meetings/2026-09-02-cold-call-reporting]] · [Fathom @1:05:31](https://fathom.video/calls/807325013?timestamp=3931)

## Update 2026-10-05

**Back in scope (Sep 29).** The proposed non-HM experiment routes by the **lead's title** (HR to one table, founder to another) instead of by the job posting, so the workflows need rebuilding. Daniel writes the copy, and Gaston works out the operations. No launch decision yet (*"depende de si queremos lanzar"*) ([@29:00](https://fathom.video/calls/840247722?timestamp=1740)).

*From fathom-task-sync run 10 (Sep 28 – Oct 1 meetings).*

## Rescoped 2026-10-05 (Gaston, J4 from run 10)

**The question is settled: route by the lead's title.** What's left is building it. **New done =** an
operational design for the non-HM experiment's routing (HR leads → one Clay table, founders → another) that
covers which workflows need rebuilding, ready to launch.

Gaston confirmed it's pending and his. Daniel was writing the copy for this experiment and **has left Near**, so who writes the copy is now open.

> Daniel: *"tendríamos que hacer un ruteo en función al título de los leads… vas pensando cómo operativamente funciona"*

[Fathom @29:00](https://fathom.video/calls/840247722?timestamp=1740) · [@32:35](https://fathom.video/calls/840247722?timestamp=1955)
