# Known Clay Tables — HireWithNear Workspace (447061)

This file contains pre-mapped table IDs and field IDs for all active tables.
When working with a table listed here, use the IDs directly — no API lookup needed.

**Note:** "Written Job URL" and "Job LinkedIn URL" both refer to the LinkedIn job post URL for the open role.

If a table is NOT listed here, fall back to the search workflow in SKILL.md.

**Matching rules:** Match the user's table reference against the name AND all aliases below (case-insensitive). Partial matches count.

**Last updated:** 2026-03-26

---

## 1. US Open Jobs — No Hiring Manager (new primary)

> **Lookup order:** 1a → 1b → 1c. Script tries each in sequence; stops at first match.

### 1a. US Open Jobs - No HM (new primary)

| Property | Value |
|----------|-------|
| **Table ID** | `t_0tdyro7QesUNY3WJrt2` |
| **Aliases** | US OJ - No HM, US OJ - No hiring managers |
| **Default View ID** | `gv_TgwDWXPdg8Ci` (assumed — verify on first run) |

| Clay Field Name | Field ID |
|----------------|----------|
| Work Email | `f_0tc2a2qEFRZthdct3Cs` *(assumed — update if wrong)* |
| Written Job URL | `f_QIP4GfH5XFZo` *(assumed)* |
| First Name (cleaned) | `f_hiEPcKlj0lTB` *(assumed)* |
| Last Name (cleaned) | `f_fvs0rK0ntN1H` *(assumed)* |
| Employee Count | `f_0t5mtcfvJknGywASv4z` *(assumed)* |

**Note:** Field IDs copied from table 1b as starting assumption. Update after first successful run.

### 1b. US Open Jobs — No Hiring Manager

| Property | Value |
|----------|-------|
| **Table ID** | `t_0t59d2y3ZuD4396Kz5B` |
| **Default View ID** | `gv_TgwDWXPdg8Ci` (15,740 records) |

| Clay Field Name | Field ID |
|----------------|----------|
| Work Email | `f_0tc2a2qEFRZthdct3Cs` |
| Written Job URL | `f_QIP4GfH5XFZo` |
| First Name (cleaned) | `f_hiEPcKlj0lTB` |
| Last Name (cleaned) | `f_fvs0rK0ntN1H` |
| Employee Count | `f_0t5mtcfvJknGywASv4z` |

### 1c. Copy of Leads — US OJ No Hiring Manager (last fallback)

| Property | Value |
|----------|-------|
| **Table ID** | `t_0tbt48xVeCFCi8pFzip` |
| **Default View ID** | `gv_TgwDWXPdg8Ci` (509 records) |

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

## 3. LatAm Open Jobs — No HMs

> **Lookup order:** 3a → 3b. Script tries each in sequence; stops at first match.

### 3a. LatAm Open Jobs - No HMs (new primary)

| Property | Value |
|----------|-------|
| **Table ID** | `t_0te5kjxke6yWVRzedb7` |
| **Aliases** | LatAm Open Jobs - No HMs, LatAm OJ - No HMs |
| **Default View ID** | `gv_TgwDWXPdg8Ci` (assumed — verify on first run) |

| Clay Field Name | Field ID |
|----------------|----------|
| Work Email | `f_0tckabyNnK9wNBNNUWm` *(assumed — update if wrong)* |
| Written Job URL | `f_QIP4GfH5XFZo` *(assumed)* |
| First Name (cleaned) | `f_hiEPcKlj0lTB` *(assumed)* |
| Last Name (cleaned) | `f_fvs0rK0ntN1H` *(assumed)* |
| Employee Count | `f_0t6acqvuQxjjQNTWhbK` *(assumed)* |

**Note:** Field IDs copied from table 3b as starting assumption. Update after first successful run.

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

## 4. LatAm Open Jobs — Hiring Managers

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

## 5. Canada Open Jobs — No HM

> **Lookup order:** 5a → 5b. Script tries each in sequence; stops at first match.

### 5a. Canada Open Jobs - No HM (new primary)

| Property | Value |
|----------|-------|
| **Table ID** | `t_0te5lh6AoWkxd39ktT8` |
| **Aliases** | Canada Open Jobs - No Hiring Managers, Canada Open Jobs - No HM, Canada OJ - No HMs |
| **Default View ID** | `gv_3cMh8vzuFqm4` (assumed — verify on first run) |

| Clay Field Name | Field ID |
|----------------|----------|
| Work Email | `f_0taaxyjNBGfFWKYUnxK` *(assumed — update if wrong)* |
| Job LinkedIn Url | `f_0taawsuMjxnV74YtCZ8` *(assumed)* |
| First Name (clean) | `f_0taaxkd4HWteakU9qwZ` *(assumed)* |
| Last Name (clean) | `f_0taaxkl9BQmnF5u9PVG` *(assumed)* |
| Employee Count | `f_0taayd3VvuPn9po6cYQ` *(assumed)* |

**Note:** Field IDs copied from table 5b as starting assumption. Update after first successful run.

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

## 6. Canada Open Jobs — Hiring Managers

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
