---
type: task
title: "Run Smartlead spam tests across all ~500 inboxes"
created: 2026-08-13
updated: 2026-08-21
priority: high
status: open
from-meeting: "[[wiki/meetings/2026-08-13-deliverability-root-cause]]"
related: ["[[wiki/tasks/2026-08-13-confirm-spam-tests-consume-capacity]]", "[[wiki/tasks/2026-08-14-monthly-deliverability-protocol-and-playbook]]", "[[wiki/tasks/2026-08-13-train-hector-spam-tests]]"]
sources: ["[[bibliography/2026-08-13 - Deliverability Root Cause - Meeting]]"]
---

# Run spam tests across all ~500 inboxes

Run Smartlead's spam/inbox-placement tests on the retiring inbox group to prove whether emails were
landing in spam. Each test covers only 10 mailboxes on the current Unlimited plan, so **~50 tests**
are needed for ~500 inboxes.

**Why:** This is the measurement that settles whether deliverability explains August. Decided against
upgrading Smartlead to $379/mo (from $174) just to unlock bulk testing — run 50 batches instead.
Tests run on the **retiring** group because resting inboxes should be clean. Progress as of Aug 18:
5 active tests (50 inboxes) completed, **100% primary placement**. Gaston's theory for the earlier
Microsoft spam result: an AI-written email variable rendered blank on a test lead, so a blank email
went out.

**Timing:** "a final de la otra semana, por lo menos una primera medida" — first read-out targeted
end of the following week, full coverage in ~2 weeks. No hard date set.

> "Vamos a hacer ese cambio, Gaston, y vamos a poner a correr los test."

**Source:** [[wiki/meetings/2026-08-13-deliverability-root-cause]] · [Fathom @27:20](https://fathom.video/calls/784480827?timestamp=1640)

## Update 2026-08-21 — hard cap of 5 concurrent tests

**New runtime constraint:** only **five spam placement tests can run simultaneously**. That rules out
testing the pool in one pass — it becomes a rolling batch of five per week. Gaston committed to
running five more this week on a different set of inboxes, continuing after last weekend's five.

Results so far remain clean. This constraint also stretches the original ~2-week full-coverage
estimate considerably — worth re-scoping how much of the ~500-inbox pool is actually worth covering.

> "we can only have, like, five tests running simultaneously... I'm going to run five more tests this
> week with, like, different inboxes"

**Source:** [[wiki/meetings/2026-08-21-weekly-check]] · [Fathom @42:00](https://fathom.video/calls/792826882?timestamp=2520)
