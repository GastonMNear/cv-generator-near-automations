# Smartlead Lead API — field reference

Everything here was verified against the live API on 2026-09-09 across six real leads spanning
the Apollo/EXP010, EXP012 Sales-GTM, Asia No-HM, Canada HMs and LatAm HMs campaign families.

## The call

```bash
curl -s "https://server.smartlead.ai/api/v1/leads/?email={EMAIL}&api_key={SMARTLEAD_API_KEY}"
```

One call, keyed by email. No campaign or table needs to be known first — the campaign comes back
in the response.

## Gotchas worth knowing before you debug

### 403 Forbidden is a blocked User-Agent, not rate limiting

Smartlead is behind Cloudflare, which rejects Python's default `urllib` User-Agent with
`403 Forbidden / error code: 1010`. This is the single most misleading failure mode here:

- It looks exactly like throttling, so the instinct is to add exponential backoff.
- **Backoff never clears it.** Verified: retries at 10s/20s/40s/80s all returned 403.
- The same URL via `curl` returns 200 immediately.
- `x-ratelimit-remaining` was `199/200` throughout — the quota was never near exhausted.

Fix: send any real User-Agent header. Confirmed working with both `curl/8.7.1` and a Chrome UA.

Real rate limiting arrives as **429**, with `x-ratelimit-limit` (200), `x-ratelimit-remaining`
and `x-ratelimit-reset` headers.

### 401 means the key was rotated

`{"message": "Invalid API Key"}` with HTTP 401. Not retryable — the key in `.env` is stale.

### A null employee_count is normal

Older leads frequently lack `employee_count`; newer leads carry it. Report it as unavailable in
the output next to the CV and finish the workflow — it is supplementary, never a blocker.

### A miss returns `{}` with HTTP 200

Not a 404. Detect a miss by checking for an absent `id`, not by status code.

### `/campaigns` is 403 for this key

The key is scoped to lead endpoints. `GET /campaigns` returns 403 regardless of User-Agent, so
campaign metadata must come from the lead's own `lead_campaign_data`.

## Response shape

Top level: `id`, `first_name`, `last_name`, `email`, `company_name`, `website`, `location`,
`linkedin_profile`, `company_url`, `is_unsubscribed`, `created_at`, `custom_fields`,
`lead_campaign_data`.

The pipeline-relevant values live in `custom_fields`:

| Custom field | Purpose | Reliability |
|---|---|---|
| `job_url` | The job post — **canonical field** | The field to read; null on a minority of leads |
| `job_linkedin_url` | The job post, legacy field name | Only populated where `job_url` is null |
| `employee_count` | LinkedIn headcount | Null on many **older** leads; present on newer ones |
| `company_linkedin_url` | Company page (not a job post) | Present on some campaigns |
| `open_role_title` | Role, written for email copy | Often lowercase/abbreviated; null sometimes |
| `normalized_company_name` | Shortened company name | Frequently over-clipped; sometimes absent |
| `industry` | Company industry | Usually present |
| `email_one` / `email_two` / `email_three`, `subject_line` | The campaign copy that was sent | Present |
| `prospect_title` | Lead's own title | Often empty string |

`lead_campaign_data[]` carries `campaign_id`, `campaign_name`, `last_sent_at`, `last_reply_at`.
A lead often appears in two campaigns — the original plus a `SUB | ...` follow-up.

## The job URL: read `job_url`, fall back to `job_linkedin_url`

**`job_url` is the canonical job-post field** — read it first. `job_linkedin_url` is the legacy
name and is still the only populated field on a minority of leads, so it remains a fallback.

The two are **never both populated**, so a null in one is not a miss. Verified 2026-09-09 across
seven leads:

| Lead | `job_url` | `job_linkedin_url` |
|---|---|---|
| ayush@mach33media.com | SET | null |
| craig.t@blackretebuilders.com | SET | null |
| zainab@clickstalentagency.com | SET | null |
| benjamin@covenantgolfsociety.com | SET | null |
| dante@entrycapital.com.br | SET | null |
| michael.hsu@curogram.com | null | SET |
| awollmann@horvath-partners.com | null | SET |

`fetch_lead_smartlead.py` checks `job_url`, `job_linkedin_url`, `job_post_url`, `linkedin_job_url`
in that order. Only if all are empty does the lead genuinely have no job post.

Do not confuse either with `company_linkedin_url` (a company page) or `linkedin_profile` (the
lead's own profile).

## Two company-name fields — take whichever exists, prefer the longer

`company_name` (top level) and `normalized_company_name` (custom field) both hold company names.
**At least one is always populated, but either can be empty individually**, so read both and use
whichever is present. When both are populated, the longer one is nearly always better —
`normalized_company_name` is shortened for email copy and drops meaningful words.

| Lead | `company_name` | `normalized_company_name` | Chosen | Real name (job post) |
|---|---|---|---|---|
| ayush@mach33media.com | Mach33 Media | Mach33 | Mach33 Media | Mach33 Media |
| zainab@clickstalentagency.com | Clicks Talent | Clicks | Clicks Talent | Clicks Talent Agency |
| awollmann@horvath-partners.com | Horváth USA | Horváth | Horváth USA | Horváth |
| craig.t@blackretebuilders.com | Blackrete | *(absent)* | Blackrete | Blackrete Builders Inc |

Two things this shows:

- With only one field populated (Blackrete), that value is used even when clipped — which is why
  the job post still wins whenever it yields a name.
- Picking the longer field recovers the full name where one exists:
  `benjamin@covenantgolfsociety.com` stores the complete "The Covenant Golf Society" in
  `company_name` alongside a clipped "Covenant Golf" in `normalized_company_name`. In every lead
  tested, `company_name` was the same length or longer — but since either field can be empty on
  its own, reading both and taking the longer non-empty value is what makes that safe.

## Titles are written for email copy, not for documents

Observed company-name clipping even after choosing the longer field:

| Lead | Chosen name | Real name (from job post) | Still clipped? |
|---|---|---|---|
| craig.t@blackretebuilders.com | Blackrete | Blackrete Builders Inc | yes |
| dante@entrycapital.com.br | Entry | Entry Capital | yes |
| benjamin@covenantgolfsociety.com | The Covenant Golf Society | The Covenant Golf Society | no |

`open_role_title` is similarly informal: "estimators", "founding AE",
"sr talent manager influencer", "investment and credit analysts".

**Therefore: let the job-post extraction (Step 2) decide the company name and job title.** Use
Smartlead's copies as a cross-check that the URL points at the expected role, and as a last-resort
fallback if extraction yields nothing.

## What this replaced

The Clay path had to infer a table from a campaign name, walk ordered fallback chains, and
linearly scan records (LatAm HMs is ~33k rows, 2–3 minutes). It also missed leads whose stored
address was a variant — `michael.hsu@curogram.com` needed a domain scan to find in Clay, and
resolves directly by email in Smartlead.
