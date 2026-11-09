# Smartlead SmartDelivery Weekend Tests — Execution Handoff

## Prompt to give the executing agent

> Work inside `/Users/gastonmurillo/Documents/Near Automations/Near-AI-Agent`. Read `/Users/gastonmurillo/Documents/Near Automations/Near-AI-Agent/handoff.md` completely, then execute it exactly. This task is authorized to create the specified Smartlead SmartDelivery automatic tests, which cause real emails to be sent. Do not alter the requirements, providers, campaign, inbox classifications, exclusions, dates, or schedule. Complete every preflight and canary gate before bulk creation. Stop and report any mismatch instead of guessing.

The remainder of this file is the complete task specification. No additional prompt is required.

## Objective and authorization

Create automatic Smartlead SmartDelivery deliverability tests that cover every eligible inbox in the account exactly once while preserving domain and category boundaries.

The user explicitly authorizes:

- Creating the tests described here through the SmartDelivery API.
- Scheduling the tests to send real seed-list emails on Saturdays and Sundays.
- Using paused helper campaign `3806282` and its sequence-1 mapping `10217009` as the copy/source campaign.
- Using both available receiving providers: G Suite (`20`) and Office365 (`21`).
- Applying a 45-minute interval between test emails.

The user does **not** authorize modifying, deleting, pausing, or stopping unrelated campaigns, inboxes, or pre-existing tests. A newly created test may be stopped only if its verified configuration differs from this specification and it has not already completed. Never delete a test.

## Non-negotiable requirements

1. Fetch and check all Smartlead inboxes at execution time.
2. Confirm campaign `3806282` contains every eligible inbox and excludes exactly the three prohibited inboxes before creating anything.
3. Exclude every inbox carrying the exact tag `[Don't use] Sales Inbox AEs`.
4. Classify remaining inboxes using exact tag names:
   - Exact tag `A` → category A.
   - Exact tag `B` → category B.
   - Neither exact tag → category Other.
   - An inbox with both A and B is an error; stop.
5. Keep domains atomic: all eligible inboxes from one domain must be in the same test. Never split a domain between tests.
6. Keep categories isolated: A only with A, B only with B, and Other only with Other.
7. A test may contain at most 10 inboxes. Target 9–10 inboxes, with the one approved B-category exception of 8 inboxes.
8. Every eligible inbox must appear in exactly one test. Excluded inboxes must appear in zero tests.
9. Use both provider IDs `[20, 21]` for every test. Do not remove, alternate, or otherwise change providers.
10. Throttle sends at one email every 45 minutes:
    - `all_email_sent_without_time_gap: false`
    - `min_time_btwn_emails: 45`
    - `min_time_unit: "minutes"`
11. Every test must run only on Saturday and Sunday. No weekday send is permitted.
12. Use timezone `America/New_York` and start time `09:00`.
13. Start Saturday, August 15, 2026 at 9:00 AM EDT.
14. End Monday, August 31, 2026 at 11:59:59.999 PM EDT. Because only weekend days are enabled, the last actual run should be Sunday, August 30.
15. Use the exact naming scheme described below.
16. Create and verify one canary test before creating the remaining tests.
17. Make creation idempotent and stop on the first unresolved error or discrepancy.

## Important clarification about the 45-minute interval

The 45-minute value controls **pacing**, not the number of messages an inbox sends. There is no verified SmartDelivery setting that directly caps test messages per sender inbox.

The user initially asked for a maximum of 15 emails per inbox, then explicitly clarified: **do not change providers; set the interval to 45 minutes and leave everything else unchanged.** Honor that final decision. Do not attempt to enforce a quantity cap by removing a provider, duplicating inboxes, changing groups, or changing the weekend schedule.

### Authorized helper campaign after two failed canaries

The first canary attempt used campaign `3620482`, sequence-1 mapping `9544032`, and returned HTTP 400: `No leads available for the selected or lower sequence`. A second authorized attempt used sequence-2 mapping `9544033` and returned the same response. Exact-name reconciliation confirmed that neither attempt created a canary.

Read-only investigation found that campaign `3620482` had no eligible lead for any email step: leads that stopped at steps 1–5 were all completed, and all 567 active leads had already received step 6 and were waiting on the final manual step. No further mapping from that campaign should be attempted.

The user created paused helper campaign `3806282`, named `Deliverability test campaign | DO NOT USE`, specifically to resolve this prerequisite. It has:

- Status `PAUSED`.
- One lead with status `STARTED` and no sequence sent.
- Exactly 504 attached inboxes, matching the eligible manifest set.
- Exactly the three prohibited inboxes absent.
- Six email sequence variants that match campaign `3620482` exactly.
- Sequence-1 mapping ID `10217009`.

Use campaign `3806282` and mapping `10217009` for the new canary and all 55 tests. Do not retry either old mapping, do not add or modify leads, and do not alter campaigns `3620482` or `3806282`. Preserve both failed entries in `creation-log.jsonl` and append the helper-campaign attempt.

These are real sends to SmartDelivery seed addresses. Treat their volume as additional mailbox/provider activity; do not assume a normal campaign or warmup limit will throttle SmartDelivery.

SmartDelivery uses the selected campaign and sequence as copy/source configuration. Do not add seed recipients as campaign leads and do not call any lead-creation endpoint. Use SmartDelivery reports—not campaign “Emails Sent” analytics—as the source of truth for execution reconciliation.

A completed test already in this account provides the current reference behavior:

- SmartDelivery test ID: `508595`
- Name: `A Inboxes spam test`
- Campaign: `3570933`
- Providers: G Suite and Office365
- Sender inboxes: 10
- Delivered seed messages: 137 total
- Distribution: 13 or 14 messages per sender inbox
- Provider result split: 80 G Suite and 57 Office365 messages

Leave test `508595` untouched. With the same provider pool, groups containing fewer than 10 inboxes may send more messages per inbox. The 45-minute interval keeps those sends spread through the day. At 137 total messages, an 8-inbox group would take approximately 12 hours 45 minutes at the longest sender queue, still less than the 24-hour gap between daily runs.

## Known-good inventory snapshot

The following was verified live on August 14, 2026. Re-fetch it before execution; do not blindly trust the snapshot.

- Total connected Smartlead inboxes: **507**
- Inbox IDs attached to helper campaign `3806282`: exactly **504** IDs
- Missing from helper campaign: exactly the **3 approved exclusions**
- Extra in campaign: **0**
- All 507 had successful SMTP and IMAP connections and type `GMAIL`
- Excluded by `[Don't use] Sales Inbox AEs`: **3**
- Eligible after exclusion: **504**
- No inbox had both A and B tags
- No domain crossed category boundaries
- No domain contained more than 10 eligible inboxes

Expected eligible distribution:

| Category | Inboxes | Domains | Domain sizes | Required tests |
|---|---:|---:|---|---:|
| A | 126 | 42 | 42 domains × 3 inboxes | 14 tests × 9 |
| B | 206 | 69 | 68 domains × 3; 1 domain × 2 | 22 tests × 9; 1 test × 8 |
| Other | 172 | 168 | 166 domains × 1; 2 domains × 3 | 18 tests × 9–10 |
| **Total** | **504** | **279** | — | **55 tests** |

The expected count is 55 rather than merely “around 50” because domain blocks cannot be split.

The three expected exclusions are:

- `franco.pereyra@gonearstaffing.com`
- `franco.pereyra@gonearremote.com`
- `franco.pereyra@gostaffingnear.com`

All three were in category Other before exclusion. Exclusion must be based on the exact tag, with the explicit addresses used as a cross-check. Stop if the tag/address relationship has changed.

## Dates and scheduler values

Use these exact values:

| Meaning | Local value | API value |
|---|---|---|
| Timezone | America/New_York | `America/New_York` |
| Enabled days | Sunday and Saturday | `[0, 6]` |
| Start time | 2026-08-15 09:00:00 EDT | `2026-08-15T13:00:00.000Z` |
| End time | 2026-08-31 23:59:59.999 EDT | `2026-09-01T03:59:59.999Z` |
| Repeat interval | Daily, constrained by enabled days | `every_days: 1` |
| Send throttle | One message every 45 minutes | `45` + `minutes` |

For SmartDelivery's scheduler, `0` is Sunday and `6` is Saturday.

Before any creation, compare the current time with the start timestamp. If the start time has already passed, **do not create tests with a past start time**. Stop and ask the user for a revised start date. Never silently move the schedule.

## Test names and ranges

Use these exact category labels:

- `A Inb`
- `B Inb`
- `Other Inb`

Use this exact format:

```text
{category} Inb | Test {category-local test number} | Inb {category-local inclusive lower}-{category-local inclusive upper}
```

Rules:

- Test numbering restarts at 1 for each category.
- Inbox ranges are cumulative within that category.
- Use a plain hyphen with no spaces inside the range.
- The range must equal the actual number of sender inboxes in that test.

Examples and expected endpoints:

- `A Inb | Test 1 | Inb 1-9`
- `A Inb | Test 14 | Inb 118-126`
- `B Inb | Test 1 | Inb 1-9`
- `B Inb | Test 22 | Inb 190-198`
- `B Inb | Test 23 | Inb 199-206` — the approved 8-inbox exception
- `Other Inb | Test 1 | Inb 1-10`
- `Other Inb | Test 10 | Inb 91-100`
- `Other Inb | Test 11 | Inb 101-109`
- `Other Inb | Test 18 | Inb 164-172`

## Deterministic grouping algorithm

The manifest must be reproducible.

### Normalize and classify

1. Lowercase and trim every `from_email`.
2. Extract the domain as the substring after the final `@`; lowercase it.
3. Read tag names from `tags[].tag_name` and compare exact names case-insensitively.
4. Exclude `[Don't use] Sales Inbox AEs` before category packing.
5. Assign A, B, or Other as defined above.
6. Sort inboxes inside each domain lexicographically by email.
7. Sort domains lexicographically unless the packing rule below explicitly moves a block.

### Category A

- Confirm there are 42 domain blocks of size 3.
- Take domains in lexicographic order, three domains per test.
- This yields 14 tests of 9 inboxes.

### Category B

- Confirm there are 68 domain blocks of size 3 and one block of size 2.
- Reserve the size-2 block and the final two lexicographically sorted size-3 blocks for the last test: `2 + 3 + 3 = 8`.
- Pack the remaining 66 size-3 blocks three domains per test.
- This yields 22 tests of 9 followed by one test of 8.
- The final test is `B Inb | Test 23 | Inb 199-206`.

### Category Other

- Confirm there are 166 size-1 blocks and two size-3 blocks.
- Use target capacities of ten tests with 10 inboxes followed by eight tests with 9 inboxes:

```text
[10,10,10,10,10,10,10,10,10,10,9,9,9,9,9,9,9,9]
```

- Sort domain blocks by descending size, then lexicographically by domain.
- Assign each whole block to the first bin with enough remaining capacity.
- Then flatten each bin in domain order and email order.
- Every target bin must be filled exactly. This yields 172 inboxes across 18 tests.

### Manifest validation invariants

Fail before any API write unless all are true:

- Exactly 504 eligible unique email addresses and account IDs.
- Exactly 55 test groups.
- Category counts: A 126, B 206, Other 172.
- Test counts: A 14, B 23, Other 18.
- Every group has 9–10 inboxes except exactly one B group with 8.
- No group exceeds 10.
- No test contains more than one category.
- Every domain appears in exactly one group.
- Every eligible inbox appears exactly once across the manifest.
- Every excluded inbox appears zero times.
- Every manifest inbox belongs to campaign `3806282`.
- The campaign account-ID set exactly equals the eligible manifest account-ID set.
- Names are unique and their stated ranges match group sizes.

## Workspace and authentication

Project root:

```text
/Users/gastonmurillo/Documents/Near Automations/Near-AI-Agent
```

The API key is available as `SMARTLEAD_API_KEY` in the project `.env`. Never print, log, or place the API key in an artifact. Use `curl`; Python `requests` and `urllib` have returned Cloudflare 403 responses in this environment.

An existing read-only helper is available:

```text
/Users/gastonmurillo/Documents/Near Automations/Near-AI-Agent/.agents/skills/smartlead-campaign-creator/scripts/list_inboxes.py
```

Useful cross-check commands:

```bash
python3 .agents/skills/smartlead-campaign-creator/scripts/list_inboxes.py --campaign 3806282
python3 .agents/skills/smartlead-campaign-creator/scripts/list_inboxes.py --campaign 3806282 --tags
```

The helper prints one line per inbox as:

```text
id | from_email | from_name | comma-separated tags
```

For programmatic grouping, fetch JSON directly with `curl` rather than parsing the display output.

## Relevant APIs

### Core Smartlead API

Base URL:

```text
https://server.smartlead.ai/api/v1
```

Authentication is the query parameter `?api_key=$SMARTLEAD_API_KEY`.

Read endpoints:

```text
GET /email-accounts/?offset={offset}&limit=100
GET /campaigns/3806282
GET /campaigns/3806282/email-accounts
GET /campaigns/3806282/sequences
GET /campaigns/3806282/leads?offset=0&limit=10
```

Paginate `/email-accounts/` until a page contains fewer than 100 records. Build the eligible set by removing the three exactly tagged exclusions. Compare that eligible set against the set returned for campaign `3806282`; they must be identical.

Expected helper state: campaign `3806282` is `PAUSED`, contains exactly one `STARTED` lead, and contains sequence-1 mapping ID `10217009`. Re-read and verify all three facts before creation.

### SmartDelivery API

Base URL:

```text
https://smartdelivery.smartlead.ai/api/v1
```

Read endpoints:

```text
GET  /spam-test/seed/providers
POST /spam-test/report                         body: {}
GET  /spam-test/{spamTestId}
GET  /spam-test/report/{spamTestId}/sender-accounts
GET  /spam-test/report/{spamTestId}/schedule-history
GET  /spam-test/report/{spamTestId}/sender-account-wise
POST /spam-test/report/{spamTestId}/providerwise   body: {}
```

Creation endpoint:

```text
POST /spam-test/schedule
```

Emergency stop for a newly created, misconfigured test only:

```text
PUT /spam-test/{spamTestId}/stop
```

Official API documentation:

- https://api.smartlead.ai/api-reference/smart-delivery/list-tests
- https://api.smartlead.ai/api-reference/smart-delivery/test-details
- https://api.smartlead.ai/api-reference/smart-delivery/sender-report
- https://helpcenter.smartlead.ai/en/articles/237-how-to-run-an-automatic-deliverability-test-using-smartdelivery
- https://helpcenter.smartlead.ai/en/articles/240-what-is-sending-throttling-in-smartdelivery

The public creation endpoint exists, but Smartlead's published request-body documentation is incomplete. Safe validation probing previously confirmed that the public endpoint recognizes:

- `test_name`
- `provider_ids` (plural)
- `sender_accounts`
- `scheduler_cron_value.days: [0,6]`

The staged UI endpoints under `/api/spam-test/...` without `/v1` require an authenticated Smartlead browser session and do not accept the API key alone. Use the public `/api/v1/spam-test/schedule` endpoint for creation.

## Creation payload

Create each test with the following shape, substituting only the exact manifest name, matching description, and sender email list:

```json
{
  "test_name": "A Inb | Test 1 | Inb 1-9",
  "description": "Weekend-only SmartDelivery coverage test; category A; inboxes 1-9",
  "spam_filters": ["spam_assassin"],
  "link_checker": true,
  "all_email_sent_without_time_gap": false,
  "min_time_btwn_emails": 45,
  "min_time_unit": "minutes",
  "campaign_id": 3806282,
  "sequence_mapping_id": 10217009,
  "provider_ids": [20, 21],
  "sender_accounts": [
    "sender1@example.com",
    "sender2@example.com"
  ],
  "is_warmup": false,
  "schedule_start_time": "2026-08-15T13:00:00.000Z",
  "test_end_date": "2026-09-01T03:59:59.999Z",
  "every_days": 1,
  "scheduler_cron_value": {
    "tz": "America/New_York",
    "days": [0, 6],
    "startHour": "09:00"
  }
}
```

Important field behavior:

- Creation uses `provider_ids`; test details may return `provider_id`.
- The SmartDelivery field is spelled `min_time_btwn_emails`.
- `sender_accounts` contains sender email strings, not account IDs.
- `test_with_sl_account` was rejected as an unsupported public creation field; omit it.
- Do not add a weekday-only toggle or replace `[0,6]` with an empty array. In the current UI implementation, an empty day array can mean all days rather than weekends only.

## Execution procedure

### Phase 1 — Read-only preflight

1. Load the API key without printing it.
2. Fetch all email accounts with pagination.
3. Fetch all helper campaign `3806282` accounts.
4. Confirm the helper campaign account-ID set exactly equals the 504-account eligible set; the only all-account IDs absent must be the three approved exclusions.
5. Confirm every account has successful SMTP and IMAP status.
6. Confirm helper campaign `3806282` remains `PAUSED`.
7. Fetch helper campaign leads and confirm there is exactly one lead with status `STARTED`.
8. Fetch campaign sequences and confirm mapping `10217009` exists and is sequence number 1.
9. Fetch SmartDelivery providers and confirm:
   - `20` is G Suite.
   - `21` is Office365.
10. Classify, exclude, group, and validate the manifest.
11. List existing SmartDelivery tests and check all 55 intended names for collisions.
12. Confirm the fixed start timestamp is still in the future.

If helper campaign `3806282` differs from the eligible 504-inbox set, stop and report the missing/extra addresses and IDs. Do not silently alter the manifest or campaign.

### Phase 2 — Persist the dry-run manifest

Create this directory:

```text
output/smartdelivery-tests-2026-08/
```

Before any API write, save:

```text
output/smartdelivery-tests-2026-08/manifest.json
output/smartdelivery-tests-2026-08/manifest.csv
```

Each manifest row/object must contain:

- Test name
- Category
- Category-local test number
- Inclusive lower and upper range
- Inbox count
- Ordered inbox emails
- Ordered inbox IDs
- Ordered domains
- Campaign ID
- Sequence mapping ID
- Provider IDs
- Timezone and enabled days
- Local/API start and end timestamps
- 45-minute throttle fields

Print a concise summary with counts and validation results. Do not print credentials or SMTP/IMAP passwords.

### Phase 3 — Idempotency and collision handling

Before each POST:

1. Refresh the SmartDelivery test list.
2. Match by exact test name.
3. If absent, create it once.
4. If an API request times out or returns an ambiguous 5xx response, do **not** retry blindly. Refresh the list and determine whether the test was created.
5. If the exact name already exists, read its details and sender accounts:
   - Skip it only if every observable field and sender email exactly matches the manifest.
   - Confirm the weekend schedule through the creation response or authenticated UI/session before treating it as a match.
   - If anything differs, stop. Do not overwrite, stop, or delete a pre-existing test.

Record every attempted creation and result in:

```text
output/smartdelivery-tests-2026-08/creation-log.jsonl
```

Each log entry should include timestamp, test name, request fingerprint excluding secrets, HTTP status, returned test ID, verification status, and any error.

### Phase 4 — Canary

Use the first manifest entry as the canary:

```text
A Inb | Test 1 | Inb 1-9
```

1. POST the canary once.
2. Capture its returned SmartDelivery test ID.
3. Read it back through:
   - `/spam-test/{id}`
   - `/spam-test/report/{id}/sender-accounts`
4. Verify exact name, type automatic/auto, campaign, sequence, providers, nine sender emails, SpamAssassin, link checker, 45-minute throttle, start timestamp, and end timestamp.
5. Verify the scheduler is exactly `America/New_York`, start hour `09:00`, and days `[0,6]`.
6. Re-fetch helper campaign `3806282` and its lead after the canary. Confirm the campaign remains `PAUSED` and the lead remains `STARTED` before creating any remaining test. SmartDelivery must not mutate either one.

The public detail response observed previously did not echo `scheduler_cron_value`. Therefore:

- Prefer the creation response if it includes the scheduler.
- Otherwise use the existing signed-in Smartlead browser session or authenticated UI network response to verify the canary visually/semantically.
- Do not infer weekends merely because a UI toggle appears off.
- Do not create the remaining 54 tests unless Saturday/Sunday-only scheduling is positively verified.

If the newly created canary is wrong, stop it if possible before its first run, record what differed, and stop execution. Never mutate test `508595` or another pre-existing test.

### Phase 5 — Bulk creation

After the canary passes, create the remaining manifest entries sequentially. Sequential creation makes failures and idempotent recovery easier to audit.

After every creation:

1. Record the returned ID.
2. Read back test details.
3. Read back sender accounts.
4. Compare against the manifest.
5. Stop immediately on any mismatch.

Do not retry 4xx validation errors. For 429 responses, wait according to `Retry-After` when present and use bounded exponential backoff. For ambiguous timeouts/5xx responses, reconcile by exact name before deciding whether another POST is safe.

### Phase 6 — Final reconciliation

After all intended tests exist, re-list and verify them as one set.

Required final assertions:

- Exactly 55 intended names exist once each.
- 14 A tests, 23 B tests, and 18 Other tests.
- Exactly 504 unique eligible sender inboxes across those tests.
- Every eligible inbox occurs once.
- The three excluded inboxes occur zero times.
- Every domain occurs in one test only.
- No test mixes categories.
- No test exceeds 10 senders.
- Exactly one test has 8 senders and it is the final B test.
- All other tests have 9 or 10 senders.
- Campaign is `3806282` everywhere.
- Sequence mapping is `10217009` everywhere.
- Providers are exactly `[20,21]` everywhere.
- Throttle is exactly 45 minutes everywhere.
- Start and end timestamps are exact everywhere.
- Timezone/start hour are exact everywhere.
- Enabled days are exactly `[0,6]` everywhere; no weekday is enabled.
- No unrelated test was changed.

Write the final report to:

```text
output/smartdelivery-tests-2026-08/final-reconciliation.md
```

The report must include:

- Overall pass/fail
- Test IDs and names
- Counts by category
- Total unique inboxes and domains
- Exclusions confirmed
- Schedule confirmation method
- Any skipped idempotent matches
- Any errors/retries
- A clear statement that no weekday is configured

## Stop conditions

Stop without bulk creation and report the exact evidence if any of these occur:

- The current time is at or after the fixed start timestamp.
- Helper campaign `3806282` does not contain exactly the eligible 504-inbox set.
- Helper campaign `3806282` is no longer `PAUSED`.
- Its single lead is absent, duplicated, or no longer `STARTED` before the canary is created.
- The live inventory differs from 507 total or 504 eligible.
- Any expected exclusion is missing or an unexpected inbox carries the exclusion tag.
- An inbox has both A and B tags.
- A domain crosses categories.
- A domain contains more than 10 eligible inboxes.
- The deterministic packing cannot satisfy the approved sizes.
- Campaign sequence `10217009` is absent or is not sequence number 1.
- Provider IDs or names differ from the verified pair.
- A desired test name already exists with a different configuration.
- The API rejects or ignores `[0,6]`.
- Weekend-only scheduling cannot be positively verified.
- The API rejects the 45-minute throttle.
- Sender accounts returned after creation differ from the manifest.
- The helper campaign or its lead changes state during canary creation.
- Any operation would require changing a pre-existing test.

Do not improvise around these failures. Return a concise blocker report containing the endpoint, HTTP status/body with secrets removed, affected inboxes/tests, and the next user decision required.

## Definition of done

The task is complete only when:

1. The read-only inventory and campaign coverage preflight passes.
2. The deterministic 55-test manifest passes every invariant.
3. The canary is created and positively verified, including weekends only.
4. All 55 tests exist with the exact requested configuration.
5. Final reconciliation proves exact-once coverage of 504 eligible inboxes.
6. The three excluded inboxes are absent.
7. Both providers remain enabled for every test.
8. Every test uses a 45-minute sending interval.
9. Every test ends at the specified end-of-month timestamp.
10. The manifest, creation log, and reconciliation report are saved under `output/smartdelivery-tests-2026-08/`.
11. The user receives a concise summary with the output paths, created test IDs, and any caveats.
