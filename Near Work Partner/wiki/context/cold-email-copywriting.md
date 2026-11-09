---
type: context
title: Cold Email Copywriting Standards
created: 2026-07-10
updated: 2026-07-10
tags: [context, outreach, copywriting, cold-email]
status: active
related: ["[[context/outreach-playbook]]", "[[context/staffing-recruiting-cold-email-playbook]]", "[[context/outbound-engine]]", "[[tools/clay]]", "[[tools/smartlead]]"]
---

# Cold Email Copywriting Standards

Use this page whenever drafting, reviewing, or improving outbound email copy for Near campaigns.

Use [[context/staffing-recruiting-cold-email-playbook]] alongside this page for broader staffing/recruiting copywriting principles: relevance over personalization, one campaign/one angle, sequence variation, subject lines, CTAs, proof matching, testing, and credibility rules.

The standard is simple: **sharp, specific, relevant, and easy to reply to.** No fluffy startup copy, no generic AI prose, no over-explaining Near, and no claims we cannot support.

## Core Principle

Every email must answer, in the prospect's mind:

1. Why are you emailing me?
2. Why now?
3. Why is this relevant to my hiring problem?
4. What is the easiest next step?

For Open Jobs campaigns, the strongest reason is usually: **they are hiring for a role Near can help fill right now.**

## Default Email Shape

Use this structure unless a campaign intentionally tests something else:

1. **Signal:** mention the specific hiring trigger.
2. **Relevance:** connect Near to that role, company context, or hiring pattern.
3. **Proof or value:** use a benchmark profile, similar placement, speed, cost, or LatAm/timezone fit.
4. **CTA:** ask one low-friction question.

Keep Email 1 short, usually around 60-90 words. If it needs more than that, the angle is probably doing too much.

## What Makes Copy Good

- It sounds like a person noticed something specific.
- It uses the prospect's actual context: open role, department, company size, geography, LatAm/global hiring footprint, relevant role family, or posted compensation.
- It has one idea, not three.
- It makes the next action easy: "Want me to send the profile?", "Worth a look?", "Should I send a benchmark?", "Is this worth routing to whoever owns the search?"
- It is plain English. No marketing adjectives unless they carry meaning.
- It respects the prospect's likely knowledge. If they already hire in LatAm/global markets, do not explain nearshore hiring like it is new.
- It uses controlled personalization from Clay fields instead of generic AI-generated compliments.

## What Makes Copy Bad

- Generic opener: "I hope you're doing well" when there is a stronger signal available.
- Vague value prop: "We help companies scale efficiently."
- Overwritten AI language: "I noticed your impressive growth trajectory."
- Multiple CTAs in one email.
- Introducing objections the prospect has not raised.
- Claiming a candidate is available when the asset is only a benchmark profile or past placement example.
- Using awkward raw fields: legal company names, full LinkedIn job titles, all-caps role strings, country lists that read like scraped data.
- Copy that could be sent unchanged to 5,000 companies.

## Open Jobs Angles

### Open-role profile

Use when there is a live role Near can credibly fill.

Pattern:
> Saw {{company}} is hiring {{open_role_persona}}. Near helps teams fill roles like this with vetted LatAm talent in aligned US time zones. I have a benchmark {{role_type}} profile with {{relevant_experience}}. Want me to send it?

Rules:
- Mention the role naturally, not as a scraped title.
- Use "benchmark profile" unless there is a verified live candidate.
- Keep the CTA about sending the profile when the profile is the hook.

### Routing CTA

Use when the person may not own the role directly but can route internally.

Pattern:
> Saw {{company}} is hiring {{open_role_persona}}. If this sits with your team, I can send a quick benchmark for the kind of LatAm talent Near can place. If not, who owns the search?

Rules:
- Good for No-HM workflows and senior operators.
- Avoid sounding like a task request. Make routing easy.

### LatAm-aware company

Use when Clay shows the company already has LatAm employees.

Pattern:
> Noticed {{company}} already has team members in {{latam_countries}} and is hiring {{open_role_persona}}. If you are expanding that function, Near can help add vetted LatAm talent without rebuilding the search from scratch.

Rules:
- Do not educate them on LatAm if they already operate there.
- Position Near as faster/cleaner/more targeted.

### Global/offshore but not LatAm

Use when the company hires outside the US but does not show clear LatAm presence.

Pattern:
> Saw {{company}} has team members in {{remote_countries}} and is hiring {{open_role_persona}}. If timezone overlap matters for this role, Near can send LatAm profiles closer to US working hours.

Rules:
- Contrast timezone alignment without insulting their current offshore setup.
- Avoid "cheap labor" framing.

### US-only / category awareness

Use when the company appears to hire only in the US.

Pattern:
> Saw {{company}} is hiring {{open_role_persona}}. For roles like this, Near helps US teams compare vetted LatAm profiles against the US search so they can move faster and reduce comp pressure.

Rules:
- Do not assume they know nearshore hiring.
- Explain the category in one sentence, not a paragraph.

### Cost / savings

Use only when compensation fields and approved claims support it.

Pattern:
> Saw {{company}} is hiring {{open_role_persona}}. Based on the role scope, Near could likely show LatAm profiles at a materially lower comp range while keeping US-timezone overlap. Worth seeing a benchmark?

Rules:
- Use "likely" or "benchmark" when estimating.
- Do not invent exact savings.
- If using large savings claims, ground them in Compensation Guide logic or approved case studies.

## Follow-Up Standards

Email 2 and Email 3 should not become generic after a personalized Email 1. The July 09 Clay walkthrough flagged this as an improvement opportunity.

Good follow-ups:
- Reuse one specific field from the job/company context.
- Ask a smaller question than Email 1.
- Add one new reason to respond.
- Stay short.

Bad follow-ups:
- "Just following up."
- "Bumping this to the top of your inbox."
- Repeating the full value prop.
- Adding unrelated proof or a second offer.

Examples:

Email 2:
> Worth sending the {{role_type}} benchmark, or is {{open_role_persona}} not a priority right now?

Email 3:
> If {{company}} is still hiring for {{open_role_persona}}, I can send a quick LatAm comp/profile benchmark. Useful, or should I close the loop?

## Personalization Fields To Use

Prioritize:
- First name, cleaned.
- Normalized company name.
- Normalized open role / open role persona.
- Job description snippet or years of experience.
- Role family.
- LatAm countries.
- Remote/global countries.
- Employee-count segment.
- Hiring country.
- Posted compensation, only when present.
- Estimated LatAm compensation, only when grounded in Compensation Guides.
- LeadSource/persona, when it affects tone or confidence.

Avoid:
- Long legal company names.
- Raw job titles that sound scraped.
- Unsupported compensation claims.
- Country lists that are too long or awkward.
- Overly specific job-description details that may be wrong or hallucinated.

## Persona Guidance

### Hiring Manager

Lead with the role and useful profile.

Tone: direct, practical, role-specific.

CTA: "Want me to send the profile?" or "Worth seeing a benchmark?"

### CEO / Founder

Lead with business impact: speed, cost, hiring capacity, or multiple open roles.

Tone: concise, outcome-focused.

CTA: "Worth a quick look?" or "Should I send a benchmark to whoever owns recruiting?"

### Talent / People / Recruiter

Lead with search support and quality.

Tone: helpful, not threatening.

CTA: "Want me to send a benchmark profile?" or "Would this help with the search?"

### Department Head

Lead with team need and role fit.

Tone: practical, peer-to-peer.

CTA: "Should I send the profile?" or "Is this role still open?"

## Agent Drafting Process

When asked to write campaign copy:

1. Identify the campaign type: Open Jobs HM, Open Jobs No-HM, retargeting, reactivation, event, AI services, LinkedIn follow-up, or experiment.
2. Identify the primary audience/persona.
3. Identify the available Clay fields and which are safe to use.
4. Choose one angle.
5. Draft Email 1 plus follow-ups.
6. Check variables, claims, tone, and CTA.
7. Provide variants only when the test needs variants. Otherwise provide one best version.

Before drafting, ask for missing information only if it materially changes the copy. If the missing field can be represented as a variable, draft with the variable.

## AI Prompting Rules For Clay Copy Columns

Clay AI copy prompts should be constrained.

Include:
- Campaign goal.
- Persona.
- Available fields.
- Approved examples.
- Hard word limit.
- Tone requirements.
- Claims that are allowed.
- Claims that are not allowed.
- Required output format.

Do not ask AI to "write a great cold email" without constraints.

Prompt shape:
```text
Write a concise cold email to {{persona}} at {{company}}.

Context:
- Company: {{normalized_company_name}}
- Open role: {{open_role_persona}}
- Job context: {{job_description_snippet}}
- LatAm/global signal: {{latam_or_remote_context}}
- Approved claim: Near helps teams hire vetted LatAm talent in US-aligned time zones, often at materially lower comp than US hiring.

Rules:
- 60-90 words.
- Plain English.
- Mention the open role in the first sentence.
- Do not say a candidate is available unless explicitly provided.
- Use "benchmark profile" if referring to a profile.
- One CTA only.
- No hype, no compliments, no "I hope you're well."

Output only the email body.
```

## QA Checklist

Before copy goes live:

- The first sentence references a real signal.
- The email has one angle.
- The CTA is easy to answer.
- All variables render.
- Names and job titles are normalized.
- No fake candidate availability claim.
- No unsupported savings, salary, timeline, or case-study claim.
- Email 2 and Email 3 are not generic if personalization fields are available.
- Smartlead preview is checked for spintax and formatting.
- The copy matches the campaign's actual routing and Smartlead campaign.

## Best Default

When unsure, write less.

The best Near cold email usually reads like:

> Saw the open role. We can help with that specific kind of hire. I have a relevant benchmark/profile/proof point. Want me to send it?

That is the baseline. Add complexity only when the campaign hypothesis needs it.
