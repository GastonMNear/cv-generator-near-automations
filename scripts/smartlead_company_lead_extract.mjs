import fs from "node:fs/promises";
import path from "node:path";

const DEFAULT_COMPANIES = [
  "Ventrus Sciences",
  "Dolce Vita Stays",
  "Dataplatr",
  "Nancy Sandhu",
  "Allos",
  "Donde",
  "BizAcuity",
  "Premier Networx",
  "Voyage",
  "Advocates Beyond Borders",
  "InnReg",
];

const BASE_URL = process.env.SMARTLEAD_API_BASE_URL || "https://server.smartlead.ai/api/v1";
const PAGE_LIMIT = Number(process.env.SMARTLEAD_PAGE_LIMIT || 100);
const MAX_PAGES_PER_CAMPAIGN = Number(process.env.SMARTLEAD_MAX_PAGES_PER_CAMPAIGN || 1000);
const REQUEST_DELAY_MS = Number(process.env.SMARTLEAD_REQUEST_DELAY_MS || 400);
const RATE_LIMIT_WAIT_MS = Number(process.env.SMARTLEAD_RATE_LIMIT_WAIT_MS || 65000);
let lastRequestAt = 0;

const FREE_EMAIL_DOMAINS = new Set([
  "aol.com",
  "gmail.com",
  "googlemail.com",
  "hotmail.com",
  "icloud.com",
  "live.com",
  "me.com",
  "msn.com",
  "outlook.com",
  "proton.me",
  "protonmail.com",
  "yahoo.com",
  "ymail.com",
]);

function parseArgs(argv) {
  const args = {
    companies: DEFAULT_COMPANIES,
    campaignIds: null,
    outDir: "exports/smartlead-company-leads",
    envPath: ".env",
  };

  for (const arg of argv) {
    if (arg.startsWith("--companies=")) {
      args.companies = arg
        .slice("--companies=".length)
        .split(",")
        .map((value) => value.trim())
        .filter(Boolean);
    } else if (arg.startsWith("--campaign-ids=")) {
      args.campaignIds = new Set(
        arg
          .slice("--campaign-ids=".length)
          .split(",")
          .map((value) => value.trim())
          .filter(Boolean)
      );
    } else if (arg.startsWith("--out-dir=")) {
      args.outDir = arg.slice("--out-dir=".length);
    } else if (arg.startsWith("--env=")) {
      args.envPath = arg.slice("--env=".length);
    } else {
      throw new Error(`Unknown argument: ${arg}`);
    }
  }

  return args;
}

async function loadEnvFile(envPath) {
  let text;
  try {
    text = await fs.readFile(envPath, "utf8");
  } catch (error) {
    if (error.code === "ENOENT") return;
    throw error;
  }

  for (const rawLine of text.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#")) continue;
    const index = line.indexOf("=");
    if (index === -1) continue;
    const key = line.slice(0, index).trim();
    let value = line.slice(index + 1).trim();
    const first = value[0];
    const last = value[value.length - 1];
    if ((first === "\"" && last === "\"") || (first === "'" && last === "'")) {
      value = value.slice(1, -1);
    }
    if (!process.env[key]) process.env[key] = value;
  }
}

function normalizeText(value) {
  return String(value ?? "")
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/&/g, "and")
    .replace(/\b(inc|llc|ltd|limited|corp|corporation|co|company|plc|gmbh|sa|sarl|the)\b/g, " ")
    .replace(/[^a-z0-9]+/g, "");
}

function tokenParts(value) {
  return String(value ?? "")
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/&/g, " and ")
    .split(/[^a-z0-9]+/)
    .filter((token) => token && !["inc", "llc", "ltd", "limited", "corp", "corporation", "co", "company", "the"].includes(token));
}

function getByPath(object, paths) {
  for (const key of paths) {
    if (object && Object.prototype.hasOwnProperty.call(object, key) && object[key] !== null && object[key] !== undefined) {
      return object[key];
    }
  }
  return "";
}

function collectFieldValues(value, out = [], prefix = "") {
  if (!value || typeof value !== "object") return out;

  if (Array.isArray(value)) {
    value.forEach((item, index) => collectFieldValues(item, out, `${prefix}[${index}]`));
    return out;
  }

  for (const [key, nested] of Object.entries(value)) {
    const pathName = prefix ? `${prefix}.${key}` : key;
    const isCompanyLike = /company|organization|organisation|account|business/i.test(key);
    if (isCompanyLike && ["string", "number"].includes(typeof nested)) {
      out.push({ path: pathName, value: String(nested) });
    }
    if (nested && typeof nested === "object") collectFieldValues(nested, out, pathName);
  }

  return out;
}

function collectEmails(value, out = []) {
  if (!value || typeof value !== "object") return out;

  if (Array.isArray(value)) {
    for (const item of value) collectEmails(item, out);
    return out;
  }

  for (const [key, nested] of Object.entries(value)) {
    if (/email/i.test(key) && typeof nested === "string" && nested.includes("@")) out.push(nested.trim().toLowerCase());
    if (nested && typeof nested === "object") collectEmails(nested, out);
  }

  return out;
}

function emailDomain(email) {
  const match = String(email || "").toLowerCase().match(/@([^>\s]+)$/);
  if (!match) return "";
  return match[1].replace(/^[\[]|[\]]$/g, "");
}

function domainBase(domain) {
  const clean = String(domain || "").toLowerCase().replace(/^www\./, "");
  const parts = clean.split(".").filter(Boolean);
  if (parts.length < 2) return clean;
  const suffix2 = parts.slice(-2).join(".");
  if (["co.uk", "com.au", "com.br", "com.mx", "co.in"].includes(suffix2) && parts.length >= 3) {
    return parts[parts.length - 3];
  }
  return parts[parts.length - 2];
}

function companyVariableMatch(targetCompany, lead) {
  const targetNorm = normalizeText(targetCompany);
  const matches = [];

  for (const field of collectFieldValues(lead)) {
    const candidateNorm = normalizeText(field.value);
    if (!candidateNorm) continue;
    const exact = candidateNorm === targetNorm;
    const contains =
      targetNorm.length >= 5 &&
      candidateNorm.length >= 5 &&
      (candidateNorm.includes(targetNorm) || targetNorm.includes(candidateNorm));
    if (exact || contains) matches.push({ path: field.path, value: field.value });
  }

  return matches;
}

function emailDomainMatch(targetCompany, lead) {
  const targetNorm = normalizeText(targetCompany);
  const tokens = tokenParts(targetCompany);
  const firstDistinctiveToken = tokens.find((token) => token.length >= 5);
  const emails = [...new Set(collectEmails(lead))];
  const matches = [];

  for (const email of emails) {
    const domain = emailDomain(email);
    if (!domain || FREE_EMAIL_DOMAINS.has(domain)) continue;

    const base = normalizeText(domainBase(domain));
    if (!base) continue;

    const fullMatch = base === targetNorm || base.includes(targetNorm) || targetNorm.includes(base);
    const tokenMatch = firstDistinctiveToken && base.includes(normalizeText(firstDistinctiveToken));
    if (fullMatch || tokenMatch) matches.push({ email, domain });
  }

  return matches;
}

function matchLead(targetCompany, lead) {
  const companyMatches = companyVariableMatch(targetCompany, lead);
  const domainMatches = emailDomainMatch(targetCompany, lead);
  if (companyMatches.length === 0 && domainMatches.length === 0) return null;

  const methods = [];
  if (companyMatches.length > 0) methods.push("company_variable");
  if (domainMatches.length > 0) methods.push("email_domain");

  return {
    targetCompany,
    matchedBy: methods.join("+"),
    companyMatches,
    domainMatches,
  };
}

function appendApiKey(url, apiKey) {
  const parsed = new URL(url);
  parsed.searchParams.set("api_key", apiKey);
  return parsed;
}

async function sleep(ms) {
  await new Promise((resolve) => setTimeout(resolve, ms));
}

async function paceRequest() {
  const elapsed = Date.now() - lastRequestAt;
  if (elapsed < REQUEST_DELAY_MS) await sleep(REQUEST_DELAY_MS - elapsed);
  lastRequestAt = Date.now();
}

async function fetchJson(url, context, attempts = 5) {
  let lastError;
  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    await paceRequest();
    const response = await fetch(url);
    const text = await response.text();

    if (response.ok) {
      return text ? JSON.parse(text) : {};
    }

    const body = text.slice(0, 500);
    lastError = new Error(`${context}: HTTP ${response.status} ${body}`);
    if (![429, 500, 502, 503, 504].includes(response.status) || attempt === attempts) break;
    const retryAfter = Number(response.headers.get("retry-after"));
    const waitMs = response.status === 429
      ? Math.max(RATE_LIMIT_WAIT_MS, Number.isFinite(retryAfter) ? retryAfter * 1000 : 0)
      : 1000 * attempt;
    if (response.status === 429) {
      process.stderr.write(`${context}: rate limited, waiting ${Math.round(waitMs / 1000)}s before retry ${attempt + 1}/${attempts}\n`);
    }
    await sleep(waitMs);
  }
  throw lastError;
}

function listFromPayload(payload, keys) {
  if (Array.isArray(payload)) return payload;
  if (!payload || typeof payload !== "object") return [];
  for (const key of keys) {
    if (Array.isArray(payload[key])) return payload[key];
  }
  return [];
}

function totalFromPayload(payload) {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) return null;
  for (const key of ["total", "total_count", "total_leads", "count"]) {
    if (Number.isFinite(Number(payload[key]))) return Number(payload[key]);
  }
  return null;
}

function campaignId(campaign) {
  return getByPath(campaign, ["id", "campaign_id", "campaignId"]);
}

function campaignName(campaign) {
  return getByPath(campaign, ["name", "campaign_name", "campaignName"]) || "";
}

function leadIdentity(record) {
  const nestedLead = record?.lead && typeof record.lead === "object" ? record.lead : {};
  return (
    getByPath(record, ["campaign_lead_map_id", "id", "lead_id", "leadId", "email", "Email"]) ||
    getByPath(nestedLead, ["id", "lead_id", "leadId", "email", "Email"]) ||
    JSON.stringify(record).slice(0, 120)
  );
}

async function fetchCampaigns(apiKey) {
  const url = appendApiKey(`${BASE_URL}/campaigns`, apiKey);
  const payload = await fetchJson(url, "list campaigns");
  const campaigns = listFromPayload(payload, ["data", "campaigns", "results", "result"]);
  if (campaigns.length === 0) throw new Error("list campaigns returned no campaigns");
  return campaigns.filter((campaign) => campaignId(campaign));
}

async function fetchLeadPage(apiKey, campaign, pageMode, pageNumber) {
  const id = campaignId(campaign);
  const url = appendApiKey(`${BASE_URL}/campaigns/${id}/leads`, apiKey);
  url.searchParams.set("limit", String(PAGE_LIMIT));
  if (pageMode === "offset") {
    url.searchParams.set("offset", String((pageNumber - 1) * PAGE_LIMIT));
  } else {
    url.searchParams.set("page", String(pageNumber));
  }

  const payload = await fetchJson(url, `campaign ${id} leads page ${pageNumber}`);
  return {
    payload,
    leads: listFromPayload(payload, ["data", "leads", "results", "result"]),
    total: totalFromPayload(payload),
  };
}

async function fetchCampaignLeads(apiKey, campaign) {
  const id = campaignId(campaign);
  let pageMode = "offset";
  let pageNumber = 1;
  const leads = [];
  let previousPageSignature = "";

  while (pageNumber <= MAX_PAGES_PER_CAMPAIGN) {
    let page;
    try {
      page = await fetchLeadPage(apiKey, campaign, pageMode, pageNumber);
    } catch (error) {
      if (pageNumber === 1 && pageMode === "offset" && /HTTP (400|404)/.test(error.message)) {
        pageMode = "page";
        page = await fetchLeadPage(apiKey, campaign, pageMode, pageNumber);
      } else {
        throw error;
      }
    }

    const pageSignature = page.leads
      .slice(0, 3)
      .map((lead) => leadIdentity(lead))
      .join("|");
    if (pageNumber > 1 && pageSignature && pageSignature === previousPageSignature) {
      if (pageMode === "offset") {
        process.stderr.write(`Campaign ${id}: offset pagination repeated page data; retrying with page pagination\n`);
        pageMode = "page";
        pageNumber = 1;
        leads.length = 0;
        previousPageSignature = "";
        continue;
      }
      throw new Error(`campaign ${id} repeated page data while using ${pageMode} pagination`);
    }
    previousPageSignature = pageSignature;

    leads.push(...page.leads);
    if (pageNumber === 1 || pageNumber % 10 === 0) {
      const totalText = page.total === null ? "" : `/${page.total}`;
      process.stderr.write(`Campaign ${id}: fetched page ${pageNumber}, leads ${leads.length}${totalText}\n`);
    }
    if (page.leads.length < PAGE_LIMIT) break;
    if (page.total !== null && leads.length >= page.total) break;
    pageNumber += 1;
  }

  if (pageNumber > MAX_PAGES_PER_CAMPAIGN) {
    throw new Error(`campaign ${campaignId(campaign)} exceeded ${MAX_PAGES_PER_CAMPAIGN} pages`);
  }

  return leads;
}

function csvEscape(value) {
  if (value === null || value === undefined) return "";
  const text = typeof value === "string" ? value : JSON.stringify(value);
  if (/[",\n\r]/.test(text)) return `"${text.replaceAll('"', '""')}"`;
  return text;
}

function leadSummary(lead) {
  const nestedLead = lead?.lead && typeof lead.lead === "object" ? lead.lead : {};
  return {
    lead_id: getByPath(nestedLead, ["id", "lead_id", "leadId"]) || getByPath(lead, ["lead_id", "leadId", "id"]),
    email: getByPath(nestedLead, ["email", "Email", "lead_email"]) || getByPath(lead, ["email", "Email", "lead_email"]),
    first_name: getByPath(nestedLead, ["first_name", "firstName", "First Name"]) || getByPath(lead, ["first_name", "firstName", "First Name"]),
    last_name: getByPath(nestedLead, ["last_name", "lastName", "Last Name"]) || getByPath(lead, ["last_name", "lastName", "Last Name"]),
    title: getByPath(nestedLead, ["title", "job_title", "position", "Job Title"]) || getByPath(lead, ["title", "job_title", "position", "Job Title"]),
    company_name: getByPath(nestedLead, ["company_name", "company", "Company", "organization_name"]) || getByPath(lead, ["company_name", "company", "Company", "organization_name"]),
    website: getByPath(nestedLead, ["website", "company_website", "company_url", "url"]) || getByPath(lead, ["website", "company_website", "company_url", "url"]),
    status: getByPath(lead, ["status", "lead_status"]) || getByPath(nestedLead, ["status", "lead_status"]),
  };
}

function toCsv(rows) {
  const headers = [
    "target_company",
    "matched_by",
    "campaign_id",
    "campaign_name",
    "lead_id",
    "email",
    "first_name",
    "last_name",
    "title",
    "company_name",
    "website",
    "status",
    "company_match_evidence",
    "domain_match_evidence",
    "raw_lead_json",
  ];

  const lines = [headers.join(",")];
  for (const row of rows) {
    const summary = leadSummary(row.lead);
    lines.push(
      [
        row.match.targetCompany,
        row.match.matchedBy,
        campaignId(row.campaign),
        campaignName(row.campaign),
        summary.lead_id,
        summary.email,
        summary.first_name,
        summary.last_name,
        summary.title,
        summary.company_name,
        summary.website,
        summary.status,
        row.match.companyMatches,
        row.match.domainMatches,
        row.lead,
      ]
        .map(csvEscape)
        .join(",")
    );
  }
  return `${lines.join("\n")}\n`;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  await loadEnvFile(args.envPath);

  const apiKey = process.env.SMARTLEAD_API_KEY;
  if (!apiKey) throw new Error(`SMARTLEAD_API_KEY is missing. Add it to ${args.envPath} or the environment.`);

  const startedAt = new Date().toISOString();
  let campaigns = await fetchCampaigns(apiKey);
  if (args.campaignIds) {
    campaigns = campaigns.filter((campaign) => args.campaignIds.has(String(campaignId(campaign))));
  }
  const matches = [];
  const failures = [];

  for (const campaign of campaigns) {
    const id = campaignId(campaign);
    process.stderr.write(`Fetching campaign ${id} ${campaignName(campaign)}\n`);
    try {
      const leads = await fetchCampaignLeads(apiKey, campaign);
      for (const lead of leads) {
        for (const company of args.companies) {
          const match = matchLead(company, lead);
          if (match) matches.push({ campaign, lead, match });
        }
      }
    } catch (error) {
      failures.push({ campaign_id: id, campaign_name: campaignName(campaign), error: error.message });
    }
  }

  const stamp = startedAt.replace(/[:.]/g, "-");
  await fs.mkdir(args.outDir, { recursive: true });
  const jsonPath = path.join(args.outDir, `smartlead-company-leads-${stamp}.json`);
  const csvPath = path.join(args.outDir, `smartlead-company-leads-${stamp}.csv`);

  const output = {
    started_at: startedAt,
    finished_at: new Date().toISOString(),
    company_targets: args.companies,
    campaign_count: campaigns.length,
    match_count: matches.length,
    failure_count: failures.length,
    failures,
    matches,
  };

  await fs.writeFile(jsonPath, `${JSON.stringify(output, null, 2)}\n`, "utf8");
  await fs.writeFile(csvPath, toCsv(matches), "utf8");

  console.log(JSON.stringify({ jsonPath, csvPath, campaignCount: campaigns.length, matchCount: matches.length, failureCount: failures.length }, null, 2));
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
