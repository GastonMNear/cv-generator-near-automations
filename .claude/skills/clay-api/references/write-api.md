# Clay write API (internal, verified 2026-11-06)

Mechanics only. When to use them, and the safety rules, live in the calling skill
(`clay-experiment-builder`). Source: Clay's own frontend contract
(`https://app.clay.com/assets/app-*.js` / `api-contract-client-*.js`, search for the route
name). Clay renames these files on deploy; find the asset that contains `updateField`.

## Session
Run calls **inside the in-app browser on app.clay.com** with
`fetch('https://api.clay.com/v3/…', {credentials: 'include'})` (Gaston's own login). The `.env`
curl login (kevin.dubon@) returns 400 since Nov 2026. `GET /v3/me` → 200 means you're in;
401 → ask Gaston to sign in. Never type credentials.

## Fields
| Action | Call | Notes |
|---|---|---|
| Update a field | `PATCH /v3/workspaces/{ws}/tables/{t}/fields/{f}?skipActionFieldRuns=true` body `{typeSettings, name?}` | `skipActionFieldRuns=true` = save without running. `typeSettings` has the same shape GET returns (action: `actionKey`, `actionPackageId`, `inputsBinding`, `conditionalRunFormulaText`, `optionalPathsInInputs`…; formula: `formulaText`, `dataTypeSettings`). Returns the field with a new `configRevision`. Setting a `name` already used in the table → 400. |
| Create a field | `POST /v3/workspaces/{ws}/tables/{t}/fields` body `{type: "formula", name, typeSettings: {dataTypeSettings: {type: "text"}, formulaType: "text", formulaText}}` | Formula fields compute for every row (free). |
| Delete a field | `DELETE /v3/workspaces/{ws}/tables/{t}/fields/{f}` body `{}` | Listed for completeness. Deletes need Gaston's explicit OK per field. |
| Run cells | `PATCH /v3/tables/{t}/run` body `{fieldIds:[f], runRecords:{recordIds:[r…]}, forceRun:true}` → `{runMode:"INDIVIDUAL"}` | Reruns one column on chosen rows only (verified 2026-11-09). `forceRun` is needed when the cell already has a result or error. Downstream columns that depend on `f` may run too, so check dependents first. Also accepts `runRecords.viewId`. Each run of a paid action costs credits, and an external action (Smartlead add) fires again. Run rows one at a time for rate-limited integrations, then poll `GET /records/{r}`. |
| Run status | `GET /v3/tables/{t}/views/{v}/fields/{f}/runstatus` → `statusCounts[{status, count, staleCount}]` | `status: null` = never ran. Use the "All rows" view. |

`inputsBinding` entries: `{name, formulaText}` (a Clay formula string, e.g. `"\"gpt-5.4-mini\""`,
`"{{f_x}}?.response"`) or `{name, formulaMap}` (an object, e.g. a route's `rowData`, an add-lead's
`custom_fields`). `optionalPathsInInputs: {prompt: [["f_a"], ["f_src","parent","Key"]]}` lists
inputs allowed to be blank. Anything else blank → `ERROR_BLANK_TOKEN`.

## Routes ("Send table data", actionKey `route-row`)
- Create: `POST /v3/{ws}/workbooks/{wb}/add-route-to-table` body `{originTableId, destinationTableId}`
  → `{destinationTable, routingField}`. It creates the route column **and** a routing source on
  the destination, attached to its existing source field. Defaults: name "Send table data",
  auto-mapped `rowData`, inputs `autoExtractColumns: "true"` etc. It auto-creates destination
  columns for mapped names the destination lacks.
- A route's destination can't be changed by PATCHing `tableId` (runs fail: `sourceId`
  undefined). Create a new one.
- Config: `tableId`, `referencedTableId`, `rowData` (formulaMap: destination name → formula),
  `listData` + `type: "list"` for one-row-per-person routes, run condition.

## Tables / workbooks
- Duplicate a table: `POST /v3/workspaces/{ws}/tables/{t}/duplicate` body `{name?}` →
  `{table, oldViewIdToNewViewIdMap}`. **Unverified**: test with Gaston before relying on it.
- No duplicate-workbook endpoint was found in the contract. Duplicate workbooks in the UI.
- Workbook graph (read): `GET /v3/workspaces/{ws}/workbooks/{wb}/overview` → `nodes`, `edges`
  (`SourceSubscription`, `RouteRow` with `actionFieldId` → `targetNodeId`).

## Records
- Full cell values: `GET /v3/tables/{t}/records/{r}` → `cells[f].externalContent.fullValue`.
  `bulk-fetch-records` returns previews only (e.g. "Status Code: 200").
- Cell staleness: `cells[f].metadata.isStale` + `staleReason` (e.g. `TABLE_AUTO_RUN_OFF`).
