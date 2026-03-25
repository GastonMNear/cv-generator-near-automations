# Known Clay Tables — HireWithNear Workspace (447061)

This file contains pre-mapped table IDs for frequently used tables.
When working with a table listed here, use the ID directly — no API lookup needed.

If a table is NOT listed here or the reference is ambiguous, fall back to the search workflow in SKILL.md.

**Matching rules:** Match the user's table reference against the name AND all aliases below (case-insensitive). Partial matches count — e.g. "US OJ no HM" matches table #1.

---

## 1. US Open Jobs - No Hiring Manager

| Property | Value |
|----------|-------|
| **Table ID** | `t_0t59d2y3ZuD4396Kz5B` |
| **Aliases** | US OJ - No HM, US OJ - No hiring managers |
| **Default View ID** | `gv_TgwDWXPdg8Ci` |

**Field IDs** (verified 2026-03-23):

| Field | ID | Name | Notes |
|-------|----|------|-------|
| Email (primary) | `f_0tc2a2qEFRZthdct3Cs` | Work Email | Plain email, most reliable — use this first |
| Email (fallback) | `f_SUTHMU5bi2XD` | Validated Email | May be empty for some leads |
| Email (fallback 2) | `f_0tc2a2nscarDNn3TRFU` | Find work email | Has `✅` prefix — strip before comparing |
| LinkedIn Job URL | `f_QIP4GfH5XFZo` | Written Job URL | |
| Full Name | `f_rOj3SQqDVF8U` | Full Name (cleaned) | |
| Employee Count | `f_0t5mtcfvJknGywASv4z` | Employee Count | |
| First Name | `f_hiEPcKlj0lTB` | First Name (cleaned) | |
| Last Name | `f_fvs0rK0ntN1H` | Last Name (cleaned) | |
| Open Role Title | `f_9XFV2vIqjwAh` | open_role_title | |

**Email field note (discovered 2026-03-23):** `f_SUTHMU5bi2XD` (Validated Email) is empty for some leads. Always search `f_0tc2a2qEFRZthdct3Cs` (Work Email) first — it is populated more consistently.

**Fallback table:** If a lead is not found here, also search `t_0tbt48xVeCFCi8pFzip` (Copy of Leads - US OJ no hiring manager). Same aliases, same view ID (`gv_TgwDWXPdg8Ci`, 509 records). Email field is different — see table 1b below.

---

## 1b. Copy of Leads - US OJ no hiring manager (fallback)

| Property | Value |
|----------|-------|
| **Table ID** | `t_0tbt48xVeCFCi8pFzip` |
| **Aliases** | Same as table 1 — use as fallback when lead not found in `t_0t59d2y3ZuD4396Kz5B` |
| **Default View ID** | `gv_TgwDWXPdg8Ci` (509 records) |

**Field IDs** (verified 2026-03-16):

| Field | ID | Name |
|-------|----|------|
| Email (primary) | `f_0tbt65kNZrgzvDoEAmi` | Find work email (has ✅ prefix — strip when comparing) |
| Email (plain) | `f_0tbt65uGbguMonif8dU` | Work email (no prefix) |
| LinkedIn Job URL | `f_QIP4GfH5XFZo` | Written Job URL |
| Full Name | `f_rOj3SQqDVF8U` | Full Name (cleaned) |
| Employee Count | `f_0t5mtcfvJknGywASv4z` | Employee Count |
| First Name | `f_hiEPcKlj0lTB` | First Name (cleaned) |
| Last Name | `f_fvs0rK0ntN1H` | Last Name (cleaned) |
| Open Role Title | `f_9XFV2vIqjwAh` | open_role_title |
| Company Name | `f_PKjeJjHjbIXX` | company_name |

**Notes:**
- Email is stored with "✅ " prefix in `f_0tbt65kNZrgzvDoEAmi` — strip before comparing
- LinkedIn Job URL and Name/EC field IDs are identical to the main table
| Company Name | `f_PKjeJjHjbIXX` | company_name |

---

## 2. US Open Jobs - Hiring Managers

| Property | Value |
|----------|-------|
| **Table ID** | `t_0t5pvx3g4o5WfysopqA` |
| **Aliases** | US OJ - HMs, US OJ - Hiring Managers |
| **Default View ID** | `gv_TgwDWXPdg8Ci` (Default View — 24,000+ records) |

**Field IDs** (verified 2026-03-16):

| Field | ID | Name |
|-------|----|------|
| Email | `f_0t063ygVDhWMs5MT4MD` | Work Email |
| LinkedIn Job URL | `f_0t06147KZtafpAaiDTz` | Job LinkedIn URL |
| Full Name | `f_0t063rgYs9kuKxSpxpT` | Full Name (cleaned) |
| First Name | `f_0t063qfcKw3gnzRcxxG` | First Name (cleaned) |
| Last Name | `f_0t063qh6gvgnYPy4av4` | Last Name (cleaned) |
| Employee Count | `f_0t062fr5fKsUy27nJhf` | Employee Count |
| Company Name | `f_0t060r658Wja27AstZG` | Company Name |
| Job Title | `f_0t060rsDJXy6EbBFdCD` | Imported Job Title |

**Notes:**
- Table has 4 views: `gv_UAchMQstUgXy` (Errored Rows, ~424 records), `gv_TgwDWXPdg8Ci` (Default View, 24,000+), `gv_pHj6RUyXmFjy` (Fully Enriched Rows), `gv_3cMh8vzuFqm4` (Non Enrichment Columns)
- **Always use `gv_TgwDWXPdg8Ci` (Default View)** — first view is Errored Rows with only ~424 records
- Email is in "Work Email" field — fields named "Email One/Two/Three" contain email draft copy, NOT contact emails
- Table has 98 fields total; same schema as Canada Open Jobs | HMs

---

## 3. LatAm Open Jobs - No HMs - All openings - v1

| Property | Value |
|----------|-------|
| **Table ID** | `t_aNvk4jWMNeG7` |
| **Aliases** | LatAm Open Jobs - No HMs, LatAm OJ - No HMs |
| **Default View ID** | `gv_TgwDWXPdg8Ci` |

**Field IDs** (verified 2026-03-16):

| Field | ID | Name |
|-------|----|------|
| Email | `f_SUTHMU5bi2XD` | Validated Email |
| LinkedIn Job URL | `f_QIP4GfH5XFZo` | Written Job URL |
| Full Name | `f_rOj3SQqDVF8U` | Full Name (cleaned) |
| Employee Count | `f_0t6acqvuQxjjQNTWhbK` | Employee Count |
| First Name | `f_hiEPcKlj0lTB` | First Name (cleaned) |
| Last Name | `f_fvs0rK0ntN1H` | Last Name (cleaned) |
| Open Role Title | `f_9XFV2vIqjwAh` | open_role_title |
| Company Name | `f_PKjeJjHjbIXX` | company_name |

---

## 4. LatAm Open Jobs - Hiring Managers (all)

| Property | Value |
|----------|-------|
| **Table ID** | `t_0t6ghvgCsvvvqAus4bp` |
| **Aliases** | LatAm Open Jobs - Hiring Managers, LatAm OJ - Hiring Managers, LatAm OJ - HMs |
| **Default View ID** | `gv_TgwDWXPdg8Ci` (assumed — same schema as US/Canada HMs, unverified) |

**Field IDs** (assumed same schema as US HMs / Canada HMs — verify on first run):

| Field | ID | Name |
|-------|----|------|
| Email | `f_0t063ygVDhWMs5MT4MD` | Work Email |
| LinkedIn Job URL | `f_0t06147KZtafpAaiDTz` | Job LinkedIn URL |
| Full Name | `f_0t063rgYs9kuKxSpxpT` | Full Name (cleaned) |
| Employee Count | `f_0t062fr5fKsUy27nJhf` | Employee Count |

**Notes:**
- Field IDs assumed from US HMs / Canada HMs (same 98-field schema pattern) — update this entry after first successful run

---

## 5. Canada Open Jobs | No HM | All openings (remote)

| Property | Value |
|----------|-------|
| **Table ID** | `t_0taasak5KAa5zbTmTJd` |
| **Aliases** | Canada Open Jobs - No Hiring Managers, Canada Open Jobs - No HM, Canada OJ - No HMs |
| **Default View ID** | `gv_3cMh8vzuFqm4` |

**Field IDs** (verified 2026-03-16):

| Field | ID | Name |
|-------|----|------|
| Email (primary) | `f_0taaxydYnGTxbpHQFnp` | Find work email |
| Email (validated) | `f_0taaxyjNBGfFWKYUnxK` | Work Email |
| LinkedIn Job URL | `f_0taawsuMjxnV74YtCZ8` | Job LinkedIn Url |
| Full Name (clean) | `f_0taaxktKoU2pAViurV7` | Full Name (clean) |
| Full Name (raw) | `f_0taaxdmchK4dMMphf5J` | Full Name (uncleaned) |
| First Name | `f_0taaxkd4HWteakU9qwZ` | First Name (clean) |
| Last Name | `f_0taaxkl9BQmnF5u9PVG` | Last Name (clean) |
| Employee Count | `f_0taay8jKxJZYCy4AoV6` | Employee Count |
| Job Title | `f_0taawst2p7ggbxro37b` | Imported Job Title |
| Company Name | `f_0taawstSxwvwpTZE9Ay` | Imported Company Name |
| Lead Title | `f_0taaxpwuXVMYbRoGAA7` | Lead Title |

**Notes:**
- Email search must check BOTH `Find work email` AND `Work Email` — "Find Work Email (5)" is a separate enrichment field and may not match
- Email values in `Find work email` may be prefixed with "✅ " — strip this when comparing
- Table has 92 fields; "Email One/Two/Three" fields contain draft email copy, NOT contact email addresses

---

## 6. Canada Open Jobs | HMs | All Openings

| Property | Value |
|----------|-------|
| **Table ID** | `t_0t746txPqz5sjFMtut2` |
| **Aliases** | Canada Open Jobs - HMs, Canada OJ - HMs |
| **Default View ID** | `gv_TgwDWXPdg8Ci` |

**Field IDs** (verified 2026-03-16):

| Field | ID | Name |
|-------|----|------|
| Email | `f_0t063ygVDhWMs5MT4MD` | Work Email |
| LinkedIn Job URL | `f_0t06147KZtafpAaiDTz` | Job LinkedIn URL |
| Full Name | `f_0t063rgYs9kuKxSpxpT` | Full Name (cleaned) |
| First Name | `f_0t063qfcKw3gnzRcxxG` | First Name (cleaned) |
| Last Name | `f_0t063qh6gvgnYPy4av4` | Last Name (cleaned) |
| Employee Count | `f_0t062fr5fKsUy27nJhf` | Employee Count |
| Company Name | `f_0t060r658Wja27AstZG` | Company Name |
| Job Title | `f_0t060rsDJXy6EbBFdCD` | Imported Job Title |

**Notes:**
- Email is in "Work Email" field, NOT "Email One" (which contains email draft text)
- Search must use view `gv_TgwDWXPdg8Ci` (Default View) — first view (Errored Rows) only has 102 records
