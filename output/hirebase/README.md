# Hirebase sub_industry filter

Built 2026-10-20 from `GET /v2/jobs/data/industries` and `/subindustries`. No search calls were made.

## Files
| File | What it is |
|---|---|
| `hirebase_subindustries_raw.json` | `{industry: [subindustries]}` exactly as the API returned them |
| `fetch_errors.log` | Non-200 responses |
| `industry_mapping.csv` | 487 rows: HubSpot industry → Hirebase (industry, sub_industry), confidence, note |
| `excluded_subindustries.csv` | Every left-out pair, with the reason |
| `sub_industry_filter.txt` / `.json` | **The final filter**: 325 unique strings, comma-separated / JSON array |
| `build_mapping.py` | Source of truth. Edit the mapping here and re-run `python3 build_mapping.py` |

## Counts
- 25 industries listed; 23 returned subindustries. **`Other` and `Retail` return 404 "Industry not found"** even though `/industries` lists them, so all retail sits under `Retail & Wholesale`.
- 429 (industry, sub) pairs = 424 unique strings. Five strings appear under two industries: Publishing, Food & Beverage, Architecture & Design, Real Estate Technology, Executive Office.
- **Included: 329 pairs → 325 unique strings.** Excluded: 100 pairs, including all of Public Administration (30) and Public Safety (16).
- All 89 HubSpot industries are in the CSV. Human Resources and Farming are marked `excluded` (Gaston, 2026-10-20) and contribute nothing to the filter.

## How the filter behaves (from the 2026-10-20 test call)
- `sub_industry` works on its own; no `industry` param is needed.
- It matches on **company** tags (`company_data.subindustries`), not on the job itself.
- Values combine with OR. A company tagged "AI & ML" matched `["AI & ML","Fintech"]` without being Fintech.
- So a duplicate string (e.g. "Publishing") only needs to appear once, and you can't include it under one industry while excluding it under another.

## Review these: low-confidence mappings
| HubSpot industry | Mapped to | Suggested `company_keywords` |
|---|---|---|
| Consumer Services | E-Commerce & Internet Services; Personal Care & Household | `home services`, `consumer services` |

Medium-confidence mappings with no dedicated Hirebase bucket. The closest sub is used, and a keyword would sharpen it:
- Venture Capital & PE → Investment (`venture capital`, `private equity`)
- Investment Banking → Financial Markets / Securities (`investment banking`, `M&A advisory`)
- Restaurants → Recreation & Travel / Food & Beverage (`restaurant`)
- Cosmetics → Personal Care & Household (`cosmetics`, `beauty`, `skincare`)
- Market Research → Information Services (`market research`)
- Newspapers → Publishing (`newspaper`, `news media`)
- Wireless → Telecommunications (`wireless`)
- Industrial Automation → Construction Technology & Automation / IoT (`industrial automation`, `robotics`)
- Mechanical or Industrial Engineering → Heavy & Civil Engineering / Industrial Design (`engineering services`)
- Media Production → Film, Digital Media, Multimedia Arts (`video production`)

## Second pass (2026-10-20, revised): 276 strings
Gaston asked to cut only subs where a remote role Near can place is highly unlikely, and to keep every HubSpot
industry with placements covered. 49 more strings removed (see `CUT` in `build_mapping.py`, reasons in
`excluded_subindustries.csv`): farm/agriculture operations, mining and commodity plant manufacturing, disaster relief,
fashion/craft design niches, a few low-fit product niches, and in-person-only services (labs, studios, retreats).
**The filter is now 276 strings.** Every HubSpot industry still has at least one sub in it, except Human Resources and
Farming, which Gaston excluded explicitly. The counts at the top describe the first pass.

## Exclusions confirmed by Gaston (2026-10-20)
Human Resources, Farming (HubSpot industry), Grocery Stores, Supermarkets, Outsourcing/Offshoring, Air Transportation.

## Judgment calls I'm unsure about
**Included, could be cut:**
- Agriculture subs still mapped from other industries: Agri-Tech (Computer Software), Agro-Processing (Food Production), Agricultural R&D (Research), Agricultural Chemicals (Chemicals), Agricultural Machinery (Machinery), Farm Supplies Wholesaling (Wholesale), Agricultural Real Estate (Real Estate).
- Field-heavy mining: `Coal Mining`, `Mining Support Activities`, `Non-Metallic Mineral Mining`, `Specialized Mining`.
- `Fitness Centers & Gyms`, `Home Health Care`, `Rehabilitation`, `Ambulatory Care`: in-person heavy.
- `Transportation for Travel`: may pull in airlines (Airlines/Aviation excluded).
- `Computer & Peripheral Equipment Manufacturing`, `Hardware & Equipment`: overlap Computer Hardware (0 placements). Kept for electronics/networking.
- `Travel R&C`: undefined abbreviation; assumed research & consulting.
- `Tobacco Manufacturing`, `Railroad Rolling Stock Manufacturing`, `Disaster Relief & Reconstruction`, `Disaster Relief & Humanitarian Aid`, `Themed Entertainment`: coverage-only picks.
- `Architecture & Design`: kept as Design. It may also pull architecture firms (Architecture & Planning has 0 placements).

**Excluded, could be added back:**
- `Performing Arts`, `Visual Arts`, `Arts, Culture & Humanities`, `Religious Education`, `Senior & Assisted Living Real Estate`.
