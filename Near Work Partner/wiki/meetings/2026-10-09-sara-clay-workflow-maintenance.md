---
type: meeting
title: "Clay Session — Workflow maintenance (row cleanup, source reset, company-table limits) with Sara"
created: 2026-10-13
updated: 2026-10-13
attendees: ["Gaston Murillo — trainer", "Sara Calderon — Clay trainee"]
meeting-type: internal
duration-min: 68
recording_id: 191422014
fathom-url: "https://fathom.video/calls/854742988"
tags: [type/meeting, meeting-type/internal, clay, training, maintenance]
status: mature
related: ["[[wiki/meetings/2026-09-29-sara-clay-session-6]]", "[[wiki/meetings/2026-09-14-sara-clay-session-5]]"]
sources: ["[[bibliography/2026-10-09 - Clay Session Workflow Maintenance - Meeting]]"]
---

# Clay Session — Workflow maintenance — 2026-10-09

## TLDR
- **Sara takes over daily Clay workflow maintenance** from Tue Oct 13. Gaston sends her a checklist doc plus the recording [@1:00:18](https://fathom.video/calls/854742988?timestamp=3618).
- **Clay has two separate 50k limits: table rows and source records.** Either one stops imports, and then new leads stop flowing to campaigns [@14:13](https://fathom.video/calls/854742988?timestamp=853).
- **LATAM Company Table 2 is at ~39k.** Gaston offered a Tuesday call to build **Company Table 3** live with Sara [@39:21](https://fathom.video/calls/854742988?timestamp=2361).
- **Idea:** an AI that runs the daily checks and only flags workflows that need action. Estimate: ~20 → ~5 min/day [@1:01:00](https://fathom.video/calls/854742988?timestamp=3660). Viktor was not named.
- Gaston turned off 2FA on a shared tool account so Sara and Ale can log in (see Open Questions).

## Maintenance rules (checklist source)
**Row cleanup** (when a table nears 50k rows) [@00:46](https://fathom.video/calls/854742988?timestamp=46)
1. Filter on: *Previously Found Recruiting Company* has results · *Previously Found Recruiting Company 2* has results · *Write to Exclusion Lookup* has results · *Qualified (merge)* is not checked. **Switch AND → OR.**
2. Tools → **Download CSV** *before* deleting. Upload it to the Drive **"Clay Deleted Rows"** folder → region → HM / No-HM subfolder [@05:12](https://fathom.video/calls/854742988?timestamp=312).
3. Select all, then right-click → Delete rows. Large deletes leave leftovers, so refresh and delete again [@24:00](https://fathom.video/calls/854742988?timestamp=1440).
4. Still too many rows? Clear the filters, then filter on *Created at ≤* an old date (e.g. late August), export, and delete [@09:42](https://fathom.video/calls/854742988?timestamp=582).
5. **Never delete qualified or recent rows** (last days/weeks) [@16:21](https://fathom.video/calls/854742988?timestamp=981).
6. Clear all filters before leaving the table.

**Source reset** (Open Jobs sources)
- Click Delete source and close the prompt. This is only a way to see the source's record count. Act at ~35–45k [@16:21](https://fathom.video/calls/854742988?timestamp=981).
- Choose **"Delete source, but keep rows"**. "Delete rows" would wipe the table [@24:00](https://fathom.video/calls/854742988?timestamp=1440).
- To add the new source: + → See past searches → Workspace → the saved search (e.g. *Latam Open Jobs No Hiring Managers*). Then set **Exclude jobs = Latam Jobs US Recent table**, locations = TAM countries, employment type full-time, days since posted = 1 [@26:30](https://fathom.video/calls/854742988?timestamp=1590).
- Skim the 50-row preview for junk titles (e.g. *costureiro*). Add them to *Job titles to exclude* without trailing spaces, then **Update search** [@28:27](https://fathom.video/calls/854742988?timestamp=1707).
- Save to table → import and run (leave auto-run on). Once it finishes, set the schedule to **Daily** at 7–9 am and click **Save schedule** [@31:07](https://fathom.video/calls/854742988?timestamp=1867).
- **Quirk:** bulk imports don't trigger the first enrichment. Use the *Previously Found* column → "left to run" filter → **Force run** on the *filtered* rows only. Never force-run the whole table, because it would re-push old leads [@36:00](https://fathom.video/calls/854742988?timestamp=2160).

**Cadence:** LATAM and US **No-HM** fill fastest. Check them daily and clean them about every 2–3 days. HM workflows are low volume (1–2k/day). Apollo Open Jobs is loaded from Apollo by CSV (500–900 companies/day, so no source reset), and it needs a weekly row cleanup [@48:00](https://fathom.video/calls/854742988?timestamp=2880). The daily pass covers every workflow: US (several), LATAM ×2, Canada ×2, Asia ×2, Apollo ×1. For each one, check the row count, the source count, that the source ran today, and that today's leads went to the campaigns. Each check takes about 3 minutes if nothing needs deleting [@49:00](https://fathom.video/calls/854742988?timestamp=2940).

**Hidden limit: company/lead tables.** *Send to Company Table 2* errored this week even though the table had only ~25k rows. The cause: the "rows from…" table feed is also a source with its own 50k cap. The fix was to delete that source and re-create the Send-to-table column so a fresh source gets built. The same risk applies to the lead tables (*Send table data*). Check these sources and column errors every 2–3 days [@39:21](https://fathom.video/calls/854742988?timestamp=2361).

## Key Decisions
- One shared Drive folder for all deleted-row CSVs, whoever does the cleanup.
- Sara owns maintenance from the week of Oct 13, with the checklist as support.
- AI-assisted checking is parked as a follow-up.

## Action Items
**Gaston**
- [ ] Send Sara the maintenance checklist doc (from this call) + recording [@1:00:51](https://fathom.video/calls/854742988?timestamp=3651)
- [ ] Tue Oct 13: build LATAM Company Table 3 with Sara on a call. Pause the workflow, add the column/lookup, then restart [@39:21](https://fathom.video/calls/854742988?timestamp=2361)
- [ ] *(tentative)* Split the LATAM workflows into HM / No-HM folders like US ("capaz que le agrego unas carpetas") [@16:21](https://fathom.video/calls/854742988?timestamp=981)
- [ ] *(idea)* AI daily check that flags workflows needing cleanup [@1:07:13](https://fathom.video/calls/854742988?timestamp=4033)

**Sara**
- [ ] Start the daily maintenance checks Tue Oct 13. Add a daily calendar reminder [@1:07:13](https://fathom.video/calls/854742988?timestamp=4033)
- [ ] Tell Ale the shared login works again [@1:04:47](https://fathom.video/calls/854742988?timestamp=3887)

## Open Questions
- **2FA was removed on a shared tool account** (tool not named; Andrés was involved) [@1:02:48](https://fathom.video/calls/854742988?timestamp=3768). Login now asks for nothing, and the email-factor option wasn't available. Should 2FA be restored?
- Are the "folders" Clay workflow folders or Drive subfolders? Fathom says Drive, but the transcript reads as Clay.

## Full Transcript
See Fathom: https://fathom.video/calls/854742988
