---
type: meeting
title: "Clay working session with Alexia: workflow architecture, run conditions, first practice exercise"
created: 2026-10-23
updated: 2026-10-23
attendees: ["Gaston Murillo — Outbound", "Alexia Galeana Castro — helping Gaston (Clay/automation)"]
meeting-type: internal
duration-min: 62
recording_id: 195064248
fathom-url: "https://fathom.video/calls/867098213"
tags: [type/meeting, meeting-type/internal, clay, training]
status: mature
related: ["[[wiki/meetings/2026-10-16-alexia-sync]]", "[[wiki/meetings/2026-10-09-alexia-sync]]", "[[wiki/meetings/2026-10-09-sara-clay-workflow-maintenance]]"]
sources: ["[[bibliography/2026-10-21 - Clay Working Session - Meeting]]"]
---

# Clay working session (Alexia) — 2026-10-21

*(Fathom title: "Clay working session". The live session planned in the Oct 16 sync, held Wed Oct 21 rather than Tue Oct 20. Conducted in Spanish, with some English from Alexia. ~62 min, screen-share walkthrough of live workflows. Gaston's screen froze around @11:41, so the first ~11 minutes were explained without visuals. Diarization drifts: the @16:00 segment labelled Alexia contains Gaston's explanation.)*

## TLDR
- **Architecture walkthrough:** Gaston explained the standard three-table pattern: a **Jobs** table, a **Companies** table and a **Leads** table per workflow. Company-level enrichments run once per company in the Companies table and are pulled back into Jobs with a free lookup [@00:00](https://fathom.video/calls/867098213?timestamp=0), [@13:38](https://fathom.video/calls/867098213?timestamp=818).
- **Rule for where an enrichment goes:** put it in the table it depends on. Lead-level steps (work email) go in Leads, job-level steps (qualify the role) go in Jobs, and company-level steps (headcount, industry) go in Companies [@17:00](https://fathom.video/calls/867098213?timestamp=1020).
- **Run conditions are the hard part.** They both cut unqualified rows (skip people search at ≥500 employees) and route rows. Experiment 6 splits hiring managers 50/50 between baseline and challenger with a random A/B formula [@17:00](https://fathom.video/calls/867098213?timestamp=1020), [@29:09](https://fathom.video/calls/867098213?timestamp=1749), [@47:45](https://fathom.video/calls/867098213?timestamp=2865).
- **Next step = a practice exercise, not production access.** Gaston will send Alexia a ~100-record **webinar-attendee list** (the same exercise Sara got) with instructions. She asked for a hard deadline. They then review it together [@38:04](https://fathom.video/calls/867098213?timestamp=2284), [@1:00:53](https://fathom.video/calls/867098213?timestamp=3653), [@1:01:22](https://fathom.video/calls/867098213?timestamp=3682).
- **Sara's exit date:** Alexia says Sara's contract is temporary and runs **to Nov 12**. Charlie has already spoken with her, and she may leave earlier, but she is held until her contract-sending process is automated [@58:27](https://fathom.video/calls/867098213?timestamp=3507). Alexia later added *"Sara va a quedarse todavía unas dos semanas"* ("Sara will stay about two more weeks") [@1:00:42](https://fathom.video/calls/867098213?timestamp=3642).
- **Viktor cost pushback:** Alexia said leadership is *"medio hartos"* ("kind of fed up") with how much Viktor is used, because it bills by API and is getting expensive [@57:00](https://fathom.video/calls/867098213?timestamp=3420). Gaston restated that **Clay maintenance is the first automation target** because its rules are clear. Building whole workflows with AI is "further off" [@55:38](https://fathom.video/calls/867098213?timestamp=3338).

## Clay rules taught in this session
These rules aren't in the playbook docs yet. They are worth folding into the Clay learning guide.

**Table structure**
- **Three tables per workflow: Jobs → Companies → Leads.** Jobs are qualified in Jobs, companies are enriched and qualified in Companies, and the people found go to Leads [@13:38](https://fathom.video/calls/867098213?timestamp=818).
- **Company table mechanics:** check whether this is the company's *first occurrence* in the Jobs table. If it is, send it with **Send Table Data**, carrying only 4 fields: company name, domain, LinkedIn URL and **identifier**. The identifier merges domain and LinkedIn URL, so it is filled even when one of them is empty. The Companies table **auto-dedupes on the identifier**. Results come back to every job row through **Lookup Single Row in Other Table** [@00:00](https://fathom.video/calls/867098213?timestamp=0), [@13:02](https://fathom.video/calls/867098213?timestamp=782).
- **After a cleanup, "first occurrence" only means first in the current table.** A company whose rows were deleted can be sent again. That is harmless: auto-dedupe deletes the duplicate before any enrichment runs, so no credits are spent [@13:38](https://fathom.video/calls/867098213?timestamp=818).
- **Send Table Data → "one row for each item in a list"** turns a Find People result (e.g. 5 people) into 5 Leads rows. Each person needs their own row for name cleaning, email lookup and copy. New rows are **appended at the bottom**, never overwrite [@07:03](https://fathom.video/calls/867098213?timestamp=423), [@08:00](https://fathom.video/calls/867098213?timestamp=480).
- **Cross-workflow tables are the exception.** Keep everything inside the workflow's own tables. Only shared data such as the staffing **Exclusion Lookup** lives in a separate folder, and every workflow queries it [@22:09](https://fathom.video/calls/867098213?timestamp=1329).
- **The company-table pattern isn't a Clay template.** Gaston added it later to save credits. There is often more than one valid build, for example separate baseline/challenger tables vs one table with a conditional prompt variable [@50:12](https://fathom.video/calls/867098213?timestamp=3012).

**Cost model**
- **Lookups are free. Enrichments cost Clay credits. AI steps cost API money**, not Clay credits. Don't bother optimizing free steps. Optimize the paid ones [@17:00](https://fathom.video/calls/867098213?timestamp=1020).

**Run conditions**
- **Run conditions** are formulas in a column's run settings. Use them to (a) stop spending on unqualified rows, e.g. don't search people at companies with more than 500 employees (or ≥550 for a buffer), and (b) route rows to different tables [@17:00](https://fathom.video/calls/867098213?timestamp=1020), [@29:09](https://fathom.video/calls/867098213?timestamp=1749).
- **The AI helper box writes the formula, but reference columns with `/`.** Type `/` and pick `Work Email` so the formula uses the column variable, not the literal text. Then use the per-row preview to check it runs only where it should [@43:16](https://fathom.video/calls/867098213?timestamp=2596).
- **Dependencies chain transitively.** Work Email only runs if `Full Name Clean` exists. A step conditioned on Work Email therefore implicitly requires the clean name too. Copy should never be written before the name is cleaned, or emails go out as "Hi Gasti, MD" [@44:20](https://fathom.video/calls/867098213?timestamp=2660), [@46:26](https://fathom.video/calls/867098213?timestamp=2786).

**Specific steps**
- **Work email is a waterfall:** several providers are tried in sequence until one finds the email. If none does, the cell stays empty and downstream steps show "run condition not met" [@44:20](https://fathom.video/calls/867098213?timestamp=2660).
- **Smartlead check in Leads:** look the lead up in Smartlead by work email (run condition: work email exists). Already-contacted leads skip copywriting [@38:04](https://fathom.video/calls/867098213?timestamp=2284).
- **Staffing exclusion loop:** first look the company up in the **Exclusion Lookup** table (free). If it isn't there, an AI **Company Type** step classifies it. When the answer is `Recruiting`, a **Write to Exclusion Lookup** step adds it, so the AI never runs twice on the same company [@21:02](https://fathom.video/calls/867098213?timestamp=1262), [@22:09](https://fathom.video/calls/867098213?timestamp=1329).
- **People search:** three search paths today (Clay, AI, Apollo). Apollo often finds CEOs that Clay misses. A fourth provider is being added; the transcript has it as "Mold Sets" and the name is unverified [@00:00](https://fathom.video/calls/867098213?timestamp=0).
- **Name cleaning:** an AI step strips credentials and suffixes, e.g. "Lincoln Anderson Jr." → "Lincoln Anderson". It sometimes mis-picks the surname ("Barry Gordon ICD, CEA…" came out as "Barry Zert") [@08:00](https://fathom.video/calls/867098213?timestamp=480), [@29:09](https://fathom.video/calls/867098213?timestamp=1749).

**Workflow map**
- **Hiring-manager (HM) workflows** have a recruiter per job row, so the Jobs table doubles as the lead list and name cleaning and email run there. Experiment 6 also finds the **CEO** for every job and sends them to a *No Hiring Manager CEO Leads* table in parallel, because CEOs at the right size are the best-converting segment by far [@29:09](https://fathom.video/calls/867098213?timestamp=1749).
- **Experiment 6 A/B routing:** a `random AB output` formula gives `baseline` or `need confirmation` 50/50. Run conditions then send each lead to its own Leads table (Leads Baseline vs Challenger 2 "Need Confirmation"). Each table has its own copy prompts and its own Smartlead campaign. The "Guess Opener" challenger was dropped for underperforming [@29:09](https://fathom.video/calls/867098213?timestamp=1749).
- **Folder map:** *Open Jobs Campaigns* holds 80–90% of sends. It is split by region (US, LATAM, Canada, Asia) plus **Apollo Open Jobs**, which is US jobs sourced from Apollo instead of LinkedIn. Each region has separate **HM** and **No-HM** workflows. The live HM workflow is *Experiment 6 US Open Jobs Hiring Managers* [@27:00](https://fathom.video/calls/867098213?timestamp=1620).
- **Hirebase:** Gaston is building a Hirebase-fed Open Jobs workflow. It catches jobs posted on company sites rather than LinkedIn. The Find Jobs source imported ~1,400 jobs that day [@00:00](https://fathom.video/calls/867098213?timestamp=0), [@22:09](https://fathom.video/calls/867098213?timestamp=1329).

## Key Decisions
- **Alexia ramps through exercises before touching production.** She asked for this: *"me gusta estar segura antes de moverla"* ("I like to be sure before I touch it"). The sequence is a simple exercise, a joint review, then a more complex one (sending leads to another table, company lookups) [@53:08](https://fathom.video/calls/867098213?timestamp=3188), [@53:20](https://fathom.video/calls/867098213?timestamp=3200).
- **The first exercise is the webinar list, not an Open Jobs build.** Its steps are find the people, clean names with AI, find emails and prompt AI to write the email. The Smartlead upload is optional [@38:04](https://fathom.video/calls/867098213?timestamp=2284).
- **Automation priority stays Clay maintenance first.** AI-built workflows come later, because builds depend on context that keeps changing [@55:38](https://fathom.video/calls/867098213?timestamp=3338).

## Action Items
**Gaston**
- [ ] Send Alexia the ~100-record webinar-list Clay exercise with instructions and a deadline. Done when she has the list, the steps (find → clean name with AI → find email → AI-written email) and a due date. *"te paso entonces ese ejercicio y te mando... instrucciones de cómo encararlo"* ("I'll send you that exercise and some instructions on how to approach it") [@1:00:53](https://fathom.video/calls/867098213?timestamp=3653). She asked for the deadline at [@1:01:22](https://fathom.video/calls/867098213?timestamp=3682).
- [ ] Afterwards, review the exercise with her, either live or after she has tried it [@1:00:53](https://fathom.video/calls/867098213?timestamp=3653).

**Alexia**
- [ ] Attempt the exercise by the deadline Gaston sets. She is out Friday Oct 23 [@1:00:42](https://fathom.video/calls/867098213?timestamp=3642).

## Context
- Fathom's action item (exercise plus instructions plus deadline, then schedule a review @38:20) matches the transcript.
- Gaston assumed Alexia had already read "the document" on company tables (*"No sé si eso lo leíste en el documento, entiendo que sí"*, "I don't know if you read that in the document, I assume so") [@00:00](https://fathom.video/calls/867098213?timestamp=0). It is unclear whether this means the consolidated training doc promised on Oct 16. The Viktor Looms weren't mentioned.
- Alexia's other work: she automated ~60–70% of her own job with Viktor. A Bullhorn outage since Monday Oct 19 undid much of that, and Sara is helping her with manual loading. Alexia says the top Viktor spender is "GAN" (name as transcribed).
- Alexia called herself both *"supuestamente soy ingeniera"* ("supposedly I'm an engineer") and *"yo estudié administración de empresas"* ("I studied business administration"). The second line sounds like a joke, so `team.md`'s "engineering degree" stands.

## Open Questions
- Was the consolidated training doc ever sent to Alexia? Gaston talked as if she had read it.
- Given the Viktor cost pushback, is Viktor still the right agent for Clay maintenance, or should it be Claude? Alexia leaned Claude: *"Preferably está con Claude"* ("preferably with Claude").
- Sara has ~2 weeks or until Nov 12. Who owns daily Clay maintenance after that if neither Viktor nor Alexia is ready?

## Full Transcript
See Fathom: https://fathom.video/calls/867098213
