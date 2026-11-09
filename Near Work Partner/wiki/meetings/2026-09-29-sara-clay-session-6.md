---
type: meeting
title: "Clay Session #6 — Open Jobs workflow end to end (HM vs No-HM, first-occurrence trick, Companies table, comp guides)"
date: 2026-09-29
recording_id: 187816881
fathom-url: https://fathom.video/calls/838488094
attendees: ["Gaston Murillo — trainer", "Sara Sofia Calderon Henriquez — trainee"]
language: Spanish
duration-min: 60
tags: [meeting, clay, training, open-jobs, no-hm, credits, run-conditions, compensation, personalization]
status: processed
related: ["[[wiki/meetings/2026-09-14-sara-clay-session-5]]", "[[wiki/meetings/2026-09-08-clay-session-4]]", "[[wiki/meetings/2026-09-02-clay-session-3]]"]
sources: ["[[bibliography/2026-09-29 - Clay Session 6 - Meeting]]"]
---

# Clay Session #6 — 2026-09-29

## TLDR

A ~60-minute session, almost all of it Gaston walking Sara through the **Open Jobs (OJ) workflow from
end to end**. That was the step left over from session #5. Gaston says this **finishes the platform
walkthrough**. What's left is the **workflow-maintenance videos** he already sent her (she hadn't
watched them yet) plus her questions. **HM vs No-HM.** Each Hiring Manager job row already names a
recruiter, so the person is worked in the jobs table itself. No-HM rows have no contact, so they add an
AI **Lead Title Search** step (titles chosen by company size), then the Clay → AI → Apollo people
waterfall, then a separate Leads table. **The main lesson was saving credits.** The source is capped
on purpose at **10 jobs per company**. A self-lookup "first occurrence" helper picks **one row per
company**, so company-level AI steps run once. Companies go to a deduped **Companies table** where
Enrich Company runs once. A company qualifies at **2–550 employees**, HQ in **US/Canada**, not Defense &
Space Manufacturing, and no "Recruiting" in the industry. Only qualified companies get the **Employee
Headcount by Country** enrichment. The results come back to every job row through a lookup with the
**maximum 600 s delay**. **Pay accuracy.** AI-only LATAM pay estimates had sales quoting roughly
**$2k/month for roles that cost ~$5k**, and leads got angry. The fix is an AI role-match into the
sales team's **LATAM Compensation Guidelines** table, then an AI that narrows the range. **Follow-ups:**
Gaston sends Sara this recording. Sara watches the videos and sends her questions in one message.

> [!note] **Numbering:** "#6" counts ingested sessions. Session #5 pencilled in a Sep 15 review and a
> Wed Sep 16 OJ session. Neither has a transcript, and this call is the OJ walkthrough, so the Sep 16
> session probably slipped to this one. **Links are coarse:** Fathom folded most of the call into two
> long segments (@01:16 and @10:15), so most links point to the start of a segment.

## Key Decisions

**The OJ walkthrough finishes the platform demo. Next comes maintenance, taught through videos.**
> *"con eso creo que ya cubriríamos como lo que es el... La muestra de la plataforma en sí"* (with that I think we'd cover the platform demo itself)
[@01:16](https://fathom.video/calls/838488094?timestamp=76)

**The source is capped on purpose at 10 jobs per company, not 1.**
> *"a mí me interesa contactar a una empresa por más de un rol"* (I want to contact a company about more than one role)
[@10:15](https://fathom.video/calls/838488094?timestamp=615)

**Company-level work runs once per company and gets copied to every job row. Job-level work runs per row.**
> *"Gastar créditos... en una sola de esas 10 y después esos resultados replicarlos"* (spend credits on just one of those 10, then replicate the results)
[@10:15](https://fathom.video/calls/838488094?timestamp=615)

**The HubSpot client lookup stays per job row, not in the Companies table.** It's slow (over 10 min on
thousands of rows) and costs no Clay credits, so efficiency matters less than reading a finished result.
> *"esa eficiencia tanto a mí no me importa porque igual no me consume créditos"* (I don't care much about that efficiency because it doesn't use credits)
[@10:15](https://fathom.video/calls/838488094?timestamp=615)

**LATAM pay ranges must be anchored to sales' Compensation Guidelines, never AI-only.** This came out of
pricing complaints from sales.
[@10:15](https://fathom.video/calls/838488094?timestamp=615)

## Action Items

- **Gaston** — send Sara this session's recording. He said it three times: *"te paso también esta
  recording"* (I'll also send you this recording), *"Te mando este recording"*, and *"ahora cuando puedo
  te mando la recording esta"* (I'll send it as soon as I can). He called it *"súper importante"*
  because it covers the whole workflow.
  [@01:16](https://fathom.video/calls/838488094?timestamp=76) · [@59:34](https://fathom.video/calls/838488094?timestamp=3574) · [@1:00:18](https://fathom.video/calls/838488094?timestamp=3618)
- **Sara** — watch the maintenance videos and send all her questions **in one message** at the end.
  [@00:30](https://fathom.video/calls/838488094?timestamp=30) · [@57:44](https://fathom.video/calls/838488094?timestamp=3464) · [@59:33](https://fathom.video/calls/838488094?timestamp=3573)
- **Gaston** (offer, not taken up): send the **Lead Title Search prompt**. *"si querés te puedo mandar
  el prompt, vos podés meterte acá y ver el prompt también"* (if you want I can send you the prompt; you
  can also look at it here). [@01:16](https://fathom.video/calls/838488094?timestamp=76) (Fathom puts it @05:13)
- **Gaston** (vague): *"en algún momento... capaz"* (at some point… maybe) give Sara a duplicate of the
  OJ workflow so she can rebuild it step by step. [@59:34](https://fathom.video/calls/838488094?timestamp=3574)

## Context — rules Gaston taught (not documented elsewhere)

**Maintenance (what the videos cover).** OJ workflows get checked **every 2–3 days**. Tables have a
row cap, and the OJ source caps how many new records it can bring in. **If either cap is hit, the
workflow stops running and the regular sends stop.** [@01:16](https://fathom.video/calls/838488094?timestamp=76)

**HM vs No-HM** [@01:16](https://fathom.video/calls/838488094?timestamp=76)
- **HM:** every job row has `Recruiter Name` + `Recruiter LinkedIn URL`, so each row is a job and a
  person at once. Name cleanup and work email run right there. The new version still has leads tables for HM.
- **No-HM:** an AI **Lead Title Search** step lists titles worth targeting for the role, based on
  company size. Under ~50 employees it goes after founders / co-founders / VPs. Around 50–250 and larger,
  it goes after the head of the hiring department (e.g. Head of Marketing for a Marketing Analyst) plus
  recruiting/HR, because a CEO at 450 people *"no tiene ni idea"* (has no idea) about the role.
- That response is passed as the **Job Title Keywords variable** into the three people-finding steps,
  run as a waterfall: **Clay → AI (LinkedIn search) → Apollo**. If any of them finds ≥ 1 person, the
  row continues.
- No-HM people go to a **Leads table** because one job can produce several people (e.g. 2 at the same
  company), and a jobs row can't hold more than one.

**OJ jobs-table sequence** [@10:15](https://fathom.video/calls/838488094?timestamp=615)
1. **Previously found recruiting company**, the Exclusion lookup.
2. **Timing check**: is the posting recent?
3. **Lookup into the HM table.** A job already worked in the HM workflow is skipped in No-HM, so it
   doesn't use credits twice. This coordinates the two tables.
4. **First-occurrence helper.** A Lookup Single Row into **the same table** on `Company LinkedIn =
   Company LinkedIn`. The helper outputs true when the looked-up row's company LinkedIn **and** its
   job LinkedIn URL both equal this row's. That happens exactly **once per company**. It is not
   necessarily the top row or the earliest one (in the example it was row 14 of rows 10–20).
5. **Company Type** (the AI staffing classifier) runs **only on the first occurrence**. If it says
   "Other", an AI company-domain search runs, but only on the first occurrence **and** only when the
   domain is empty.
6. **Company LinkedIn merge** is written as a *formula*, not a merge column, so it can drop URLs that
   contain `/life`. Domain + LinkedIn merge into the **Company Identifier**. Staffing hits get written to the Exclusion table.
7. **Send to Companies Table.**

**Companies table** [@10:15](https://fathom.video/calls/838488094?timestamp=615)
- Deduped on **Company Identifier**: one row per company, whatever its job count or posting dates.
- **Enrich Company** (1 credit per company) returns employee count, industry, description, HQ, and
  **Qualified for Outreach**. Qualified means industry ≠ Defense and Space Manufacturing, employee
  count **2–550**, industry doesn't contain "Recruiting", and HQ in **US or Canada**.
- Only if qualified does it run a second enrichment, **Find Employee Headcount by Country**. Formulas
  on top of it: country count (`.length`), **LATAM countries capped at the first 3**, and
  **non-LATAM ("remote") countries capped at 3**. The cap keeps the email natural ("teammates in 7
  countries, like the US, Switzerland or Ireland") and stops it listing every country.

**Back in the jobs table: the lookup delay** [@10:15](https://fathom.video/calls/838488094?timestamp=615)
- A Lookup Single Row into the Companies table on Company Identifier brings company data back to
  **every** job of that company, not only the first occurrence.
- **Run Settings can hold a Delay as well as a Run Condition.** This lookup uses the **maximum 600 s**.
  If the lookup ran right away it would find the company row before its enrichments finished, so
  `qualified` would read **false** even though the company never got evaluated. One record enriches in
  seconds, but a bulk push of ~5,000 companies takes minutes. Timing doesn't matter for automated sends,
  so it uses the maximum.

**Job-level steps (one per row)** [@10:15](https://fathom.video/calls/838488094?timestamp=615)
- HubSpot client lookup (see Key Decisions).
- **Open Role Persona**: a casual version of the job title for the email. Gaston thinks the prompt
  could be better, since "Admin Coord" felt forced.
- Lead Title Search and the three people-finding steps, then a **casual company name** (e.g. "Near"
  rather than "HireWithNear").
- An **AI with web search** fetches the LinkedIn **job description**. It feeds:
  - **Role qualification.** US-only or on-site duties make a role unqualified.
  - **JD Analysis.** Years of experience (N/A if not given) plus a **Specific Experience Snippet**, a
    one-line phrase that drops into the email.
- **Compensation:** `Job Compensation US` comes from the posting, or AI infers it. Then the
  `Estimated LATAM Pay Range`. **What went wrong:** with only the US number, the AI's LATAM estimate was
  often far off. **Laura and Pedro** (sales) reported leads quoted ~$2k/month for roles that actually
  price at ~$5k/month, *"la persona se fue enojada"* (the person left angry). **The fix:** sales gave a
  **LATAM Compensation Guidelines** Excel. It went to CSV and then into a Clay table. An AI gets the full
  list of guideline roles plus the JD/title and returns the closest guideline role (e.g. Travel
  Coordinator → **Event Coordinator**). The lookup then always hits, giving a min–max (e.g. 24k–42k),
  and a final AI narrows it (e.g. 30–40k) for seniority. This is the **~4th–5th version** of the workflow.
- **Leads table:** its only formula is **Lead Source** (Apollo / AI / Clay). Everything else is carried
  over. Then name cleanup → work email → **Email 1** (fully personalized), **Email 2** (one-liner),
  **Email 3** (break-up) → upload to Smartlead.

**How Email 1 is built:** casual role name + *"since [Company] has teammates in N countries, like
X, Y or Z"* (or the LATAM countries) + *"we placed a [similar role] for a company in your industry for
~[LATAM range]"* + *"we have a candidate with [Specific Experience Snippet]"* + a CTA asking for
resumes or a chat. [@10:15](https://fathom.video/calls/838488094?timestamp=615)

**Teaching intent:** *"la idea es que vos también, eventualmente, puedas empezar a tener estas ideas"*
(the idea is that you eventually start having these ideas too). Several designs are valid, and the HubSpot
placement shows the trade-off. Once built, the workflow is left running and only needs a few minutes of
maintenance a week. [@10:15](https://fathom.video/calls/838488094?timestamp=615) · [@57:44](https://fathom.video/calls/838488094?timestamp=3464)

## Open Questions

- **Did the session #5 recording ever reach Sara?** She has "the videos" (the maintenance set). It's
  unclear whether the Sep 14 recording was among them. [@00:23](https://fathom.video/calls/838488094?timestamp=23)
- **What does the `Hiring Country` column do?** Gaston: *"el hiring country, ni idea"* (the hiring
  country, no idea). It may be dead or undocumented.
- **Is the Open Role Persona prompt worth improving?** It was flagged ("Admin Coord") but nobody owns it.
- **When does the next session (Sara's Q&A) happen?** It depends on her watching the videos. No date was set.
- **Are any OJ flows hitting the row or source caps right now?** That's the failure mode Gaston
  described. It may be worth checking against the dead Coworkers US OJ HM flow (unconfirmed link).
