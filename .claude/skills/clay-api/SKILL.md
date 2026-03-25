---
name: clay-api
description: This skill provides comprehensive guidance for interacting with the Clay API (api.clay.com). Use this skill when reading data from Clay tables, listing workspace resources, fetching row data, authenticating with Clay, or building automations that pull data from Clay. The skill covers the undocumented internal API patterns, curl-based session authentication, endpoint discovery, and correct data fetching workflows.
---

# Clay API Skill

## Overview

Clay does not have a publicly documented REST API. The `api.clay.com/v3` endpoints are internal app APIs that require session cookie authentication. This skill documents the discovered API patterns for reading and writing data to Clay entirely from the terminal via curl — no browser or Playwright needed.

## What Clay Contains

Clay is a data enrichment and outbound sales platform. The HireWithNear workspace contains:

### Data Entities (Table Types)

| Type | Description | Example Data |
|------|-------------|--------------|
| `company` | Company profiles with firmographic data | Domain, name, industry, headcount, location, PE/VC status |
| `people` | Individual person profiles with contact info | Full name, job title, LinkedIn profile, company domain, location, email |
| `spreadsheet` | Generic data tables (custom imports, lists) | Any structured data — imports from HubSpot, CSVs, custom columns |
| `jobs` | Job listing data | Job title, LinkedIn job URL, company name/domain, location, posted date |

### What You Can Read

- **Company data**: Domain, company name, industry, headcount range, city, country, PE/VC classification
- **People data**: Full name, first/last name, job title, LinkedIn profile URL, company domain, company name, location
- **Job listings**: Job title, LinkedIn job URL, company name, company domain, location, posted date
- **Enrichment results**: AI-generated data, career page URLs, LinkedIn job listings, company lookups
- **Workspace resources**: All tables, workbooks, folders — with owner info and settings
- **Actions catalog**: 1,132 available enrichment actions (company enrichment, people finder, email finder, AI tools, CRM integrations, etc.)
- **App accounts**: 14 user-owned integrations (HubSpot, Smartlead, Google Sheets, PhantomBuster, Slack, etc.) plus 106 Clay-managed enrichment accounts
- **Table metadata**: Full field schema — field IDs, names, types, data types, filter operators, sort capability

### Key Integrations Available via Actions

HubSpot, Salesforce, Apollo.io, LinkedIn, Google Sheets, Airtable, Smartlead AI, PhantomBuster, Anthropic Claude, OpenAI GPT, Slack, and 100+ more enrichment providers.

## Authentication

### Session Cookie (Full Access — Primary Method)

To authenticate with Clay, POST to the login endpoint and capture the `claysession` cookie from the `Set-Cookie` response header.

#### Login via curl

```bash
# Read credentials from .env
source .env

# Login and capture the session cookie
CLAY_SESSION=$(curl -s -D - -X POST "https://api.clay.com/v3/auth/login" \
  -H "Content-Type: application/json" \
  -H "Origin: https://app.clay.com" \
  -H "Referer: https://app.clay.com/" \
  -d "{\"email\":\"$CLAY_USERNAME\",\"password\":\"$(echo $CLAY_PASSWORD | sed 's/\$/\\$/g')\",\"source\":\"web\"}" \
  2>&1 | grep -i 'set-cookie' | sed 's/.*claysession=\([^;]*\).*/claysession=\1/')

# Use in subsequent requests
curl -s "https://api.clay.com/v3/me" -H "Cookie: $CLAY_SESSION"
```

#### Login Requirements

- **URL**: `POST https://api.clay.com/v3/auth/login`
- **Headers**: `Origin: https://app.clay.com` and `Referer: https://app.clay.com/` are REQUIRED
- **Body**: `{"email":"...","password":"...","source":"web"}`
- **Response**: `Set-Cookie: claysession=<value>; Domain=api.clay.com; HttpOnly; Secure`
- **Cookie expiry**: 7 days
- **Rate limiting**: Too many failed attempts triggers rate limiting (429/504). Wait 30-60 seconds.

#### Password Escaping

The password in `.env` (`CLAY_PASSWORD`) may contain `$` characters. When using in bash:
- Use single quotes around the JSON body, or
- Escape `$` as `\$` in double-quoted strings, or
- Use `--data-raw` flag with single-quoted JSON

#### Making API Calls

After obtaining the session cookie, use it in the `Cookie` header for all requests:

```bash
curl -s "https://api.clay.com/v3/endpoint" -H "Cookie: $CLAY_SESSION"
```

#### Session Expiry

If requests return 401 "You must be logged in", the session has expired. Re-run the login command above.

### API Key (Limited — Write Only)

The Clay API key from Settings > Profile (`CLAY_API_KEY` in `.env`) only works for:
- POST requests that create resources (tables, sources)
- Schema validation (returns required field errors)
- NOT for reading data (GET requests return 401)

Header format: `Authorization: Bearer <CLAY_API_KEY>`

### Fallback: Playwright (If curl Login Fails)

If curl-based login is blocked (e.g., by bot detection or CAPTCHA), fall back to Playwright:

1. Use `mcp__plugin_playwright_playwright__browser_navigate` to go to `https://app.clay.com`
2. Log in with `CLAY_USERNAME` and `CLAY_PASSWORD` from `.env`
3. After login, extract the session cookie using `mcp__plugin_playwright_playwright__browser_run_code`:
   ```javascript
   async (page) => {
     const context = page.context();
     const cookies = await context.cookies('https://api.clay.com');
     return cookies.find(c => c.name === 'claysession');
   }
   ```
4. Use the extracted `claysession` value in curl for all subsequent requests

## Workspace Details

- **Workspace ID**: `447061`
- **Workspace Name**: HireWithNear
- **Billing Plan**: proApril2023
- **User ID**: `1033117` (kevin.dubon@hirewithnear.com)

## Table Resolution Workflow

Before fetching data from a Clay table, resolve the table ID using this two-step process:

### Step 1: Check Known Tables

Read `references/known-tables.md` for pre-mapped table IDs and field IDs. If the target table is listed there, use the IDs directly — skip to the data fetching workflow.

### Step 2: Search for Unknown Tables (Fallback)

If the table is NOT in the known tables reference, authenticate and search:

```bash
# Authenticate first (see Authentication section)
# Then list ALL tables in the workspace (includes tables nested inside workbooks)
curl -s "https://api.clay.com/v3/workspaces/447061/tables" -H "Cookie: $CLAY_SESSION"
```

Search the response for the table by name. Once found, fetch its metadata to get field IDs:

```bash
curl -s "https://api.clay.com/v3/tables/${TABLE_ID}" -H "Cookie: $CLAY_SESSION"
```

**Important:** Use `/workspaces/{id}/tables` (GET) to find tables by name — it returns ALL tables including those inside workbooks. The `/workspaces/{id}/resources_v2/` (POST) endpoint only returns root-level resources and will miss tables nested in workbooks.

After discovering a new table, consider updating `references/known-tables.md` with the table ID and key field IDs for future use.

## API Endpoints Reference

All endpoints use base URL `https://api.clay.com/v3`.

For complete endpoint documentation including request/response schemas and field mappings, see `references/clay-api-endpoints.md`.

### Quick Reference — Read Operations

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/my-workspaces` | GET | List user's workspaces |
| `/workspaces/{id}` | GET | Workspace details, credits, feature flags |
| `/workspaces/{id}/resources_v2/` | POST | List all folders, workbooks, and tables |
| `/workspaces/{id}/permissions` | GET | Workspace permissions |
| `/workspaces/{id}/users` | GET | Workspace team members |
| `/tables/{tableId}` | GET | Table metadata and column definitions |
| `/tables/{tableId}/count` | GET | Row count |
| `/tables/{tableId}/views/{viewId}/records/ids` | GET | All record IDs in a view |
| `/tables/{tableId}/bulk-fetch-records` | POST | Fetch row data by record IDs |
| `/tables/{tableId}/fieldrun` | GET | Field enrichment run status |
| `/sources?tableId={tableId}` | GET | Data sources for a table |
| `/me` | GET | Current user info |
| `/actions?workspaceId={id}` | GET | Available actions/enrichments |
| `/subscriptions/{id}` | GET | Subscription details |

## Data Fetching Workflow

To read rows from a Clay table via curl:

### Step 1: Get Table Info

Fetch table metadata to understand columns and get the default view ID:
```bash
curl -s "https://api.clay.com/v3/tables/${TABLE_ID}" -H "Cookie: $CLAY_SESSION"
```

### Step 2: Get Record IDs

Fetch all record IDs for a view:
```bash
curl -s "https://api.clay.com/v3/tables/${TABLE_ID}/views/${VIEW_ID}/records/ids" \
  -H "Cookie: $CLAY_SESSION"
# Response: { "results": ["r_abc123", "r_def456", ...] }
```

### Step 3: Bulk Fetch Records

Fetch actual row data in batches (50-100 IDs per request):
```bash
curl -s -X POST "https://api.clay.com/v3/tables/${TABLE_ID}/bulk-fetch-records" \
  -H "Cookie: $CLAY_SESSION" \
  -H "Content-Type: application/json" \
  -d '{"recordIds": ["r_abc123", "r_def456"]}'
# Response: { "results": [{ "id", "tableId", "cells": { "fieldId": { "value" } } }] }
```

### Important Notes on Data Shape

- Cells use **field IDs** (e.g., `f_bu5mcFgUkc5q`) not column names
- To map field IDs to column names, use the table metadata from Step 1
- Batch record fetches to avoid timeouts (50-100 records per request)
- Record IDs have prefix `r_`, field IDs have prefix `f_`, table IDs have prefix `t_`

## Listing Workspace Resources

To list all tables, folders, and workbooks:
```bash
curl -s -X POST "https://api.clay.com/v3/workspaces/447061/resources_v2/" \
  -H "Cookie: $CLAY_SESSION" \
  -H "Content-Type: application/json" \
  -d '{}'
```

Response includes resources with `resourceType` of `FOLDER`, `WORKBOOK`, or `TABLE`.

## Table Types

When creating tables (via API key auth), valid types are:
- `spreadsheet` — Generic spreadsheet table
- `company` — Company enrichment table
- `people` — People enrichment table
- `jobs` — Job listings table

## Field Metadata Schema

Each table's fields are returned in the `GET /tables/{tableId}` response under `table.fields[]`. Each field object has:

| Property | Type | Description |
|----------|------|-------------|
| `id` | string | Unique field ID (prefix `f_`) — used as key in record cells |
| `tableId` | string | Parent table ID |
| `name` | string | Human-readable column name |
| `type` | string | Field type — see types below |
| `description` | string/null | Optional description of the field |
| `typeSettings.dataTypeSettings.type` | string | Data type of the field value |
| `supportedFilterOperators` | array | Available filter operators for this field |
| `isSortable` | boolean | Whether this field supports sorting |
| `isLocked` | boolean | Whether the field is locked from editing |
| `isExtractedField` | boolean | Whether this field was auto-extracted from a source |
| `groupId` | string/null | Field group ID for grouped columns |
| `createdAt` / `updatedAt` | ISO date | Timestamps |

### Field Types

| Field Type | Data Type | Description |
|------------|-----------|-------------|
| `text` | `text` | Plain text value |
| `number` | `number` | Numeric value |
| `date` | `date` | Date/datetime value |
| `formula` | `text`, `url`, `date` | Computed/extracted field — auto-populated from sources |
| `action` | `json` | Enrichment action result (AI, API calls, lookups) |
| `source` | (none) | Data import source marker (not a data column) |

### Filter Operators by Data Type

**Text fields**: `EQUAL`, `NOT_EQUAL`, `CONTAIN`, `CONTAIN_ANY`, `NOT_CONTAIN`, `NOT_CONTAIN_ANY`, `EMPTY`, `NOT_EMPTY`

**Number fields**: `EQUAL`, `NOT_EQUAL`, `GREATER_THAN`, `GREATER_THAN_OR_EQUAL`, `LESS_THAN`, `LESS_THAN_OR_EQUAL`, `EMPTY`, `NOT_EMPTY`

**Action fields**: `HAS_ERROR`, `NOT_ERRORED`, `RESULTS`, `NO_RESULTS`, `HAS_NOT_RUN`, `QUEUED`, `IS_RUNNING`, `IS_NOT_RUNNING`, `IS_STALE`, `RUN_CONDITION_NOT_MET`

### Action Fields (Enrichments)

Action-type fields contain enrichment configuration in `typeSettings`:
- `actionKey`: The action identifier (e.g., `claygent`, `use-ai`, `lookup-company-in-other-table`)
- `actionVersion`: Version number
- `inputsBinding`: Array of input parameter bindings (references to other field IDs)
- `actionDefinition`: Full action metadata including `displayName`, `description`, `inputParameterSchema`, `outputParameterSchema`

### Mapping Field IDs to Names

Record cells use field IDs as keys. To get human-readable names:
1. Fetch table metadata: `GET /tables/{tableId}`
2. Build a map from `table.fields`: `{ f.id: f.name for f in fields }`
3. Apply to record cells when reading data

## Safety Rules

- **NEVER** perform write operations (POST to create/update/delete) without explicit user confirmation
- **READ operations are safe** — all GET requests and bulk-fetch-records
- Session cookies expire after 7 days — re-authenticate if requests return 401
- The API is undocumented and internal — endpoints may change without notice
