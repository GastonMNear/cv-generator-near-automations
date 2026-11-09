# Clay to BigQuery via GitHub Actions

This bridge lets Clay send lead rows to GitHub Actions, then GitHub Actions writes them into:

`near-outbound-analytics.outbound.leads`

Why this shape: Clay can call a normal HTTP endpoint, while GitHub Actions can handle Google IAM/OAuth and use Application Default Credentials for BigQuery. The script uses BigQuery load jobs instead of streaming inserts so it works on BigQuery's free tier.

## Files

- `.github/workflows/clay-to-bigquery.yml` receives Clay's `repository_dispatch` event and authenticates to Google Cloud.
- `scripts/insert_clay_lead_to_bigquery.mjs` validates, normalizes, and inserts the row(s).
- `package.json` pins the BigQuery client dependency.

## BigQuery Table Schema

The script sends exactly these fields:

```sql
campaign_id STRING,
campaign_name STRING,
email STRING,
company_domain STRING,
company_name STRING,
prospect_title STRING,
employee_count STRING,
industry STRING,
role STRING,
job_country STRING,
open_job_title STRING
```

`employee_count` is treated as `STRING` because Clay/headcount data is often a range or formatted text. You can cast it later in analysis views if the source column becomes consistently numeric.

## One-Time Google Setup

1. In Google Cloud, create a service account for this bridge, for example:
   `github-clay-bq-writer@near-outbound-analytics.iam.gserviceaccount.com`
2. Grant the service account the minimum BigQuery permissions needed to stream into this table:
   - `roles/bigquery.dataEditor` on dataset `outbound`
   - `roles/bigquery.jobUser` on project `near-outbound-analytics`
3. Create a JSON key for that service account.
4. In GitHub, add a repository secret named `GCP_BQ_SERVICE_ACCOUNT_JSON` with the full minified JSON key.

Workload Identity Federation is cleaner long term because it avoids service account keys, but the JSON key route is the shortest path to get Clay flowing into BigQuery.

## One-Time GitHub Setup

1. Create a random shared secret, for example with:

   ```bash
   openssl rand -hex 32
   ```

2. Add it to GitHub repository secrets as:

   `CLAY_GITHUB_INGEST_SECRET`

3. Create a fine-grained GitHub token for Clay with:

   - Repository access: only this repository
   - Permissions: `Contents: Read and write`

GitHub requires write-level repository contents permission for the repository dispatch endpoint.

## Clay HTTP Request

In Clay, add an HTTP API enrichment/action with:

Method:

`POST`

URL:

`https://api.github.com/repos/GastonMNear/clay-leads-to-BQ/dispatches`

Headers:

```text
Accept: application/vnd.github+json
Authorization: Bearer YOUR_FINE_GRAINED_GITHUB_TOKEN
X-GitHub-Api-Version: 2026-03-10
Content-Type: application/json
```

Body:

```json
{
  "event_type": "clay_lead_to_bigquery",
  "client_payload": {
    "ingest_secret": "YOUR_CLAY_GITHUB_INGEST_SECRET",
    "lead": {
      "campaign_id": "{{campaign_id}}",
      "campaign_name": "{{campaign_name}}",
      "email": "{{email}}",
      "company_domain": "{{company_domain}}",
      "company_name": "{{company_name}}",
      "prospect_title": "{{prospect_title}}",
      "employee_count": "{{employee_count}}",
      "industry": "{{industry}}",
      "role": "{{role}}",
      "job_country": "{{job_country}}",
      "open_job_title": "{{open_job_title}}"
    }
  }
}
```

Use the actual Clay column tokens in place of the `{{...}}` placeholders.

Important: keep the lead fields nested under `client_payload.lead`. GitHub limits `client_payload` to 10 top-level properties, and the lead has 11 fields.

## Test Before Turning It On

1. In GitHub, open Actions > `Clay lead to BigQuery` > Run workflow.
2. Use this test payload:

   ```json
   {
     "lead": {
       "campaign_id": "test-campaign",
       "campaign_name": "Codex test",
       "email": "test@example.com",
       "company_domain": "example.com",
       "company_name": "Example Inc",
       "prospect_title": "VP Talent",
       "employee_count": "100",
       "industry": "Software",
       "role": "Hiring Manager",
       "job_country": "US",
       "open_job_title": "Senior Accountant"
     }
   }
   ```

3. Confirm a row exists in BigQuery:

   ```sql
   SELECT *
   FROM `near-outbound-analytics.outbound.leads`
   WHERE email = 'test@example.com'
   ORDER BY campaign_id
   LIMIT 10;
   ```

4. Once the manual test works, test one Clay row.
5. After one Clay row works, enable the HTTP action for the whole Clay table/workflow.

## Batch Payload Option

If Clay sends multiple leads in one request, use `leads` instead of `lead`:

```json
{
  "event_type": "clay_lead_to_bigquery",
  "client_payload": {
    "ingest_secret": "YOUR_CLAY_GITHUB_INGEST_SECRET",
    "leads": [
      {
        "campaign_id": "123",
        "campaign_name": "US Open Jobs",
        "email": "person@example.com"
      }
    ]
  }
}
```

The script requires `email` and `campaign_id`; all other fields may be blank.
