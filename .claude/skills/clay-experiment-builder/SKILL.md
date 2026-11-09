---
name: clay-experiment-builder
description: >
  Builds, changes and audits Near's Clay outbound workflows end to end, and sets up the
  matching Smartlead campaigns, up to launch. Four modes: LAUNCH a new cold-email experiment
  from a one-line request ("Launching EXP015 for Product — duplicate the EXP014 Engineering
  workflow, new challenger Email 1 attached"), REPLICATE an existing experiment to another
  segment or region ("replicate EXP014 to Sales/GTM and Marketing"), IMPROVE an existing
  workflow (swap a prompt, model, lookup, companies table, routing, campaign mapping), or
  AUDIT one read-only (map tables, broken references, baseline vs challenger, Clay→Smartlead
  variables, lead check vs Smartlead). Use it whenever Gaston mentions launching, building,
  cloning, replicating or setting up an experiment / EXP0xx / a new segment or challenger arm,
  reusing a companies table, changing or fixing columns in a Clay workflow, re-pointing routes
  or lookups, "is this workflow wired correctly", connecting Clay leads tables to Smartlead
  campaigns, or checking/starting the new campaigns, even if he doesn't name the skill. Not
  for daily row/source maintenance (clay-daily-control) or one-off lead lookups (clay-api).
---

# Clay experiment builder

Turns a one-line request into a fully wired Clay workflow plus Smartlead campaigns. It also
replicates, improves and audits existing workflows. It is a **living skill**: every run keeps
a build log and ends by proposing updates to this skill, applied after Gaston's OK.

Worked examples (read when a step feels underspecified):
`Near Work Partner/logs/2026-11-06-eng-email1-experiment-build.md` (new experiment) and
`Near Work Partner/logs/2026-11-06-exp014-sales-marketing-build.md` (replicate + reuse an
existing companies table + launch).

## Safety rules (read before anything else)

Every action here touches live outbound: a wrong run spends credits or emails real people;
a wrong delete loses data the workflow depends on.

1. **Never run rows.** No column runs, "run all", source refreshes or re-runs. Save every
   edit with `?skipActionFieldRuns=true` (the `cb` helpers do) and check run status after.
2. **Auto-run.** Never add or edit an **action** column on a table with `AUTO_RUN_ON: true`:
   ask Gaston to turn it off, or to confirm for that table. A **formula** column on an
   auto-run table costs nothing but fills every row at once, so it needs an OK that names the
   table and its row count. Some tables must stay on (a reused companies table enriches new
   companies), so never toggle auto-run yourself.
3. **Deletes need a batch OK.** Never delete, clear or rename anything without Gaston's OK
   for that exact batch (IDs listed). With that OK, `cb.deleteFields` deletes only: columns
   created in this run, Clay's auto-created pass-through columns, or columns listed by ID,
   and only if nothing references them. **Tables, sources, rows and campaigns are never
   deleted by you**: list them for Gaston (e.g. an orphaned duplicate companies table).
4. **Smartlead.** Create-only. Never edit, pause or delete an existing campaign. An existing
   campaign (even ACTIVE) may be **read** as a clone template. Starting campaigns is Gate D only.
5. **Back up before every edit** with `cb.backup`, saved to the run's backup folder and linked
   from the log (templates.md). Every change must be reversible from its backup.
6. **Four approval gates.** Gaston's explicit OK (A) after audit + plan, before any write;
   (B) before creating Smartlead campaigns; (C) before routing Clay to them; (D) before
   starting campaigns. An OK covers what you showed, nothing more. If the work changes shape, ask again.
7. **Ambiguity stops work.** Two candidate columns/tables (two companies tables, an empty one
   and a full one, unclear baseline), a label you can't map, an unknown workflow family:
   stop and ask. Don't pick.

Access: Clay through the in-app browser with Gaston's own login (`/v3/me` must be 200; on a
401 ask him to sign in, never type credentials). Smartlead through `SMARTLEAD_API_KEY` in
`.env` (scripts here use `scripts/sl.py`). API mechanics: `clay-api` (`references/write-api.md`,
`clay-api-endpoints.md`) and `smartlead-campaign-creator` (§Clone an existing campaign 1:1).

## Pick the mode

| Request looks like | Mode | Writes? |
|---|---|---|
| "Launching EXP0xx for <segment> … new challenger Email 1" | **Launch** (new experiment) | yes, gated |
| "replicate / roll out / copy EXP0xx to <segment(s)/region>" | **Replicate** (same experiment, new segment) | yes, gated |
| "swap the model / prompt / title search", "point X at the companies table", "fix the routing", "map the arms to the campaigns" | **Improve** | yes, gated |
| "review / audit / check EXP0xx", "is this wired right", "why aren't leads reaching …", "check the leads vs Smartlead" | **Audit** | no |
| "start / activate the campaigns" (after a build) | **Gate D** of the run that created them | yes, gated |

Every mode starts with the same read-only audit (§1). Audit mode stops after the report.
One request can cover several segments: run them in parallel through each step, one build log.

## Workflow families

A family = a workflow shape (tables, roles, columns, naming, Smartlead pattern), described in
`references/conventions.md` §Families. Known: **US OJ No-HM experiment (EXP012/EXP014 line)**.
For any workflow, first match it to a family from the audit (`cb.audit` roles + column names).
**No match** (HM workflows, Asia/Canada/LatAm, HireBase, a new layout): still run the audit,
describe the anatomy you found, ask Gaston what differs from the nearest family, and end the
run with a proposed new family entry. Never apply one family's field IDs or defaults to another
without checking them in the audit.

## Inference: what to work out yourself vs ask

Fill everything you can from the family conventions and the source workflow, then ask
**once**, in a single message, for only what's left. State every inference in the plan so
Gaston can veto it.

**Infer:**
- Names (workbook, tables, campaigns, build log) from the family's naming patterns.
- Source workflow: from the request, `clay-daily-control/references/active-workflows.md`,
  `clay-api/references/known-tables.md` and the workspace table list.
- Arms: baseline = the source's baseline leads table, unchanged. Challenger = a duplicate of
  it with only the column under test changed. Email 2/3 byte-identical across arms.
- **Launch:** challenger Email 1 rebuilt from the attached copy (`clay-recipes` §Email prompt).
- **Replicate:** challenger Email 1 = the source's challenger prompt, with only its
  segment-specific **examples** swapped (slot examples like "Cybersecurity Engineer", "Elastic
  SIEM"). No new copy is needed; don't ask for any. Same experiment ID; names carry the segment.
- Segment text: the lead title search and any prompt examples get the new department
  (`clay-recipes` §Swap a segment). Keep the family's size rules unless Gaston gives others.
- Jobs source: a new segment needs its own job-title keywords. Draft them (or confirm the
  ones already set) and show them at Gate A. Gaston edits the source in the UI.
- Companies table: prefer an **existing, already-enriched table for that segment** (e.g. the
  previous experiment's `<Segment> | Companies Table`) over the empty copy a duplicate makes,
  so you don't pay to enrich companies again. Show it as an inference; ask if more than one fits.
- Smartlead: clone the **source experiment's own arm campaigns**, by ID (baseline from
  baseline, challenger from challenger), into the source's inbox set, start date today, DRAFTED.
- Models: a deprecated model in a column you touch → the family's current default; both arms together.

**Ask only for:** copy that isn't attached (Launch), numbers in the copy with no data or
fallback, which companies table when several fit, the keyword list approval, the jobs-source
schedule if it's already pulling, anything the family marks **ask**.

## Run

Keep a build log from the first step (`references/templates.md`). Write each entry right after
its step. Backups go to the backup folder; the log links them.

### 0. Session + source
Check `/v3/me`. Load `scripts/clay-builder.js` (read it, run its text with
`mcp__Claude_Browser__javascript_tool`; it defines `window.cb`). Find the source workbook.
Workbook duplication isn't in Clay's API: if the target workbook doesn't exist, ask Gaston to
duplicate the source in the UI and rename it, then continue on the copy. Same for a new
challenger leads table (duplicate the baseline leads table, rename it).

### 1. Audit (read-only)
`window._a = cb.audit("<workbookId>")`, then read `await window._a` in the next call (big
workbooks or a hidden pane can pass the 45 s tool timeout). Read **`warnings` first**: links to
a missing table, to an empty companies table while a fuller one exists, to another workbook's
table with the same name as one here (a duplicate still wired to its source), a jobs source that
already pulled rows. `external` lists the intended shared links (Exclusion Lookup, comp guide,
cross-workflow routes): check them against the family, no action. Then: tables + roles + auto-run, models, routes/lookups and targets,
A/B formulas, jobs source, `refScan` (LIVE = fix or ask), `armDiff`, Smartlead mapping. Add:
- Diff vs the source workbook by field ID (`cb.armDiff` works across workbooks: duplicates keep IDs).
  Expect only table pointers + the segment text; anything else is a finding.
- Segment text left over (`clay-recipes` §Swap a segment, keyword scan).
- Companies table plan if it's being reused (`clay-recipes` §Reuse an existing companies table).
- Run status: `cb.runTotals(table)` on each table you'll touch (baseline for "0 runs").
- The family's audit checklist (conventions §Audit checklist): OK / ⚠ + reason each.

### 2. Plan → **Gate A**
Audit + plan in the templates.md format: one line per change (table, field ID, before → after),
every inference, the questions, the delete batch (IDs) if any, and what Gaston does in the UI.
**Stop and wait.** Approval can be per item.

### 3. Clay edits (after Gate A), dependencies first
Each: back up → edit → re-read → verify → log.
1. Segment text: lead title search, then prompt examples (§Swap a segment).
2. Models (§Swap a model), both arms.
3. Challenger Email 1 (§Email prompt), incl. `optionalPathsInInputs` for every nullable input.
4. Email 2/3 identical across arms (§Make Email 2/3 identical).
5. Companies table: reuse/swap (§Reuse an existing companies table), incl. `A/B Output`.
6. Routes whose destination must change: create new (§Create a route), never re-point.
7. Approved deletes (`cb.deleteFields`), then rename new columns that were blocked by old names.
8. Verify: `cb.audit` again (no `warnings` left that you were meant to fix, no LIVE refs), arms
   differ only in the column(s) under test, `cb.runTotals` unchanged, no reference to the old
   tables. Report and wait for Gaston's Clay approval before Smartlead.

### 4. Smartlead → **Gate B**
Show the clone plan (source campaign IDs, new names, inbox count) plus the inbox load
(`python3 scripts/inbox_load.py <source_id> <other experiment campaign ids>`, informational).
After the OK: `smartlead-campaign-creator` §Clone 1:1, one campaign first as a test, verify,
then the rest. Diff each vs its source and vs the first new one; re-read the sources to prove
they weren't written (`updated_at` unchanged).

### 5. Routing → **Gate C**
Per leads table, `Add Lead to Campaign` → its own campaign. Show the mapping + the variable
contract check. After the OK change **only `campaign_id`** (guard on the old value), verify,
check run status. Then the ready-to-launch report (templates.md).

### 6. First run + lead check
Gaston runs rows. When leads land (interim or final), run the full lead check
(`clay-recipes` §Lead check): every lead, right arm, identical copy, no empty variables, plus
reach (Clay adds skipped as "already in another campaign").

### 7. Start → **Gate D**
Only on Gaston's explicit request, only campaigns created in this run, only after a clean lead
check: `python3 scripts/start_campaigns.py --ids … --created-this-run … --approved-by "<his words>"`.
It refuses unless each is DRAFTED/PAUSED, has leads and has OOO set.

### 8. Register + references
Add new workbooks to `clay-daily-control/references/active-workflows.md` (with a Change log
line) and IDs to `clay-api/references/known-tables.md` + `wiki/tools/smartlead.md`, after OK.

### 9. Close the loop (every run, every mode)
End the build log with `## Skill update proposals` (templates.md): new gotchas, conventions,
family entries, recipe or script fixes, each with file + exact text + status. Show them in
chat; apply only after Gaston's OK; mark each applied/rejected so the next run sees it.

## Improve / Audit
**Improve:** §1 audit, then a plan limited to the requested change plus anything it breaks
(ref scan before and after), the gates that apply, same log and proposals.
**Audit:** §0–§1 only, plus `clay-recipes` §Full-run review if rows ran and §Lead check if
leads are in Smartlead. No writes. Still propose skill updates.

## Reference files
- `references/conventions.md`: families (anatomy, field IDs, naming, defaults, variable
  contract, audit checklist), inbox rule, how to add a family. Read at the start of every run.
- `references/clay-recipes.md`: step-by-step recipes. Read the recipe before each edit.
- `references/gotchas.md`: what broke before. Skim before writing anything.
- `references/templates.md`: build log + backups, Gate A message, ready-to-launch report,
  skill update proposals.
- `scripts/clay-builder.js` (browser): `cb.audit`, `refScan`, `armDiff`, `schemaDiffByName`,
  `keysReadFrom`, `reuseCheck`, `runStatus`, `runTotals`, `backup`, `patch`, `addFormulaField`,
  `createRoute`, `newColumnsSince`, `deleteFields`, `refsTo`, `leadHashes`, `fullRecord`, `dump`.
- `scripts/*.py` (local): `lead_check.py`, `inbox_load.py`, `start_campaigns.py`, `save_dump.py`, `sl.py`.
