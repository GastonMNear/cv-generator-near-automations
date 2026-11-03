# Hirebase credit optimization (2026-11-03)

Proposal only. Nothing is live: the routine still runs `references/search_filters.json` (saved here as
`baseline_search_filters_2026-11-03.json`). No `/v2/jobs/search` calls were made; every unit count below comes
from the free `/v2/jobs/estimate`.

## TLDR

**Core config (`core_search_filters.json`) = baseline + two exclusions. Both target units that almost never become a lead.**

1. **`job_titles` exclusions** (31 words: nurse, RN, therapist, physician, attorney, licensed, "participants",
   technician-type field roles and similar; full list in the file). In Clay these titles are 5.9% of job rows,
   and the role check rejects 96% of the ones it judges. They produced **4 of 2,305 Smartlead leads (0.2%) and no
   positives**. In the historic No-HM campaigns the same words have a 0.30% positive rate (3 of 997), against 0.78% overall.
2. **`company_keywords: ["-blackbox"]`** drops one mass poster, Clients Blackbox: **654 live jobs since Oct 20,
   7.6% of that window**. All 42 of its deduped Clay rows stop at HubSpot do-not-contact, so it has produced **0 leads**.
   It posts in bursts on Mondays (Oct 20, Oct 27). This reverses the 2026-10-21 "no company exclusions" call;
   approved by Gaston on 2026-11-03 and live in `search_filters.json` together with #1.

| | Units / month | Smartlead leads / month | Positives / month | Booked / month |
|---|---:|---:|---:|---:|
| Baseline (276 subs) | ~20,000 | ~4,900 | ~8.5 | ~4 |
| **Core** | **~18,000** (−9% to −14%) | ~4,900 (−0.2%) | ~8.5 (no positive came from the cut) | ~4 |
| Core + expansion (Hybrid, 1–50 emp.) | ~22,800 | not known (no prior) | not known | not known |

- Estimates by window: baseline 8,643 / 4,697 / 967 jobs (date_posted ≥ Oct 20 / ≥ Oct 27 / ≥ Nov 2) → core
  7,421 / 4,272 / 871. So −14.1% / −9.0% / −9.9%. Steady state is about −10%, plus the Blackbox bursts when they happen.
- Units/month for the baseline is your ~20k figure. The other rows scale it by the estimate ratios.
- Leads and positives use HireBase's own rates (2,305 leads from 14 posting days; 4 positives and 2 booked
  from 1,945 contacted, 0.21% / 0.10%). Leads are still maturing, so treat the positives as a floor. The historic
  No-HM prior, weighted by size, would put it nearer 0.47%.
- Headroom on 25k: core 18k + expansion 4.8k leaves ~2.2k for a backfill day and a 429 re-run (see Side finding).
- I did **not** cut sub-industries in the core. The sub filter is a weak lever: dropping it entirely only adds 1.7%
  (8,785 vs 8,643), because most companies carry several tags. A cut of the worst healthcare-provider and insurance
  subs only saves 2.5%, and it costs leads (see "Deeper cuts").

## A. Unit funnel (Clay jobs table export, 6,353 rows, posted Oct 20 – Nov 2)

Units → rows: Clay's webhook table dedupes on `title - company`, so each row is one unique role. The unit count
for this window isn't stored anywhere (run files live in the routine's temp dir). ~20k/month × 14/30 ≈ 9.3k
units → 6,353 rows means about **32% of units disappear at dedupe**. On Oct 20 alone it was 1,249 units → 570 rows.

| Stage (first gate a row fails) | Rows | % of rows |
|---|---:|---:|
| 1. Recruiting agency (Clay lookup; slips past `hide_recruiting_agencies`) | 591 | 9.3% |
| 2. Job already in another US OJ workflow (LinkedIn / Sales / Mkt / Eng / Apollo) | 970 | 15.3% |
| 3. Role not placeable (Clay Role Qualification = Unqualified) | 1,346 | 21.2% |
| 4. Company not qualified, or a repeat company (Qualified? merge = false) | 1,279 | 20.1% |
| 5. HubSpot do-not-contact | 332 | 5.2% |
| 6. Reached contact search | 1,835 | 28.9% |
| → job produced ≥1 Smartlead lead | 1,156 | 18.2% |
| → Smartlead leads (campaign 4217467) | 2,305 | ~25 per 100 units |
| → contacted (Email 1 sent) | 1,933 | ~21 per 100 units |

Join check: 2,303 of 2,318 Smartlead leads (99.4%) match a Clay `Job Url` on `custom_fields.job_url`
(exact URL incl. query string). All 4,810 rows of the Baseline1 leads export match too.

**By role family** (title keyword rules; same rules applied to historic `open_role_title`):

| Role family | Clay rows | Role rejected | Leads / 100 rows | HB contacted / pos | Hist. No-HM n | Hist. pos % | Hist. booked % |
|---|---:|---:|---:|---:|---:|---:|---:|
| Ops / PM / admin | 1,195 | 17% | 41.2 | 430 / 1 | 24,145 | 0.68% | 0.08% |
| Engineering / IT | 1,015 | 12% | 36.9 | 303 / 0 | 17,099 | 0.59% | 0.10% |
| Sales / BD | 806 | 12% | 45.7 | 316 / 1 | 15,417 | 1.02% | 0.20% |
| Data / AI | 513 | 16% | 35.3 | 151 / 0 | 4,217 | 0.55% | 0.14% |
| Other | 484 | 32% | 31.4 | 119 / 0 | 9,399 | 0.91% | 0.13% |
| **Field / trades / in-person** | 454 | **53%** | **18.3** | 64 / 0 | 5,137 | **0.41%** | 0.04% |
| **Healthcare / clinical** | 433 | **60%** | **17.8** | 64 / 0 | 1,703 | **0.23%** | 0.06% |
| Marketing | 350 | 6% | 40.6 | 126 / 1 | 6,946 | 1.61% | 0.20% |
| Product / design | 328 | 3% | 47.3 | 135 / 0 | 4,527 | 1.06% | 0.18% |
| Customer success / support | 310 | 9% | 46.1 | 115 / 0 | 4,341 | 0.51% | 0.16% |
| Finance / accounting | 279 | 25% | 36.9 | 89 / 1 | 6,673 | 0.46% | 0.10% |
| HR / recruiting | 95 | 5% | 20.0 | 11 / 0 | 1,860 | 0.59% | 0.05% |
| **Legal** | 91 | **59%** | **16.5** | 10 / 0 | 804 | 0.87% | 0.00% |

The title exclusions take out the part of the bolded families that Clay rejects (96% rejection, 4 leads). Words I tested and kept because Near does place some of them: technician (helpdesk / IT support
techs), driver (kernel-driver engineers), paralegal, construction (BD roles at construction firms).

**By company size** (Clay LinkedIn employee count, propagated by domain):

| Size | Clay rows | Leads / 100 rows | HB contacted / pos / booked | Hist. No-HM n | Hist. pos % | Hist. booked % | Hirebase units (≥Oct 20) |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1–10 | 344 | 27.3 | 85 / 0 / 0 | 3,756 | **3.19%** | 0.64% | 1,058 |
| 11–50 | 505 | 83.8 | 361 / 3 / 2 | 11,114 | **0.94%** | 0.17% | 1,604 |
| 51–200 | 1,215 | 77.8 | 780 / 1 / 0 | 20,077 | 0.26% | 0.04% | 3,462 |
| 201–500 | 857 | 93.5 | 671 / 0 / 0 | 19,034 | **0.13%** | 0.02% | 2,507 |
| 500+ (LinkedIn, despite Hirebase ≤500) | 490 | 8.6 | 36 / 0 / 0 | 2,510 | 0.12% | 0.00% | — |
| not enriched (stopped before enrichment) | 2,942 | 0 | — | — | — | — | — |

The gradient holds within each campaign and for both CEO/founder and non-CEO prospects
(201–500: 0.12% CEO, 0.13% other; 11–50: 1.14% / 0.78%). **Company size is the strongest quality signal in the
data, much stronger than industry.** The 1–10 band has the best reply quality but the worst contact yield
(27 leads per 100 rows), so finding contacts at micro-companies is a Clay lever worth a look.

**Other dimensions:** salary band, job board and seniority show no meaningful difference in leads per row
(26–48 per 100 rows, except the boards with tiny n). Workday and Paylocity have higher role-rejection rates
(28–37%), and LinkedIn-hosted jobs are 58% agencies (45 rows). None of these is a Hirebase filter anyway:
there is no `job_board` filter (422), and an `experience` or `job_category` include-list drops the 16% / 12% of
jobs that have no tag.

**Mass posters** (live units since Oct 20 vs deduped Clay rows): Clients Blackbox 654 units → 42 rows → 0 leads
(HubSpot do-not-contact). Kled AI shows 96 rows but 0 live units now (expired). Everyone else in the top 10 is ≤50
units. `company_name` is include-only (`-X` returns 0 jobs), so `company_keywords` with `-` is the only exclusion route.

## B. Lead quality

HireBase alone: **1,945 contacted, 4 positives (0.21%), 2 booked (0.10%)**, all at Email 1. No segment has
≥300 contacted leads *and* a positive, so I rank nothing on HireBase rates. They're shown above as
"HB contacted / pos" for direction only.

Prior used instead: the US OJ No-HM historic campaigns 2676153, 2812730, 3570933, 3804793, 3570999, 3804786
(102,268 contacted, 788 positives = 0.77%, 126 booked; matches the Oct 29 benchmark). All 16 US OJ HM campaigns
were also pulled (25,571 / 647 / 81) but not used for ranking, because the HM motion converts at ~3× No-HM.
Positive = categories with `sentiment_type: positive` plus Not Qualified. Booked = Meeting Booked.

**Industry prior** (LinkedIn industry from `custom_fields.industry`, filled on 57,754 of 102,268 contacted; n ≥ 300, worst first):

| LinkedIn industry | Hist. n | pos | pos % | booked | HB Clay rows | HB leads | HB contacted / pos |
|---|---:|---:|---:|---:|---:|---:|---:|
| Environmental Services | 587 | 0 | 0.00% | 0 | 15 | 13 | 10 / 0 |
| Banking | 796 | 0 | 0.00% | 0 | 15 | 9 | 9 / 0 |
| Pharmaceutical Manufacturing | 557 | 0 | 0.00% | 0 | 30 | 15 | 14 / 0 |
| Information Technology and Services | 557 | 0 | 0.00% | 0 | 55 | 24 | 22 / 0 |
| Construction | 939 | 1 | 0.11% | 0 | 11 | 17 | 16 / 0 |
| Hospitals and Health Care | 3,348 | 4 | 0.12% | 1 | 262 | 219 | 196 / 0 |
| Computer and Network Security | 772 | 1 | 0.13% | 0 | 149 | 49 | 40 / 0 |
| Manufacturing | 767 | 1 | 0.13% | 1 | 18 | 16 | 14 / 0 |
| Biotechnology Research | 1,086 | 2 | 0.18% | 0 | 109 | 73 | 69 / 0 |
| Insurance | 1,740 | 4 | 0.23% | 1 | 111 | 63 | 55 / 0 |
| Software Development | 7,279 | 31 | 0.43% | 7 | 618 | 425 | 362 / 1 |
| IT Services and IT Consulting | 2,748 | 12 | 0.44% | 1 | 197 | 139 | 123 / 0 |
| Financial Services | 3,560 | 17 | 0.48% | 7 | 183 | 133 | 107 / 0 |
| Non-profit Organizations | 1,454 | 9 | 0.62% | 0 | 72 | 50 | 45 / 0 |
| Advertising Services | 2,045 | 19 | 0.93% | 4 | 152 | 70 | 66 / 0 |
| Business Consulting and Services | 1,543 | 15 | 0.97% | 3 | 83 | 64 | 49 / 1 |
| Technology, Information and Internet | 2,215 | 28 | 1.26% | 6 | 183 | 100 | 90 / 1 |
| Marketing Services | 763 | 16 | 2.10% | 5 | 25 | 29 | 19 / 0 |

(Full table, including industries with n < 300, is in the scratch `analysis.json`; ask if you want it saved here.)
Industry rates are partly a size effect: low-rate industries skew to larger companies.

**Expected positives per 100 units** = contacted per 100 units × prior, by size band (the strongest factor):
1–10 ≈ 0.24, 11–50 ≈ 0.20, 51–200 ≈ 0.05, 201–500 ≈ 0.03. In other words, 201–500 uses 29% of units for
~10% of expected positives. **Decision (Gaston, 2026-11-03): keep it.** 1–10 and 11–50 are always fetched, and
larger companies fill whatever credits remain. `feed.py` now fetches the bands in that order and skips the larger
ones when the period's remaining quota is tight (see the hirebase-job-feed skill).

## C. Keep / cut / expansion lists

**Core cuts (in `core_search_filters.json`):**

| Cut | Units saved (≥Oct 20 / ≥Oct 27) | Leads lost | Evidence |
|---|---:|---:|---|
| `job_titles` exclusions (31 words) | −568 (−6.6%) / −401 (−8.5%) | 4 of 2,305 | 96% role-rejected in Clay; prior 0.30% (n=997) |
| `company_keywords: ["-blackbox"]` | −654 (−7.6%) / −24 | 0 | 42/42 rows HubSpot do-not-contact; approved by Gaston 2026-11-03 |

**Sub-industries: keep all 276.** Ranked "first to cut" if a deeper trim is ever needed, all from industries ≤0.23% prior:

| Optional deeper cut | Units saved vs core | Prior | Note |
|---|---:|---:|---|
| Healthcare-provider subs: Telemedicine, Healthcare Support Services, Medical Practices, Home Health Care, Rehabilitation, Hospitals, Ambulatory Care, Dental, Vision Care, Medical Education & Training | together with insurance: −217 (−2.9%) / −143 (−3.3%) | Hospitals & HC 0.12% (n=3,348); Medical Practices 0.32% | H&HC companies give 9.5% of HB leads (high yield), so the cut loses roughly as many leads as units |
| Insurance, Health Insurance | (incl. above) | 0.23% (n=1,740) | |
| Biotechnology, Medical R&D, Pharmaceuticals | ~−2% | 0.18% / 0.00% (n=1,086 / 557) | |
| Company size 201–500 | −29% | 0.13% (n=19,034) | Not a cut (Gaston): fetched last, and only with spare credits |

**Expansion (ranked by expected value; `expansion_search_filters.json` is #1, run as a second search next to the core):**

| # | Add | Units / month | Prior | Recommendation |
|---|---|---:|---|---|
| 1 | **Hybrid, US, 1–10 + 11–50 employees** (core subs + title exclusions) | ~4,800 (2,039 / 1,130 / 245 per window; 1–10 alone ~1,200, 11–50 ~3,500) | Size band is the best (3.2% / 0.94%), but hybrid has **no prior** | Run as a tagged test and read it at 3,600 contacted. Risk: your Nov 3 hypothesis is that HireBase replies are better *because* the list is 100% remote. |
| 2 | Remote Contract + Part Time, 1–50 employees | ~500 | none | Small; only if Near places these |
| 3 | Drop `sub_industry` entirely | ~+350 (+1.7%) | n/a | Mostly government and public-safety companies; low value |
| 4 | Company size 501–1,000 | ~5,800 | 0.12% (500+, n=2,510) | Don't: Clay disqualifies 71% of 500+ companies |

Already at full coverage: `geofilter_params.mode: auto` instead of strict adds 0 at 1–50. Reposted signal: only 6 jobs (signals start Oct 20).

## D. Side finding: the 429 double-billing (proposal, `feed.py` not edited)

`feed.py` calls `sys.exit` on any non-200 search page *before* saving the run file. So on Nov 3, when the plan
cap returned a 429 at page 6, pages 1–5 (500 units) were billed and then thrown away, and the rerun paid for them again.
Proposed changes:
1. On a non-200 page, save and post the jobs fetched so far, then exit with a `--resume-page N` hint. A rerun
   starts at page N, so pages already paid for are never fetched again.
2. Pre-flight quota check: read `Hirebase-Usage-Included-Remaining` from the first page's headers. If it's below the
   estimate, stop before page 2, or fetch only what fits, oldest first. (Neither `/estimate` nor any usage endpoint
   returns the quota, so the first page is the earliest point it can be checked.)
3. Worth considering: the documented `ingested_after` + `sort_by: first_ingested` polling replaces the
   date_posted logic. It never re-bills a job and it catches late-indexed jobs.

## Caveats and assumptions

- Monthly units are your ~20k baseline scaled by estimate ratios. Estimates count jobs *still live*, so older
  windows undercount what was billed. That's why I report three windows.
- Role families and title exclusions use keyword rules on titles. Historic titles are normalized
  (`open_role_title`, e.g. "sr eng"), so family assignment is approximate there.
- The leads export covers the Baseline1 table only. All lead counts come from Smartlead 4217467 directly, joined on `job_url`.
- HireBase leads are 12 days old on average. Its positive rate (0.21%) is a floor; Wrong Person is 30% of real replies.
- The historic prior mixes motions and periods (Nov–Jun 0.98%, Jun 30+ 0.52%), and the post-split Routing CTA cohort
  is CEO/founder-heavy at <50 employees. I checked that the size gradient holds within each campaign and within non-CEO prospects.
- Smartlead categories are live, so re-pulling later can change positives.
- `company_keywords: ["-blackbox"]` is a word-level exclusion on company descriptions. Today it removes exactly
  Clients Blackbox (8,643 → 7,989 = −654 = its whole count), but it would also drop any future company whose
  description says "blackbox".

## Files

- `baseline_search_filters_2026-11-03.json`: the live config as of today, unchanged.
- `core_search_filters.json`, `core_estimate_response.json`
- `expansion_search_filters.json`, `expansion_estimate_response.json` (a second search, run in addition to core)
- `baseline_estimate_response.json`: the same three windows for the baseline, for comparison.
