# Clay API Endpoint Reference
<!-- Author: Kevin Dubon -->

## Base URL

`https://api.clay.com/v3`

## Authentication Methods

### Method 1: Session Cookie (Full Access — Primary Method)

Obtained via curl login to `POST /v3/auth/login`:
- Required headers: `Origin: https://app.clay.com`, `Referer: https://app.clay.com/`
- Body: `{"email":"...","password":"...","source":"web"}`
- Returns `Set-Cookie: claysession=<value>` — use as `Cookie: claysession=<value>` header
- Credentials: `.env` → `CLAY_USERNAME`, `CLAY_PASSWORD`
- Cookie expiry: 7 days

### Method 2: API Key (Write-Only, Limited)
- Header: `Authorization: Bearer <CLAY_API_KEY>`
- Works for: POST requests that create resources
- Does NOT work for: GET requests (returns 401)
- Key location: `.env` → `CLAY_API_KEY`

### Method 3: Playwright Fallback
- If curl login is blocked by bot detection, log in via Playwright browser
- Extract `claysession` cookie using `context.cookies('https://api.clay.com')`
- Then use extracted cookie in curl for all subsequent requests

## Workspace Endpoints

### GET /my-workspaces
Returns all workspaces the authenticated user belongs to.

**Response:**
```json
{
  "results": [{
    "id": 447061,
    "name": "HireWithNear",
    "billingPlanType": "proApril2023",
    "billingEmail": "franco@hirewithnear.com",
    "credits": {
      "basic": 1397999.40,
      "longExpiry": 0,
      "actionExecution": 999999363523
    },
    "featureFlags": { ... },
    "abilities": {
      "canUpdate": true,
      "canDelete": true,
      "canCreateResource": true,
      "canManageBilling": true,
      "canManageAccess": true,
      "canManageAppAccounts": true
    }
  }]
}
```

### GET /workspaces/{workspaceId}
Returns detailed workspace information.

### GET /workspaces/{workspaceId}/permissions
Returns workspace permission settings.

### GET /workspaces/{workspaceId}/users
Returns all users in the workspace.

### POST /workspaces/{workspaceId}/resources_v2/
Lists all resources (folders, workbooks, tables) in the workspace.

**Request body:** `{}` (empty object)

**Response:**
```json
{
  "resources": [
    {
      "resourceType": "FOLDER",
      "id": "f_...",
      "name": "Folder Name",
      "parentFolderId": null,
      "createdAt": "2025-01-07T19:55:16.188Z"
    },
    {
      "resourceType": "WORKBOOK",
      "id": "wb_...",
      "name": "Workbook Name",
      "ownerId": "605733",
      "owner": { "id": 605733, "email": "...", "fullName": "..." }
    },
    {
      "resourceType": "TABLE",
      "id": "t_...",
      "name": "Table Name",
      "type": "spreadsheet|company|people|jobs",
      "ownerId": "534026",
      "owner": { "id": 534026, "email": "...", "fullName": "..." },
      "tableSettings": { "AUTO_RUN_ON": true, "DEDUPE_FIELD_ID": "f_..." }
    }
  ]
}
```

## Table Endpoints

### GET /tables/{tableId}
Returns table metadata including full field definitions and views.

**Response structure:**
```json
{
  "table": {
    "id": "t_...",
    "workspaceId": 447061,
    "createdByUserId": "...",
    "name": "Table Name",
    "description": null,
    "type": "spreadsheet|company|people|jobs",
    "icon": null,
    "parentFolderId": "f_...",
    "tableSettings": { ... },
    "workbookId": "wb_...",
    "defaultAccess": "...",
    "ownerId": "...",
    "isSandbox": false,
    "abilities": { ... },
    "firstViewId": "gv_...",
    "owner": { "id": ..., "email": "...", "fullName": "..." },
    "fields": [ ... ],
    "views": [ ... ]
  },
  "extraData": null
}
```

**Table keys:** `id`, `workspaceId`, `createdByUserId`, `name`, `description`, `type`, `icon`, `parentFolderId`, `tableSettings`, `createdAt`, `updatedAt`, `deletedAt`, `fieldGroupMap`, `workbookId`, `defaultAccess`, `ownerId`, `isSandbox`, `isHiddenFromNavigation`, `abilities`, `firstViewId`, `owner`, `fields`, `views`

### GET /tables/{tableId}?extraDataViewId={viewId}&includeExtraData=true
Returns table metadata with additional view-specific data.

### GET /tables/{tableId}/count
Returns the total number of rows in the table.

### GET /tables/{tableId}/fieldrun
Returns the enrichment run status for fields.

### GET /tables/{tableId}/views/{viewId}/records/ids
Returns all record IDs for a specific view.

**Response:**
```json
{
  "results": ["r_8MkC8Y8jeuNJ", "r_B6QMVUf7epBv", "r_pTr38JprK6KX", ...]
}
```

### POST /tables/{tableId}/bulk-fetch-records
Fetches actual row data for specified record IDs.

**Request body:**
```json
{
  "recordIds": ["r_8MkC8Y8jeuNJ", "r_B6QMVUf7epBv"]
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "r_8MkC8Y8jeuNJ",
      "tableId": "t_G8ZFmeDN3ouB",
      "cells": {
        "f_bu5mcFgUkc5q": { "value": "Company Name" },
        "f_SU4578K7PHWw": { "value": "domain.com" },
        "f_QgY3VUKuyDTc": { "value": "City" },
        "f_GkDT4fqfbUW4": { "value": "Country" },
        "f_7iuUN2d8PpUY": { "value": "Industry" },
        "f_5rdJ3sbVarwh": { "value": "51-100" },
        "f_created_at": { "value": "2025-02-03T15:49:33.160Z" },
        "f_updated_at": { "value": "2025-02-03T15:49:33.160Z" }
      },
      "recordMetadata": {},
      "createdAt": "2025-02-03T15:49:33.206Z",
      "updatedAt": "2025-02-03T15:49:33.206Z"
    }
  ]
}
```

**Important:** Cells use field IDs, not column names. Map field IDs to names using the table metadata endpoint.

## Field Metadata Schema

Each field in `table.fields[]` has the following structure:

```json
{
  "id": "f_5rdJ3sbVarwh",
  "tableId": "t_G8ZFmeDN3ouB",
  "type": "text",
  "name": "Headcount",
  "description": null,
  "supportedFilterOperators": [
    { "operator": "EQUAL", "needsValue": true },
    { "operator": "EMPTY", "needsValue": false }
  ],
  "isSortable": true,
  "createdAt": "2025-02-03T15:49:32.139Z",
  "updatedAt": "2025-02-03T15:49:32.139Z",
  "isLocked": false,
  "typeSettings": {
    "dataTypeSettings": { "type": "text" }
  },
  "isExtractedField": false,
  "extractedField": null,
  "groupId": null
}
```

### Field Types

| type | dataType | Description | Sortable |
|------|----------|-------------|----------|
| `text` | `text` | Plain text string | Yes |
| `number` | `number` | Numeric value | Yes |
| `date` | `date` | Date/datetime ISO string | Yes |
| `formula` | `text`, `url`, `date` | Auto-computed/extracted field from sources | Yes |
| `action` | `json` | Enrichment action result (AI, API calls, lookups) | No |
| `source` | (none) | Data import source marker — not a data column | No |

### Action Field Extended Schema

Action-type fields contain enrichment configuration:

```json
{
  "id": "f_GcE5ZXhMCnPx",
  "type": "action",
  "name": "Career Page URL",
  "typeSettings": {
    "dataTypeSettings": { "type": "json" },
    "actionKey": "claygent",
    "actionVersion": 1,
    "actionPackageId": "...",
    "inputsBinding": [
      { "name": "companyIdentifier", "formulaText": "{{f_SU4578K7PHWw}}" }
    ]
  },
  "actionDefinition": {
    "key": "claygent",
    "displayName": "AI Web Researcher",
    "description": "...",
    "package": { "displayName": "Clay", "icon": "..." },
    "inputParameterSchema": [
      { "name": "param", "type": "text", "description": "...", "optional": false }
    ],
    "outputParameterSchema": [],
    "rateLimitRules": { ... }
  },
  "inputFieldIds": ["f_SU4578K7PHWw"],
  "conditionalRunFieldIds": [],
  "delayFieldIds": []
}
```

### Filter Operators by Type

**Text/Formula (text):** `EQUAL`, `NOT_EQUAL`, `CONTAIN`, `CONTAIN_ANY`, `NOT_CONTAIN`, `NOT_CONTAIN_ANY`, `EMPTY`, `NOT_EMPTY`

**Number:** `EQUAL`, `NOT_EQUAL`, `GREATER_THAN`, `GREATER_THAN_OR_EQUAL`, `LESS_THAN`, `LESS_THAN_OR_EQUAL`, `EMPTY`, `NOT_EMPTY`

**Action:** `HAS_ERROR`, `NOT_ERRORED`, `RESULTS`, `NO_RESULTS`, `HAS_NOT_RUN`, `QUEUED`, `AWAITING_CALLBACK`, `RETRY`, `RUN_CONDITION_NOT_MET`, `IS_STALE`, `IS_RUNNING`, `IS_NOT_RUNNING`

### View Schema

Each view in `table.views[]`:
```json
{
  "id": "gv_G58JF9KCsqjj",
  "name": "Default View",
  "type": "grid"
}
```

## Example Table Schemas (HireWithNear Workspace)

### Company Table Fields (e.g., "Companies with 50+ employees in HS")

| Field ID | Name | Type | Data Type |
|----------|------|------|-----------|
| `f_5jDPpFGrcSkP` | Record ID | number | number |
| `f_5rdJ3sbVarwh` | Headcount | text | text |
| `f_7iuUN2d8PpUY` | Industry | text | text |
| `f_bPqTQQapW9uX` | PE/VC industry? | text | text |
| `f_bu5mcFgUkc5q` | Company Name | text | text |
| `f_GkDT4fqfbUW4` | Country | text | text |
| `f_QgY3VUKuyDTc` | City | text | text |
| `f_SU4578K7PHWw` | Domain | text | text |
| `f_created_at` | Created At | date | date |
| `f_updated_at` | Updated At | date | date |
| `f_7ZUR9mKCuYbo` | People Search | action | json |

### People Table Fields (e.g., "Find People from Companies...")

| Field ID | Name | Type | Data Type | Extracted? |
|----------|------|------|-----------|------------|
| `f_WhvX2wuYvanS` | First Name | formula | text | Yes |
| `f_iRhdwmAR3i3F` | Last Name | formula | text | Yes |
| `f_9BakPTkmKXC6` | Full Name | formula | text | Yes |
| `f_HxFYNCxJR8vf` | Job Title | formula | text | Yes |
| `f_YyQsuKMywhKn` | LinkedIn Profile | formula | url | Yes |
| `f_xeJTeQ5Mqqer` | Company Domain | formula | url | Yes |
| `f_Y2ydfhnWjVCx` | Company name | formula | text | Yes |
| `f_drbnmBTs7qv9` | Location | formula | text | Yes |
| `f_iDsw5yU6F5hS` | Claygent result | formula | url | Yes |
| `f_GcE5ZXhMCnPx` | Career Page URL | action | json | No |
| `f_HxCEfa6jV88j` | Company Table Data | action | json | No |
| `f_WgG6uRxZhMbV` | LinkedIn Job Listings | action | json | No |
| `f_PfRdXj2JyyFd` | Imported Profiles | source | — | No |
| `f_created_at` | Created At | date | date | No |
| `f_updated_at` | Updated At | date | date | No |

### Jobs Table Fields (e.g., "Find Jobs Table")

| Field ID | Name | Type | Data Type | Extracted? |
|----------|------|------|-----------|------------|
| `f_KhNDEkqKU2Jt` | Job Title | formula | text | Yes |
| `f_dG5D7MtSVWJu` | Job LinkedIn URL | formula | url | Yes |
| `f_ppiJeYj5nAZp` | Company Name | formula | text | Yes |
| `f_MU6ieNk4wnHg` | Company Domain | formula | url | Yes |
| `f_V3rAjQ6bfwnU` | Location | formula | text | Yes |
| `f_VPjgnpZDYpMM` | Posted On | formula | date | Yes |
| `f_NWeiA2XUDDv7` | Imported Jobs | source | — | No |
| `f_created_at` | Created At | date | date | No |
| `f_updated_at` | Updated At | date | date | No |

## Source Endpoints

### GET /sources?tableId={tableId}
Returns data sources configured for a table.

**Response (when sources exist):**
```json
[{
  "id": "s_nysdcW5heJSw",
  "workspaceId": 447061,
  "name": "Find People from Companies...",
  "type": "v3-action",
  "typeSettings": {
    "name": "...",
    "idPath": "profile_id",
    "inputs": {
      "limit": "5000",
      "company_table_id": "t_..."
    }
  }
}]
```

## App Account Endpoints

### GET /app-accounts?workspaceId={workspaceId}
Returns all connected app accounts (both user-owned and Clay-managed).

**Response item:**
```json
{
  "id": "aa_xnyqeMxKyUtm",
  "name": "franco-clay-account",
  "appAccountTypeId": "clay",
  "isSharedPublicKey": false,
  "userOwnerId": 496405,
  "workspaceOwnerId": 447061,
  "abilities": { "canUpdate": true, "canDelete": true }
}
```

## Action Endpoints

### GET /actions?workspaceId={workspaceId}
Returns all available enrichment actions (1,132 in HireWithNear workspace).

Actions are grouped by package (provider). Key categories:
- **Clay**: Person/company enrichment, Find People, Find Jobs, Claygent AI
- **Apollo.io**: Find people, enrich contacts, search companies
- **HubSpot**: Create/update/lookup contacts, companies, deals
- **Google Sheets**: Read/write rows, lookup data
- **Anthropic/OpenAI**: AI text generation, analysis
- **Smartlead AI**: Email campaign management
- **LinkedIn**: Profile enrichment, job search
- **Airtable**: CRUD operations on records
- 100+ more enrichment providers

## Billing Endpoints

### GET /subscriptions/{workspaceId}
Returns subscription details.

### GET /billingplans/{workspaceId}?source=frontend
Returns billing plan information.

### GET /credit-accrual?workspaceId={workspaceId}&rewardsOnly=true
Returns credit accrual information.

## Invalid Endpoints (Return 404/NoMatchingURL)

These endpoints do NOT exist:
- `/campaigns` — Clay has no standalone campaigns endpoint
- `/leads` — No leads entity; leads are just rows in tables
- `/contacts` — No contacts entity; contacts are rows in people tables
- `/enrichments` — Use `/actions` instead
- `/integrations` — Use `/app-accounts` instead
- `/webhooks` — No standalone webhooks endpoint

## ID Prefixes

| Prefix | Entity |
|--------|--------|
| `t_` | Table |
| `r_` | Record (row) |
| `f_` | Field (column) — also used for folder IDs in resources |
| `s_` | Source |
| `wb_` | Workbook |
| `gv_` | Grid View |
| `aa_` | App Account |

## Known Workspace Data (HireWithNear)

### Workspace Info
- **Workspace ID**: `447061`
- **Name**: HireWithNear
- **Plan**: proApril2023

### Workspace Users
- **Franco Pereyra** (ID: 496405) — franco@hirewithnear.com
- **María Paz Marengo** (ID: 534026) — paz@hirewithnear.com
- **Gaston Murillo** (ID: 605733) — gaston.murillo@hirewithnear.com
- **Camila Bagnati** (ID: 533723) — camila@hirewithnear.com
- **Kevin Dubon** (ID: 1033117) — kevin.dubon@hirewithnear.com

### User-Owned App Accounts (14)
- Clay: `aa_xnyqeMxKyUtm` (Franco)
- OpenAI GPT-3: `aa_va8uRRPqu4MM` (Gaston)
- Slack: `aa_0syj97bbWVPaiqE7k9E` (Gaston)
- Smartlead AI: `aa_pXfJXCvpNKSx`, `aa_0t3s3zqmKuP8TZVe2su`
- Anthropic: `aa_hcEY4U6rcc8x`
- HubSpot: `aa_0szurc0dCa3scZaCdmR` (Paz), `aa_0syrxp7ZDvWdhZUpnQj` (Gaston), `aa_px5NY4kvFZmJ` (HTTP)
- Google Sheets: `aa_MARWFqEBayyG` (Franco), `aa_0t8yrblGmpjfZZWU5k8` (Gaston)
- PhantomBuster: `aa_0sw0dh1DopArHPR2nEe` (Gaston)
- Clay Sequencer Smartlead: `aa_0t48turTdKnxNpBpp6e`

### Workspace Resources Summary
- **10 Folders**: Sales Development, Open Jobs Campaigns, Retargeting, Marketing, etc.
- **23 Workbooks**: Campaign workbooks, enrichment workbooks
- **20 Tables**: Company lists, people lists, job listings, custom spreadsheets

### Feature Limits
- Workspace row limit: 15,000,000
- Workspace user limit: 10
- Table column limit: 100
- Table computable column limit: 40
- Plan num rows limit: 50,000
- Find people search limit: 50,000
- Scheduled sources limit: 100
- Scheduled tables limit: 100
