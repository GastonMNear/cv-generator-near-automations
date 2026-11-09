---
type: meeting
title: "Cold Call Reporting"
created: 2026-09-02
updated: 2026-09-08
attendees: ["Gaston Murillo — outbound automation", "Daniel Ardila — outbound lead", "Ivan Valenzuela — cold calling"]
meeting-type: internal
duration-min: 76
recording_id: 179412115
fathom-url: "https://fathom.video/calls/807325013"
tags: [type/meeting, meeting-type/internal]
status: mature
sources: ["[[bibliography/2026-09-02 - Cold Call Reporting - Meeting]]"]
---

# Cold Call Reporting

## TLDR
- **The cold-call funnel was redesigned live to mirror the email funnel**, with Positive Conversation
  Rate computed over **Human Pickups, not Dials** — *"quiero sacar el Positive Conversation del Human
  Pickup, no el Total Dialers."*
- **Reporting stays manual, deliberately.** Gaston blocked building the JustCall API automation because
  a dialer change is expected *"la semana que viene o la próxima"* and would force a full rebuild.
- **Unresolved data-integrity problem:** ~1,780–3,269 machine pickups but only 118–301 voicemails
  actually left. Root cause never found; Ivan revealed much of the gap is **silent calls he had been
  mislabelling** as "no contact / left voicemail".
- **The re-engagement subsequence recency window was settled at 1–2 weeks** — *"las últimas dos semanas
  que sabemos que es el tiempo de maturity, la segunda es casi que quemar capacity, pero es tratar de
  rescatar algo."* **This supersedes the vault's earlier ~2–3 month assumption.**
- **No-HM routing settled:** engineering → all to new copy always; Sales/Marketing → all to new copy
  **except CEOs at companies under 50**, who stay on baseline. From a live analysis: 11 calls booked
  from 1,724 contacts (0.64%) — Sales 6, Marketing 3, Engineering 2.

## Key Decisions

### The redesigned funnel
| Cold-call metric | Definition | Email equivalent |
|---|---|---|
| **Dials** | Calls placed. Target 800/day, 4,000/week | Emails sent |
| **Connect Rate** | Reaching a valid/live number | Emails landed |
| **Machine Pickups** | Answering machine or IVR (JustCall's definition) — 75% that week | Ignored us |
| **Human Pickups** | Answered by a real person | **Replies** |
| **Positive Conversations** | The positive subset of Human Pickups | **Positive replies** |
| **Positive Conversation Rate** | Positive Conversations ÷ **Human Pickups** | Positive reply rate |
| **Calls Booked rate** | Booked ÷ Positive Conversations | Booked ÷ positive reply |
| **Bad Data %** | Wrong Number + Personal Line (pre-existing, kept) | — |

- **Positive Conversations = three dispositions:** Contacted–Booked, Worth/Email Follow Up (two
  JustCall dispositions **to be unified into one**), and **On Hold – Budget/Approval Timing** — added
  mid-discussion after Daniel initially missed it.
- **Human Pickups = everything except** AI gatekeeper, silent calls, and No Contact.
- **Silent calls collapse into one category** — no human-vs-machine split. Same for AI gatekeepers.
- **Drop "Qualify"** from Cold Calling Daily Data; it isn't automatic.
- **Only the Daily tab gets restructured** — Weekly and Monthly are untouchable.
- **JustCall dispositions must match the Excel exactly**, or the eventual automated import imports
  errors. **Add new dispositions, never delete old ones** — deleting blanks out historical data.
- **A call booked by email after a dial still counts as Contacted–Booked** on the cold-call side, to
  avoid inflating the rate.
- **Engineering keywords excluded from the original No-HM campaign** so those leads skip a baseline
  that isn't working for them.

## Action Items
- [ ] Write re-engagement copy, set Smartlead variables, load leads, start sends — *Gaston* — due: 2026-09-03
- [ ] Edit No-HM routing to the CEO-under-50 bifurcation — *Gaston* — due: 2026-09-03
- [ ] Send leads to JustCall — *Gaston* — *"mañana en la mañana"* (2026-09-03, softer than the above)
- [ ] Enter Cold Calling Daily Data daily, right after shift end; remove Qualify; backfill — *Ivan*
- [ ] Book a JustCall support call re: voicemail limits and disposition editing — *Ivan*
- [ ] Update JustCall dispositions: add Left Voicemail + No Contact, remove No Connected on 2nd Dial — *Ivan*
- [ ] Reclassify silent calls as "Silent Call" going forward — *Ivan*
- [ ] Review the outbound strategy doc to settle roles-vs-titles segmentation — *Daniel*
- [ ] Decide the dialer — *Daniel* — *"yo tampoco sé ni qué putas hacer con eso"*

## Context
**Re-engagement mechanism:** Clay detects an already-enriched person who posted a new open job → pushes
to Smartlead → sets a **tag** on the lead → the tag triggers a **subsequence inside the existing
campaign**. Three AI-written emails are set as lead-level variables, named in this call as
**`email1_re-engage` / `email2_re-engage` / `email3_re-engage`**, replacing the baseline's email1/2/3.
The tag name was left open ("new", "re-engage", "re-attempt"). The subsequence exports as if it were a
separate campaign, named campaign + suffix.

> [!note] The vault's `subsequence_email_1/2/3` and `lead_category` are the **same three-slot structure
> and tag trigger under different labels** — the transcript never uses the vault's names. Mapping inferred.

**Copy angle (one shared version, not per-role):** do **not** reference prior contact — Daniel found it
*"patético"*. Lead with post recency (*"vi la publicación hace X días de tal rol"*) plus an offer of
high-profile candidates, pulling the **job post date** as a variable. Justified as non-creepy because
LinkedIn shows "meet the hiring team". Subject line to be tested, not finalised — *"saw your role search
on LinkedIn"* floated.

**Decision-making-unit logic (unchanged):** under 50 employees → CEO; ~50–300 → heads of the relevant
area; above → heads of area + HR. Gaston hedged the 300 figure himself.

**Why CEOs-under-50 are protected:** the one segment with demonstrated performance, against untested
copy — *"me concentraría en el segmento que mejor performa y eso no lo cambiaría."* Engineering is
carved out of that protection because the data shows it dragging below benchmark, so there is no
baseline performance there worth protecting. **Already-uploaded leads keep running unchanged** (~5 per
campaign, so the report is unaffected).

## Open Questions
- **Roles vs person-titles is the largest unresolved question.** Gaston built No-HM by *role being
  hired*; both converged in-call on *title of the recipient* being more logical — *"estoy cada vez más
  seguro que deberíamos hacerlo por las personas"* — deferred to Daniel's strategy-doc review.
  **Expect this to reopen the routing rule above.**
- **Prior-"no" exclusion still undecided.** Gaston raised the non-responder problem; it dissolved into a
  copy-tone debate. Sharper than the vault records: this was about **non-responders**, and leads who
  explicitly said no were **never discussed at all**.
- **The voicemail gap is unexplained** — no quantified cause. Partial contributors: silent calls and full
  mailboxes. Daniel's question about differentiating voicemails per attempt went unanswered.
- **~1,000 hiring-manager records lack a title**, possibly never exported from an older base — this
  directly constrains any title-based segmentation.
- **Machine Pickup is not a reliable signal** — sometimes an AI gatekeeper, and some leak through as
  human pickups. Accepted as known imprecision, not fixed.
- **Not all calls get a disposition** — a connected 30-second call with a recorded voicemail had none.
  Undermines any disposition-derived rate.
- **Ivan's backfilled history is self-declared unreliable.** Daniel floated running an AI over it to
  homogenise; never assigned.
- **Two positive replies from the new segment campaigns both asked for CVs instead of routing** — which
  was the campaigns' actual objective. *"Curioso, porque ahora el objetivo era el routing."* **Nobody
  drew a conclusion.** A quiet signal the routing hypothesis may be wrong.

## Full Transcript
See Fathom: https://fathom.video/calls/807325013

> [!warning] Diarization is badly broken — multi-person exchanges collapse into single blocks and
> misattribute throughout. Attribution here is grounded in content. Figures spoken during screen-share
> appear unlabelled; where ambiguous the range is given (machine pickups 1,780/1,879/3,269 across
> different windows; voicemails 118/268/301). One analysis figure at 1:09:30 is garbled beyond recovery.
> **PhoneBurner, Deep Blue, the "4 vs 20 reattempts" comparison and the "only 2 Parallel dialers" detail
> do not appear in this transcript** — the alternative dialer is unnamed, at ~$160/seat. Those vault
> details come from elsewhere.
