# Templates

## Build log
File: `Near Work Partner/logs/YYYY-MM-DD-<exp>-<segment(s)>-build.md`, frontmatter
`type: log`, `date`, `workbooks: [wb_…]`, `family`. First lines: the request verbatim, the mode,
the source workflow, the family. Then one entry per step, written right after the step:

```
### <n> <short title>
- **Goal:** what this step was for, and why
- **Did:** exact actions (table, column, field ID, endpoint or UI path)
- **Result:** what changed (before → after) or what was found
- **Learned:** gotchas, conventions, patterns, anything that saves time next time
- **Open:** questions or doubts for Gaston
```

**Backups** go to `Near Work Partner/logs/backups/<log file name without .md>/<tableId>__<fieldId>.json`
(`cb.backup` → `cb.dump` → `save_dump.py --backups`). Under the editing step, list each:
`#### Backup: <table> / <field> — <name> (rev <configRevision>) → backups/<…>/<file>.json`.
Columns with the same `configRevision` (identical copies in two tables) are saved once; the log
says "identical to <file>". Small configs (< ~2k chars) may go inline as a JSON block.

Last sections: `## Skill update proposals`.

## Audit + plan (Gate A message)
```
# <EXP> <segment>: audit + plan (no writes yet)

**Mode / family:** <Launch|Replicate|Improve> · <family>
**Source:** <workflow> (`wb_…`) → **target:** <name> (`wb_…`)
<one-sentence verdict: ready to edit / blocked by …>

## Workflow map
| Table | ID | Rows | Auto-run | Role / key columns |

## Warnings from the audit
- <each cb.audit warning, explained>

## Inferred (veto any)
- <inference> — <why>

## Findings
| Check | Status | Detail |   ← conventions §5 checklist, OK / ⚠

## Plan (in order, each saved without running, backed up first)
| # | Table | Field | Before → After |

## Deletes (needs your OK for this batch)
| Table | Field ID | Name | Why |

## Gaston does in the UI
- duplicates / table deletes / source edits / auto-run toggles / subsequences / OOO

## Questions
1. … (only what couldn't be inferred)
```
For segment text, show **current / reference / proposed** side by side with what changed and why.

## Ready-to-launch report
```
# <EXP> <segment>: ready to launch
| | <segment> |
|---|---|
| Clay | lead title search, companies table in use, changed columns (field ID, before → after), auto-run state, 0 rows run |
| Smartlead | Baseline <id> / Challenger1 <id>, DRAFTED, 0 leads, <n> inboxes, residuals |
| Routing | arm → campaign ID → variables checked |
- Inbox load: <capacity>, <sharing campaigns>
- Orphans for Gaston: <tables>
- ⚠ Open items: …
- To launch, Gaston: 1. OOO (+ subsequences) in the Smartlead UI 2. run the jobs table
  3. tell me when leads land → lead check 4. "start them" → Gate D
- Registry / references: updated (or pending OK)
```

## Skill update proposals (end of every run)
```
## Skill update proposals
| # | File | Change | Exact text (or summary + where) | Because (step) | Status |
|---|---|---|---|---|---|
| 1 | references/gotchas.md | add | "…" | step 14: … | proposed |
```
Status: `proposed` → `applied <date>` or `rejected <date>: <Gaston's reason>`. Before proposing,
read the proposals tables of the recent `Near Work Partner/logs/*-build.md` so a rejected idea
isn't re-proposed unless something changed.
