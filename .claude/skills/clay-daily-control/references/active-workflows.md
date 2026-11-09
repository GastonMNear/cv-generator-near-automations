# Active Clay workflows — the daily control list

Only these workbooks get the full daily check. `scan.js` takes the IDs in the **Workbook ID**
column. Everything else under *Open Jobs Campaigns* / *New Outbound Engine Open Jobs* gets
only a quick "is it moving?" probe, which surfaces candidates for this list.

**Change this list only after Gaston confirms.** Every daily run may propose:
- **Add:** a new workflow or campaign. Its sources moved in the last 3 days and it isn't in this list.
- **Replace:** a new version of a listed workflow (e.g. V3 next to V2, same folder). The new one
  goes in and the old one comes out.
- **Remove:** a listed workflow renamed `[Old]` / `[Paused]`, or with no source activity in 3+ days.

When an entry changes, log it in *Change log* below with the date and Gaston's reason.

Seeded 2026-11-03 from a live scan: every workbook whose sources moved in the last 72h, minus
`[Old]` / `[Paused]` ones. Gaston still has to confirm the seed (see Change log).

Link: `https://app.clay.com/workspaces/447061/workbooks/<Workbook ID>`

| Region | Workflow | Workbook ID | Type |
|---|---|---|---|
| US | [NO HM EXPs] US Open Jobs \| No HMs \| Candidate led vs routing CTA vs EXP008 | `wb_0thes7n5ga6XvyAz9Do` | No HM |
| US | [EXP014] - US Open Jobs \| No HMs \| Engineering Segment + MoltSets | `wb_0to30ny9K4KKH9JRRsG` | No HM |
| US | [EXP014] - US Open Jobs \| No HMs \| Sales/GTM Segment + MoltSets | `wb_0to3a8tnaiMVHUdoZHW` | No HM |
| US | [EXP014] - US Open Jobs \| No HMs \| Marketing Segment + MoltSets | `wb_0to3a8le5e8q6NG2mnE` | No HM |
| US | [EXP013] US OJ \| No HMs \| HR leaders | `wb_0tmnk5aYo6DqcHJTehN` | No HM (leads only) |
| US | HireBase \| US Open Jobs \| No HMs | `wb_0tn7o6gNXhJRY4NqXAK` | No HM (webhook source) |
| US | [EXP 006] US Open Jobs - Hiring Managers | `wb_0ti9p6bDTqxPMASMtdV` | HM |
| US | US OJ HMs Re-activation campaign \| HMs with new hiring signals | `wb_0tkssfqWPnY6Ex9HogW` | HM (leads only) |
| US | Coworkers \| US OJ HMs | `wb_0te93vpCKmwDaotCdM8` | HM |
| US | HubSpot cold accounts - Open Jobs from companies in CRM | `wb_0ti4jibrcZYjdDJdZBS` | HubSpot source |
| US | [EXP010] Apollo Open jobs \| TheirStack + PredictLeads scrape | `wb_0tjm5v6Nzoik7YWmQj9` | Apollo (CSV, weekly cleanup) |
| LATAM | Latam Open jobs \| No HMs \| V3 - With Companies Table | `wb_0tj9oxa6r3nZqENkyh4` | No HM |
| LATAM | LatAm Open Jobs - Hiring Managers (all) | `wb_0t6ghqvDTSNNbrTJqYP` | HM |
| Canada | Canada Open Jobs \| No HMs \| With Companies Table | `wb_0tlgnz4vac8N6Q8VBfK` | No HM |
| Canada | Canada Open Jobs \| HMs \| All Openings | `wb_0t746qfEw7oDTjBsb26` | HM |
| Asia | Asia Open Jobs \| No HMs \| V2 | `wb_0tfaequD9jakBGVK2Dg` | No HM |
| Asia | ASIA Open Jobs - Hiring Managers | `wb_0tfaeqoEJVXSSt7deyd` | HM |

**Shared (always checked by `scan.js`):** Exclusion Lookup `t_2w6YPVuSrbj7`, in workbook
*Recruiting Companies to Exclude*. Every workflow's *Write to Exclusion Lookup* writes here.

## Change log

- 2026-11-03: seeded with 18 workflows from the live scan. **Pending Gaston's confirmation.**
- 2026-11-06: added the 3 EXP014 workbooks (Engineering, Sales/GTM, Marketing; all launched 2026-11-06). Added by clay-experiment-builder review, Gaston OK 2026-11-06 ("implement your recommended changes"). They reuse the EXP012 companies tables, which the EXP012 workbooks also still feed.
- 2026-11-09: removed the 3 EXP012 workbooks (Engineering, Marketing, Sales/GTM). Gaston: "EXP012 is old, replaced by EXP014." All other US entries confirmed current (HubSpot cold accounts included, despite no source activity in 72h).
- 2026-11-09: removed [EXP009] CEOs Multi-role Savings (`wb_0tj967r4cCx4cCDHAve`). Gaston: paused.
