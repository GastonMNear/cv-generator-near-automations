---
type: analysis
title: "Open Jobs lead supply vs email capacity — where the funnel loses volume"
created: 2026-11-09
updated: 2026-11-09
status: done
scope: "LinkedIn Open Jobs US / LATAM / Canada, HM + No-HM (Asia excluded). HireBase, Apollo, HubSpot reported separately."
related: ["[[tasks/2026-11-09-analyze-lead-supply-vs-capacity]]", "[[outbound/campaign-insights]]", "[[tools/clay]]", "[[logs/clay-daily-control]]"]
---

# Open Jobs lead supply vs email capacity (2026-11-09)

Question (Andrés, via Gaston): are we getting fewer LinkedIn jobs than before, or losing them later in the funnel? Where is the bottleneck that keeps us at ~19k of 25k emails/week?

## TLDR

1. **The bottleneck isn't LinkedIn job volume. It's the step from qualified company to a *new*, not-yet-contacted company or lead.** Jobs in and qualified companies are flat or up. But companies that reach lead search fell **−22%** (US No-HM ~3.3k → ~2.6k/wk), and **~40% of found leads with an email are already in Smartlead**, so they're never added.
2. **Gap:** last 8 weeks sent **19.4k vs 25k** = **~5.6k emails/wk ≈ 1,870 leads/wk short** (3.0 emails per new lead).
3. LinkedIn OJ uploads fell **~6.0k → ~4.2k/wk (−1.8k)** from Jun–Aug to L8W; US No-HM is ~1.2k of that. The new sources (HireBase + Apollo + HubSpot, ~1.75k/wk) **only replaced that loss**. Apollo and HubSpot are themselves decaying.

## Definitions used

Gaston answered capacity only (25k emails/wk). The other stages use these defaults; change them if they don't match how we count.
- **Week:** Mon–Sun, by the date the row was **added to Clay** (`Created At`). LinkedIn *posted* date falls in the same week for 96–99% of jobs, so it tells the same story. Apollo and HubSpot posted dates lag (8–83% same week), because those jobs are older when imported.
- **New jobs in:** unique LinkedIn job IDs, current rows + Drive deleted-rows CSVs, deduped by job ID.
- **Passed filters/exclusions:** distinct companies on jobs rows with `Qualified? (merge)` (HM tables: `Qualified?`) = true.
- **Leads found:** leads-table rows with a work email. HM: jobs rows with an email (LATAM/CA), or HM leads-table rows (US).
- **Uploaded:** Smartlead campaign-lead `created_at` in the mapped campaigns (subsequences excluded).
- **Capacity:** 25,000 emails/wk (sheet shows 25,175). To convert emails to leads: L8W emails sent ÷ leads added (all campaigns) = **3.01 emails per new lead**.

## Summary: historic avg vs L8W vs L4W

Historic = full available history for that stage (weeks and start in brackets). Jun–Aug is shown because that's "the past" in the hypothesis. L8W = Sep 14–Nov 8, L4W = Oct 12–Nov 8.

| Region | Stage | Historic avg | Jun–Aug | L8W | L4W | Δ L8W vs hist | Δ L4W vs hist |
|---|---|---:|---:|---:|---:|---:|---:|
| US No-HM | Jobs in | 26,352 (10w, from Aug 31) | n/a (gap) | 27,935 | 30,833 | +6% | +17% |
| US No-HM | Qualified cos | 5,451 (12w, Aug 17) | 5,356 (2w) | 5,731 | 5,823 | +5% | +7% |
| US No-HM | Leads w/ email | 5,830 (19w, Jun 29) | 6,472 | 5,474 | 6,029 | −6% | +3% |
| US No-HM | Uploaded | 2,833 (46w, Dec 1) | **4,330** | **3,134** | 3,336 | +11% | +18% |
| US HM | Jobs in | 1,965 (16w, Jul 13) | 2,244 | 1,723 | 1,585 | −12% | −19% |
| US HM | Qualified cos | 590 | 572 | 588 | 552 | 0% | −7% |
| US HM | Leads | 728 (16w, Jul 13) | 608 | 755 | 698 | +4% | −4% |
| US HM | Uploaded | 527 (49w) | 545 | 505 | 458 | −4% | −13% |
| LATAM No-HM | Jobs in | 50,452 (8w) | n/a (gap) | 50,748 | 54,507 | +1% | +8% |
| LATAM No-HM | Qualified cos | 692 (12w, Aug 24) | — | 761 | 741 | +10% | +7% |
| LATAM No-HM | Leads w/ email | 566 (14w, Aug 3) | 790 (4w) | 460 | 449 | −19% | −21% |
| LATAM No-HM | Uploaded | 443 (43w) | 417 | 288 | 283 | −35% | −36% |
| LATAM HM | Jobs in | 5,061 (21w) | 2,909 | 7,320 | 7,685 | +45% | +52% |
| LATAM HM | Qualified cos | 402 (10w, Aug 31) | n/a (gap) | 374 | 330 | −7% | −18% |
| LATAM HM | Leads | 251 (10w) | n/a | 230 | 199 | −8% | −21% |
| LATAM HM | Uploaded | 231 (43w) | ~188 excl. Aug 3 re-engage bulk | 150 | 142 | −35% | −39% |
| Canada No-HM | Jobs in | 2,034 (8w, Sep 14) | n/a (new workbook) | 2,034 | 1,548 | 0% | −24% |
| Canada No-HM | Qualified cos | 106 | n/a | 106 | 93 | 0% | −12% |
| Canada No-HM | Leads w/ email | 173 | n/a | 173 | 116 | 0% | −33% |
| Canada No-HM | Uploaded | 296 (39w) | 208 | **73** | 50 | −75% | −83% |
| Canada HM | Jobs in | 206 (48w) | 177 | 198 | 214 | −4% | +4% |
| Canada HM | Qualified cos | 84 | 70 | 70 | 71 | −16% | −16% |
| Canada HM | Uploaded | 50 | 41 | 44 | 43 | −13% | −14% |
| *HireBase* | Uploaded | 1,160 (3w, from Oct 19) | — | 1,160 | 1,160 | — | — |
| *Apollo EXP010* | Uploaded | 1,479 (11w, Aug 17) | — | 1,192 | 822 | −19% | −44% |
| *HubSpot cold accts* | Uploaded | 694 (13w, biweekly) | 642 | 230 | 149 | −67% | −79% |

### Capacity vs uploads (weekly)

| Week | Emails sent | Short of 25k | Leads added (all, sheet) | LinkedIn OJ uploads (6 groups) | HireBase + Apollo + HubSpot + clients |
|---|---:|---:|---:|---:|---:|
| Jun 1 | 18,411 | 6,589 | 6,031 | 6,349 | 0 |
| Jun 8 | 24,647 | 353 | 16,862 | 7,347 | 0 |
| Jun 15 | 23,653 | 1,347 | 7,459 | 5,304 | 0 |
| Jun 22 | 14,770 | 10,230 | 5,472 | 7,458 | 0 |
| Jun 29 | 18,451 | 6,549 | 7,344 | 6,881 | 0 |
| Jul 6 | 22,688 | 2,312 | 9,081 | 5,177 | 0 |
| Jul 13 | 18,233 | 6,767 | 5,604 | 5,515 | 0 |
| Jul 20 | 23,498 | 1,502 | 2,186 | 4,154 | 924 |
| Jul 27 | 18,226 | 6,774 | 5,065 | 1,151 | 0 |
| Aug 3 | 23,097 | 1,903 | 27,498 | 11,346 (incl. 4.4k LATAM HM re-engage bulk) | 361 |
| Aug 10 | 23,581 | 1,419 | 6,972 | 5,931 | 0 |
| Aug 17 | 23,895 | 1,105 | 7,742 | 5,477 | 1,846 |
| Aug 24 | 20,385 | 4,615 | 6,203 | 6,045 | 0 |
| Aug 31 | 20,486 | 4,514 | 6,459 | 2,805 | 3,304 |
| Sep 7 | 18,598 | 6,402 | 6,121 | 4,384 | 1,712 |
| Sep 14 | 19,557 | 5,443 | 7,247 | 4,381 | 2,319 |
| Sep 21 | 20,470 | 4,530 | 6,380 | 3,982 | 1,815 |
| Sep 28 | 19,956 | 5,044 | 5,720 | 3,772 | 1,699 |
| Oct 5 | 17,878 | 7,122 | 5,833 | 4,167 | 1,080 |
| Oct 12 | 17,329 | 7,671 | 5,422 | 3,754 | 1,176 |
| Oct 19 | 18,541 | 6,459 | 6,534 | 4,897 | 1,314 |
| Oct 26 | 19,687 | 5,313 | 6,284 | 3,896 | 2,024 |
| Nov 2 | 21,659 | 3,341 | 8,178 | 4,698 | 2,564 |

- Jun–Aug: sent avg 21.0k, LinkedIn OJ uploads ~6.0k/wk.
- L8W: sent avg 19.4k (5.6k short ≈ **1,865 leads/wk**), LinkedIn OJ ~4.2k/wk, new sources ~1.75k/wk.
- L4W: sent 19.3k (5.7k short ≈ **1,890 leads/wk**).

## Causes, ranked

**1. Saturation: qualified companies are increasingly ones we've already processed or contacted.** Confidence: medium-high.
- US No-HM jobs in (+6% L8W) and qualified companies (+5%) are not down. But companies reaching lead search fell from ~3,296/wk (Jun 29–Aug 24, excluding Jul 27) to ~2,575/wk (L8W), −22%. Leads per company held steady at 2.3–2.8, and upload/leads at ~57–60%. So the loss sits between "company qualified" and "company sent to lead search" (`First Occurrence of Company?` / `Lookup Company in this workflow` / `Already in HM workflow?`).
- New (never-seen) qualified companies per week fall much faster than qualified jobs:
  - EXP012 tables (complete, never cleaned): new qualified companies 1,660 (Sep 14) → 965 (Oct 26), −42%, vs qualified jobs −30%.
  - Canada No-HM: 106 → 27, −75%.
  - US HM: ~650 → ~510, −20%.
  - LATAM No-HM: ~460 → ~260.
- Leads blocked because they're already in Smartlead (Sep 14–Nov 8): US No-HM ≈ **40%** of leads with email (Baseline1 6,211 "could not add, existingLeadsInOtherCampaigns" vs 11,748 added; EXP012 tables "run condition not met" ≈ added). LATAM 37%, Canada 60%, HireBase 42%. Checked: `Cold Email Creation` only runs when `!{Look up lead in campaign}?.id`, and `Add Lead` needs all four copy fields. So "run condition not met" = already in a campaign.
- That share has been ~35–50% every week since June, so it's a ceiling we've always had. What changed is fewer *new* companies upstream of it.
- Size: −720 companies/wk × 2.5 leads × ~57% ≈ **−1,000 uploads/wk**. That's most of the US No-HM drop (4,330 → 3,134).

**2. Small and secondary feeders collapsing.** Confidence: high (direct counts).
- Canada No-HM uploads 208 → 73/wk (−135). Jobs −24% L4W, and 60% of found leads are already in Smartlead.
- Coworkers (US HM) Clay adds went from ~130–370/wk in May–Jul to ~0 after Aug 31.
- LATAM No-HM uploads 417 → 288 (leads −19%).
- Separate sources decaying: Apollo 3.2k (Aug 31) → ~0.8–0.9k/wk (−44% L4W). HubSpot cold accounts −79% L4W (fed once on Oct 30).

**3. LinkedIn job volume: no broad drop.** Confidence: medium. We can't see US No-HM job volume before Aug 31 (see gaps).
- Flat or up: US No-HM jobs +6%/+17%, LATAM No-HM +1%/+8%, Canada HM flat, LATAM HM jobs up.
- Down: US HM jobs −12%/−19% (2.2k → 1.6k/wk), but qualified companies only −7% L4W. Canada No-HM −24% L4W.
- EXP012 per-segment searches fell 8.2k → ~4.5k/wk, but the main search picked up the difference (Oct 16: 13.4k rows in one day).

**4. One-off outages and operational leaks.** Confidence: medium. Each costs about a week of volume.
- **Week of Jul 27:** near-zero everywhere (US No-HM 510 uploads, US HM 0 job rows). This lines up with the Clay credit purchase task (Jul 22–Aug 1).
- **Week of Aug 31:** EXP012 cutover. US No-HM uploads 1,418. On Sep 1–8 the main table qualified ~20–140 jobs/day vs ~900 normally.
- **Bulk imports don't start the first enrichment:**
  - LATAM: 3,915 Nov 2 rows were never enriched.
  - US: 2,852 rows on Nov 6 needed a manual run.
  - Each LATAM miss costs about one day of LATAM leads (~60–90).
- **Not causes:**
  - The 50k row cap: no blocked import days are visible.
  - The Exclusion Lookup at 50k: it lets *more* through, not less.
  - Upload firing: Clay adds ≈ Smartlead uploads; rate-limit errors are ~30/wk.

## Fixes (estimated leads/week recovered)

1. **Re-route "already contacted" companies instead of dropping them.** When a qualified company was already processed, or its lead is already in Smartlead, look for a different persona (HR leader / dept head / CEO, as EXP013 already does from other tables at 450–570 leads/wk). Or re-enter companies after a cooldown (e.g. ≥8 weeks, no reply) with the new job as the angle, the way the US HM re-activation campaign works.
   - Pool: ~2.2k US No-HM leads/wk blocked + ~3k repeat qualified companies/wk.
   - **+800–1,500 leads/wk** if 30–50% yield a new contact. Medium confidence; it depends on cooldown rules and how much EXP013 already covers.
2. **Restore the stalled feeders to their Aug–Sep levels:**
   - Apollo: weekly CSV reload, ~2.0k → 0.8k → back to ~1.5k (+~700).
   - HubSpot cold accounts: ~690 → ~150 (+~400).
   - Coworkers: ~190 → 0 (+~190).
   - **+1,000–1,300 leads/wk.** Medium-high confidence: they ran at these levels before, though part of the Apollo/HubSpot decay may be pool depletion.
3. **Guard rails in `clay-daily-control`:** alert when a source imports rows but the first enrichment doesn't start, when a day has 0 imported rows, or when qualified/day drops below ~50% of the 7-day average.
   - **~0 in a normal week, protects ~300–1,000 in an incident week.**

Fixes 1 + 2 (~1,800–2,800/wk) are enough to close the ~1,870 leads/wk gap. Neither needs more LinkedIn job volume.

## Data coverage and gaps (no estimates filled)

| Region / stage | Weeks covered | Gap |
|---|---|---|
| US No-HM jobs in | Aug 31 → Nov 8 (CSV + live) | **Jun 1 – Aug 30 missing.** Cleanups before Aug 17 weren't backed up (only a May export: May 4–18, partial). The Aug 17–30 exports contain only qualified rows, so jobs in isn't measurable those weeks. |
| US No-HM qualified cos | Aug 17 → Nov 8 | Sep+ is summed across the main + EXP012/EXP014 tables, so it's an upper bound (a company in two segments counts twice). |
| US No-HM leads | Jun 29 → Nov 8 (live leads tables + Baseline1 leads CSV of Oct 20) | — |
| US HM | Jul 13 → Nov 8 (table created Jul 16, never cleaned) | Week of Jul 27 has 0 job rows (outage). Leads before Jul 13 = Coworkers only, so excluded. |
| LATAM No-HM jobs | Aug 3 (Aug 5–9 only), Sep 14, Sep 28 → Nov 8 | Aug 10 – Sep 13 missing. Sep 21 partial (9.4k). Qualified from Aug 24 (live survivors). |
| LATAM HM | Jobs Jun 15 → Nov 8; qualified/leads Aug 31 → | Backups before Aug 31 contain almost no qualified rows. Either they were deleted without a backup or the qualification changed. Excluded. |
| Canada No-HM | Sep 14 → Nov 8 (new workbook) | Older `[Old]` CA workbooks not read. |
| Canada HM | Dec 8, 2025 → Nov 8 (never cleaned) | — |
| Uploads (Smartlead) | Dec 2025 → Nov 8, all in-scope campaigns | Campaign-level only. A lead moved between campaigns may count twice. |

Other caveats:
- The two Nov 9 deletion CSVs had no `Created At`. Dates were recovered from the Nov 6 full backup by job ID. The rest (4.9k US, 15.7k LATAM rows) are dated by `Posted At`.
- EXP012 ↔ main-table duplicate jobs were removed using a 40-job sample per week (overlap 0–60%, peak in the week of Oct 12).
- **The Outbound metrics sheet has no per-campaign blocks for the 4 biggest US No-HM campaigns** (`3570933`, `3570999`, `3804786`, `3804793`). Since Aug 3, ~7–11k sends/wk are unassigned there. Fix this before using the sheet for per-campaign capacity.

## Method (to reproduce)

All read-only. No Clay, Smartlead or Drive writes and no credits spent.
1. **Clay (live):** in-app browser with Gaston's session. `GET /tables/{id}` (fields), `GET /views/{firstView}/records/ids`, `POST /bulk-fetch-records` in batches of 1,000. 41 tables: the jobs + leads tables of every in-scope workbook, plus the EXP012 jobs/leads tables (removed from the registry but live Sep 2–Nov 6), HireBase, Apollo and HubSpot. Per row kept: job ID (digits from `Job LinkedIn Url`), `Created At`, `Posted At`, Qualified, companyIdentifier, email present, Add Lead status. Aggregated in the browser.
   - The `.env` Clay cookie returns 401, and the page can't POST to localhost, so data can't be moved to disk. Aggregate in the browser and move only small outputs.
2. **Drive:** every CSV under *Clay Deleted Rows* (non-Asia), via the `.env` OAuth token (`drive/v3 alt=media`). 36 files, 825k rows. Region by majority job location (two "LATAM HM" folder files are really LATAM No-HM). Deduped by (region-type, job ID), keeping the earliest `Created At`.
3. **Union:** checked live rows against the CSVs with job-ID samples:
   - US main table live ⊂ Nov 6 full backup, except Nov 7–8.
   - LATAM / LATAM HM live rows are qualified survivors, disjoint from the deleted-row CSVs, so summed.
   - EXP012 tables deduped with the sampled overlap.
4. **Smartlead:** `GET /campaigns`, then `GET /campaigns/{id}/leads` (offset, 100 per page) for all non-subsequence OJ campaigns, mapped to groups by name. Weekly by campaign-lead `created_at`.
5. **Capacity:** Outbound metrics › *Email Campaign Metrics (Weekly)*, rows "Emails sent" / "Leads added".
6. **Funnel diagnostics:** new-vs-seen companies per week (first appearance of a companyIdentifier in each table), Add Lead status mix (added / `SUCCESS` "could not add" / `ERROR_RUN_CONDITION_NOT_MET`), and the run-condition formulas read from field `typeSettings`.
