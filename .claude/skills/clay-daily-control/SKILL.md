---
name: clay-daily-control
description: >
  Daily maintenance check of Near's Clay Open Jobs workflows. Reads every active workflow
  (listed in references/active-workflows.md): jobs-table row counts, Find Jobs source
  records vs the 50k cap, "Rows from" send-feed sources, Companies/Leads table fill, whether
  each source ran in the last day, the shared Exclusion Lookup. Reports back in chat what
  needs action (row cleanup, source refresh, new company table, leads-table decision) and
  proposes registry changes when a new workflow or version appears. Runs through the in-app
  browser with Gaston's own Clay login. Use this whenever Gaston says "daily Clay control",
  "check Clay", "Clay maintenance", "are any tables near 50k", "do we need a cleanup", "did
  the sources run", or asks about Clay row/source limits, even without naming the skill.
  Review by default. Export/upload and filter changes may proceed when requested; deleting rows needs a separate explicit confirmation of the concrete batch.
---

# Clay daily control

Clay has two separate 50k limits: **table rows** and **source records**. Either one stops
imports, and then leads stop reaching campaigns. "Send table data" feeds (the `Rows from: …`
sources on Companies and Leads tables) are sources too, with their own 50k cap. They can
fill up while the destination table is still at 25k. The full process (Gaston's Looms and the
Oct 9 session with Sara) is in `Near Work Partner/wiki/tools/clay.md` → *Maintenance Rules*.

## Run

1. **Session.** Open `https://app.clay.com` in the in-app browser (`mcp__Claude_Browser__preview_start`
   with `url`). Check the login: `fetch('https://api.clay.com/v3/me',{credentials:'include'})`.
   On a 401, ask Gaston to sign in with Google in the browser pane, and wait. **Never type
   credentials yourself.** The `.env` `CLAY_USERNAME`/`CLAY_PASSWORD` login (kevin.dubon@)
   returns `400 Unable to login` since Nov 2026, so don't use it.
2. **Scan.** Read `references/active-workflows.md` and collect the Workbook IDs. Read
   `scripts/scan.js` and run its text plus `await clayScan([<ids>])` in one
   `mcp__Claude_Browser__javascript_tool` call. It takes ~30s and makes only GET calls.
   Large output: `JSON.stringify` the result and keep only tables with flags plus each
   workbook's key counts.
3. **Report** in chat (format below). Then ask, one decision at a time, about anything needing
   Gaston: approvals, leads-table calls, registry changes.
4. **Act within the requested scope.** Export/upload and necessary view filters can proceed when requested. Delete only after a separate explicit yes for the exact reviewed batch.
5. **Log.** Prepend one entry to `Near Work Partner/logs/clay-daily-control.md`: date, flags
   found, what was approved and done, and the before/after counts.

## Flags → what to do

| Flag | Meaning | Action |
|---|---|---|
| `A_ROW_CLEANUP` | Jobs table ≥ 35k rows | Propose a row cleanup (below). Delete only after a yes. |
| `B_SOURCE_REFRESH` | Find Jobs source ≥ 35k records | Recommend a source refresh. **Manual for now** (UI-only; a wrong click deletes the table). Link the workbook. |
| `C_NEW_COMPANY_TABLE` | Companies table ≥ 35k rows that is still receiving rows | Flag only. Gaston builds the next company table (process in `wiki/tools/clay.md`). |
| `C_MIGRATED` | Full Companies table whose feeds went quiet while a sibling Companies table receives rows | Already migrated. Mention it under *Watch*, no action. |
| `D_SEND_FEED_NEAR_CAP` | A live `Rows from:` feed ≥ 40k records | Flag. The fix is to delete that feed's source and re-create the Send table data column. Gaston does it. |
| `LEADS_AT_LIMIT` | Leads table ≥ 35k rows | **Flag only. Gaston decides.** |
| `EXCLUSION_AT_LIMIT` | Shared Exclusion Lookup ≥ 35k rows | Flag at the top of the report. At 50k, *Write to Exclusion Lookup* silently stops adding competitors in every workflow. |
| `SOURCE_NOT_RUN` | Scheduled source with no activity for 26h+ | Flag. Check whether it's a weekend or a real stall. |
| `SOURCE_STATUS` | Source last action not `SUCCESS` | Flag with the status. |

**Old feeds:** `Rows from:` sources with no activity in 72h are leftovers from earlier versions.
They don't raise D, so ignore them.

## Row cleanup rules (A)

From Gaston's Looms and the Oct 9 session:
- Jobs table only, newest workbook version. 4 filters in **one OR group**:
  `Previously Found Recruiting Company` has results · `Previously Found Recruiting Company 2`
  has results · `Write to Exclusion Lookup` has results · `Qualifyer! (merge)` is not checked.
- **Cleanup priority (Gaston, 2026-11-06): try to preserve the last 7 days, but this is a preference, not an absolute prohibition.** Start with older, non-qualified rows matching the cleanup signals above. If none match or they cannot create enough capacity, inspect better alternatives (e.g. destination rollover) and then consider more recent non-qualified rows. Prioritize non-qualified over qualified rows when relaxing the age window. Delete qualified rows only as a last resort when no better alternative provides the required capacity; prefer older qualified rows before the newest ones.
- The four-signal OR group is the starting cleanup selection. A last-resort qualified-row batch may fall outside it; document that exception explicitly and obtain confirmation for those exact rows. Use the table's actual qualification field name (e.g. `Qualified? (merge)`), rather than assuming the historical `Qualifyer!` label.
- **Never silently broaden a batch.** Show the exact fixed age cutoff, qualification criteria, row count, proposed capacity after deletion, and why the fallback is needed. Keep unfinished enrichments out of cleanup batches. Do not interpret a blank qualification as a completed negative result without checking upstream status.
- **Deletion always requires a separate explicit confirmation of that exact batch**, including any recent or qualified rows. A request to continue cleanup, relax the rules, export, or upload is not confirmation to delete an unspecified set.
- **Drive backup scope (Gaston, 2026-11-06): upload only the CSV containing the exact rows selected for deletion. Do not export or upload the entire table by default.** Keep the cleanup filters active for export. Verify that CSV membership/count matches the proposed deletion batch and that upload to the user-specified folder completed before deletion; do not substitute a stale backup. Full-table exports/uploads require a separate explicit request.
- Download the CSV **before** deleting. Production CSVs go to Drive *Clay Deleted Rows / {Region}
  Open Jobs / {HM | No HM}*. Test-workflow CSVs go to
  `https://drive.google.com/drive/u/0/folders/1T3XpFo4C93ZIDFxJVQfNEDQAL7p02Xv4`.
  File name: `{Table name} - deleted rows - YYYY-MM-DD.csv`.
- Big deletes leave leftovers, so re-count and repeat. Clear filters at the end.
- **Apollo (EXP010)** is different. It's CSV-loaded, so there's no source refresh, and it gets
  a weekly cleanup: *Apollo companies w/ open jobs* → Run condition not met on the first
  *Find jobs* column + Created At ≥ 1 month old. *Jobs Openings – Apollo Companies* → contacts
  ≥ 1 month old.

**Not built yet (phase 2):** the API calls to filter, export and delete rows aren't mapped.
Until they are, a yes on A means doing it in the browser pane, following the rules above, on
the **test workflow first**. Production cleanups normally follow a validated test run. An explicit user instruction to operate on a named production table may override that sequencing; it never waives the separate batch-deletion confirmation or verified backup requirements.

## Source refresh reference (B, manual)

### Required checks before removal

- Confirm the workflow/workbook, destination table name **and ID**, current source, row count, source inputs/exclusions, and schedule. Locate and inspect the intended replacement saved search **before deleting the current source**. Similar names are not interchangeable; use the workflow-specific mapping or Gaston's screenshot/instructions. If the replacement cannot be identified unambiguously, leave the current source in place and ask.
- For **US No HM / Candidate led vs routing CTA vs EXP008**, Gaston confirmed this exact saved search from his screenshot on **2026-11-06**:
  **`[New] US Open Jobs | NO HMs | Key segment exclusions (mkt, sales & eng)`**.
  Workbook: `wb_0thes7n5ga6XvyAz9Do`. Import destination: **Remote Jobs, US, Recent**, table **`t_0thes7nB88VNvTTfFfU`**. Do not choose an HM search, an EXP014 segment search, another similarly named search, a Companies table, or a downstream Leads table. This mapping is specific to this workflow, not a default for all US workflows.
- Check the saved search's full inputs, especially *Job titles to exclude*, against the intended workflow. Preserve the screenshot-confirmed segment exclusions. Record the exact saved-search name (and ID if exposed), destination, and before counts in the log.

### Remove only the source; preserve all rows

- Use the source's **Delete source** control, then choose **"Delete source but keep rows"** (or the UI's equivalent explicitly stating that existing rows are retained). **Never choose an option deleting associated rows or the table.** Read the complete confirmation before submitting. If there is no explicit keep-rows option, stop and ask; never infer safety from a generic Delete label.
- Verify that the source was removed and that the table still has the same rows before creating its replacement. If counts differ, investigate and do not continue blindly. Source deletion is a separate action from any previously approved row cleanup; that cleanup approval does not authorize deleting source-associated rows.

### Re-create and verify routing and execution

- + → See past searches → the **verified workflow-specific saved search** → recheck exclusions → Update search → Save to table. Verify the existing destination **table ID and name** in the import dialog, then **Import and run**. Do not create a new table or import directly into the downstream Leads table by accident.
- Check auto-run and dependency settings. Bulk imports may not trigger the first enrichment: identify newly imported rows whose `Previously Found Recruiting Company` enrichment has not run, and Force run **only those new rows**. Use a fixed import-time cutoff and/or stable record IDs to distinguish them from older unrun rows. **Never force-run the entire table or older leads**, which can re-push existing leads.
- Verify new rows actually land in the intended Jobs table, the first enrichment starts/completes, and eligible rows progress through the existing Companies/Leads routing. Validate destination table references; do not equate a successful import with successful workflow execution. If no new rows import or none qualify, report that downstream execution could not be demonstrated rather than claiming success.
- Set and save the intended recurring schedule. The documented standard is **Daily 9:30 AM EST**, but record any existing mismatch and obtain approval before changing that workflow's schedule; do not silently alter it during a refresh.
- Verify replacement source name/inputs, destination, run status, schedule, and before/after table/source counts. Log the actions and evidence, including that removal preserved the existing rows. Do not claim the refresh complete until routing and execution checks pass (or clearly report what remains unverified).

## Registry upkeep

`scan.js` returns three lists to compare with `references/active-workflows.md`:
- `candidates`: workbooks not in the list whose sources moved in 72h. Propose **add**, or
  **replace** when one looks like a new version of a listed workflow (same folder, V2→V3,
  "With Companies Table", etc.).
- `missing`: listed IDs that no longer exist. Propose **remove**.
- A listed workflow now named `[Old]`/`[Paused]`, or with no source activity in 72h: propose **remove**.

Edit the file only after Gaston confirms, and add a dated line to its *Change log*.

## Report format

Keep it tight. Lead with what needs action and skip the healthy workflows (just count them).

```
Clay daily control — YYYY-MM-DD  (18 workflows, 15 OK)

Needs action
1. [A] Remote Jobs, US, Recent — NO HM EXPs: 36,349 rows → cleanup? (link)
2. [B] LatAm HMs source "Find jobs": 32,498/50k → refresh soon (link)
3. [Leads] … → your call

Watch (≥35k, or migrated)
- …

Registry
- New: "X" (folder) moving since … → add?
```

## Known gotchas

- `/workspaces/447061/workbooks` gives `parentFolderId`. Resolve folder paths with
  `/folders/{id}`. `resources_v2` only returns root items and ignores folder filters.
- Each table carries `tableSettings.DEDUPE_FIELD_ID` / `DEDUPE_KEEP_STRATEGY`. The jobs tables
  dedupe on a field, so re-imported jobs don't duplicate.
- Find Jobs sources carry `scheduleConfig.schedule.value` (times + timezone). Since 2026-11-07
  the LATAM No-HM source (`s_0to51yk7DJFTWWFVzQw`) runs at **09:00 America/Buenos_Aires** (= the old
  07:00 Bogota, kept at Gaston's request), not the 9:30 EST standard. Point out mismatches, don't change them.

## Export and backup notes (verified 2026-11-06)

- UI: Tools → Export → Download CSV. The export uses current view filters: keep the exact cleanup filters active so the CSV contains only rows proposed for deletion. Retrieve completed exports from workspace **Exports** → row menu → Download. Download may open a separate S3 tab, so a download event on the originating tab can time out while the browser still transfers the file. Wait for the final `.csv` filename; never upload a `.crdownload` as a complete backup.
- Parse CSV with a CSV reader (embedded newlines make line counts unreliable). Check row count and consistent column count; preserve the original file. CSV exports contain rendered values, not reliable per-cell pending status, so inspect live enrichment completion before proposing deletion.
- US No HM backup folder confirmed by Gaston: `https://drive.google.com/drive/u/0/folders/1W-SaVPzKw9Zg1JeiWhR_AfjPF2K8blQ2` (**US | No Hiring Managers**). Use any newer destination supplied by the user.
- Name unapproved batches `{Table name} - proposed cleanup - YYYY-MM-DD.csv`; use `{Table name} - deleted rows - YYYY-MM-DD.csv` once deletion is verified. Keep only the deletion-batch CSV in Drive; do not upload full-table snapshots unless explicitly requested.

### Source-refresh UI observations (2026-11-06)
- A saved search can be inspected from the source header's + / See past searches before removing the old source. Keep that verified configuration open while removing the old source in another tab. Save to table must confirm the exact existing table ID.
- Replacement sources default to **Manually**: explicitly restore and save their schedule. The UI displays the local timezone; preserve the same instant (e.g. old 07:00 GMT-5 = 09:00 GMT-3). After setting a native time field, press Tab to commit/enable Save schedule, then verify the saved value after reload.
- Import and run may still leave the first enrichment unrun. Combine a fixed current-import Created At cutoff with the first column's has not run filter, select the exact batch, and verify the force-run confirmation names only that column and that batch size. Expect normal downstream company-lookup delays; distinguish active progression from completed lead delivery.

### LATAM No HM run (2026-11-06/07) — reusable findings
- **Saved-search mapping:** LATAM No HM V3 (`wb_0tj9oxa6r3nZqENkyh4`, Jobs `t_0tj9oxnrWnaxcz6PZxf`) → **`LatAm OJ | No HMs`** (Saved by you, Gaston). Not `Latam OJ HMs`. It matches the old source exactly (80 title exclusions, 25 LATAM locations, Full-time, 1 day, limit 24,999, 10/company, no recruiter). Source `s_0to51yk7DJFTWWFVzQw`, daily 09:00 GMT-3.
- **Find exactly the new rows:** the source column filter **"is from source" → the new source** (`SELECT_SOURCE`) + first column **has not run**. More precise than a Created At cutoff. Then column menu → Run column → **"Run N empty or out-of-date rows"** (safer than Force run). The "Confirm run" dialog states the row count.
- **Qualified false vs blank:** the UI only offers checked/not checked for `Qualified? (merge)`. In this workbook, `Find in Companies Table` **has results** ⇔ Qualified=false (verified 1:1). Use that to separate a final "no" from an unfinished blank.
- **Exact cleanup preflight via API (read-only):** `views/{All rows}/records/ids` + `bulk-fetch-records` in batches of 1,000 (`cells[f].metadata.status`: SUCCESS / SUCCESS_NO_DATA / ERROR_RUN_CONDITION_NOT_MET / QUEUED; missing = not run). Compare the view's IDs against the computed batch before exporting/deleting. View filters are saved server-side (`views[].filter`); a PATCH while the UI is open gets overwritten, so build them in the UI.
- **Bulk delete:** the dialog keeps spinning and `/count` lags for minutes. Check progress with `records/ids` and don't repeat the delete.
- **Drive backup without the UI:** resumable upload `upload/drive/v3/files?uploadType=resumable` with the `.env` OAuth token; verify the `md5Checksum` against the local file. LATAM No HM folder: `1u01m-yCy5Cm5Jd1yxADt7SfOOWP4HzNx` (**Latam | No Hiring Managers**).
- **Hidden browser pane:** popovers don't show in screenshots and clicks by coordinate fail. Use `find`/`ref` and read dialogs via DOM (`[role=dialog]`). Typing without verified focus can rename a column: check with the API afterwards.
- **Credits:** "Import and run" estimates ~1 credit/row × the limit (e.g. ~24.9K). Re-importing the same day brings back jobs that were just deleted (dedupe no longer sees them): mention it before importing.

### US No HM cleanup (2026-11-09) — API shortcuts, verified
- **View filters via API:** `PATCH /v3/workspaces/447061/tables/{t}/views/{v}/filter`, body = the filter object itself (not `{filter}`). Do it while the table isn't open in the UI, then reload. `PATCH /tables/{t}/views/{v}` with `{filter}` is silently ignored. Max 2 levels: top OR of AND groups (deeper groups get dropped).
- Filter types: `RESULTS` / `NO_RESULTS` / `RUN_CONDITION_NOT_MET` / `HAS_ERROR` (action columns), `CHECKED` / `NOT_CHECKED` (checkbox; NOT_CHECKED covers false + blank), `LESS_THAN` with ISO `value` (dates, e.g. `2026-10-15T03:00:00.000Z` = 00:00 GMT-3).
- `records/ids` ignores view filters (returns the whole table). Read the filtered count from the UI header (`N/total`).
- Temp view: `POST /tables/{t}/views {name}` creates one; `DELETE /tables/{t}/views/{v}` removes it. Use one per cleanup instead of touching shared views.
- Export via API: after Tools → Export → Download CSV, poll `GET /workspaces/447061/exports/{ej_id}` until `status: FINISHED`, then curl `downloadUrl` (S3, ~48 MB per 22k rows, slow). The UI also auto-saves a copy to the browser's downloads.
- "Unqualified, final" in this table = Qualified false (⇔ `Find in Companies Table` has results) **or** blank with `Previously Found Recruiting Company?` / `(2)` / `Already in HM workflow?` has results. Blank with a companies-table lookup still pending is unfinished: keep it out. Freeze the batch with `Created At < today` so the daily import can't join it.
- Bulk-fetching all 44k rows takes ~7 min: run it in the background on `window` and poll. It's lost if the tab navigates.
