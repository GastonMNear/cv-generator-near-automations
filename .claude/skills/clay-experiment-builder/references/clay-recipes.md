# Recipes (verified 2026-11-06 on EXP014 Engineering, Sales/GTM, Marketing)

Each recipe assumes `scripts/clay-builder.js` is loaded (`window.cb`) and the safety rules in
SKILL.md. Field IDs in examples are the US OJ No-HM family's (conventions §2.2); for another
family read them from the audit. Every edit:
**backup → write (skipActionFieldRuns) → re-read after ~3 s → diff vs backup → run status → log.**

## Contents
- Edit a column without running it
- Swap a segment (lead title search, prompt examples, keyword guard)
- Change the jobs source search (Gaston's UI step)
- Swap a model
- Email prompt (fixed copy + slots) and optional inputs
- Make Email 2/3 identical across arms
- Create a route (destination change)
- Reuse an existing companies table (or swap one)
- Delete a batch (after Gaston's OK)
- Map arms to Smartlead campaigns
- Full-run review (after Gaston runs rows)
- Lead check (Clay vs Smartlead, every lead)
- Inbox load
- Start campaigns (Gate D)
- Moving big JSON / backups to files

## Edit a column without running it
```js
const bk = await cb.backup('t_…', ['f_…']);   // then cb.dump(bk) → save_dump.py --backups (templates.md)
const r = await cb.patch('t_…', 'f_…', ts => { cb.setInput(ts, 'model', '"gpt-5.4-mini"'); });
// r = {field, changed:[keys], savedAsIntended, runStatus}
```
`cb.patch` refuses: a field without a backup (or not created this run), an action column on an
auto-run table (`{allowAutoRun:true}` only after Gaston confirmed that table), a formula on an
auto-run table without `{allowFormulaOnAutoRun:true}`, and a field whose `configRevision` changed
since the backup. A formula column is edited via `ts.formulaText`.

## Swap a segment (lead title search, prompt examples, keyword guard)
Use for Replicate, and for Launch when the segment changes.
1. Read the current prompt (`cb.inputs(t, f).prompt`) and the same field in a **reference
   workflow for the target segment** if one exists (e.g. EXP012 `<Segment>`): cloned IDs match.
   Use the reference as the starting point for the department vocabulary, the current prompt for
   structure and rules.
2. Lead title search: keep the structure and size rules; swap only (a) the two guideline
   examples ('VP X' / 'VP of X', permutations), (b) the department-heads example list, one clause
   per sub-function the jobs-source keywords cover (e.g. Sales: sales, SDR/BD, rev ops/CRM,
   CS/AM, solutions engineers, partnerships, GTM), (c) the seniority example (a role from this
   segment → its leaders). Show current / reference / proposed side by side at Gate A.
3. Other prompts with segment examples (the challenger Email 1's slot examples, e.g. [ROLE] /
   [ROLE_LOWER] / [EXPERIENCE]): swap the examples only, never the template or rules.
4. Apply with **guarded exact-phrase replacement**: each old phrase must occur exactly once
   (abort otherwise); change only the `prompt` input; guard on `configRevision`.
5. Leftover check after replacing: case-insensitive for words (`/ngineer|software|devops/i`),
   **case-sensitive with word boundaries for acronyms** (`/\bCTO\b/`, since `/CTO/i` matches
   "Director"), and whitelist phrases the new text is meant to contain ("solutions engineer").
6. Verify: prompt equals the intended text, everything else byte-identical, run status unchanged.
   Lead title search output feeds `MoltSets Titles` (≤2-word titles); long permutations reach
   Clay/Apollo but not MoltSets. That's fine.

## Change the jobs source search (Gaston's UI step)
Source edits by API are unverified. You prepare it:
1. `cb.sourceSummary(jobsTable)`: keywords, excludes, days, locations, `runSettings`, schedule,
   `records` already pulled. Never print `exclude_job_identifiers`.
2. A duplicated workbook's source can be **scheduled and already pulling** (2,759 rows before any
   edit on EXP014 Sales/GTM). If its keywords aren't the new segment's yet, the jobs table fills
   with the wrong roles: flag it at Gate A and ask whether to keep the schedule.
3. Draft include/exclude lists for the segment (or confirm the ones set). After the OK, Gaston
   edits the saved search in the UI. Re-read `cb.sourceSummary` to confirm.

## Swap a model
Change only the `model` input. Check the column sets no temperature/JSON-mode/reasoning parameter
the new model rejects. List all models with `cb.audit(...).models`. Both arms together.

## Email prompt (fixed copy + slots) and optional inputs
Pattern (full text: EXP014 Eng build log, step 15): `# Task` → `# Template` (copy verbatim) →
`# Inputs` (one line per field) → `# Slot rules` (one per slot, with fallbacks and examples) →
`# Output` (JSON `subject_line` + `email_one`, no signature, no brackets left, don't reword).
- Keep the output schema keys the downstream formulas read.
- Normalized titles are abbreviated ("cybersecurity eng"): include a clean-the-title rule.
- A jobs value the leads table lacks: add it to the arm's routes' `rowData`
  (`"Key": "{{f_jobsField}}?.response"`) and read `{{f_source}}?.parent?.["Key"]`. No new column.
- **Every input that can be blank goes in `optionalPathsInInputs.prompt`** (`["f_x"]` or
  `["f_source","parent","Key"]`), or the cell fails with ERROR_BLANK_TOKEN and the lead is lost.
- Slot examples must match the segment (Swap a segment §3).
- Same model as the baseline arm unless Gaston says otherwise.

## Make Email 2/3 identical across arms
`cb.armDiff(baseline, challenger)`. A fresh duplicate shows zero differences before the Email 1
edit. If Email 2/3 drifted, copy the baseline field's `typeSettings` verbatim onto the challenger
(same field ID). If it references helper columns the challenger lacks, **ask**.

## Create a route (destination change)
A route's destination can't change after creation (runs fail with `sourceId` undefined).
```js
const destIds = (await cb.table('t_dest')).fields.map(f => f.id);   // ORIGINAL list, once per destination
const r = await cb.createRoute({workbookId, origin:'t_jobs', dest:'t_dest', template: oldOrTwinTypeSettings,
          label:['Baseline','Challenger'] /* only for arm routes */, name:'<final name>', destBaselineIds: destIds});
// → {newFieldId, name, identical, destAutoRun, destSources, autoCreatedDestColumns, otherNewDestColumns, runStatus}
```
- Origin auto-run must be off: the new column starts with **no run condition**.
- `add-route-to-table` **auto-creates a pass-through formula column in the destination for every
  origin column name the destination lacks** (36 per companies table on EXP014). They appear
  **asynchronously**: `createRoute` waits 10 s; check again with `cb.newColumnsSince(dest, destIds)`
  before deleting. A duplicated leads table already has the names, so none appear there.
- The new column can't take the old one's name while the old exists (400): it stays "Send table
  data" until the old one is deleted, then rename (`cb.patch(origin, newId, ts=>{}, {name})`).
- Table column cap: if create fails with "table size limit", the old column must be deleted
  first (needs the batch OK), then create, verify, and only then continue.
- Old column: `cb.refsTo(oldId, [every table in the workbook])` must be empty before deleting.

## Reuse an existing companies table (or swap one)
Typical case: a duplicated workbook made an empty companies copy; Gaston moved in the segment's
existing enriched table (e.g. EXP012 `<Segment> | Companies Table`) to avoid paying for
enrichment again.
1. **Identify both** from `cb.audit(...).warnings` (lookup/route → EMPTY table while a fuller one
   exists). Confirm with Gaston which one is real if it isn't obvious (a "Don't use" name helps).
2. **Map every link** in the jobs table: the send route (`Send To Companies Table`), the lookup
   (`Find in Companies Table`), and every column reading the lookup (`cb.keysReadFrom(jobs, lookupId)`).
3. **Schema by name**: `cb.schemaDiffByName(emptyCopy, reused)` → columns the workflow needs that
   the reused table lacks. On EXP014 only `A/B Output`. Lookups read by column name, so **no field
   remap** is needed for columns that exist; the merge formulas stay as they are.
4. **Reuse check**: `cb.reuseCheck(reused)` → dedupe key (`companyIdentifier`, keep oldest: known
   companies add a source link, not a row), enrichment run status (all settled = nothing to
   re-enrich), `AUTO_RUN_MODE` (`keep_existing` = existing rows don't re-run), its own outbound
   links (route/lookup/write columns: must not feed another workflow's tables), and other
   workflows still feeding it (report; deduped, so harmless).
5. Gate A plan: add missing columns, re-point the lookup, re-create the send route, delete the old
   send column + auto-created columns (batch with IDs), orphan table for Gaston.
6. After the OK:
   - Missing `A/B Output`: `cb.addFormulaField(reused, 'A/B Output', '{{f_0thet2wFVpWUoSZrmP9}} ? (Math.random() < 0.5 ? "Baseline" : "Challenger") : ""', {allowFormulaOnAutoRun:true})`.
     It takes ~10 s to fill a 10k-row table; sample again before calling it broken.
   - Lookup: `tableId` input + `referencedTableId` only (filter field ID must exist there).
   - Send route: Create a route (above), template = the old send column's backup.
   - Merge formulas reading a **deleted** lookup: drop the `|| {{deleted}}?.record?.[X]` half (only
     if it's exactly two halves joined by ` || `, else ask).
7. Verify: `cb.audit` again → no link to the empty copy, enrichment run status unchanged, jobs
   `runTotals` unchanged. The empty copy becomes an orphan: list it for Gaston, never delete it.

## Delete a batch (after Gaston's OK)
```js
await cb.deleteFields('t_…', ['f_…', …], {approvedBy:'<Gaston\'s words>', approvedIds:['f_old…'], scanTables:[every table in the workbook + any table that routes into it]});
```
Deletes only columns created this run, pass-through auto-columns, or `approvedIds`, and only if
`refsTo` finds nothing. Returns per-field `deleted` / `skipped: <why>`. Log every result.

## Map arms to Smartlead campaigns
Per leads table, `Add Lead to Campaign`: change only the `campaign_id` input, guarded on its current
value and `configRevision`. Verify every other input byte-identical, referenced fields exist,
custom-field keys = the variable contract, run status unchanged.

## Full-run review (after Gaston runs rows)
- `cb.runStatus` / `cb.runTotals` use an unfiltered view and check its count (a table's first view
  can be "Errored Rows").
- `staleReason: TABLE_AUTO_RUN_OFF` = an upstream value changed while auto-run was off; cosmetic
  unless the value changed.
- Previews ("Status Code: 200") hide payloads: `cb.fullRecord(t, rid)` → `cells[f].externalContent.fullValue`.
- Funnel: recruiter filter → first occurrence → companyType → send to companies (watch the
  source's `numSourceRecords`, not row count: dedupe) → lookup found → Qualified → A/B → role
  qualified → contact chain → route per arm → email waterfall → Cold Email (ERROR_BLANK_TOKEN) → Add Lead.
- MoltSets search is a `limit: 1` fuzzy match: check that hit titles make sense.

## Lead check (Clay vs Smartlead, every lead)
Run interim (leads landing) and final (before Gate D).
1. Browser: `cb.dump(await cb.leadHashes({<campaignId>: '<leadsTableId>', …}, '<Final Work Email id>', ['<Subject Line>','<Email One>','<Email Two>','<email_three>']))`
   (field IDs in the same order as `--vars`). The harness saves the output to a file.
2. `python3 scripts/lead_check.py --clay-file <file> --vars subject_line,email_one,email_two,email_three`
   → every Smartlead lead: present in Clay, right arm, all variables identical (SHA-256 of trimmed
   text; Clay's trailing space doesn't matter), none empty. Target: 0 problems.
3. Reach: for Add Lead cells with SUCCESS, `cb.fullRecord` → `lead_actually_added` /
   `skipped_in_other_campaign_count`. Report the skip rate per arm and segment (EXP014: Marketing
   ~75%, Sales/GTM ~93%) and what it means for reaching the readout threshold. Similar rates
   across arms = the test stays fair.
4. Also report duplicates: the same email twice in one table (Smartlead keeps one) or in two
   segments' tables (it lands only in the first campaign).

## Inbox load
`python3 scripts/inbox_load.py <source_campaign_id> <other campaign ids of the experiment>` →
capacity (Σ `message_per_day`), sent today, the experiment's caps, and every active campaign
sharing the inboxes. Informational; never change inboxes.

## Start campaigns (Gate D)
Only on Gaston's explicit request, only campaigns created in this run, after a clean lead check:
`python3 scripts/start_campaigns.py --ids <ids> --created-this-run <ids from the log> --approved-by "<his words>"`.
It blocks unless each is DRAFTED/PAUSED, has leads and has OOO set, then starts and re-reads.

## Moving big JSON / backups to files
`javascript_tool` output over the limit is saved to a file by the harness. `cb.dump(obj)` pads the
output on purpose so that always happens. Then:
- backups: `python3 scripts/save_dump.py <file> "Near Work Partner/logs/backups/<log name>" --backups`
- anything else: `python3 scripts/save_dump.py <file> <out.json>`
Never paste large configs by hand. Small configs (< ~2k chars) can go straight into the log.
