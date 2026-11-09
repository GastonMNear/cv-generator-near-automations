#!/usr/bin/env node

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";

const ROOT = path.resolve(import.meta.dirname, "..");
const OUTPUT_DIR = path.join(ROOT, "output", "smartdelivery-tests-2026-08");
const CORE_BASE = "https://server.smartlead.ai/api/v1";
const DELIVERY_BASE = "https://smartdelivery.smartlead.ai/api/v1";
const CAMPAIGN_ID = 3806282;
const SEQUENCE_MAPPING_ID = 10217009;
const PROVIDER_IDS = [20, 21];
const START = "2026-08-15T13:00:00.000Z";
const END = "2026-08-17T03:59:59.999Z";
const EXCLUSION_TAG = "[Don't use] Sales Inbox AEs";
const EXPECTED_EXCLUSIONS = [
  "franco.pereyra@gonearremote.com",
  "franco.pereyra@gonearstaffing.com",
  "franco.pereyra@gostaffingnear.com",
];
const CATEGORY_CONFIG = {
  A: { label: "A Inb", counts: [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9] },
  B: { label: "B Inb", counts: [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 8] },
  Other: { label: "Other Inb", counts: [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 9, 9, 9, 9, 9, 9, 9, 9] },
};

function fail(message, details) {
  const suffix = details === undefined ? "" : `\n${JSON.stringify(details, null, 2)}`;
  throw new Error(`${message}${suffix}`);
}

function assert(condition, message, details) {
  if (!condition) fail(message, details);
}

function readApiKey() {
  const dotenv = fs.readFileSync(path.join(ROOT, ".env"), "utf8");
  const line = dotenv.split(/\r?\n/).find((entry) => entry.startsWith("SMARTLEAD_API_KEY="));
  assert(line, "SMARTLEAD_API_KEY is missing from .env");
  let value = line.slice("SMARTLEAD_API_KEY=".length).trim();
  if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
    value = value.slice(1, -1);
  }
  assert(value, "SMARTLEAD_API_KEY is empty in .env");
  return value;
}

const API_KEY = readApiKey();

function apiRequest(method, base, endpoint, body) {
  const separator = endpoint.includes("?") ? "&" : "?";
  const url = `${base}${endpoint}${separator}api_key=${encodeURIComponent(API_KEY)}`;
  const args = ["-sS", "--max-time", "60", "--request", method, url, "--write-out", "\n%{http_code}|%header{retry-after}"];
  if (body !== undefined) {
    args.push("--header", "content-type: application/json", "--data", JSON.stringify(body));
  }
  const result = spawnSync("curl", args, { encoding: "utf8", maxBuffer: 20 * 1024 * 1024 });
  if (result.error) fail(`curl failed for ${method} ${endpoint}`, result.error.message);
  const output = result.stdout ?? "";
  const splitAt = output.lastIndexOf("\n");
  const rawBody = splitAt === -1 ? output : output.slice(0, splitAt);
  const trailer = splitAt === -1 ? "0|" : output.slice(splitAt + 1);
  const [statusText, retryAfterText = ""] = trailer.split("|", 2);
  const status = Number(statusText);
  let json;
  try {
    json = rawBody ? JSON.parse(rawBody) : null;
  } catch {
    fail(`Non-JSON response from ${method} ${endpoint} (HTTP ${status})`, rawBody.slice(0, 1000));
  }
  if (status < 200 || status >= 300) {
    const error = new Error(`${method} ${endpoint} returned HTTP ${status}\n${JSON.stringify(json, null, 2)}`);
    error.httpStatus = status;
    error.responseBody = json;
    error.retryAfter = retryAfterText.trim();
    throw error;
  }
  return { status, json };
}

function coreGet(endpoint) {
  return apiRequest("GET", CORE_BASE, endpoint).json;
}

function deliveryRequest(method, endpoint, body) {
  return apiRequest(method, DELIVERY_BASE, endpoint, body);
}

function sleep(milliseconds) {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, milliseconds);
}

function deliveryRequestWithBackoff(method, endpoint, body, maxAttempts = 5) {
  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    try {
      return deliveryRequest(method, endpoint, body);
    } catch (error) {
      if (error.httpStatus !== 429 || attempt === maxAttempts) throw error;
      const retryAfterSeconds = Number(error.retryAfter);
      const waitMilliseconds = Number.isFinite(retryAfterSeconds) && retryAfterSeconds > 0
        ? retryAfterSeconds * 1000
        : (2 ** (attempt - 1)) * 1000;
      sleep(waitMilliseconds);
    }
  }
  fail(`Exhausted retries for ${method} ${endpoint}`);
}

function normalizeEmail(value) {
  return String(value ?? "").trim().toLowerCase();
}

function domainOf(email) {
  const at = email.lastIndexOf("@");
  assert(at > 0 && at < email.length - 1, "Invalid sender email", email);
  return email.slice(at + 1);
}

function tagNames(account) {
  return (account.tags ?? []).map((tag) => String(tag.tag_name ?? "").trim());
}

function hasTag(account, name) {
  const wanted = name.toLowerCase();
  return tagNames(account).some((tag) => tag.toLowerCase() === wanted);
}

function categoryOf(account) {
  const a = hasTag(account, "A");
  const b = hasTag(account, "B");
  assert(!(a && b), "Inbox has both A and B tags", {
    id: account.id,
    email: account.from_email,
    tags: tagNames(account),
  });
  return a ? "A" : b ? "B" : "Other";
}

function unique(values) {
  return [...new Set(values)];
}

function sameSet(left, right) {
  const a = [...new Set(left)].sort();
  const b = [...new Set(right)].sort();
  return a.length === b.length && a.every((value, index) => value === b[index]);
}

function fetchAllAccounts() {
  const accounts = [];
  for (let offset = 0; ; offset += 100) {
    const page = coreGet(`/email-accounts/?offset=${offset}&limit=100`);
    assert(Array.isArray(page), "Email-account endpoint did not return an array");
    accounts.push(...page);
    if (page.length < 100) break;
  }
  return accounts;
}

function findProviderPairs(value, output = []) {
  if (Array.isArray(value)) {
    for (const item of value) findProviderPairs(item, output);
  } else if (value && typeof value === "object") {
    if (value.provider_id !== undefined && value.provider_name !== undefined) {
      output.push({ id: Number(value.provider_id), name: String(value.provider_name) });
    }
    for (const nested of Object.values(value)) findProviderPairs(nested, output);
  }
  return output;
}

function buildDomainBlocks(accounts) {
  const domains = new Map();
  for (const account of accounts) {
    const email = normalizeEmail(account.from_email);
    const domain = domainOf(email);
    const category = categoryOf(account);
    if (!domains.has(domain)) domains.set(domain, { domain, category, accounts: [] });
    const block = domains.get(domain);
    assert(block.category === category, "Domain crosses category boundaries", {
      domain,
      categories: [block.category, category],
    });
    block.accounts.push({ ...account, email, domain, category });
  }
  for (const block of domains.values()) {
    block.accounts.sort((a, b) => a.email.localeCompare(b.email));
    assert(block.accounts.length <= 10, "Domain has more than 10 eligible inboxes", {
      domain: block.domain,
      count: block.accounts.length,
    });
  }
  return [...domains.values()];
}

function packManifest(accounts) {
  const blocks = buildDomainBlocks(accounts);
  const byCategory = Object.fromEntries(["A", "B", "Other"].map((category) => [
    category,
    blocks.filter((block) => block.category === category),
  ]));

  byCategory.A.sort((a, b) => a.domain.localeCompare(b.domain));
  assert(byCategory.A.length === 42 && byCategory.A.every((block) => block.accounts.length === 3),
    "Category A domain distribution differs", byCategory.A.map((block) => [block.domain, block.accounts.length]));
  const aGroups = [];
  for (let index = 0; index < byCategory.A.length; index += 3) aGroups.push(byCategory.A.slice(index, index + 3));

  byCategory.B.sort((a, b) => a.domain.localeCompare(b.domain));
  const bTwo = byCategory.B.filter((block) => block.accounts.length === 2);
  const bThree = byCategory.B.filter((block) => block.accounts.length === 3);
  assert(byCategory.B.length === 69 && bTwo.length === 1 && bThree.length === 68,
    "Category B domain distribution differs", byCategory.B.map((block) => [block.domain, block.accounts.length]));
  const reservedThree = bThree.slice(-2);
  const remainingThree = bThree.slice(0, -2);
  const bGroups = [];
  for (let index = 0; index < remainingThree.length; index += 3) bGroups.push(remainingThree.slice(index, index + 3));
  bGroups.push([...bTwo, ...reservedThree].sort((a, b) => a.domain.localeCompare(b.domain)));

  const otherSizes = byCategory.Other.map((block) => block.accounts.length).sort((a, b) => a - b);
  assert(byCategory.Other.length === 168 && otherSizes.filter((size) => size === 1).length === 166 && otherSizes.filter((size) => size === 3).length === 2,
    "Category Other domain distribution differs", byCategory.Other.map((block) => [block.domain, block.accounts.length]));
  const otherTargets = CATEGORY_CONFIG.Other.counts;
  const otherBins = otherTargets.map((capacity) => ({ capacity, blocks: [] }));
  const orderedOther = [...byCategory.Other].sort((a, b) => b.accounts.length - a.accounts.length || a.domain.localeCompare(b.domain));
  for (const block of orderedOther) {
    const bin = otherBins.find((candidate) => candidate.capacity - candidate.blocks.reduce((sum, item) => sum + item.accounts.length, 0) >= block.accounts.length);
    assert(bin, "Category Other first-fit packing failed", { domain: block.domain, size: block.accounts.length });
    bin.blocks.push(block);
  }
  for (const bin of otherBins) {
    const count = bin.blocks.reduce((sum, block) => sum + block.accounts.length, 0);
    assert(count === bin.capacity, "Category Other bin did not fill exactly", { capacity: bin.capacity, count });
    bin.blocks.sort((a, b) => a.domain.localeCompare(b.domain));
  }
  const otherGroups = otherBins.map((bin) => bin.blocks);

  const categoryGroups = { A: aGroups, B: bGroups, Other: otherGroups };
  const manifest = [];
  for (const category of ["A", "B", "Other"]) {
    let lower = 1;
    categoryGroups[category].forEach((groupBlocks, index) => {
      const orderedAccounts = groupBlocks.flatMap((block) => block.accounts);
      const count = orderedAccounts.length;
      const upper = lower + count - 1;
      const label = CATEGORY_CONFIG[category].label;
      manifest.push({
        test_name: `${label} | Test ${index + 1} | Inb ${lower}-${upper}`,
        description: `Weekend-only SmartDelivery coverage test; category ${category}; inboxes ${lower}-${upper}`,
        category,
        category_local_test_number: index + 1,
        inclusive_lower: lower,
        inclusive_upper: upper,
        inbox_count: count,
        ordered_inbox_emails: orderedAccounts.map((account) => account.email),
        ordered_inbox_ids: orderedAccounts.map((account) => Number(account.id)),
        ordered_domains: groupBlocks.map((block) => block.domain),
        campaign_id: CAMPAIGN_ID,
        sequence_mapping_id: SEQUENCE_MAPPING_ID,
        provider_ids: PROVIDER_IDS,
        timezone: "America/New_York",
        enabled_days: [0, 6],
        local_start: "2026-08-15 09:00:00 EDT",
        api_start: START,
        local_end: "2026-08-16 23:59:59.999 EDT",
        api_end: END,
        every_days: 1,
        start_hour: "09:00",
        all_email_sent_without_time_gap: false,
        min_time_btwn_emails: 45,
        min_time_unit: "minutes",
      });
      lower = upper + 1;
    });
  }
  return { manifest, blocks };
}

function validateManifest(manifest, eligible, excluded) {
  assert(manifest.length === 55, "Manifest test count differs", manifest.length);
  const categoryCounts = Object.fromEntries(["A", "B", "Other"].map((category) => [category,
    manifest.filter((test) => test.category === category).reduce((sum, test) => sum + test.inbox_count, 0)]));
  const testCounts = Object.fromEntries(["A", "B", "Other"].map((category) => [category,
    manifest.filter((test) => test.category === category).length]));
  assert(JSON.stringify(categoryCounts) === JSON.stringify({ A: 126, B: 206, Other: 172 }), "Category counts differ", categoryCounts);
  assert(JSON.stringify(testCounts) === JSON.stringify({ A: 14, B: 23, Other: 18 }), "Test counts differ", testCounts);
  const allEmails = manifest.flatMap((test) => test.ordered_inbox_emails);
  const allIds = manifest.flatMap((test) => test.ordered_inbox_ids);
  assert(allEmails.length === 504 && unique(allEmails).length === 504, "Manifest email exact-once invariant failed");
  assert(allIds.length === 504 && unique(allIds).length === 504, "Manifest ID exact-once invariant failed");
  assert(sameSet(allEmails, eligible.map((account) => normalizeEmail(account.from_email))), "Manifest emails differ from eligible emails");
  assert(sameSet(allIds, eligible.map((account) => Number(account.id))), "Manifest IDs differ from eligible IDs");
  assert(excluded.every((account) => !allEmails.includes(normalizeEmail(account.from_email))), "Excluded inbox appears in manifest");
  const eight = manifest.filter((test) => test.inbox_count === 8);
  assert(eight.length === 1 && eight[0].test_name === "B Inb | Test 23 | Inb 199-206", "Eight-inbox exception differs", eight.map((test) => test.test_name));
  assert(manifest.every((test) => test.inbox_count <= 10 && (test.inbox_count >= 9 || test === eight[0])), "Group-size invariant failed");
  assert(unique(manifest.map((test) => test.test_name)).length === 55, "Manifest names are not unique");
  assert(manifest.every((test) => test.inclusive_upper - test.inclusive_lower + 1 === test.inbox_count), "A manifest name range does not match its inbox count");
  const domainTests = new Map();
  for (const test of manifest) {
    for (const domain of test.ordered_domains) {
      if (!domainTests.has(domain)) domainTests.set(domain, []);
      domainTests.get(domain).push(test.test_name);
    }
  }
  const splitDomains = [...domainTests].filter(([, names]) => unique(names).length !== 1);
  assert(splitDomains.length === 0, "A domain was split across tests", splitDomains);
  assert(manifest[13].test_name === "A Inb | Test 14 | Inb 118-126", "A endpoint name differs", manifest[13].test_name);
  assert(manifest[36].test_name === "B Inb | Test 23 | Inb 199-206", "B endpoint name differs", manifest[36].test_name);
  assert(manifest[46].test_name === "Other Inb | Test 10 | Inb 91-100", "Other test 10 name differs", manifest[46].test_name);
  assert(manifest[47].test_name === "Other Inb | Test 11 | Inb 101-109", "Other test 11 name differs", manifest[47].test_name);
  assert(manifest[54].test_name === "Other Inb | Test 18 | Inb 164-172", "Other endpoint name differs", manifest[54].test_name);
  return { categoryCounts, testCounts, uniqueDomains: domainTests.size };
}

function csvCell(value) {
  const text = Array.isArray(value) ? JSON.stringify(value) : String(value);
  return `"${text.replaceAll('"', '""')}"`;
}

function writeManifest(manifest) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  fs.writeFileSync(path.join(OUTPUT_DIR, "manifest.json"), `${JSON.stringify(manifest, null, 2)}\n`);
  const headers = Object.keys(manifest[0]);
  const rows = [headers.map(csvCell).join(","), ...manifest.map((test) => headers.map((header) => csvCell(test[header])).join(","))];
  fs.writeFileSync(path.join(OUTPUT_DIR, "manifest.csv"), `${rows.join("\n")}\n`);
}

function listTests() {
  const response = deliveryRequestWithBackoff("POST", "/spam-test/report", {});
  assert(Array.isArray(response.json), "SmartDelivery report endpoint did not return an array");
  return response.json;
}

function leadRows(value) {
  if (Array.isArray(value)) return value;
  for (const key of ["data", "leads", "results"]) {
    if (Array.isArray(value?.[key])) return value[key];
  }
  fail("Campaign leads endpoint did not return a recognized lead collection", sanitize(value));
}

function verifyHelperState() {
  const campaign = coreGet(`/campaigns/${CAMPAIGN_ID}`);
  const leadsResponse = coreGet(`/campaigns/${CAMPAIGN_ID}/leads?offset=0&limit=10`);
  const leads = leadRows(leadsResponse);
  const campaignStatus = String(campaign?.status ?? "").trim().toUpperCase();
  assert(campaignStatus === "PAUSED", "Helper campaign is not PAUSED", {
    campaign_id: CAMPAIGN_ID,
    observed_status: campaign?.status ?? null,
  });
  assert(leads.length === 1, "Helper campaign does not contain exactly one lead", {
    campaign_id: CAMPAIGN_ID,
    observed_count: leads.length,
    lead_ids: leads.map((lead) => lead.id ?? lead.lead_id ?? null),
  });
  const leadStatus = String(leads[0]?.status ?? leads[0]?.lead_status ?? "").trim().toUpperCase();
  assert(leadStatus === "STARTED", "Helper campaign lead is not STARTED", {
    campaign_id: CAMPAIGN_ID,
    lead_id: leads[0]?.id ?? leads[0]?.lead_id ?? null,
    observed_status: leads[0]?.status ?? leads[0]?.lead_status ?? null,
  });
  return {
    campaign_id: CAMPAIGN_ID,
    campaign_status: campaignStatus,
    lead_count: leads.length,
    lead_id: leads[0]?.id ?? leads[0]?.lead_id ?? null,
    lead_status: leadStatus,
  };
}

function preflight({ persist = true, allowCollisions = false } = {}) {
  assert(Date.now() < Date.parse(START), "Fixed start timestamp has already passed", { now: new Date().toISOString(), start: START });
  const all = fetchAllAccounts();
  const helperState = verifyHelperState();
  const campaign = coreGet(`/campaigns/${CAMPAIGN_ID}/email-accounts`);
  const sequences = coreGet(`/campaigns/${CAMPAIGN_ID}/sequences`);
  const providersResponse = deliveryRequest("GET", "/spam-test/seed/providers").json;
  assert(Array.isArray(campaign), "Campaign email-account endpoint did not return an array");
  assert(Array.isArray(sequences), "Campaign sequence endpoint did not return an array");

  assert(all.length === 507 && unique(all.map((account) => Number(account.id))).length === 507 && unique(all.map((account) => normalizeEmail(account.from_email))).length === 507,
    "Connected-account inventory differs", { count: all.length });
  const unhealthy = all.filter((account) => account.is_smtp_success !== true || account.is_imap_success !== true || account.type !== "GMAIL");
  assert(unhealthy.length === 0, "An account failed SMTP/IMAP/type preflight", unhealthy.map((account) => ({ id: account.id, email: account.from_email, smtp: account.is_smtp_success, imap: account.is_imap_success, type: account.type })));
  const excluded = all.filter((account) => hasTag(account, EXCLUSION_TAG));
  assert(excluded.length === 3 && sameSet(excluded.map((account) => normalizeEmail(account.from_email)), EXPECTED_EXCLUSIONS),
    "Exclusion tag/address relationship differs", excluded.map((account) => ({ id: account.id, email: account.from_email, tags: tagNames(account) })));
  const eligible = all.filter((account) => !hasTag(account, EXCLUSION_TAG));
  assert(eligible.length === 504, "Eligible inbox count differs", eligible.length);
  assert(campaign.length === 504, "Campaign inbox count differs", campaign.length);
  assert(sameSet(campaign.map((account) => Number(account.id)), eligible.map((account) => Number(account.id))),
    "Campaign inbox set differs from the eligible account set", {
      missing: eligible.filter((account) => !campaign.some((candidate) => Number(candidate.id) === Number(account.id))).map((account) => ({ id: account.id, email: account.from_email })),
      extra: campaign.filter((account) => !eligible.some((candidate) => Number(candidate.id) === Number(account.id))).map((account) => ({ id: account.id, email: account.from_email })),
    });
  const selectedSequence = sequences.find((sequence) => Number(sequence.id) === SEQUENCE_MAPPING_ID);
  assert(selectedSequence, "Sequence mapping is absent", SEQUENCE_MAPPING_ID);
  assert(Number(selectedSequence.seq_number) === 1, "Selected mapping is not sequence number 1", {
    id: selectedSequence.id,
    seq_number: selectedSequence.seq_number,
  });
  const providers = findProviderPairs(providersResponse);
  const selectedProviders = providers.filter((provider) => PROVIDER_IDS.includes(provider.id)).sort((a, b) => a.id - b.id);
  assert(JSON.stringify(selectedProviders) === JSON.stringify([{ id: 20, name: "G Suite" }, { id: 21, name: "Office365" }]),
    "Provider IDs or names differ", selectedProviders);

  const { manifest } = packManifest(eligible);
  const summary = validateManifest(manifest, eligible, excluded);
  const campaignIds = new Set(campaign.map((account) => Number(account.id)));
  assert(manifest.every((test) => test.ordered_inbox_ids.every((id) => campaignIds.has(id))), "A manifest inbox is absent from the campaign");
  const intendedNames = new Set(manifest.map((test) => test.test_name));
  const collisions = listTests().filter((test) => intendedNames.has(test.test_name ?? test.name));
  const historicalStoppedCanary = collisions.filter((test) => testIdOf(test) === 509065
    && (test.test_name ?? test.name) === manifest[0].test_name
    && String(test.status ?? "").toUpperCase() === "STOPPED");
  const unresolvedCollisions = collisions.filter((test) => !historicalStoppedCanary.includes(test));
  if (!allowCollisions) {
    assert(unresolvedCollisions.length === 0, "An intended SmartDelivery test name already exists beyond the authorized stopped canary", unresolvedCollisions.map((test) => ({ id: test.id ?? test.spam_test_id, name: test.test_name ?? test.name, status: test.status })));
  }

  if (persist) writeManifest(manifest);
  return {
    manifest,
    summary: {
      connected: all.length,
      excluded: excluded.length,
      eligible: eligible.length,
      campaign: campaign.length,
      tests: manifest.length,
      ...summary,
      providers: selectedProviders,
      helper_state: helperState,
      sequence_mapping_id: SEQUENCE_MAPPING_ID,
      existing_name_collisions: collisions.length,
      authorized_historical_stopped_canary_collisions: historicalStoppedCanary.length,
      start_is_future: true,
    },
  };
}

function fingerprint(payload) {
  return crypto.createHash("sha256").update(JSON.stringify(payload)).digest("hex");
}

function buildPayload(test) {
  return {
    test_name: test.test_name,
    description: test.description,
    spam_filters: ["spam_assassin"],
    link_checker: true,
    all_email_sent_without_time_gap: false,
    min_time_btwn_emails: 45,
    min_time_unit: "minutes",
    campaign_id: CAMPAIGN_ID,
    sequence_mapping_id: SEQUENCE_MAPPING_ID,
    provider_ids: PROVIDER_IDS,
    sender_accounts: test.ordered_inbox_emails,
    is_warmup: false,
    schedule_start_time: START,
    test_end_date: END,
    every_days: 1,
    scheduler_cron_value: {
      tz: "America/New_York",
      days: [0, 6],
      startHour: "09:00",
    },
  };
}

function sanitize(value) {
  if (Array.isArray(value)) return value.map(sanitize);
  if (!value || typeof value !== "object") return value;
  return Object.fromEntries(Object.entries(value)
    .filter(([key]) => !/(password|secret|token|api[_-]?key)/i.test(key))
    .map(([key, nested]) => [key, sanitize(nested)]));
}

function appendCreationLog(entry) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  fs.appendFileSync(path.join(OUTPUT_DIR, "creation-log.jsonl"), `${JSON.stringify(entry)}\n`);
}

function extractTestId(value) {
  if (Array.isArray(value)) {
    for (const item of value) {
      const found = extractTestId(item);
      if (found !== null) return found;
    }
  } else if (value && typeof value === "object") {
    for (const key of ["spam_test_id", "id"]) {
      const candidate = Number(value[key]);
      if (Number.isInteger(candidate) && candidate > 0) return candidate;
    }
    for (const nested of Object.values(value)) {
      const found = extractTestId(nested);
      if (found !== null) return found;
    }
  }
  return null;
}

function schedulerObjects(value, output = []) {
  if (Array.isArray(value)) {
    for (const item of value) schedulerObjects(item, output);
  } else if (value && typeof value === "object") {
    if (value.tz !== undefined || value.days !== undefined || value.startHour !== undefined || value.scheduler_cron_value !== undefined) {
      output.push(value.scheduler_cron_value ?? value);
    }
    for (const nested of Object.values(value)) schedulerObjects(nested, output);
  }
  return output;
}

function creationSchedulerVerified(response) {
  return schedulerObjects(response).some((scheduler) => scheduler
    && scheduler.tz === "America/New_York"
    && scheduler.startHour === "09:00"
    && Array.isArray(scheduler.days)
    && JSON.stringify([...scheduler.days].map(Number).sort((a, b) => a - b)) === JSON.stringify([0, 6]));
}

function verifyTest(testId, test) {
  const detail = deliveryRequestWithBackoff("GET", `/spam-test/${testId}`).json;
  const senders = deliveryRequestWithBackoff("GET", `/spam-test/report/${testId}/sender-accounts`).json;
  assert(detail && typeof detail === "object", "Canary detail response is invalid", detail);
  assert(Array.isArray(senders), "Canary sender response is invalid", senders);
  const observed = {
    id: Number(detail.id),
    test_name: detail.test_name,
    test_type: String(detail.test_type ?? "").toLowerCase(),
    description: detail.description,
    link_checker: detail.link_checker,
    campaign_id: Number(detail.campaign_id),
    sequence_mapping_id: Number(detail.sequence_mapping_id),
    provider_ids: (detail.provider_id ?? detail.provider_ids ?? []).map(Number).sort((a, b) => a - b),
    spam_filters: detail.spam_filters,
    min_time_btwn_emails: Number(detail.min_time_btwn_emails),
    min_time_unit: detail.min_time_unit,
    all_email_sent_without_time_gap: detail.all_email_sent_without_time_gap,
    schedule_start_time: detail.schedule_start_time,
    test_end_date: detail.test_end_date,
    every_days: Number(detail.every_days),
    is_warmup: detail.is_warmup,
    sender_emails: senders.map((sender) => normalizeEmail(sender.from_email)).sort(),
  };
  const expected = {
    id: Number(testId),
    test_name: test.test_name,
    test_type: "auto",
    description: test.description,
    link_checker: true,
    campaign_id: CAMPAIGN_ID,
    sequence_mapping_id: SEQUENCE_MAPPING_ID,
    provider_ids: PROVIDER_IDS,
    spam_filters: ["spam_assassin"],
    min_time_btwn_emails: 45,
    min_time_unit: "minutes",
    all_email_sent_without_time_gap: false,
    schedule_start_time: START,
    test_end_date: END,
    every_days: 1,
    is_warmup: false,
    sender_emails: [...test.ordered_inbox_emails].sort(),
  };
  assert(JSON.stringify(observed) === JSON.stringify(expected), "Canary read-back differs from manifest", { expected, observed });
  return { detail, senders, observed };
}

function createCanary() {
  const { manifest } = preflight({ persist: true, allowCollisions: true });
  const test = manifest[0];
  const exactMatches = listTests().filter((candidate) => (candidate.test_name ?? candidate.name) === test.test_name);
  const payload = buildPayload(test);
  const historicalStoppedCanary = exactMatches.filter((candidate) => testIdOf(candidate) === 509065
    && String(candidate.status ?? "").toUpperCase() === "STOPPED");
  const currentVerifiedMatches = exactMatches.filter((candidate) => hasVerifiedCreationRecord(test, testIdOf(candidate)));
  assert(currentVerifiedMatches.length <= 1, "More than one current-run canary has a positive creation record", currentVerifiedMatches.map(testIdOf));
  const unknownMatches = exactMatches.filter((candidate) => !historicalStoppedCanary.includes(candidate) && !currentVerifiedMatches.includes(candidate));
  assert(unknownMatches.length === 0, "Canary name collision is neither the authorized stopped canary nor a verified current-run canary", unknownMatches.map((candidate) => ({ id: testIdOf(candidate), status: candidate.status })));
  const beforeMatchIds = new Set(exactMatches.map(testIdOf));
  let testId;
  let creationResponse = null;
  let httpStatus = null;
  let createdNow = false;
  if (currentVerifiedMatches.length === 0) {
    let response;
    try {
      response = deliveryRequestWithBackoff("POST", "/spam-test/schedule", payload);
    } catch (error) {
      const reconciled = listTests().filter((candidate) => (candidate.test_name ?? candidate.name) === test.test_name);
      const newExactMatches = reconciled.filter((candidate) => !beforeMatchIds.has(testIdOf(candidate)));
      appendCreationLog({
        timestamp: new Date().toISOString(),
        test_name: test.test_name,
        request_fingerprint: fingerprint(payload),
        http_status: error.httpStatus ?? null,
        returned_test_id: newExactMatches.length === 1 ? testIdOf(newExactMatches[0]) : null,
        verification_status: newExactMatches.length === 0 ? "FAILED_NOT_CREATED" : "AMBIGUOUS_RECONCILIATION_REQUIRED",
        error: sanitize(error.responseBody ?? { message: error.message }),
        exact_name_reconciliation_count: newExactMatches.length,
        retry_attempted: false,
      });
      throw error;
    }
    httpStatus = response.status;
    creationResponse = response.json;
    testId = extractTestId(creationResponse);
    if (testId === null) {
      const reconciled = listTests().filter((candidate) => (candidate.test_name ?? candidate.name) === test.test_name);
      const newExactMatches = reconciled.filter((candidate) => !beforeMatchIds.has(testIdOf(candidate)));
      assert(newExactMatches.length === 1, "Canary creation response lacked an ID and new-ID reconciliation failed", sanitize(creationResponse));
      testId = testIdOf(newExactMatches[0]);
    }
    createdNow = true;
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    fs.writeFileSync(path.join(OUTPUT_DIR, "canary-creation-response.json"), `${JSON.stringify(sanitize(creationResponse), null, 2)}\n`);
  } else {
    testId = testIdOf(currentVerifiedMatches[0]);
  }

  let verification;
  try {
    verification = verifyTest(testId, test);
  } catch (error) {
    let stopResult = null;
    if (createdNow && Date.now() < Date.parse(START)) {
      try {
        stopResult = deliveryRequest("PUT", `/spam-test/${testId}/stop`).json;
      } catch (stopError) {
        stopResult = { error: stopError.message };
      }
    }
    appendCreationLog({
      timestamp: new Date().toISOString(),
      test_name: test.test_name,
      request_fingerprint: fingerprint(payload),
      http_status: httpStatus,
      returned_test_id: testId,
      verification_status: "FAILED_STOPPED",
      error: error.message,
      stop_result: sanitize(stopResult),
    });
    throw error;
  }
  const schedulerVerified = creationSchedulerVerified(creationResponse);
  const helperStateAfterCanary = verifyHelperState();
  appendCreationLog({
    timestamp: new Date().toISOString(),
    test_name: test.test_name,
    request_fingerprint: fingerprint(payload),
    http_status: httpStatus,
    returned_test_id: testId,
    verification_status: schedulerVerified ? "PASS" : "CORE_PASS_SCHEDULER_PENDING",
    created_now: createdNow,
    scheduler_verified: schedulerVerified,
    scheduler_verified_from_creation_response: schedulerVerified,
    helper_state_after_canary: helperStateAfterCanary,
  });
  fs.writeFileSync(path.join(OUTPUT_DIR, "canary-core-verification.json"), `${JSON.stringify({
    test_id: testId,
    test_name: test.test_name,
    core_verified: true,
    scheduler_verified: schedulerVerified,
    scheduler_method: schedulerVerified ? "creation response" : null,
    helper_state_after_canary: helperStateAfterCanary,
    observed: verification.observed,
  }, null, 2)}\n`);
  return { testId, createdNow, schedulerVerified, creationResponse: sanitize(creationResponse), observed: verification.observed };
}

function confirmCanarySchedule(testId, method) {
  assert(method && method.trim(), "A positive scheduler verification method is required");
  const manifest = JSON.parse(fs.readFileSync(path.join(OUTPUT_DIR, "manifest.json"), "utf8"));
  const test = manifest[0];
  const markerPath = path.join(OUTPUT_DIR, "canary-core-verification.json");
  const marker = JSON.parse(fs.readFileSync(markerPath, "utf8"));
  assert(Number(marker.test_id) === Number(testId), "Canary ID does not match the core-verification artifact", {
    expected: marker.test_id,
    observed: testId,
  });
  verifyTest(Number(testId), test);
  const helperStateAfterCanary = verifyHelperState();
  const verified = {
    ...marker,
    scheduler_verified: true,
    scheduler_method: method.trim(),
    scheduler_verified_at: new Date().toISOString(),
    helper_state_after_canary: helperStateAfterCanary,
  };
  fs.writeFileSync(markerPath, `${JSON.stringify(verified, null, 2)}\n`);
  appendCreationLog({
    timestamp: new Date().toISOString(),
    test_name: test.test_name,
    request_fingerprint: fingerprint(buildPayload(test)),
    http_status: null,
    returned_test_id: Number(testId),
    verification_status: "PASS",
    scheduler_verified: true,
    scheduler_verification_method: method.trim(),
    helper_state_after_canary: helperStateAfterCanary,
  });
  return verified;
}

function acceptCanaryExecutionWindow(testId) {
  const method = "user-authorized immediate sends; fixed end is Sunday Aug 16, 2026 EOD";
  const manifest = JSON.parse(fs.readFileSync(path.join(OUTPUT_DIR, "manifest.json"), "utf8"));
  const test = manifest[0];
  const markerPath = path.join(OUTPUT_DIR, "canary-core-verification.json");
  const marker = JSON.parse(fs.readFileSync(markerPath, "utf8"));
  assert(Number(marker.test_id) === Number(testId), "Canary ID does not match the core-verification artifact", {
    expected: marker.test_id,
    observed: testId,
  });
  verifyTest(Number(testId), test);
  const helperStateAfterCanary = verifyHelperState();
  const accepted = {
    ...marker,
    scheduler_verified: marker.scheduler_verified === true,
    execution_window_accepted: true,
    scheduler_method: method,
    execution_window_accepted_at: new Date().toISOString(),
    helper_state_after_canary: helperStateAfterCanary,
  };
  fs.writeFileSync(markerPath, `${JSON.stringify(accepted, null, 2)}\n`);
  appendCreationLog({
    timestamp: new Date().toISOString(),
    test_name: test.test_name,
    request_fingerprint: fingerprint(buildPayload(test)),
    http_status: null,
    returned_test_id: Number(testId),
    verification_status: "PASS",
    scheduler_verified: marker.scheduler_verified === true,
    execution_window_accepted: true,
    scheduler_verification_method: method,
    helper_state_after_canary: helperStateAfterCanary,
  });
  return accepted;
}

function readCreationLog() {
  const logPath = path.join(OUTPUT_DIR, "creation-log.jsonl");
  if (!fs.existsSync(logPath)) return [];
  return fs.readFileSync(logPath, "utf8")
    .split(/\r?\n/)
    .filter(Boolean)
    .map((line) => JSON.parse(line));
}

function testIdOf(value) {
  return Number(value?.id ?? value?.spam_test_id);
}

function exactNameMatches(name) {
  return listTests().filter((candidate) => (candidate.test_name ?? candidate.name) === name);
}

function readVerifiedCanaryMarker() {
  const markerPath = path.join(OUTPUT_DIR, "canary-core-verification.json");
  assert(fs.existsSync(markerPath), "Canary verification artifact is missing");
  const marker = JSON.parse(fs.readFileSync(markerPath, "utf8"));
  assert(marker.core_verified === true, "Canary core verification is not complete", marker);
  assert(marker.scheduler_verified === true || marker.execution_window_accepted === true,
    "Canary schedule or execution window is not approved", marker);
  assert(marker.scheduler_method, "Canary schedule verification method is missing", marker);
  return marker;
}

function verifiedCurrentRunIds(test) {
  const wantedFingerprint = fingerprint(buildPayload(test));
  return unique(readCreationLog()
    .filter((entry) => entry.test_name === test.test_name
      && entry.request_fingerprint === wantedFingerprint
      && entry.verification_status === "PASS"
      && Number(entry.returned_test_id) > 0
      && (entry.scheduler_verified === true
        || entry.scheduler_verified_from_creation_response === true
        || entry.execution_window_accepted === true
        || Boolean(entry.scheduler_verification_method)))
    .map((entry) => Number(entry.returned_test_id)));
}

function hasVerifiedCreationRecord(test, testId) {
  return verifiedCurrentRunIds(test).includes(Number(testId));
}

function writeCreationResponse(testId, response) {
  const responseDir = path.join(OUTPUT_DIR, "creation-responses");
  fs.mkdirSync(responseDir, { recursive: true });
  fs.writeFileSync(path.join(responseDir, `${testId}.json`), `${JSON.stringify(sanitize(response), null, 2)}\n`);
}

function createOrVerifyManifestTest(test, canaryMarker) {
  const payload = buildPayload(test);
  const priorVerifiedIds = verifiedCurrentRunIds(test);
  assert(priorVerifiedIds.length <= 1, "More than one verified current-run test exists", {
    test_name: test.test_name,
    ids: priorVerifiedIds,
  });
  if (priorVerifiedIds.length === 1) {
    const testId = priorVerifiedIds[0];
    verifyTest(testId, test);
    appendCreationLog({
      timestamp: new Date().toISOString(),
      test_name: test.test_name,
      request_fingerprint: fingerprint(payload),
      http_status: null,
      returned_test_id: testId,
      verification_status: "SKIPPED_IDEMPOTENT_MATCH",
      scheduler_verified: false,
      execution_window_accepted: true,
      scheduler_verification_method: "prior verified creation record and direct ID read-back",
    });
    return { testId, createdNow: false, skipped: true };
  }
  const beforeMatches = exactNameMatches(test.test_name);
  assert(beforeMatches.length <= 1, "Intended test name exists more than once", {
    test_name: test.test_name,
    ids: beforeMatches.map(testIdOf),
  });

  if (beforeMatches.length === 1) {
    const testId = testIdOf(beforeMatches[0]);
    verifyTest(testId, test);
    assert(hasVerifiedCreationRecord(test, testId), "Existing exact-name test lacks positive schedule evidence from this authorized run", {
      test_name: test.test_name,
      test_id: testId,
    });
    appendCreationLog({
      timestamp: new Date().toISOString(),
      test_name: test.test_name,
      request_fingerprint: fingerprint(payload),
      http_status: null,
      returned_test_id: testId,
      verification_status: "SKIPPED_IDEMPOTENT_MATCH",
      scheduler_verified: false,
      execution_window_accepted: true,
      scheduler_verification_method: "prior verified creation record",
    });
    return { testId, createdNow: false, skipped: true };
  }

  let response = null;
  let testId = null;
  let httpStatus = null;
  let ambiguousReconciliation = false;
  try {
    response = deliveryRequestWithBackoff("POST", "/spam-test/schedule", payload);
    httpStatus = response.status;
    testId = extractTestId(response.json);
  } catch (error) {
    const reconciled = exactNameMatches(test.test_name);
    appendCreationLog({
      timestamp: new Date().toISOString(),
      test_name: test.test_name,
      request_fingerprint: fingerprint(payload),
      http_status: error.httpStatus ?? null,
      returned_test_id: reconciled.length === 1 ? testIdOf(reconciled[0]) : null,
      verification_status: reconciled.length === 1 ? "AMBIGUOUS_RECONCILED" : "FAILED_NOT_CREATED",
      error: sanitize(error.responseBody ?? { message: error.message }),
      exact_name_reconciliation_count: reconciled.length,
      retry_attempted: error.httpStatus === 429,
    });
    const ambiguous = error.httpStatus === undefined || error.httpStatus === null || error.httpStatus >= 500;
    assert(ambiguous && reconciled.length === 1, "Test creation failed and exact-name reconciliation did not prove one created test", {
      test_name: test.test_name,
      http_status: error.httpStatus ?? null,
      response: sanitize(error.responseBody ?? { message: error.message }),
      exact_name_reconciliation_count: reconciled.length,
    });
    testId = testIdOf(reconciled[0]);
    ambiguousReconciliation = true;
  }

  if (testId === null) {
    const reconciled = exactNameMatches(test.test_name);
    assert(reconciled.length === 1, "Creation response lacked a test ID and exact-name reconciliation failed", {
      test_name: test.test_name,
      response: sanitize(response?.json),
      exact_name_reconciliation_count: reconciled.length,
    });
    testId = testIdOf(reconciled[0]);
  }

  const verification = verifyTest(testId, test);
  if (response) writeCreationResponse(testId, response.json);
  appendCreationLog({
    timestamp: new Date().toISOString(),
    test_name: test.test_name,
    request_fingerprint: fingerprint(payload),
    http_status: httpStatus,
    returned_test_id: testId,
    verification_status: "PASS",
    created_now: true,
    ambiguous_reconciliation: ambiguousReconciliation,
    scheduler_verified: creationSchedulerVerified(response?.json),
    execution_window_accepted: true,
    scheduler_verified_from_creation_response: creationSchedulerVerified(response?.json),
    scheduler_verification_method: creationSchedulerVerified(response?.json)
      ? "creation response"
      : `same exact scheduler payload as accepted canary ${canaryMarker.test_id}: ${canaryMarker.scheduler_method}`,
    observed: verification.observed,
  });
  return { testId, createdNow: true, skipped: false };
}

function createRemainingTests() {
  const { manifest } = preflight({ persist: true, allowCollisions: true });
  const canaryMarker = readVerifiedCanaryMarker();
  const canary = manifest[0];
  assert(Number(canaryMarker.test_id) > 0 && canaryMarker.test_name === canary.test_name,
    "Verified canary marker does not match the first manifest entry", canaryMarker);
  const canaryMatches = exactNameMatches(canary.test_name);
  const currentCanaryMatches = canaryMatches.filter((candidate) => testIdOf(candidate) === Number(canaryMarker.test_id));
  assert(currentCanaryMatches.length === 1,
    "Verified current-run canary is not present exactly once", canaryMatches.map((candidate) => ({ id: testIdOf(candidate), name: candidate.test_name ?? candidate.name, status: candidate.status })));
  verifyTest(canaryMarker.test_id, canary);
  assert(hasVerifiedCreationRecord(canary, canaryMarker.test_id), "Canary lacks a positive creation record with schedule evidence");
  verifyHelperState();

  const results = [];
  for (const test of manifest.slice(1)) {
    const result = createOrVerifyManifestTest(test, canaryMarker);
    results.push({ test_name: test.test_name, test_id: result.testId, created_now: result.createdNow, skipped: result.skipped });
    console.log(JSON.stringify(results.at(-1)));
  }
  return results;
}

function finalReconciliation() {
  const { manifest, summary } = preflight({ persist: true, allowCollisions: true });
  const canaryMarker = readVerifiedCanaryMarker();
  const verified = [];
  for (const test of manifest) {
    const currentRunIds = verifiedCurrentRunIds(test);
    assert(currentRunIds.length === 1, "An intended name does not have exactly one verified current-run test ID", {
      test_name: test.test_name,
      current_run_ids: currentRunIds,
    });
    const testId = currentRunIds[0];
    const result = verifyTest(testId, test);
    assert(hasVerifiedCreationRecord(test, testId), "A final test lacks positive schedule evidence", {
      test_name: test.test_name,
      test_id: testId,
    });
    verified.push({ test_id: testId, test_name: test.test_name, observed: result.observed });
  }

  const senderEmails = verified.flatMap((item) => item.observed.sender_emails);
  assert(senderEmails.length === 504 && unique(senderEmails).length === 504,
    "Final sender exact-once count differs", { total: senderEmails.length, unique: unique(senderEmails).length });
  assert(EXPECTED_EXCLUSIONS.every((email) => !senderEmails.includes(email)), "An excluded inbox appears in final tests");
  const categoryCounts = Object.fromEntries(["A", "B", "Other"].map((category) => [
    category,
    manifest.filter((test) => test.category === category).length,
  ]));
  assert(JSON.stringify(categoryCounts) === JSON.stringify({ A: 14, B: 23, Other: 18 }), "Final category test counts differ", categoryCounts);

  const logs = readCreationLog();
  const skipped = logs.filter((entry) => entry.verification_status === "SKIPPED_IDEMPOTENT_MATCH");
  const errors = logs.filter((entry) => String(entry.verification_status ?? "").startsWith("FAILED"));
  const retries = logs.filter((entry) => entry.retry_attempted === true);
  const lines = [
    "# SmartDelivery Weekend Tests — Final Reconciliation",
    "",
    "**Overall:** PASS",
    "",
    `- Tests: 55 (A: ${categoryCounts.A}, B: ${categoryCounts.B}, Other: ${categoryCounts.Other})`,
    `- Unique eligible sender inboxes: ${unique(senderEmails).length}`,
    `- Unique domains: ${summary.uniqueDomains}`,
    `- Exclusions confirmed absent: ${EXPECTED_EXCLUSIONS.join(", ")}`,
    `- Campaign ID: ${CAMPAIGN_ID}`,
    `- Sequence mapping ID: ${SEQUENCE_MAPPING_ID}`,
    `- Providers on every test: [${PROVIDER_IDS.join(", ")}]`,
    "- Throttle on every test: 45 minutes",
    `- Start: ${START}`,
    `- End: ${END}`,
    `- Execution-window acceptance: ${canaryMarker.scheduler_method}; every remaining test used the identical scheduler payload`,
    "- Enabled-days request on every test: [0,6] (Sunday and Saturday)",
    "- Immediate Friday sends were explicitly accepted by the user; every test ends Sunday, August 16 at EOD.",
    `- Skipped idempotent matches: ${skipped.length}`,
    `- Logged failed attempts: ${errors.length} (includes the two preserved obsolete-campaign canary attempts)`,
    `- Logged retry attempts: ${retries.length}`,
    "- No unrelated test was changed.",
    "",
    "## Test IDs and names",
    "",
    ...verified.map((item) => `- ${item.test_id} — ${item.test_name}`),
    "",
    "## Logged errors and retries",
    "",
    ...(errors.length === 0
      ? ["- None"]
      : errors.map((entry) => `- ${entry.timestamp} — ${entry.test_name} — HTTP ${entry.http_status ?? "unknown"} — ${JSON.stringify(entry.error ?? null)}`)),
    ...(retries.length === 0
      ? ["- No retries were attempted."]
      : retries.map((entry) => `- Retry recorded for ${entry.test_name} at ${entry.timestamp}.`)),
    "",
  ];
  fs.writeFileSync(path.join(OUTPUT_DIR, "final-reconciliation.md"), `${lines.join("\n")}\n`);
  return {
    status: "PASS",
    tests: verified.length,
    categories: categoryCounts,
    unique_inboxes: unique(senderEmails).length,
    unique_domains: summary.uniqueDomains,
    exclusions: EXPECTED_EXCLUSIONS,
    schedule_method: canaryMarker.scheduler_method,
    execution_window_accepted: true,
    skipped_idempotent_matches: skipped.length,
    failed_log_entries: errors.length,
    retry_log_entries: retries.length,
    report: path.join(OUTPUT_DIR, "final-reconciliation.md"),
    test_ids: verified.map((item) => item.test_id),
  };
}

const command = process.argv[2] ?? "preflight";
try {
  if (command === "preflight") {
    const result = preflight({ persist: true });
    console.log(JSON.stringify({ status: "PASS", manifest_dir: OUTPUT_DIR, ...result.summary }, null, 2));
  } else if (command === "canary") {
    const result = createCanary();
    console.log(JSON.stringify({
      status: result.schedulerVerified ? "PASS" : "CORE_PASS_SCHEDULER_PENDING",
      test_id: result.testId,
      created_now: result.createdNow,
      scheduler_verified_from_creation_response: result.schedulerVerified,
      observed: result.observed,
      creation_response: result.creationResponse,
    }, null, 2));
  } else if (command === "confirm-canary-scheduler") {
    const testId = Number(process.argv[3]);
    const method = process.argv.slice(4).join(" ");
    assert(Number.isInteger(testId) && testId > 0, "A valid canary test ID is required");
    const result = confirmCanarySchedule(testId, method);
    console.log(JSON.stringify({ status: "PASS", ...result }, null, 2));
  } else if (command === "accept-execution-window") {
    const testId = Number(process.argv[3]);
    assert(Number.isInteger(testId) && testId > 0, "A valid canary test ID is required");
    const result = acceptCanaryExecutionWindow(testId);
    console.log(JSON.stringify({ status: "PASS", ...result }, null, 2));
  } else if (command === "bulk") {
    const result = createRemainingTests();
    console.log(JSON.stringify({ status: "PASS", processed: result.length, results: result }, null, 2));
  } else if (command === "reconcile") {
    console.log(JSON.stringify(finalReconciliation(), null, 2));
  } else if (command === "fingerprint") {
    const { manifest } = preflight({ persist: false });
    console.log(fingerprint(manifest));
  } else {
    fail(`Unknown command: ${command}`);
  }
} catch (error) {
  console.error(`PREFLIGHT FAILED: ${error.message}`);
  process.exitCode = 1;
}
