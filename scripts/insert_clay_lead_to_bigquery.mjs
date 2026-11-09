import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const PROJECT_ID = process.env.BIGQUERY_PROJECT_ID || "near-outbound-analytics";
const DATASET_ID = process.env.BIGQUERY_DATASET_ID || "outbound";
const TABLE_ID = process.env.BIGQUERY_TABLE_ID || "leads";
const DRY_RUN = process.env.DRY_RUN === "true";

const BIGQUERY_FIELDS = [
  "campaign_id",
  "campaign_name",
  "email",
  "company_domain",
  "company_name",
  "prospect_title",
  "employee_count",
  "industry",
  "role",
  "job_country",
  "open_job_title",
];

const FIELD_ALIASES = {
  campaign_id: ["campaign_id", "Campaign ID", "Campaign Id", "campaign id"],
  campaign_name: ["campaign_name", "Campaign Name", "campaign name"],
  email: ["email", "Email", "Work Email", "work_email", "work email"],
  company_domain: [
    "company_domain",
    "Company Domain",
    "company domain",
    "Domain",
    "domain",
  ],
  company_name: ["company_name", "Company Name", "company name"],
  prospect_title: [
    "prospect_title",
    "Prospect Title",
    "prospect title",
    "Title",
    "title",
    "Job Title",
  ],
  employee_count: [
    "employee_count",
    "Employee Count",
    "employee count",
    "Headcount",
    "headcount",
  ],
  industry: ["industry", "Industry"],
  role: ["role", "Role", "Persona", "persona"],
  job_country: ["job_country", "Job Country", "job country", "Country", "country"],
  open_job_title: [
    "open_job_title",
    "Open Job Title",
    "open job title",
    "Open Role",
    "open role",
  ],
};

function readJsonFromEnv(name) {
  if (!process.env[name]) return null;

  try {
    return JSON.parse(process.env[name]);
  } catch (error) {
    throw new Error(`${name} is not valid JSON: ${error.message}`);
  }
}

function readGithubEvent() {
  const manualPayload = readJsonFromEnv("MANUAL_PAYLOAD_JSON");
  if (manualPayload) return { name: process.env.GITHUB_EVENT_NAME, payload: manualPayload };

  if (!process.env.GITHUB_EVENT_PATH) return { name: null, payload: {} };

  const event = JSON.parse(fs.readFileSync(process.env.GITHUB_EVENT_PATH, "utf8"));
  const payload = event.client_payload || event.inputs?.payload_json || {};
  return {
    name: process.env.GITHUB_EVENT_NAME,
    payload: typeof payload === "string" ? JSON.parse(payload) : payload,
  };
}

function assertDispatchSecret(eventName, payload) {
  const expectedSecret = process.env.CLAY_GITHUB_INGEST_SECRET;
  if (!expectedSecret || eventName === "workflow_dispatch") return;

  if (payload.ingest_secret !== expectedSecret) {
    throw new Error("Invalid or missing Clay ingest secret.");
  }
}

function firstPresentValue(source, aliases) {
  for (const alias of aliases) {
    if (Object.hasOwn(source, alias) && source[alias] !== undefined) {
      return source[alias];
    }
  }

  return null;
}

function cleanValue(field, value) {
  if (value === null || value === undefined) return null;

  const text = String(value).trim();
  if (text === "") return null;

  if (field === "email") return text.toLowerCase();
  return text;
}

function normalizeLead(rawLead) {
  if (!rawLead || typeof rawLead !== "object" || Array.isArray(rawLead)) {
    throw new Error("Each lead must be a JSON object.");
  }

  const row = {};
  for (const field of BIGQUERY_FIELDS) {
    row[field] = cleanValue(field, firstPresentValue(rawLead, FIELD_ALIASES[field]));
  }

  if (!row.email) throw new Error("Lead is missing required field: email.");
  if (!row.campaign_id) throw new Error(`Lead ${row.email} is missing required field: campaign_id.`);

  return row;
}

function extractLeads(payload) {
  if (Array.isArray(payload.leads)) return payload.leads;
  if (payload.lead) return [payload.lead];

  const hasLeadField = BIGQUERY_FIELDS.some((field) =>
    Object.hasOwn(payload, field)
  );
  if (hasLeadField) return [payload];

  throw new Error("Payload must include either `lead`, `leads`, or lead fields.");
}

function insertIdFor(row) {
  return crypto
    .createHash("sha256")
    .update(`${row.campaign_id}|${row.email}|${row.open_job_title || ""}`)
    .digest("hex")
    .slice(0, 32);
}

function summarizeRows(rows) {
  return rows.map((row) => ({
    campaign_id: row.campaign_id,
    campaign_name: row.campaign_name,
    email: row.email,
    company_domain: row.company_domain,
  }));
}

async function insertRows(rows) {
  const { BigQuery } = await import("@google-cloud/bigquery");
  const bigquery = new BigQuery({ projectId: PROJECT_ID });
  const table = bigquery.dataset(DATASET_ID).table(TABLE_ID);

  const loadFilePath = path.join(
    os.tmpdir(),
    `clay-leads-${insertIdFor(rows[0])}.jsonl`
  );
  const contents = rows.map((row) => JSON.stringify(row)).join("\n") + "\n";

  fs.writeFileSync(loadFilePath, contents, "utf8");

  const [job] = await table.load(loadFilePath, {
    sourceFormat: "NEWLINE_DELIMITED_JSON",
    writeDisposition: "WRITE_APPEND",
  });

  console.log(`BigQuery load job ${job.id} completed.`);
}

async function main() {
  const { name: eventName, payload } = readGithubEvent();
  assertDispatchSecret(eventName, payload);

  const rows = extractLeads(payload).map(normalizeLead);
  console.log(`Prepared ${rows.length} lead row(s) for ${PROJECT_ID}.${DATASET_ID}.${TABLE_ID}`);
  console.log(JSON.stringify(summarizeRows(rows), null, 2));

  if (DRY_RUN) {
    console.log("DRY_RUN=true; skipping BigQuery insert.");
    return;
  }

  await insertRows(rows);
  console.log(`Inserted ${rows.length} row(s) into BigQuery.`);
}

main().catch((error) => {
  console.error(error.message);

  if (error.name === "PartialFailureError" && Array.isArray(error.errors)) {
    console.error(JSON.stringify(error.errors, null, 2));
  }

  process.exit(1);
});
