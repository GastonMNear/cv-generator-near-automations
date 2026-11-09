---
type: meeting
title: "Clay Session #5 — Company-qualification sequence for the CEOs 11–50 exercise"
date: 2026-09-14
recording_id: 182919738
fathom-url: https://fathom.video/calls/822740469
attendees: ["Gaston Murillo — trainer", "Sara Sofia Calderon Henriquez — trainee"]
language: Spanish
duration-min: 76
tags: [meeting, clay, training, run-conditions, hubspot, exclusions]
status: processed
related: ["[[wiki/meetings/2026-09-08-clay-session-4]]", "[[wiki/meetings/2026-09-02-clay-session-3]]"]
sources: ["[[bibliography/2026-09-14 - Clay Session 5 - Meeting]]"]
---

# Clay Session #5 — 2026-09-14

## TLDR

This was the call that got Sara **unstuck on the session-4 exercise**. She had enriched her
500-company Apollo table (brief: companies with **11–50 employees**, the usual exclusions, target
**Founders / CEOs / Presidents**) but lost track of the order: *"ya ahí me perdí porque no tiene como el
orden"* ("that's where I got lost, because it has no order"). Gaston kept her table and rebuilt the
**company-qualification half** with her live, in order: two free Exclusion lookups (domain, then
company LinkedIn), a HubSpot "is this a client?" lookup with a contactability helper column (no
HubSpot record, **or** 0 open deals + 0 hires + last modified **more than 2 months ago**), Enrich
Company gated on all of that, then helper columns for employee count 11–50, non-profit type and LinkedIn
industry ≠ staffing/recruiting. After that came a Company Identifier merge column (LinkedIn first,
domain as fallback) and Find Contacts at Company with CEO/Founder/President keywords and assistant
exclusions. Each step was test-run on 10 rows. Most of the time went on **run-condition logic**. The
**leads half** (second table via Send Table Data, DM validation, work email) is Sara's homework,
reviewed **Tue Sep 15 around midday**. Gaston owes her this recording.

> [!warning] **Diarization is badly mixed.** Much of Gaston's teaching (e.g. *"La tabla la armé yo"*,
> "I built the table myself", about the Exclusion list) is attributed to Sara. Ownership below is
> grounded in content, not in the speaker labels.

## Key Decisions

**Order of the company-qualification steps is fixed: free lookups → HubSpot → (AI) → enrichment.**
> *"Lo primero que hago es buscar en las exclusion lookups... porque es gratis y es una forma muy fácil de descartar las staffing companies"* ("the first thing I do is check the exclusion lookups, because it's free and an easy way to rule out staffing companies")
[@05:44](https://fathom.video/calls/822740469?timestamp=344)

**Skip the AI staffing pre-filter on this exercise.** Use it only on high-volume campaigns full of
staffing companies (Open Jobs). This list is 500 static companies and isn't Open Jobs.
> *"en las campañas de open jobs... yo en vez de hacer el enrichment para todas le pongo un filtro inicial"* ("in the Open Jobs campaigns, instead of enriching all of them I put an initial filter first")
[@11:08](https://fathom.video/calls/822740469?timestamp=668)

**Run the free steps on all 500 rows now, with the workflow's auto-run off.**
> *"como hasta ahora todo es gratis... corrámoslo para las 500 empresas"* ("since everything so far is free, let's run it for all 500 companies")
[@34:55](https://fathom.video/calls/822740469?timestamp=2095)

**HubSpot contactability goes in a helper column, not a run condition.** A run condition would be
*"medio choclo"* (a mess). The 2-month threshold is Gaston's usual cutoff.
> *"yo normalmente uso tipo dos meses"* ("I normally use about two months")
[@40:00](https://fathom.video/calls/822740469?timestamp=2400)

**Company Identifier = merge of company LinkedIn (priority) and domain.** Using LinkedIn alone would
skip qualified companies that have no LinkedIn URL.
[@59:50](https://fathom.video/calls/822740469?timestamp=3590)

**Leads half is async homework, reviewed the next day at midday.**
> *"mañana lo revisamos toda esa parte, ¿te parece?"* ("we'll review that whole part tomorrow, OK?") · *"Tipo a mediodía"* ("around midday")
[@1:12:59](https://fathom.video/calls/822740469?timestamp=4379) · [@1:13:48](https://fathom.video/calls/822740469?timestamp=4428)

## Action Items

- **Gaston** — send Sara this session's recording. She asked (*"me envías, por favor, esta grabación"*, "please send me this recording") and he agreed (*"Super. Dale."*, "Great. Sure.").
  [@1:14:02](https://fathom.video/calls/822740469?timestamp=4442)
- **Sara** — run the two Exclusion lookups and the HubSpot lookup on all 500 companies, keeping the enrichment off. [@34:55](https://fathom.video/calls/822740469?timestamp=2095)
- **Sara** — create the Leads table inside the workflow, send contacts to it with Send Table Data,
  then validate decision-makers and find work emails. Work from the recordings. [@1:12:00](https://fathom.video/calls/822740469?timestamp=4320)
- **Gaston + Sara** — review session Tue Sep 15 around midday; an Open Jobs–specific step was pencilled in for *"el miércoles"* (Wed Sep 16).
  [@1:15:00](https://fathom.video/calls/822740469?timestamp=4500)

## Context — rules Gaston taught (not documented elsewhere)

**The standard company-qualification sequence** (the steps and their order are roughly the same in every campaign):
1. **Bare domain** formula from the website.
2. **Exclusion lookup #1**: Lookup Single Row in the Exclusion table on **domain**. *Run condition:* domain exists. Costs no Clay credits and no AI.
3. **Exclusion lookup #2**: same lookup on **company LinkedIn**. *Run condition:* company LinkedIn
   exists **AND** lookup #1 found nothing. It exists for rows with no domain.
4. **HubSpot**: *Lookup Object* (companies) on `domain` **OR** `LinkedIn company page`, with the search
   operator set to OR. *Run condition:* (domain exists **OR** LinkedIn exists) **AND** neither
   Exclusion lookup found a record. Pull out `ID` → "HubSpot Company ID", `number of open deals`,
   `number of hires` and `last modified date`.
5. **HubSpot helper column ("contactable")**: output true if there is **no HubSpot Company ID**, **OR**
   (ID exists **AND** open deals = 0 **AND** hires = 0 **AND** last modified **more than 2 months ago**).
   A recent modification with no deals can still mean an intro call just happened. Test it by
   typing a manual `1` into hires or deals and checking that the output flips to false.
6. **AI staffing classifier** (high-volume / Open Jobs only). If it flags staffing, **Write to Other
   Table** adds the company to the Exclusion table so it's caught for free next time.
7. **Enrich Company**. *Run condition:* both Exclusion lookups "doesn't exist" **AND** HubSpot helper = true.
8. **Helper columns**: employee count **≥ 11 AND ≤ 50**. Use the numeric *count*, not the size bucket,
   because it is more exact. Type ≠ non-profit, since they rarely pay fees. **LinkedIn** industry (from Enrich
   Company, not the Apollo column) does not contain "staffing" or "recruiting". Space manufacturing was
   floated as another excludable industry.
9. **Company Identifier** merge column: company LinkedIn URL first, domain as fallback.
10. **Find Contacts at Company** (the Clay enrichment, *not* a "lookup"). Title keywords: CEO, Chief
    Executive, Founder, Co-Founder / Co-founder / Co founder, President. Exclusions: Executive Assistant, Administrative
    Assistant and the like. Ask an AI for more positive keywords and exclusions. *Run condition:* the
    company helpers (size, industry, for-profit) are true.

**Why double-check staffing:** Gaston built the Exclusion table by hand from competitors he knows, so it is
**incomplete**. The LinkedIn-industry helper is the second check.

**Run-condition craft:**
- Put a run condition on practically every column. Otherwise, for example, an excluded staffing
  company still gets enriched.
- Chaining: condition only on the **previous** step. It carries the earlier conditions, because an
  upstream step that didn't run leaves the downstream fields empty or false. Adding them again is harmless.
- Write compound conditions as separate clauses (*"X doesn't exist AND Y doesn't exist"*). Merging
  both variables into one phrase gave the formula AI the wrong result.
- Use OR, not AND, when either identifier is enough. Sara's first HubSpot condition wrongly required both.
- In formula prompts, say **"output true"** rather than "= true", because "=" can be read as part of the formula.
- `!` negates and `!!` asserts that a value exists. `||` means OR, and parentheses group AND clauses.

**Table hygiene:** to debug rare matches, filter on **"Has results"** ("not missing input" also passes
rows that searched and found nothing), then remove the filter. Duplicate a column from the column
menu *before* opening settings, or you edit the original. Give merge columns a clear name. When two sources
collide, rename them (e.g. "Apollo Industry" vs "LinkedIn Industry"). Test every new step on 10 rows.

**Teaching intent:** Gaston wants Sara to learn the *logic* of run conditions and sequencing, not the
exact steps. Campaigns add or drop steps (e.g. the AI pre-filter; an extra Open Jobs–specific step still to be shown).

## Open Questions

- Did the Sep 15 midday review (leads half) and the Wed Open Jobs session take place? No transcript has been ingested for either.
- Does the Exclusion table get new competitors outside the Open Jobs AI write-back? Right now it is a hand-kept list.
- Should space manufacturing (and other industries) go into the standard exclusions? This was floated, not decided.
