# Known Clay Tables — HireWithNear Workspace (447061)

This file contains pre-mapped table IDs and field IDs for all active tables.
When working with a table listed here, use the IDs directly — no API lookup needed.

**Note:** "Written Job URL" and "Job LinkedIn URL" both refer to the LinkedIn job post URL for the open role.

If a table is NOT listed here, fall back to the search workflow in SKILL.md.

**Matching rules:** Match the user's table reference against the name AND all aliases below (case-insensitive). Partial matches count.

**Last updated:** 2026-09-08

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

## 1f. EXP006 — US OJ HMs (Baseline / Challengers) — **PRIMARY for US OJ HMs**

> **This is now the primary table for `us hms`.** Table 2 below is kept as the last fallback —
> it was not replaced, just demoted in the lookup order.
>
> Smartlead campaign `[EXP006] US Open Jobs - HMs - Baseline` maps here.
> The campaign name says "HMs" but the Clay lead tables are named "No HMs" — the workbook is
> `[EXP 006] US OJ HMs` (`wb_0ti9p6bDTqxPMASMtdV`) and its companies table is
> `Companies Table [EXP 006] US OJ HMs` (`t_0ti9szjXjjFNzTjw7o2`). Naming is inconsistent in
> the workspace; trust the EXP number and workbook, not the HM/No-HM suffix. Re-verified 2026-09-08.
>
> **Lookup order:** Baseline → Challenger 1 → Challenger 2 → older US OJ HMs table (section 2).

| Table | Table ID | Records |
|-------|----------|---------|
| Leads [Baseline] - US OJ No HMs | `t_0tia0aux4TRkj9eBYU7` | 1,707 *(verified 2026-09-08 — was 694 on 2026-08-14)* |
| Leads [Challenger 1] - US OJ No HMs - Guess Opener | `t_0tia5n9zXw8tKpoP4kY` | — |
| Leads [Challenger 2] - US OJ No HMs - Need Confirmation | `t_0tiaad4jKBjM5XRtR6E` | — |
| *(fallback)* US Open Jobs - Hiring Managers | `t_0t5pvx3g4o5WfysopqA` | 26,644 — see section 2 |

| Property | Value |
|----------|-------|
| **Aliases** | us hm, us hms, us oj hm, us oj hms, US Open Jobs - HMs, US Open Jobs - Hiring Managers, exp006, exp 006 |
| **Default View ID** | `gv_TgwDWXPdg8Ci` |

| Clay Field Name | Field ID |
|----------------|----------|
| Work Email | `f_0tia0fjpvejxPCJgVRF` *(verified 2026-09-08 — table-specific, NOT the shared `f_0tc2a2q…`)* |
| Written Job URL | `f_QIP4GfH5XFZo` *(verified 2026-09-08)* |
| First Name (cleaned) | `f_hiEPcKlj0lTB` *(verified 2026-09-08)* |
| Last Name (cleaned) | `f_fvs0rK0ntN1H` *(verified 2026-09-08)* |
| Employee Count | `f_0t5mtcfvJknGywASv4z` *(verified 2026-09-08)* |
| Company Name | `f_0tdysmvaFsDXQPs4Ubi` |
| open_role_title | `f_9XFV2vIqjwAh` |

**Note:** The `Work Email` field ID is unique to the EXP006 workbook — the "new primary" shared ID
`f_0tc2a2qEFRZthdct3Cs` does NOT exist here. Challenger 1/2 field IDs are assumed identical to
Baseline (same workbook, cloned schema) but are not yet verified against a real record.

**Verified end-to-end 2026-09-08:** `fetch_lead.py --table "US Open Jobs - HMs"` resolved to this
table and returned `wade@euro-wall.com` → Wade Mammon, a `linkedin.com/jobs/view/` URL, 46 employees.

**Related experiment workbooks** (same naming pattern, field IDs not yet discovered):
`EXP 008` — Baseline `t_0tiokhaWFjR2oD6UDAH`, Challenger 1 `t_0tiokhaGvd7HA2TzT6e`,
Challenger 2 `t_0tiokhatyXjh9pDBxkp`, Challenger 3 `t_0tj7qk6oPa9teQZxRZp`.
`EXP 009` — Baseline `t_0tjmiv7mvocWaH8J7TJ`, Challenger `t_0tjnuu1MkwhU8vavuaP`.

---

## 1g. EXP012 — US OJ No HM, Priority Segments (Engineering / Marketing / Sales-GTM)

> Smartlead campaigns: `[EXP012] US OJ No HM Priority Segments | Engineering | Marketing | Sales/GTM`.
> Also referred to as "US OJ Sales Segment", "US OJ Engineering Segment", etc.
>
> These are **additional** No-HM workflows targeting priority segments — the original generic
> US No-HM chain (1a–1e) still exists and is still the default when no segment is specified.
> Each segment lives in its own workbook but all three share the standard US No-HM schema.

> ⚠️ **All three leads tables are literally named `Leads - US OJ No HMs | Engineering`.**
> Marketing and Sales were cloned from the Engineering workbook and the table name was never
> updated. Identify a segment by its **table ID**, or by the sibling `<Segment> | Companies Table`
> in the same workbook — never by the leads table's own name. Verified 2026-09-08.

| Segment | Table ID | Workbook | Records |
|---------|----------|----------|---------|
| Engineering | `t_0tkqxf9m5kjbQBaj8ze` | `wb_0tkqxf9qc3Sa3s9YgF8` | 1,604 *(verified 2026-09-08)* |
| Marketing | `t_0tkr47cbUzbtpatohRK` | `wb_0tkr47cow6cvXmDF8Av` | 599 *(verified 2026-09-08)* |
| Sales/GTM | `t_0tkr5r1mvuvV42xHHWW` | `wb_0tkr5r1GJomAauCgsTA` | 1,608 *(verified 2026-09-08)* |

| Property | Value |
|----------|-------|
| **Aliases** | us eng, us engineering, us marketing, us mktg, us sales, us gtm, sales/gtm, exp012, US OJ \<segment\> Segment |
| **Default View ID** | `gv_TgwDWXPdg8Ci` (all three) |

All three tables share these field IDs — identical to the standard US No-HM schema:

| Clay Field Name | Field ID |
|----------------|----------|
| Work Email | `f_0tc2a2qEFRZthdct3Cs` *(verified 2026-09-08)* |
| Written Job URL | `f_QIP4GfH5XFZo` *(verified 2026-09-08 — real `linkedin.com/jobs/view/` links)* |
| First Name (cleaned) | `f_hiEPcKlj0lTB` *(verified 2026-09-08)* |
| Last Name (cleaned) | `f_fvs0rK0ntN1H` *(verified 2026-09-08)* |
| Employee Count | `f_0t5mtcfvJknGywASv4z` *(verified 2026-09-08)* |

**Routing:** an unqualified `us no hm` searches the generic chain (1a–1e) first and then falls
through Engineering → Marketing → Sales, so a lead is still found wherever it lives. Naming a
segment jumps straight to that one table. Note that some records have an empty Work Email (the
enrichment has not resolved one yet) — those rows cannot be matched by email.

---

## 1h. EXP010 — Apollo Open Jobs (No HM)

> Smartlead campaigns: `[EXP010] Apollo Open Jobs No HM` and `[EXP010] Apollo Open Jobs HMs`.
> Workbook `wb_0tjm5v6Nzoik7YWmQj9`.

> ⚠️ **There is no Apollo "HMs" leads table.** The workbook contains exactly one leads table
> (the No-HM one below) plus two source tables:
> `Jobs Openings - Apollo Companies` (`t_0tjz56uf9koPtBq78Qe`, type `spreadsheet`) and
> `Apollo companies w/ open jobs` (`t_0tjm5vdaEgTWqjufW5A`).
> The jobs table is keyed by job opening — it has `HM First Name (Cleaned)` and `HM Linkedin URL`
> columns but **no per-lead work email**, so `fetch_lead.py` cannot search it by email.
> If someone asks for "Apollo HMs", route them to the leads table below. Verified 2026-09-08.

| Property | Value |
|----------|-------|
| **Table ID** | `t_0tjzgf1Wv5zQS8vmWxM` |
| **Table Name** | No HM Leads [Baseline] - Apollo US OJ No HMs |
| **Aliases** | apollo, apollo open jobs, apollo no hm, apollo hms, exp010, apollo us oj, apollo baseline |
| **Default View ID** | `gv_TgwDWXPdg8Ci` (verified 2026-09-08 — 7,084 records) |

| Clay Field Name | Field ID |
|----------------|----------|
| Work Email | `f_0tc2a2qEFRZthdct3Cs` *(verified 2026-09-08)* |
| Written Job URL | `f_QIP4GfH5XFZo` *(verified 2026-09-08)* |
| First Name (cleaned) | `f_hiEPcKlj0lTB` *(verified 2026-09-08)* |
| Last Name (cleaned) | `f_fvs0rK0ntN1H` *(verified 2026-09-08)* |
| Employee Count | `f_0t5mtcfvJknGywASv4z` *(verified 2026-09-08)* |

**Note:** Because leads are Apollo-sourced rather than LinkedIn-sourced, `Written Job URL` is
frequently an ATS link (Greenhouse, Lever, Kula.ai, a company careers page) rather than a
`linkedin.com/jobs/view/` URL. The linkedin-job-extractor step must handle non-LinkedIn URLs
for this campaign — don't treat a Greenhouse link as a validation failure. Observed ATS hosts
so far: `careers.kula.ai` (plain WebFetch extracts the full JD with no auth wall — verified
2026-09-08 on `scott@joinautopilot.com`, record `r_0tkp6la96tRyhw3bS3d`).

**Scan cost:** the full 7,084-record scan runs 300 records per batch; a hit around record ~5,000
takes ~17 batches. Allow a 3–5 minute timeout for this table rather than the default.

---

## 2. US Open Jobs — Hiring Managers *(fallback — see 1f for the primary)*

> **No longer the primary for `us hms`.** As of 2026-09-08 the EXP006 baseline table (section 1f)
> is searched first; this table is the last link in that chain. It is still fully wired up — leads
> that live only here are still found, just after the three EXP006 tables are checked.

| Property | Value |
|----------|-------|
| **Table ID** | `t_0t5pvx3g4o5WfysopqA` |
| **Aliases** | *(none — reached via the 1f fallback chain)* |
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
| **Default View ID** | `gv_TgwDWXPdg8Ci` (**17,428 records** as of 2026-09-08 — large table, scan takes ~2.5 min; allow a generous timeout) |

| Clay Field Name | Field ID |
|----------------|----------|
| Work Email | `f_0t063ygVDhWMs5MT4MD` |
| Job LinkedIn URL | `f_0t06147KZtafpAaiDTz` |
| First Name (cleaned) | `f_0t063qfcKw3gnzRcxxG` |
| Last Name (cleaned) | `f_0t063qh6gvgnYPy4av4` |
| Employee Count | `f_0t062fr5fKsUy27nJhf` |

All five field IDs re-verified 2026-09-08 on lead `margarita.fernandez@22-tech.com` (record `r_0tkuhqj3pZVpvR3xzn9`, found ~row 13,500 — expect a full-length scan for recent additions).

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

## Gotchas for ad-hoc Clay scripts (verified 2026-09-08)

When writing a one-off Clay script rather than using `scripts/fetch_lead.py`:

1. **`/auth/login` needs all of these or it returns HTTP 400:**
   - body `{"email", "password", "source": "web"}` — omitting `"source"` fails
   - headers `Origin: https://app.clay.com` and `Referer: https://app.clay.com/` — omitting them fails
2. **`load_dotenv()` with no argument raises `AssertionError`** when the script is piped in via
   stdin (`python3 - <<EOF`), because it walks the call stack to find the .env. Always pass the
   path explicitly: `load_dotenv("/abs/path/.env")`. Symptom: credentials silently empty → 400.
3. **`timeout` is not available on macOS** — don't wrap long scans in it; pass a Bash tool timeout.
4. Reuse `scripts/find_by_domain.py` instead of rewriting a scanner; it already handles auth,
   the table registry, fallback chains and batching.
