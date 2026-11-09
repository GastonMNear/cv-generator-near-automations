---
type: task
title: "Remove the Smartlead re-contact limitation for leads who reopened a role"
created: 2026-08-24
updated: 2026-09-11
priority: high
status: done
from-meeting: "[[wiki/meetings/2026-08-24-priority-alignment-huddle]]"
related: ["[[wiki/tools/smartlead]]", "[[wiki/tasks/2026-08-13-fix-coworkers-clay-workflow]]"]
sources: ["[[bibliography/2026-08-24 - Priority Alignment & Cold Call Huddle - Meeting]]"]
---

# Unblock re-contacting leads who reopened a role — **Daniel's priority 4**

Remove the Smartlead constraint that prevents contacting a person we have already contacted, so we
can re-engage people from **the last year (roughly 3+ months back)** who have since **reopened a
role**.

**Why:** Daniel wants real force behind this — it unlocks a volume of high-intent leads that already
exist in the database and are currently unreachable. A reopened requisition is a fresh trigger event
on a known contact, which is a better signal than a cold lead. Ranked **4 of 5**.

**Open questions to settle while building it:**
- The 3-month floor vs. the 1-year ceiling — is the window "reopened in the last year, last contacted
  over 3 months ago"? Daniel's phrasing was loose ("desde tres meses atrás en el último año").
- How a reopened role is detected — this likely leans on the same net-new-open-jobs data that lives
  in BigQuery.
- Whether a prior explicit "no" should exclude a lead, the same question raised for the JustCall
  ghosted list in [[wiki/tasks/2026-08-21-justcall-api-move-reset-leads]].

> "acuérdate que tenemos que desbloquear del Smartlead que no podamos contactar a una persona después
> de que ya la hayamos contactado... eso también quiero que le metas mucha fuerza a eso"

## Update 2026-08-31 — the design is settled: `lead_category` → subsequence
Agreed in [[wiki/meetings/2026-08-31-cold-calling-lists]] with Daniel and Ivan. **This is the
implementation path for this task**, not a separate piece of work.

**Mechanism.** Clay finds an existing Smartlead lead in a target segment with a **new job posting**,
writes `subsequence_email_1/2/3` as **AI-generated variables** onto that lead, and updates
**`lead_category`** to a "new job posting" value — and that field update is what **triggers subsequence
enrollment**. All of it happens **inside the same campaign**. Standard sequences are 3 emails, hence
three variables.

**The rejected alternative matters as much as the chosen one.** Creating a **new campaign per
re-contact** was explicitly ruled out: it would duplicate the same lead across campaigns 3, 4, 5 times
and destroy the metrics — *"one lead is one lead, not multiple leads."*

**Bonus the design buys us:** `lead_category` doubles as an **analysis field**, showing **which attempt
finally converted** ("convinced on the 4th try") — per-attempt attribution we don't have today.

**Additional scoping requirement Gaston raised:** check the lead's **Smartlead upload date** so
re-contact only fires if the previous touch was **~2–3 months ago**. The cadence assumption is that
hiring managers reopen roles every 2–3 months, not weekly.

**Rollout order:** **Hiring Managers first** (low volume, safe test), then extend only to the
best-performing No-HM segment (**CEOs/founders at companies under 50**). Broad No-HM rollout was judged
not worth the metric noise.

> "Y updateamos la lead category para que sea new job posting. Y ese lead category lo que hace es
> triguerear que el lead se agregue a la nueva subsecuencia."

**Source:** [[wiki/meetings/2026-08-31-cold-calling-lists]] · [Fathom @07:40](https://fathom.video/calls/805161647?timestamp=460)

## Update 2026-09-01 — held at Work In Progress deliberately, and must be tested
Reported to leadership as **Work In Progress, not done** — a deliberate call in
[[wiki/meetings/2026-09-01-leadership-deck-build]].

**Why it can't be claimed yet:** the earlier API path (grab the lead ID, associate it to another
campaign) is **not a Smartlead feature** — *"no es un feature sino es un invento que estamos haciendo
ahí"*. The **sub-sequence path above is now the preferred route**, and it has **not been implemented
or tested**. It has to be proven not to break before this closes.

**The still-unanswered question, now raised three times:** whether a lead who already replied **"no"**
should be excluded. Open in this task, in
[[wiki/tasks/2026-08-21-justcall-api-move-reset-leads]], and in
[[wiki/tasks/2026-09-01-justcall-ghosting-campaign]]. **Decided in none of them.**

**Also unresolved:** the recency window. ~2–3 months was assumed Aug 31, but Daniel's original phrasing
was *"desde tres meses atrás en el último año"*. It matters for how many leads qualify.

> "no lo hemos implementado y después de eso tenemos que intentarlo a ver si se rompe"

**Source:** [[wiki/meetings/2026-09-01-leadership-deck-build]] · [Fathom @48:17](https://fathom.video/calls/806758340?timestamp=2897)

## Update 2026-09-02 — Daniel set a hard deadline, and it has slipped
Daniel dedicated Tuesday to this as **uninterrupted deep work**: *"no Slack notifications, don't talk
with anyone."* Target was **Tue Sep 1, 3 PM**. Not delivered — he chased it again Tuesday evening
(*"you don't have an excuse for not finishing that tomorrow"*), so the working deadline is now
**Thu Sep 3**. This is the **#1 priority of the week**.

**Gaston's estimate:** 4–6 hours for **both** universes, HM first then No-HM. Daniel confirmed the
replication should be cheap once the HM steps exist.

**Scope expanded — Daniel wants both universes, not just HMs.** The Aug 31 rollout plan was HMs first
as a safe low-volume test. Daniel now explicitly wants No-HM in the same push: he is choosing
**aggressive volume over clean rates** for September — *"I don't care the rates. If at the end of
September we can say that we break records, that would be better for me."* Gaston flagged the real
constraint is **capacity**, not implementation, since Apollo + new CEO campaigns + open-jobs campaigns
are already near the ceiling. **Unresolved.**

**First step Daniel named:** size the universe — how many HMs / No-HMs have **reposted or reopened** a
role. His guess was a 10–30% lift on HM campaign results; nobody knows the real number. Gaston's read:
significant for HMs (an HM on one role likely owns others), less certain for No-HM, but near-certain
for **CEOs at companies under 50** since those get contacted on any new job regardless.

**Strategic framing Daniel added:** this is a return to the **November hypothesis** — broader coverage
across accounts rather than going deep into each one — which performed well then.

**Source:** Huddle 2026-09-01 (Daniel + Gaston), ~[16:55]–[26:30]

## Update 2026-09-04 — HM reactivation reported DONE; recency window decided at 1–2 weeks
Two of this task's long-standing open questions closed this week.

**The recency window is settled: 1–2 weeks, not 2–3 months.** Decided in
[[wiki/meetings/2026-09-02-cold-call-reporting]] with a rationale the vault did not have:
**two weeks is the "maturity time"**, and the second week is *knowingly* near capacity-burn, accepted
as salvage. **This supersedes the ~2–3 month assumption and Daniel's original "desde tres meses atrás
en el último año"** — neither framing appears anywhere in the Sep 2 transcript. Strike them.

> "sería entonces irnos a la última semana al menos, Gasti, a las últimas dos semanas que sabemos que
> es el tiempo de maturity, la segunda es casi que quemar capacity, pero es tratar de rescatar algo"

**Variable naming, as spoken:** `email1_re-engage` / `email2_re-engage` / `email3_re-engage`, set as
lead-level variables replacing the baseline's email1/2/3, fired by a **tag** on the lead. The vault's
`subsequence_email_1/2/3` + `lead_category` is the same structure under different labels — the
transcript never uses the vault's names, so **that mapping is inferred, not confirmed.**

**HM reactivation reported done, No-HM ambiguous.** In [[wiki/meetings/2026-09-04-new-oj-sources-triggers]]
Daniel said *"you already fixed the hiring manager re-attempt and also the no-hiring-manager sheet, so
like the entire engine."* Gaston narrowed it to *"I finished the hiring manager reactivation"* and
flagged No-HM as outstanding — then a terminology mix-up (Daniel meant *CEOs within HM*, not No-HM
reactivation) ended with *"Then yes to everything."* **Genuinely unresolved: confirm whether the No-HM
side shipped before closing this.**

**Still undecided after three raisings:** the prior-"no" exclusion. And the Sep 2 discussion was
sharper than the vault records — it was about **non-responders**, and leads who **explicitly said no
were never discussed at all**. The gap is wider than it looked.

**The scope/capacity disagreement resolved itself, in the opposite direction.** The "I don't care the
rates" volume-maximalist position recorded from Sep 1 **does not appear** in either Sep 4 transcript.
By the end of the Sep 4 1:1 Daniel had reversed to breadth-over-depth and pre-solved the conflict by
proposing to **cut** jobs-per-company and contacts-per-company rather than add capacity. See
[[wiki/tasks/2026-09-04-no-new-sources-convert-existing-universe]].

**Source:** [[wiki/meetings/2026-09-02-cold-call-reporting]] · [Fathom @48:15](https://fathom.video/calls/807325013?timestamp=2895) · and [[wiki/meetings/2026-09-04-new-oj-sources-triggers]] · [Fathom @09:24](https://fathom.video/calls/810291056?timestamp=564)

---

## Completed 2026-09-11

**Done and sending.** The re-contact mechanism ships as part of the always-on reactivation motion. Closes **Daniel's ranked priority 4**. Resolves the ambiguity the vault carried since Sep 4 (HM reported done, No-HM unclear) — the motion is now active across the board.

*Reported done by Gaston, 2026-09-11 status sweep.*
