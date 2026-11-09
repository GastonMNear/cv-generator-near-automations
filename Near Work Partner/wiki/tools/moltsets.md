---
type: tool
title: MoltSets — Reference
created: 2026-10-23
updated: 2026-10-23
tags: [tool, moltsets, enrichment]
status: evaluating
related: ["[[tools/clay]]", "[[tools/apollo]]", "[[context/outbound-engine]]"]
---

# MoltSets

Contact-data API (public beta): business and personal emails, mobile phones, people and company search, and reverse lookups. Planned as a **fallback layer in Clay** after our email waterfall and after Clay search, AI researcher and Apollo miss.

Docs: https://developer.moltsets.com (full index at `/llms.txt`; any page as markdown by adding `.md`).

## Account (checked 2026-10-23)

- **Update 2026-11-04:** now on the **$27 plan** (`subscription_27`), with unlimited tokens. Weekly caps are 2.5k search records and 5k enrichment records. The free-plan limits below no longer apply.

- Account "Hire With Near", **free plan**: 1,000 lifetime tokens, plus a search trial of 100 results total, max 10 per call.
- Every tool costs **1 token per record found**. A miss (`status: "not_found"`) costs nothing but still counts as a request.
- **Two separate meters.** Tokens are the currency, spent by every tool. Search records are a separate cap on `search_people` and `search_companies` results. A search result spends 1 token AND 1 search record, while an email lookup spends only a token. On the free plan that means 1,000 lookups total, of which at most 100 can be search results. On paid plans tokens are unlimited and the only caps are the 5h/weekly record pools, with enrichment and search counted separately.
- **Free plan search requests are capped too.** The rate-limits doc says 100 lifetime search requests, and misses count. `get_account` reports 200 per 5h. Plan for ~100 companies searched in the free trial, not 100 hits.
- $27 plan: enrichment 1k records/5h and 5k/week (5k requests/5h); search 500 records/5h and 2.5k/week (2.5k requests/5h); 3 concurrent searches. Only hits consume records.
- Test plan (Gaston, 2026-10-23): US first. Use `search_people` with `limit: 1` on companies where Clay, AI and Apollo found no one, then spend all remaining tokens on `linkedin_to_business_email` for no-email leads. Only A/B counts as a valid email.
- Email fallback input: Gaston confirmed (2026-10-23) that leads **always have a LinkedIn URL**, so use `linkedin_to_business_email` and skip `search_business_email_by_name`.
- `personal_email_available: true`. No phone tokens (phone lookups need a separate paid add-on).
- API key: `MOLTSETS_API_KEY` in `.env`. `get_account`, `get_billing` and `get_usage` are free.
- Paid plans: $27/mo gives 500 search records per 5h; $97/mo gives 7.5k search and 15k enrichment records per 5h. Phones: $27/mo for 180 tokens.

## Calling it

- `POST https://api.moltsets.com/api/v1/tools/<tool>` with a JSON body.
- Headers: `Authorization: Bearer <key>`, `Content-Type: application/json`, **`User-Agent: <anything>`**. Without a User-Agent you get a 403.
- **A miss is HTTP 200.** Branch on `status` (`ok` / `not_found`), never on the HTTP code. The only 404 is a wrong tool name.
- Errors: `{"error":{"code":...}}`. On 429, wait `metadata.retry_after` seconds. `search_concurrency_exceeded` means too many searches in parallel (3 on Free/$27, 5 on $97).

### In Clay (HTTP API enrichment)

1. Method `POST`, endpoint as above, plus the 3 headers.
2. Response values to return: `results`. Clay traverses only one level deep.
3. Add formula columns for `status`, `email`, `risk_score` and so on.
4. Run conditions: only run when the earlier steps found nothing. Route on `status = "ok"`.

## Tools we care about

| Have → want | Tool | Body | Returns |
|---|---|---|---|
| LinkedIn URL → work email | `linkedin_to_business_email` | `{"linkedin_url": ...}` | `email, risk_score, last_validated_at` |
| LinkedIn URL → any email | `linkedin_to_best_email` | same | adds `type`: business/personal |
| Name + domain → work email | `search_business_email_by_name` | `{"name", "company"}` or `first_name`/`last_name` | `email, risk_score, linkedin_url` |
| Company + role → people | `search_people` | filters below | profiles **including `business_email` + risk** |
| Email → profile | `reverse_email_lookup` | `{"email"}` or `{"emails":[..≤100]}` | name, title, company, LinkedIn |
| LinkedIn → full profile | `reverse_linkedin_lookup` | `{"linkedin_url"}` | profile + business and personal emails |
| LinkedIn → mobile | `linkedin_to_mobile_phone` | `linkedin_url(s)` (≤100) | carrier-verified mobile (phone tokens) |

Miss chain they recommend: `linkedin_to_business_email` → `linkedin_to_best_email` → `reverse_linkedin_lookup`.

### `search_people` essentials

- Targeting a company: `company_domain` (string or a list of up to 100; full URLs are normalized). Use `company` (a name) only when there's no domain.
- Role: `title` (string or list, OR'd). 1–2 words must all match; longer titles allow some slack. Never put roles in `query`; `query` is for person names.
- `seniority` enum: Intern, Entry, Senior, Manager, Director, VP, Head, **C Suite** (with a space), Owner, Partner. About 60% of records have it.
- `department` **or** `functional_area` (never both). Values: Operations, Sales, Information Technology, Engineering, Finance, Marketing, Human Resources, Design, Legal and so on.
- Other filters: `country` (99% filled), `state`, `city`, `employee_range` (`1-10`…`5001+`), `revenue_range`, `industry` (22 buckets), `linkedin_industry`, `naics_code`. Exclusions: `exclude_company_domain` (≤100, free suppression), `exclude_country`, `exclude_seniority` and so on.
- `limit` is 1–25 (default 10) and `offset` paginates. **Each record returned costs one token/search record**, so set `limit` to how many contacts we want per company.
- Response: `results.results[]` plus `results.total`. Each person has `full_name, title, seniority, linkedin_url, business_email, business_email_risk_score, business_email_validated_at, company{domain, size, ...}, _score`.
- Lists are OR within a field and AND across fields.

## Email risk score (A–F) = send safety, NOT identity

- **A** validated deliverable → send. **B** has past engagement → send.
- **C** catch-all, **F** no signal → unknown, so send at low volume or route to a separate segment.
- **D** spam trap / do-not-mail / recent complaint → **always suppress**.
- When signals disagree: D > A > B > C > F. `last_validated_at` refreshes every 90 days and can be null.
- A grade of A does not mean the email belongs to the right person. Check that the email domain matches the company domain and that the returned company matches our row.

## Quirks

- Search is "alpha"; email tools are "beta". Watch match quality during the pilot.
- `search_people` with `limit: 1` is the cheapest probe; there is no free count. `search_linkedin_profile` supports `count_only: true` for free.
- **CEO search titles (tested 2026-11-04).** A 3-word title allows one word of slack, so `"Chief Executive Officer"` also returns CMOs and CCOs, and `"President"` matches "Vice President". Use `["CEO","Chief Executive","Founder","Co-Founder","Cofounder"]` with `limit: 3`, and post-filter titles in Clay, because there is no `exclude_title` and "Assistant to the CEO" still matches `CEO`. On 10 Clay-miss companies, the loose list gave 6 hits (2 not CEOs). The strict list gave 1 (a real CEO).
- **Leader search by seniority (tested 2026-11-04, generic no-HM workflow).** On 12 companies where Clay, AI and Apollo all missed, the job's AI title list found someone at only 2 (both weak matches). `seniority: ["Owner","C Suite","Partner","VP","Head","Director"]` with no title found someone at 9. The seniority tag is noisy ("Senior Partner Services Coordinator" = C Suite, "Area Manager" = VP), so post-filter titles in Clay. **But seniority alone ignores the job** (an SDR job could return a VP Engineering), so Gaston rejected it. **Chosen instead (tested on 30 misses):** keep only the 1–2-word titles from the job's Lead Title Search list, so loose matching can't kick in, and add `CEO, Owner, Founder, Co-Founder, Managing Partner, General Manager` for companies under 150 employees. That gave 9 relevant hits out of 30. An empty title list makes the search return anyone at the company ("Laborer"), so never send one. The `department` filter gave 4/12 and tags most founders as "Operations", so it's not useful. Business emails can sit on another domain (a parent company, or a likely wrong match such as `andromeda.tech` → `@andromeda.com.tw`).
- **Clay email-fallback gate (audit 2026-11-04).** Each validator in our waterfalls skips ("run condition not met") when the last finder returns an email that an earlier finder already returned and that was already rejected. A fallback gate that waits for `Validate <last> = SUCCESS` therefore never fires on those rows (8 of ~100 no-email rows in Baseline). The gate must also accept `ERROR_RUN_CONDITION_NOT_MET` from the validator. Rows created while a table's auto-run was off stay stuck on "not met" after auto-run is turned back on (`keep_existing`), so run the first finder on them by hand.
- Personal-email tools are US-only (`_usa` suffix; the old names are being retired).
