# Gotchas: things that broke before (living list)

Add to this file after each run (SKILL.md §9), newest first within each section. Each line:
what happens → how to avoid it → where it was found. "Eng" = EXP014 Engineering build log,
"S/M" = EXP014 Sales/GTM + Marketing build log (both `Near Work Partner/logs/2026-11-06-…`).

## Duplicating / reusing tables
- **A duplicated workbook points everything at its own EMPTY companies copy**, even after Gaston
  moves the real table in. The copy exists and is in the workbook, so "missing table" checks pass.
  → read `cb.audit().warnings` (empty vs fuller sibling). (S/M step 7)
- **The duplicate's jobs source is scheduled and starts pulling right away** (2,759 rows before
  any edit). → check `records` + keywords at Gate A. (S/M step 3)
- **A moved-in table can lack a column the workflow reads** (`A/B Output`), so nothing routes.
  → `cb.schemaDiffByName` + `cb.keysReadFrom`. (Eng step 29, S/M step 7)
- **No remap needed for lookups**: they expose `record` by column name; only missing names matter. (S/M step 7)
- **Duplicating a leads table doesn't re-point routes.** Old routes keep the old table ID and arm
  label. Re-create them right after duplicating. (Eng step 6)
- **Cloned lookups can point at deleted per-workbook copies** (404) while their filter field IDs
  still match. `GET /v3/tables/{id}` every lookup target. (Eng step 13)

## Routes and columns
- **Route destination can't be changed in place.** PATCHing `tableId` saves and even shows in the
  workbook graph, but runs fail with `sourceId … undefined`. Create a new route. (Eng step 17)
- **`add-route-to-table` creates pass-through columns in the destination** for every origin column
  name it lacks (36 per companies table) **asynchronously**: 3 of Marketing's 36 appeared after the
  first check. → `createRoute` waits 10 s; diff against the destination's ORIGINAL field list and
  check again before and after deleting. (Eng step 31, S/M step 14)
- **New route = no run condition.** Origin auto-run must be off until the config is copied. (Eng step 29)
- **PATCH with a `name` already used in the table → 400.** Rename after the old column is gone. (Eng step 31)
- **Enrichment-column cap per table** ("table size limit"): the old column must go first. (Eng step 19)
- **Deleting a test table leaves dangling `||` halves** in merge formulas. Ref scan after any
  structural change. (Eng step 29)

## Prompts and runs
- **ERROR_BLANK_TOKEN:** a blank prompt input not in `optionalPathsInInputs` fails the cell
  silently; the lead is never sent. (Eng step 33)
- **Keyword guards: acronyms need case + word boundaries.** `/CTO/i` matches "Director"; the new
  text can legitimately contain old words ("solutions engineer"). Both aborted a correct edit
  (before any write). (S/M step 10)
- **A new formula column on a 10k-row table takes ~10 s to fill.** A first sample of all blanks
  isn't a bug. (S/M step 12)
- **Not every missing-field reference is live** (prose, few-shot examples, optional paths). `refScan`
  grades them. (dry run 2026-11-06, Eng step 31)
- **A table's first view can be filtered** ("Errored Rows" first in a challenger table): run status
  on it fakes "0 runs". The helpers use "All rows"/"Default view" and check the count. (Eng step 33, S/M review)
- **Bulk-fetch returns previews only** ("Status Code: 200"). Use the single-record GET. (Eng step 33)
- **Workspace credits are shared:** a credit delta doesn't prove "no runs". (Eng step 9)
- **`/v3/sources` objects carry a ~500k-char `exclude_job_identifiers`.** Never return one whole. (Eng step 3)

## Tooling
- **No top-level `return` in a `javascript_tool` script**: the result comes back `undefined` even
  though every call ran. Use `if` blocks; read state back before retrying. (S/M step 14)
- **Hidden browser pane = slow page = 45 s timeouts.** Store the promise on `window` and read it in
  the next call; the work keeps going. (S/M step 26)
- **Shell:** never put a bare `cat` next to a heredoc in one Bash line (waits on stdin). Foreground
  `sleep` is blocked: wait inside the script instead. (Eng step 24, S/M step 20)

## Smartlead
- **Clay add-lead SUCCESS ≠ added:** leads already in another campaign are skipped (Eng ~70%,
  Marketing ~75%, Sales/GTM ~93%). Count reach from Smartlead. (Eng step 34, S/M step 26)
- **Same person in two segments' leads tables** lands only in the first campaign. (S/M step 26)
- **Campaign names can contain U+00A0**: match by ID. (Eng step 21)
- **New API campaigns default differently** (`add_unsubscribe_tag: true`, empty AI categories, OOO
  off). The clone script fixes the first two; OOO is UI-only. (Eng step 24)
- **`create_campaign.py` isn't a 1:1 cloner.** Use `clone_campaign.py`. (Eng step 20)
- **Subsequences can't be created by API.** (Eng step 25)
- **"B Inboxes" isn't a clean rotation group**: it overlaps most "A inboxes" campaigns and is shared
  by ~32 parent campaigns; new campaigns split capacity, they don't add it. (S/M step 18)
