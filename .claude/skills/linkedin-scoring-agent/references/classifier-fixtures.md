# Classifier regression fixtures

Five cases with verdicts Gaston reviewed and accepted on live rows (spec §9). Run them through the
JD Compliance Scan prompt before trusting a batch, and again after **any** edit to the prompt.

**These bodies are reconstructions, not verbatim payloads.** Each carries the decisive evidence quoted
in the spec, wrapped in the boilerplate that the spec records as having nearly flipped a verdict
(pay-transparency city/postal code, US benefits, EEO, ADA language, state lists). The original payloads
were not retained — one fetch per link, ever — and these rows now hold values, so they are no longer
eligible for a fetch. Testing on reconstructions is weaker than on the originals: it proves the prompt
discriminates the *named* traps, not that it survives every real JD.

**Pass condition: 5/5, and specifically fixtures 1 and 4 must differ.** They carry near-identical US
location language and land on opposite verdicts, purely because one adds a work-authorization clause.
Any prompt edit that collapses that pair is wrong, however reasonable it looks.

---

## Fixture 1 — row 4, Johnson Group, Account Director → `US-Specific`

Badge was `Remote`. Category 3. The 12-state list contributes nothing.

```
About the job
Johnson Group is a leading provider of restoration services. We are seeking an Account
Director to grow our commercial book of business.

Location: Remote. Candidates must be located in one of the following states: TN, GA, AL, FL,
NC, SC, VA, KY, MS, LA, TX or OK.

Must be eligible to work in the USA.

Responsibilities
- Build and maintain relationships with commercial property managers and insurance carriers
- Develop a pipeline of new business opportunities
- Represent Johnson Group at industry association events

Qualifications
- 5+ years of B2B sales experience, restoration or insurance preferred
- Bachelor's degree or equivalent experience

Benefits: medical, dental and vision coverage, 401(k) with company match, PTO.
Johnson Group is an equal opportunity employer.
```

**Verdict: US-Specific.** *"Must be eligible to work in the USA"* — Category 3, a legal status a LatAm
candidate cannot hold. Strike the state list and the verdict is unchanged, which is the tell.

## Fixture 2 — row 8, ACM Global Laboratories, Director of Cloud Software Engineering → `Remote-friendly`

Badge was `Remote`. The pay-transparency block is the trap.

```
About the job
Location: Remote

The Director of Cloud Software Engineering leads our platform engineering organization and owns
the cloud architecture roadmap.

Requirements
- 10+ years of software engineering experience, 4+ leading teams
- Deep experience with Azure or AWS; Microsoft Azure Solutions Architect or AWS Solutions
  Architect certification preferred
- Experience with regulated data environments

PAY RANGE
$165,000 - $195,000 per year
CITY: Rochester
STATE: NY
POSTAL CODE: 14624

Physical requirements: must be able to remain stationary for extended periods and operate a
computer. Reasonable accommodations will be made in accordance with the ADA.

ACM Global Laboratories is an equal opportunity employer.
```

**Verdict: Remote-friendly.** No licensure, no presence duty, no eligibility clause. The Microsoft/AWS
certifications are globally available; `CITY: Rochester / POSTAL CODE: 14624` sits under a `PAY RANGE`
heading and is the employer's location, not a residency rule; the ADA paragraph is boilerplate.

## Fixture 3 — row 9, Balance Ophthalmics, U.S. Strategic Account Manager → `US-Specific`

Badge read `Remote`. Category 2 — and note the title's "U.S." is *not* what decides it.

```
About the job
Balance Ophthalmics is commercializing a novel device for the treatment of progressive myopia.
We are hiring a U.S. Strategic Account Manager to drive adoption across ophthalmology practices.

Responsibilities
- Own revenue for an assigned territory
- Provide live procedure support in clinic
- Case coverage during initial device installations and surgeon onboarding
- Travel up to approximately 50% within the assigned territory
- Partner with marketing on regional conferences and trade shows

Qualifications
- 5+ years of medical device sales experience
- Comfortable in a clinical/surgical environment

Competitive salary, commission, medical/dental/vision and 401(k).
```

**Verdict: US-Specific.** *"live procedure support"*, *"case coverage during initial device
installations"*, *"travel up to ~50% within assigned territory"* — Category 2 presence duties that
cannot be performed from abroad. The verdict rests on the duties, not on "U.S." in the job title.

## Fixture 4 — row 140, Collaborative Fund Services, Fund Administrator → `Remote-friendly`

Badge was `Remote`. **The critical contrast with fixture 1.**

```
About the job
Location: Remote (U.S.)

Collaborative Fund Services provides fund administration to venture and growth-stage funds.
This is a fully remote position within the United States.

Responsibilities
- Prepare quarterly capital account statements and financial reporting
- Process capital calls and distributions
- Coordinate with auditors and tax preparers during year-end

Qualifications
- 3+ years in fund administration or public accounting
- CPA or equivalent experience
- Strong Excel skills

We offer medical, dental, vision, 401(k) and unlimited PTO.
Collaborative Fund Services is an equal opportunity employer.
```

**Verdict: Remote-friendly.** `Location: Remote (U.S.)` and *"fully remote position within the United
States"* describe where the employer is advertising — geography only. `CPA or equivalent experience`
states an explicit alternative, so Category 1 does not fire. No eligibility clause anywhere: nothing
here a LatAm candidate could never satisfy.

## Fixture 5 — row 146, A4AL, Legislative Intern (Volunteer) → `US-Specific`

Live badge read `On-site`; col I already held `Remote` and was **not** touched — the documented case for
never correcting an existing value. The disqualifier is in the last line, which is why the whole body
must be read.

```
About the job
Americans for Assistive Learning (A4AL) is seeking Legislative Interns to support our policy and
advocacy work. This is an unpaid volunteer position.

Responsibilities
- Track legislation and regulatory dockets relevant to assistive learning technology
- Draft memos and one-pagers for the policy team
- Support coalition calls and stakeholder outreach
- DMV-based interns may be asked to attend occasional Hill briefings in person

Qualifications
- Current undergraduate or graduate student, or recent graduate
- Interest in education or disability policy

A4AL is an equal opportunity organization and welcomes applicants of all backgrounds.

Under 52 U.S.C. § 30121 and 11 CFR 110.20, foreign nationals without legal authorization are
prohibited from volunteering or employment with PACs.
```

**Verdict: US-Specific.** The statute is a Category 3 legal bar. The `DMV-based interns may be asked
to…` line is explicitly *not* disqualifying — it is conditional on already living there — so a prompt
that fires on that line instead is right for the wrong reason and should be treated as a failure.
