---
type: meeting
title: "EXP013 building session with Paz: HR-leaders Clay workflow and the Clay rules behind it"
created: 2026-10-09
updated: 2026-10-09
attendees: ["Gaston Murillo — Outbound", "María Paz Marengo — Marketing Ops"]
meeting-type: internal
duration-min: 74
recording_id: 191478944
fathom-url: "https://fathom.video/calls/854853941"
tags: [type/meeting, meeting-type/internal]
status: mature
related: ["[[wiki/meetings/2026-10-06-lila-post-huddle-campaign-center]]", "[[wiki/tasks/2026-10-06-create-exp-13-hr-heads]]"]
sources: ["[[bibliography/2026-10-09 - EXP013 Building Session - Meeting]]"]
---

# EXP013 building session with Paz — 2026-10-09

*(Clay training disguised as a build. Gaston built Exp 13 live and narrated each choice so Paz could learn it. Fathom sometimes writes "Paz" as "Fath".)*

## TLDR
- **Exp 13 = US Open Jobs, No-HM, HR / recruiting leaders.** It got a new Clay workbook. The Exp 12 leads table was duplicated (columns only) and the old CEO/Founder baseline columns were deleted. A Smartlead campaign was duplicated from Exp 12 (*All Openings / Recruiting Leaders*, variables email1–3).
- **Routing:** an AI classifier (GPT-4.1 mini) labels each Exp 12 lead `HR` or `Other`, and defaults to `Other` when in doubt. `HR` rows go to Exp 13 through *Send Table Data → Send row*. `Other` rows keep the Exp 12 work-email chain.
- **The challenger email needs a US salary.** It comes from LinkedIn *Job Compensation* (often `unknown`). The fallback is the LATAM pay range + 40%. LATAM pay is text, so the +40% needs a 2nd AI step and then a merge into a *final estimated US pay range*.
- **The build was not finished in the call.** Gaston has since reported Exp 13 **launched**.
- Follow-up with Paz set for **Tue Oct 13**.

## Clay rules Gaston explained (not documented elsewhere)
- **Autorun off first.** Turn it off on any table you are building, and on any live parent table you touch (Exp 12), so a stray run doesn't fire every downstream step or spend credits [@04:56](https://fathom.video/calls/854853941?timestamp=296).
- **Point the Smartlead push at the new campaign before anything else.** A duplicated table still pushes to the old campaign. He once uploaded leads to the wrong one and had to delete them all from Smartlead [@05:00](https://fathom.video/calls/854853941?timestamp=300).
- **Run-condition syntax.** `!` = does not exist, `!!` = exists. The AI "generate" button can write harder formulas.
- **The US-comp AI step** runs only if `work email` exists AND `!lookup lead in campaign ID`. In other words, only spend on leads that can be contacted and aren't already in Smartlead.
- **Gate once, upstream.** Putting `HR classification == Other` on *Work Email* blocks HR rows from every later step (lookup, Email 1–3, Add lead to campaign), because each of those already requires work email or the emails to exist.
- **Sequencing.** Require `Full Name Cleaned` to exist, so parallel AI steps can't run ahead of the name cleaner.
- **Date gate:** `createdAt >= today` stops AI steps from re-running (and re-spending) on old rows that were already sent.
- **Test on 10 rows** before running a whole column, including Send Table Data.
- **"Required to run" toggle** on prompt inputs: he normally leaves it off. Prompts handle blank/unknown, and hard requirements go in the run conditions [@20:37](https://fathom.video/calls/854853941?timestamp=1237).
- **Send row vs Send row for each item in a list.** Use the per-item mode when one cell holds a list of people (Find People). Use plain *Send row* when the rows are already one lead each. Don't send `createdAt` or email-copy columns.
- **`.parent` paths.** Per-item sends nest the source fields under `.parent`. With plain *Send row* the fields sit at the top level, so delete `.parent` from each mapped column (one-time fix). This only works if the column names match exactly. Otherwise, re-pick the variable with `/`.
- **The LinkedIn URL formula** ORs `url || linkedin_url || linkedin_URL`, because Clay, Apollo and AI lead searches name the field differently.
- **Drop redundant steps downstream:** the name-cleaner AI and the CEO/Founder flag (names arrive already clean).
- **When testing with leads already sent, remove run conditions temporarily, then put them back** (lookup-in-campaign on US comp and on Email 1), and don't upload the test rows.
- **Models:** cheap GPT minis for classification and utility steps, **Sonnet 4.6 for copywriting**. Workflows break when a model is retired, so they need a manual swap.

## Key Decisions
- HR is detected by AI, not by title keywords (too many variants).
- The enrichments (work email, lookup) run in the Exp 13 table itself.
- Only Email 1 is tested. Emails 2 and 3 reuse the existing copy.
- Add an AI "casual title" step, so the email doesn't paste the prospect's literal title.

## Action Items
**Gaston**
- [ ] Send Paz a doc with the trainings condensed into one written guide [@01:16](https://fathom.video/calls/854853941?timestamp=76)
- [x] Finish Exp 13: US-comp fallback and merge, casual-title step, clean up the challenger prompt (drop the invented *savings %*), restore the removed run conditions, autorun on → [[tasks/2026-10-06-create-exp-13-hr-heads]] *(launched per Gaston, Oct 13)*
- [ ] Follow-up session with Paz on Tue Oct 13 [@1:09:35](https://fathom.video/calls/854853941?timestamp=4175)

**Paz**
- [ ] Watch the training videos (not yet seen) [@01:06](https://fathom.video/calls/854853941?timestamp=66)

## Open Questions
- Paz asked when duplicating a Smartlead campaign needs more than a rename. Gaston's answer: only when the step count differs from the source (e.g. adding email4/5). He'll do Smartlead duplication himself for now.

## Full Transcript
See Fathom: https://fathom.video/calls/854853941
