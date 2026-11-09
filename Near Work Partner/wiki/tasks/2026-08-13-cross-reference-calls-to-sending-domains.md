---
type: task
title: "Cross-reference booked calls against sending domains via the Smartlead API"
created: 2026-08-13
updated: 2026-08-19
priority: medium
status: open
from-meeting: "[[wiki/meetings/2026-08-13-deliverability-root-cause]]"
related: ["[[wiki/tasks/2026-08-13-run-spam-tests-all-inboxes]]", "[[wiki/tools/smartlead]]"]
sources: ["[[bibliography/2026-08-13 - Deliverability Root Cause - Meeting]]"]
---

# Which domains actually book calls?

Test Daniel's hypothesis that the newer inbox stack converts worse than the original one. Method
Gaston proposed: take the booked calls → hit the Smartlead API per lead to find the conversation and
which mailbox sent it → aggregate which domains and providers actually produced calls.

**Why:** If the added capacity converts worse than the original inboxes, that's a structural
explanation for calls flatlining while volume doubled — and it changes whether more capacity is worth
buying. Same approach Gaston already used to show blacklisted domains carried no positive-reply
penalty, so the method is proven. Also feeds the open question of whether Google vs Microsoft inbox
deliverability differs enough to justify splitting inboxes by lead provider.

> "Sí, lo puedo hacer con AI. Sería cuestión de... Agarrar las Calls Book y después ir a la API de
> Smart Lead y ver por cada lead hacer nada, buscar la conversación, ver qué mail lo mandó y ahí
> agarrar los inboxes que convirtieron."

**Source:** [[wiki/meetings/2026-08-13-deliverability-root-cause]] · [Fathom @30:58](https://fathom.video/calls/784480827?timestamp=1858)
