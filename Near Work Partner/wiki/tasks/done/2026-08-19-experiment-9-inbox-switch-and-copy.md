---
type: task
title: "Check Experiment 9 inbox switch and post its copy for feedback"
created: 2026-08-19
updated: 2026-08-26
priority: high
status: done
from-meeting: "[[wiki/meetings/2026-08-19-weekly-metrics-optimization]]"
related: ["[[wiki/tasks/2026-08-13-run-spam-tests-all-inboxes]]"]
sources: ["[[bibliography/2026-08-19 - Weekly Metrics & Optimization - Meeting]]"]
---

# Experiment 9: verify inbox switch, get copy feedback

Two linked checks on Experiment 9, which has produced **zero replies**:
1. Verify whether the inbox switch is actually configured on this campaign — it was skipped a month
   ago, making spam placement a candidate explanation.
2. Post the final Experiment 9 email to the group channel with the segment context and the note that
   it isn't getting positive replies, so Franco, Hayden, Michael and Andrés can suggest improvements.

**Why:** Zero replies on ~300 leads/arm needs a cause. Deliverability is the cheap thing to rule out
first; if the inbox switch was never applied, that's the answer. If it was, the copy is the suspect —
hence the group review. Weekend tests suggested spam was less severe than feared, which makes copy
the more likely culprit. The baseline arm is being dropped either way, with volume going to
multi-role savings.

> "Tengo que ver si está el inbox switch en esta campaña" · "Pero a mí yo pongo el mensaje"

**Source:** [[wiki/meetings/2026-08-19-weekly-metrics-optimization]] · [Fathom @48:09](https://fathom.video/calls/787480435?timestamp=2889)

## Update 2026-08-21 — inbox switch done, copy rework is the live half

**Item 1 is closed:** the inbox switch is configured. The Apollo campaign (Exp 010) is working too.
Exp 009 is sending, but **no new leads go in until the copy is reworked** — Daniel gated it.

**Item 2 changed shape.** Rather than posting the current copy to the group for suggestions, Gaston
owns a **rewrite** first, then shares the final version with Daniel and Felix for feedback. Felix's
outside perspective was specifically requested.

**New follow-on:** once the copy is settled, **automate the lead adding** instead of Gaston adding a
batch by hand each week. Daniel: "I strongly recommend, strongly suggest to automate the leads
adding" — he ruled out spending Monday time on manual adds for a low-volume campaign. Gaston agreed.

> "before adding new leads, we should rework on the copywriting. That's something pending on my end"

**Source:** [[wiki/meetings/2026-08-21-weekly-check]] · [Fathom @37:02](https://fathom.video/calls/792826882?timestamp=2222) · automation [@38:25](https://fathom.video/calls/792826882?timestamp=2305) · status [@36:14](https://fathom.video/calls/792826882?timestamp=2174)

## Update 2026-08-25 — copy reworked; lead adds are the live half
Gaston reworked the EXP009 (Multijobs CEOs) copy on Aug 24. Two of the three parts are now closed —
inbox switch verified (Aug 21) and the rewrite done.

**Remaining, and it is today's focus:**
1. **Verify the reworked copy actually saved** in Smartlead — confirm the campaign is serving the new
   version, not the old one. Cheap check, and the whole point of the rework is lost if it silently
   didn't apply.
2. **Add new leads** — unblocked now that Daniel's copy gate is cleared.
3. **Automate the lead adding** (Daniel: "strongly recommend") — he ruled out spending Monday time on
   manual weekly adds. Still pending; doing today's adds by hand is fine, but the automation is the
   agreed end state.

Open question: whether the reworked copy was sent to Daniel and Felix for feedback before the leads
go in. The Aug 21 agreement was rewrite → share with both → then leads. Worth confirming that
feedback loop happened rather than skipping it.

## Update 2026-08-25 — ranked priority 2; do not wait on Felix
Daniel ranked this **2 of 5**. One instruction that changes the sequencing: **proceed on Daniel's
feedback, don't block on Felix's.** Send it to Felix as a courtesy look, but the Aug 21 plan of
waiting for Felix before loading leads is superseded.

> "coge un fucking copy, mándalo a Felix y déjelo ahí... nosotros tenemos que avanzar con el feedback
> que yo ya te di"

Both agreed this is one of the highest call-generating items on the list.

## Update 2026-08-26 — done
All three parts complete: inbox switch verified (Aug 21), copy reworked (Aug 24), and the reworked
copy shipped with new leads added (Aug 25–26). Closes **priority 2 of 5**.

**One follow-on was NOT closed with it:** Daniel's "strongly recommend" to **automate the weekly
lead adding** rather than doing it by hand each week. Carried forward as its own task —
[[wiki/tasks/2026-08-26-automate-experiment-lead-adds]].
