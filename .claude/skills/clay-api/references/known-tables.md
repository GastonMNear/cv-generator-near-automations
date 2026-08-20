# Known Clay Tables — HireWithNear Workspace (447061)

This file contains pre-mapped table IDs and field IDs for all active tables.
When working with a table listed here, use the IDs directly — no API lookup needed.

**Note:** "Written Job URL" and "Job LinkedIn URL" both refer to the LinkedIn job post URL for the open role.

If a table is NOT listed here, fall back to the search workflow in SKILL.md.

**Matching rules:** Match the user's table reference against the name AND all aliases below (case-insensitive). Partial matches count.

**Last updated:** 2026-07-02

---

## 1. US Open Jobs — No Hiring Manager

> **Lookup order:** 1a → 1b → 1c → 1d → 1e. Script tries each in sequence; stops at first match.

### 1a. Leads [Baseline] - US OJ No HMs | Candidate-led CTA (new primary)

| Property | Value |
|----------|-------|
| **Table ID** | `t_0thes7nxCFpHX8XY2gT` |
| **Aliases** | US OJ - No HM, US OJ - No hiring managers |
| **Default View ID** | `gv_TgwDWXPdg8Ci` (verified 2026-07-02 — 5,792 records) |

| Clay Field Name | Field ID |
|----------------|----------|
| Work Email | `f_0tc2a2qEFRZthdct3Cs` *(verified 2026-07-02)* |
| Written Job URL | `f_QIP4GfH5XFZo` *(verified 2026-07-02)* |
| First Name (cleaned) | `f_hiEPcKlj0lTB` *(verified 2026-07-02)* |
| Last Name (cleaned) | `f_fvs0rK0ntN1H` *(verified 2026-07-02)* |
| Employee Count | `f_0t5mtcfvJknGywASv4z` *(verified 2026-07-02)* |

### 1b. Leads [Challenger] - US OJ No HMs | Routing CTA (new primary)

| Property | Value |
|----------|-------|
| **Table ID** | `t_0thg92hZWdvUw75QNRx` |
| **Default View ID** | `gv_TgwDWXPdg8Ci` (verified 2026-07-02 — 5,379 records) |

| Clay Field Name | Field ID |
|----------------|----------|
| Work Email | `f_0tc2a2qEFRZthdct3Cs` *(verified 2026-07-02)* |
| Written Job URL | `f_QIP4GfH5XFZo` *(verified 2026-07-02)* |
| First Name (cleaned) | `f_hiEPcKlj0lTB` *(verified 2026-07-02)* |
| Last Name (cleaned) | `f_fvs0rK0ntN1H` *(verified 2026-07-02)* |
| Employee Count | `f_0t5mtcfvJknGywASv4z` *(verified 2026-07-02)* |

**Note:** 1a and 1b are an A/B test pair (Baseline candidate-led CTA vs. Challenger routing CTA) with identical schema/field IDs — both are searched before falling back to the older tables below.

### 1c. US Open Jobs - No HM (fallback)

| Property | Value |
|----------|-------|
| **Table ID** | `t_0tdyro7QesUNY3WJrt2` |
| **Default View ID** | `gv_TgwDWXPdg8Ci` |

| Clay Field Name | Field ID |
|----------------|----------|
| Work Email | `f_0tc2a2qEFRZthdct3Cs` *(assumed)* |
| Written Job URL | `f_QIP4GfH5XFZo` *(assumed)* |
| First Name (cleaned) | `f_hiEPcKlj0lTB` *(assumed)* |
| Last Name (cleaned) | `f_fvs0rK0ntN1H` *(assumed)* |
| Employee Count | `f_0t5mtcfvJknGywASv4z` *(assumed)* |

### 1d. US Open Jobs — No Hiring Manager (fallback)

| Property | Value |
|----------|-------|
| **Table ID** | `t_0t59d2y3ZuD4396Kz5B` |
| **Default View ID** | `gv_TgwDWXPdg8Ci` |

| Clay Field Name | Field ID |
|----------------|----------|
| Work Email | `f_0tc2a2qEFRZthdct3Cs` |
| Written Job URL | `f_QIP4GfH5XFZo` |
| First Name (cleaned) | `f_hiEPcKlj0lTB` |
| Last Name (cleaned) | `f_fvs0rK0ntN1H` |
| Employee Count | `f_0t5mtcfvJknGywASv4z` |

### 1e. Copy of Leads - US OJ No Hiring Manager (fallback)

| Property | Value |
|----------|-------|
| **Table ID** | `t_0tbt48xVeCFCi8pFzip` |
| **Default View ID** | `gv_TgwDWXPdg8Ci` |

| Clay Field Name | Field ID |
|----------------|----------|
| Work Email | `f_0tbt65uGbguMonif8dU` |
| Written Job URL | `f_QIP4GfH5XFZo` |
| First Name (cleaned) | `f_hiEPcKlj0lTB` |
| Last Name (cleaned) | `f_fvs0rK0ntN1H` |
| Employee Count | `f_0t5mtcfvJknGywASv4z` |

---

## 2. US Open Jobs — Hiring Managers

| Property | Value |
|----------|-------|
| **Table ID** | `t_0t5pvx3g4o5WfysopqA` |
| **Aliases** | US OJ - HMs, US OJ - Hiring Managers |
| **Default View ID** | `gv_TgwDWXPdg8Ci` (26,644 records) |

| Clay Field Name | Field ID |
|----------------|----------|
| Work Email | `f_0t063ygVDhWMs5MT4MD` |
| Job LinkedIn URL | `f_0t06147KZtafpAaiDTz` |
| First Name (cleaned) | `f_0t063qfcKw3gnzRcxxG` |
| Last Name (cleaned) | `f_0t063qh6gvgnYPy4av4` |
| Employee Count | `f_0t062fr5fKsUy27nJhf` |

---

## 3. Asia Open Jobs — Hiring Managers

> **Lookup order:** 3a → 3b. Script tries each in sequence; stops at first match.

### 3a. ASIA | Under 50 emp. Leads (HMs)

| Property | Value |
|----------|-------|
| **Table ID** | `t_0tfca9kUUpNpysMebYP` |
| **Aliases** | Asia OJ HMs, Asia Open Jobs HMs, Asia Open Jobs - Hiring Managers, Asia OJ - Hiring Managers |
| **Default View ID** | `gv_0tfca9kP8mpqjWyXaQC` (verified 2026-07-02 — 178 records) |

| Clay Field Name | Field ID |
|----------------|----------|
| Work Email | `f_0tfcagrbcgwPoNj5Bw9` *(verified 2026-07-02)* |
| Job LinkedIn URL | `f_0tfcagnvCZcGMfpuHCq` *(verified 2026-07-02)* |
| First Name (cleaned) | `f_0tfcagqpQD5639msG25` *(verified 2026-07-02)* |
| Last Name (cleaned) | `f_0tfcagrnuA4eCac4qjw` *(verified 2026-07-02)* |
| Employee Count | `f_0tfcagpR5MQpQ4jSXXj` *(verified 2026-07-02)* |

### 3b. ASIA | +50 emp. Leads (HMs)

| Property | Value |
|----------|-------|
| **Table ID** | `t_0tfe0wuWVAJQcbyENqB` |
| **Default View ID** | `gv_0tfca9kP8mpqjWyXaQC` (verified 2026-07-02 — 234 records) |

| Clay Field Name | Field ID |
|----------------|----------|
| Work Email | `f_0tfcagrbcgwPoNj5Bw9` *(verified 2026-07-02)* |
| Job LinkedIn URL | `f_0tfcagnvCZcGMfpuHCq` *(verified 2026-07-02)* |
| First Name (cleaned) | `f_0tfcagqpQD5639msG25` *(verified 2026-07-02)* |
| Last Name (cleaned) | `f_0tfcagrnuA4eCac4qjw` *(verified 2026-07-02)* |
| Employee Count | `f_0tfcagpR5MQpQ4jSXXj` *(verified 2026-07-02)* |

**Note:** 3a (under 50 employees) and 3b (50+ employees) are employee-count-segmented splits of the same Asia HMs source with identical schema/field IDs. No older fallback table exists for Asia — these are brand new workflows.

---

## 4. Asia Open Jobs — No Hiring Managers

> **Lookup order:** 4a → 4b. Script tries each in sequence; stops at first match.

### 4a. ASIA | Under 50 emp. Leads (No HMs)

| Property | Value |
|----------|-------|
| **Table ID** | `t_0tfe657PnDUhThtbaj5` |
| **Aliases** | Asia OJ No HMs, Asia Open Jobs No HMs, Asia Open Jobs - No Hiring Managers, Asia OJ - No Hiring Managers |
| **Default View ID** | `gv_0tfca9kP8mpqjWyXaQC` (verified 2026-07-02 — 1,247 records) |

| Clay Field Name | Field ID |
|----------------|----------|
| Work Email | `f_0tfe835CUft9fp4UY9k` *(verified 2026-07-02)* |
| Job LinkedIn Url | `f_0tfe6id8cNEySpUT55j` *(verified 2026-07-02)* |
| First Name (cleaned) | `f_0tfe7zarivxCppNH38R` *(verified 2026-07-02)* |
| Last Name (cleaned) | `f_0tfe7zfeUn4vVrfDEQu` *(verified 2026-07-02)* |
| Employee Count (merge) | `f_0tfe6ihoVtWsNggyTCo` *(verified 2026-07-02)* |

### 4b. ASIA | +50 emp. Leads (No HMs)

| Property | Value |
|----------|-------|
| **Table ID** | `t_0tfe8z2ukw66TNuPgpp` |
| **Default View ID** | `gv_0tfca9kP8mpqjWyXaQC` (verified 2026-07-02 — 4,555 records) |

| Clay Field Name | Field ID |
|----------------|----------|
| Work Email | `f_0tfe835CUft9fp4UY9k` *(verified 2026-07-02)* |
| Job LinkedIn Url | `f_0tfe6id8cNEySpUT55j` *(verified 2026-07-02)* |
| First Name (cleaned) | `f_0tfe7zarivxCppNH38R` *(verified 2026-07-02)* |
| Last Name (cleaned) | `f_0tfe7zfeUn4vVrfDEQu` *(verified 2026-07-02)* |
| Employee Count (merge) | `f_0tfe6ihoVtWsNggyTCo` *(verified 2026-07-02)* |

**Note:** 4a and 4b are employee-count-segmented splits with identical schema/field IDs. Use "Employee Count (merge)" (`f_0tfe6ihoVtWsNggyTCo`), NOT the plain "Employee Count" field (`f_0tfe96sGWcxbnKhgV4u`) — the plain field is empty for every record in table 4b (verified 2026-07-02, 20/20 sample), while the merge field is reliably populated in both 4a and 4b. No older fallback table exists for Asia — these are brand new workflows.

---

## 5. LatAm Open Jobs — No HMs

> **Lookup order:** 3a → 3b. Script tries each in sequence; stops at first match.

### 3a. LatAm Open Jobs - No HMs (new primary)

| Property | Value |
|----------|-------|
| **Table ID** | `t_0te5kjxke6yWVRzedb7` |
| **Aliases** | LatAm Open Jobs - No HMs, LatAm OJ - No HMs |
| **Default View ID** | `gv_TgwDWXPdg8Ci` (verified 2026-04-30 — 1,409 records) |

| Clay Field Name | Field ID |
|----------------|----------|
| Work Email | `f_0tc2a2qEFRZthdct3Cs` *(verified 2026-04-30)* |
| Written Job URL | `f_QIP4GfH5XFZo` *(verified 2026-04-30)* |
| First Name (cleaned) | `f_hiEPcKlj0lTB` *(verified 2026-04-30)* |
| Last Name (cleaned) | `f_fvs0rK0ntN1H` *(verified 2026-04-30)* |
| Employee Count | `f_0t5mtcfvJknGywASv4z` *(verified 2026-04-30)* |

**Note:** Work Email field ID is `f_0tc2a2qEFRZthdct3Cs` — same as US No HM tables, NOT the same as table 3b (`f_0tckabyNnK9wNBNNUWm`). Employee Count also differs from 3b. Verified on first successful run 2026-04-30.

### 3b. LatAm Open Jobs — No HMs

| Property | Value |
|----------|-------|
| **Table ID** | `t_aNvk4jWMNeG7` |
| **Default View ID** | `gv_TgwDWXPdg8Ci` (3,314 records) |

| Clay Field Name | Field ID |
|----------------|----------|
| Work Email | `f_0tckabyNnK9wNBNNUWm` |
| Written Job URL | `f_QIP4GfH5XFZo` |
| First Name (cleaned) | `f_hiEPcKlj0lTB` |
| Last Name (cleaned) | `f_fvs0rK0ntN1H` |
| Employee Count | `f_0t6acqvuQxjjQNTWhbK` |

**Note:** "Validated Email" (`f_SUTHMU5bi2XD`) was removed from this table. "Work Email" is the new consolidated formula field (verified 2026-03-27). Table grew from 63 → 85 fields (full email enrichment pipeline added).

---

## 6. LatAm Open Jobs — Hiring Managers

| Property | Value |
|----------|-------|
| **Table ID** | `t_0t6ghvgCsvvvqAus4bp` |
| **Aliases** | LatAm Open Jobs - Hiring Managers, LatAm OJ - HMs |
| **Default View ID** | `gv_TgwDWXPdg8Ci` (**45,127 records** — large table, scan takes ~85s) |

| Clay Field Name | Field ID |
|----------------|----------|
| Work Email | `f_0t063ygVDhWMs5MT4MD` |
| Job LinkedIn URL | `f_0t06147KZtafpAaiDTz` |
| First Name (cleaned) | `f_0t063qfcKw3gnzRcxxG` |
| Last Name (cleaned) | `f_0t063qh6gvgnYPy4av4` |
| Employee Count | `f_0t062fr5fKsUy27nJhf` |

---

## 7. Canada Open Jobs — No HM

> **Lookup order:** 5a → 5b. Script tries each in sequence; stops at first match.

### 5a. Canada Open Jobs - No HM (new primary)

| Property | Value |
|----------|-------|
| **Table ID** | `t_0te5lh6AoWkxd39ktT8` |
| **Aliases** | Canada Open Jobs - No Hiring Managers, Canada Open Jobs - No HM, Canada OJ - No HMs |
| **Default View ID** | `gv_3cMh8vzuFqm4` (verified 2026-04-30 — 700 records) |

| Clay Field Name | Field ID |
|----------------|----------|
| Work Email | `f_0tc2a2qEFRZthdct3Cs` *(verified 2026-04-30)* |
| Job LinkedIn Url | `f_0taawsuMjxnV74YtCZ8` *(assumed — not yet verified)* |
| First Name (clean) | `f_0taaxkd4HWteakU9qwZ` *(assumed — not yet verified)* |
| Last Name (clean) | `f_0taaxkl9BQmnF5u9PVG` *(assumed — not yet verified)* |
| Employee Count | `f_0t5mtcfvJknGywASv4z` *(verified 2026-04-30)* |

**Note:** Work Email and Employee Count share the same field IDs as the US and LatAm new primary tables — NOT the same as table 5b. Pattern: all "new primary" tables use `f_0tc2a2qEFRZthdct3Cs` for Work Email and `f_0t5mtcfvJknGywASv4z` for Employee Count. Verified 2026-04-30.

### 5b. Canada Open Jobs — No HM

| Property | Value |
|----------|-------|
| **Table ID** | `t_0taasak5KAa5zbTmTJd` |
| **Default View ID** | `gv_3cMh8vzuFqm4` (6,004 records) |

| Clay Field Name | Field ID |
|----------------|----------|
| Work Email | `f_0taaxyjNBGfFWKYUnxK` |
| Job LinkedIn Url | `f_0taawsuMjxnV74YtCZ8` |
| First Name (clean) | `f_0taaxkd4HWteakU9qwZ` |
| Last Name (clean) | `f_0taaxkl9BQmnF5u9PVG` |
| Employee Count | `f_0taayd3VvuPn9po6cYQ` |

---

## 8. Canada Open Jobs — Hiring Managers

| Property | Value |
|----------|-------|
| **Table ID** | `t_0t746txPqz5sjFMtut2` |
| **Aliases** | Canada Open Jobs - HMs, Canada OJ - HMs |
| **Default View ID** | `gv_TgwDWXPdg8Ci` (3,449 records) |

| Clay Field Name | Field ID |
|----------------|----------|
| Work Email | `f_0t063ygVDhWMs5MT4MD` |
| Job LinkedIn URL | `f_0t06147KZtafpAaiDTz` |
| First Name (cleaned) | `f_0t063qfcKw3gnzRcxxG` |
| Last Name (cleaned) | `f_0t063qh6gvgnYPy4av4` |
| Employee Count | `f_0t062fr5fKsUy27nJhf` |
