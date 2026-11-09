// clay-builder.js — helpers for the clay-experiment-builder skill.
// Runs INSIDE the in-app browser on app.clay.com (mcp__Claude_Browser__javascript_tool), so every
// call uses Gaston's own Clay session. Load: read this file and execute its text; it defines
// window.cb. Then call e.g. `await cb.audit("wb_…")` in a later javascript_tool call.
//
// Tool hygiene: never use a top-level `return` in a javascript_tool script (the whole result comes
// back `undefined` even though every call ran). For anything slow (audit of a big workbook, a hidden
// browser pane), start it as `window._p = cb.audit(…)` and read `await window._p` in the next call.
//
// Safety by construction:
//  - Every write uses ?skipActionFieldRuns=true.
//  - Action columns can't be added/edited on a table with AUTO_RUN on (opts.allowAutoRun only after
//    Gaston confirmed it for that table in this run). Formula columns on an auto-run table need
//    opts.allowFormulaOnAutoRun (free to compute, but they fill every row at once).
//  - cb.patch refuses a field that wasn't backed up first with cb.backup() (no bypass).
//  - cb.deleteFields only deletes (a) columns created in this run, (b) Clay's auto-created
//    pass-through formulas, or (c) columns listed explicitly in opts.approvedIds, always with
//    opts.approvedBy = Gaston's words, and only if nothing references them.
//  - Keep tool outputs small: return summaries; use cb.dump() for big JSON (see recipes).

(() => {
  const WS = 447061, API = 'https://api.clay.com/v3';
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  async function j(path, opt = {}) {
    const r = await fetch(API + path, {
      credentials: 'include', ...opt,
      headers: { 'Content-Type': 'application/json', ...(opt.headers || {}) },
    });
    if (r.status === 401) throw new Error('Clay session expired: ask Gaston to sign in in the browser pane');
    const text = await r.text();
    let body; try { body = JSON.parse(text); } catch (e) { body = text; }
    if (!r.ok) {
      const err = new Error(`${opt.method || 'GET'} ${path} → ${r.status}: ${String(text).slice(0, 300)}`);
      err.status = r.status; throw err;
    }
    return body;
  }

  const table = async (id) => (await j('/tables/' + id)).table;
  const count = async (id) => (await j(`/tables/${id}/count`)).tableTotalRecordsCount;
  const clone = (o) => JSON.parse(JSON.stringify(o));
  const unq = (s) => (typeof s === 'string' ? s.replace(/^"|"$/g, '') : s);
  const TABLE_RE = /\bt_[A-Za-z0-9]{10,}\b/g;            // old IDs (t_2w6YPVuSrbj7) and new (t_0t…)
  const PASS_THROUGH = /^\{\{f_[A-Za-z0-9]+\}\}\?\.\["[^"]*"\]$/;  // add-route-to-table's auto columns
  const _created = new Set();                             // "table/field" created in this run
  const _backups = {};

  // An unfiltered view: "All rows", else "Default view". Fails if its count ≠ the table's row count
  // (a filtered first view, e.g. "Errored Rows", would fake "0 rows ran").
  async function allRowsView(tableId, tb) {
    tb = tb || await table(tableId);
    const v = tb.views.find((x) => /^all rows$/i.test(x.name)) || tb.views.find((x) => /^default view$/i.test(x.name));
    if (!v) throw new Error(`${tb.name}: no "All rows" / "Default view" view; ask Gaston which view is unfiltered`);
    return v.id;  // runStatus/runTotals then check the view's row total against the table count
  }

  // Flatten a field config into comparable strings.
  function flat(f) {
    const ts = f.typeSettings || {}; const m = {};
    (ts.inputsBinding || []).forEach((b) => {
      if (b.formulaText !== undefined) m[b.name] = b.formulaText;
      else if (b.formulaMap) m[b.name] = JSON.stringify(b.formulaMap);
    });
    if (ts.formulaText) m.__formula = ts.formulaText;
    if (ts.formulaWaterfall) m.__waterfall = JSON.stringify(ts.formulaWaterfall);
    m.__cond = ts.conditionalRunFormulaText || '';
    m.__key = ts.actionKey || f.type;
    m.__optional = JSON.stringify(ts.optionalPathsInInputs || {});
    m.__referencedTable = ts.referencedTableId || '';
    return m;
  }

  function setInput(ts, name, formulaText) {
    ts.inputsBinding = ts.inputsBinding || [];
    const b = ts.inputsBinding.find((x) => x.name === name);
    if (b) { b.formulaText = formulaText; delete b.formulaMap; }
    else ts.inputsBinding.push({ name, formulaText });
    return ts;
  }

  async function inputs(tableId, fieldId) {
    const f = (await table(tableId)).fields.find((x) => x.id === fieldId);
    if (!f) throw new Error(`field ${fieldId} not in ${tableId}`);
    return flat(f);
  }

  // Per-status counts for each field, on an unfiltered view (count-checked).
  async function runStatus(tableId, fieldIds) {
    const tb = await table(tableId); const v = await allRowsView(tableId, tb); const rows = await count(tableId); const out = {};
    for (const fid of fieldIds) {
      const r = await j(`/tables/${tableId}/views/${v}/fields/${fid}/runstatus`);
      const total = (r.statusCounts || []).reduce((a, s) => a + s.count, 0);
      if (total !== rows) throw new Error(`${tb.name}: view counts ${total} rows but the table has ${rows}; the view is filtered`);
      const name = tb.fields.find((f) => f.id === fid)?.name || fid;
      out[name] = (r.statusCounts || []).map((s) => `${s.status || 'not run'}:${s.count}${s.staleCount ? ` (stale ${s.staleCount})` : ''}`).join(', ');
    }
    return out;
  }

  // Totals across every action column of a table: {status: cells}. "0 runs" = only "not run".
  async function runTotals(tableId) {
    const tb = await table(tableId); const acts = tb.fields.filter((f) => f.type === 'action').map((f) => f.id);
    const v = await allRowsView(tableId, tb); const rows = await count(tableId); const tot = {};
    for (const fid of acts) {
      const r = await j(`/tables/${tableId}/views/${v}/fields/${fid}/runstatus`);
      for (const s of r.statusCounts || []) tot[s.status || 'not run'] = (tot[s.status || 'not run'] || 0) + s.count;
    }
    return { table: tb.name, rows, actionColumns: acts.length, cells: tot };
  }

  function pathsOf(obj, needle, p = '') {
    if (typeof obj === 'string') return obj.includes(needle) ? [p.slice(1)] : [];
    if (obj && typeof obj === 'object') return Object.entries(obj).flatMap(([k, v]) => pathsOf(v, needle, p + '.' + k));
    return [];
  }

  // Missing field refs and missing tables, graded. LIVE = used when the column runs: fix or ask.
  // optional-path-only / prose-only (conditionalRunFormulaPrompt, formulaPrompt, tableExamples) = harmless.
  const PROSE = /^(conditionalRunFormulaPrompt|formulaPrompt)$/;
  async function refScan(tableIds) {
    const all = new Set((await j(`/workspaces/${WS}/tables`)).results.map((t) => t.id));
    const out = {};
    for (const tid of tableIds) {
      const tb = await table(tid); const ids = new Set(tb.fields.map((f) => f.id));
      const sys = new Set(['f_created_at', 'f_updated_at']);
      out[tb.name] = [];
      for (const f of tb.fields) {
        const ts = f.typeSettings || {}; const s = JSON.stringify(ts);
        const refs = new Set([...(s.match(/\{\{(f_[A-Za-z0-9]+)\}\}/g) || []).map((x) => x.slice(2, -2)),
          ...JSON.stringify(ts.optionalPathsInInputs || {}).match(/f_[A-Za-z0-9]+/g) || []]);
        const missing = [...refs].filter((r) => !ids.has(r) && !sys.has(r));
        const mt = [...new Set(s.match(TABLE_RE) || [])].filter((x) => !all.has(x));
        if (!missing.length && !mt.length) continue;
        const where = Object.fromEntries([...missing, ...mt].map((r) => [r, pathsOf(ts, r)]));
        const paths = Object.values(where).flat();
        const harmless = (pth) => PROSE.test(pth.split('.')[0]) || (pth.startsWith('inputsBinding.') && ts.inputsBinding[+pth.split('.')[1]]?.name === 'tableExamples');
        const severity = paths.every(harmless) ? 'prose-only'
          : paths.every((pth) => harmless(pth) || pth.startsWith('optionalPathsInInputs')) ? 'optional-path-only' : 'LIVE';
        out[tb.name].push({ field: f.name, id: f.id, severity, missingFields: missing, missingTables: mt, where });
      }
    }
    return out;
  }

  // Jobs source summary without the huge exclude_job_identifiers list.
  async function sourceSummary(tableId) {
    const res = await j('/sources?tableId=' + tableId);
    return (res.results || res).map((s) => {
      const inp = { ...(s.typeSettings?.inputs || {}) };
      const excluded = (inp.exclude_job_identifiers || []).length; delete inp.exclude_job_identifiers;
      const sc = s.typeSettings?.scheduleConfig || s.scheduleConfig || {};
      return { id: s.id, name: s.name, type: s.type, records: s.state?.numSourceRecords ?? s.numSourceRecords, excludedJobIds: excluded,
        inputs: inp, runSettings: sc.runSettings || null, schedule: sc.schedule?.value || null };
    });
  }

  // Field-by-field diff of two tables (cloned tables share field IDs).
  async function armDiff(tA, tB) {
    const [a, b] = await Promise.all([table(tA), table(tB)]);
    const bm = Object.fromEntries(b.fields.map((f) => [f.id, f]));
    const diffs = [], onlyA = [];
    for (const f of a.fields) {
      const g = bm[f.id]; if (!g) { onlyA.push(f.name); continue; }
      if (f.type === 'source') continue;
      const x = flat(f), y = flat(g);
      const keys = [...new Set([...Object.keys(x), ...Object.keys(y)])].filter((k) => x[k] !== y[k]);
      if (keys.length) diffs.push({ field: f.name, id: f.id, keys });
    }
    const aIds = new Set(a.fields.map((f) => f.id));
    return { a: a.name, b: b.name, diffs, onlyA, onlyB: b.fields.filter((f) => !aIds.has(f.id)).map((f) => f.name) };
  }

  // Columns by NAME: what `need` has that `have` lacks (lookups expose records by column name).
  async function schemaDiffByName(needTableId, haveTableId) {
    const [n, h] = await Promise.all([table(needTableId), table(haveTableId)]);
    const hn = new Set(h.fields.map((f) => f.name));
    return { missingInHave: n.fields.filter((f) => !hn.has(f.name) && f.type !== 'source').map((f) => `${f.name} (${f.type})`),
      extraInHave: h.fields.filter((f) => !new Set(n.fields.map((x) => x.name)).has(f.name)).map((f) => f.name) };
  }

  // Record keys a table reads from a lookup field: {{lookup}}?.record?.["X"] / .record?.X
  async function keysReadFrom(tableId, lookupFieldId) {
    const tb = await table(tableId); const out = [];
    for (const f of tb.fields) {
      const s = JSON.stringify(f.typeSettings || {}).replace(/\\"/g, '"');
      const keys = [...s.matchAll(new RegExp(`\\{\\{${lookupFieldId}\\}\\}\\?\\.record\\?\\.(?:\\["([^"]+)"\\]|([A-Za-z_][A-Za-z0-9_]*))`, 'g'))].map((m) => m[1] || m[2]);
      if (keys.length && f.id !== lookupFieldId) out.push({ field: f.name, id: f.id, reads: [...new Set(keys)] });
    }
    return out;
  }

  // A companies-style table being reused: auto-run, dedupe, its action columns' run status
  // (credit exposure), its own outbound links, and every source feeding it.
  async function reuseCheck(tableId) {
    const tb = await table(tableId); const rows = await count(tableId);
    const acts = tb.fields.filter((f) => f.type === 'action');
    const outbound = acts.filter((f) => /^(route-row|lookup-|write-to-)/.test(f.typeSettings?.actionKey || ''))
      .map((f) => ({ field: f.name, action: f.typeSettings.actionKey, target: f.typeSettings.referencedTableId || unq(flat(f).tableId) }));
    const enrich = acts.filter((f) => !outbound.find((o) => o.field === f.name)).map((f) => f.id);
    const srcRes = await j('/sources?tableId=' + tableId);
    return { table: tb.name, rows, autoRun: tb.tableSettings?.AUTO_RUN_ON, autoRunMode: tb.tableSettings?.AUTO_RUN_MODE,
      dedupe: tb.tableSettings?.DEDUPE_FIELD_ID, outboundLinks: outbound,
      enrichmentRunStatus: enrich.length ? await runStatus(tableId, enrich) : {},
      sources: (srcRes.results || srcRes).map((s) => ({ id: s.id, name: s.name, records: s.state?.numSourceRecords ?? s.numSourceRecords })) };
  }

  // Pure (no API calls, unit-testable). tables: [{id,name,role,rows}] of THIS workbook;
  // routes: [{name,table,dest}]; lookups: [{name,table,target}]; names: {tableId: name} workspace-wide.
  // Warns on: missing targets; an EMPTY companies target while a fuller companies table exists here;
  // several companies tables; an external target whose NAME matches a table of this workbook (a
  // duplicate still pointing at the source workflow's copy). Other external links (shared Exclusion
  // Lookup, comp guide, cross-workflow routes) go to `external` as info.
  function linkWarnings(tables, routes, lookups, names) {
    const warnings = [], external = [];
    const here = new Map(tables.map((t) => [t.id, t]));
    const hereNames = new Set(tables.map((t) => t.name));
    const companies = tables.filter((t) => t.role === 'companies');
    const links = [...routes.map((r) => ({ kind: 'route', name: r.name, table: r.table, target: r.dest })),
      ...lookups.map((l) => ({ kind: 'lookup', name: l.name, table: l.table, target: l.target }))];
    for (const k of links) {
      const label = `${k.kind} "${k.name}" (${k.table})`;
      if (!names[k.target]) { warnings.push(`⚠ ${label} → MISSING table ${k.target}`); continue; }
      const tgt = here.get(k.target);
      if (!tgt) {
        if (hereNames.has(names[k.target])) warnings.push(`⚠ ${label} → "${names[k.target]}" (${k.target}) in ANOTHER workbook, same name as a table here: likely still the source workflow's copy`);
        else external.push(`${label} → "${names[k.target]}" (${k.target})`);
        continue;
      }
      if (tgt.role === 'companies' && tgt.rows === 0) {
        const fuller = companies.filter((t) => t.id !== tgt.id && t.rows > 0);
        if (fuller.length) warnings.push(`⚠ ${label} → EMPTY companies table "${tgt.name}" while ${fuller.map((x) => `"${x.name}" (${x.rows} rows)`).join(', ')} exist: ask which one is real`);
      }
    }
    if (companies.length > 1) warnings.push(`⚠ ${companies.length} companies tables in this workbook: ${companies.map((t) => `"${t.name}" ${t.rows} rows`).join(', ')}`);
    return { warnings, external };
  }

  async function audit(workbookId) {
    const allTables = (await j(`/workspaces/${WS}/tables`)).results;
    const list = allTables.filter((t) => t.workbookId === workbookId && !t.deletedAt);
    const allIds = new Set(allTables.map((t) => t.id));
    const inWb = new Set(list.map((t) => t.id));
    const tables = [], models = {}, routes = [], lookups = [], ab = [], addLead = [], warnings = [];
    for (const t of list) {
      const tb = await table(t.id);
      const srcRes = await j('/sources?tableId=' + t.id);
      const srcs = (srcRes.results || srcRes).map((s) => ({ id: s.id, name: s.name, type: s.type, records: s.state?.numSourceRecords ?? s.numSourceRecords }));
      const role = srcs.some((s) => s.type === 'v3-action' || s.type === 'webhook') ? 'jobs'
        : /compan/i.test(tb.name) ? 'companies' : /lead/i.test(tb.name) ? 'leads' : 'other';
      tables.push({ id: t.id, name: tb.name, role, rows: await count(t.id), autoRun: tb.tableSettings?.AUTO_RUN_ON, autoRunMode: tb.tableSettings?.AUTO_RUN_MODE, dedupe: tb.tableSettings?.DEDUPE_FIELD_ID, nFields: tb.fields.length, sources: srcs });
      for (const f of tb.fields) {
        const m = flat(f);
        if (m.model) (models[unq(m.model)] = models[unq(m.model)] || []).push(`${tb.name} / ${f.name}`);
        if (m.__key === 'route-row') {
          const dest = unq(m.tableId);
          routes.push({ table: tb.name, tableId: t.id, id: f.id, name: f.name, dest, destExists: allIds.has(dest), destInWorkbook: inWb.has(dest), label: (m.__cond.match(/===\s*'([^']+)'/) || [])[1] || '', listData: m.listData || '' });
        }
        if (/^lookup-/.test(m.__key)) { const d = unq(m.tableId); lookups.push({ table: tb.name, tableId: t.id, id: f.id, name: f.name, target: d, exists: allIds.has(d), inWorkbook: inWb.has(d) }); }
        if (f.name === 'A/B Output') ab.push({ table: tb.name, id: f.id, formula: m.__formula });
        if (m.__key === 'add-lead-to-campaign') {
          let cf = {}; try { cf = JSON.parse(m.custom_fields || '{}'); } catch (e) {}
          addLead.push({ table: tb.name, tableId: t.id, id: f.id, campaign: unq(m.campaign_id), email: m.email, customKeys: Object.keys(cf).sort(), cond: m.__cond });
        }
      }
    }
    const lw = linkWarnings(tables, routes, lookups, Object.fromEntries(allTables.map((t) => [t.id, t.name])));
    warnings.push(...lw.warnings);
    const leads = tables.filter((t) => t.role === 'leads');
    const base = leads.find((t) => /baseline/i.test(t.name)), chal = leads.find((t) => /challenger/i.test(t.name));
    const jobs = tables.find((t) => t.role === 'jobs');
    const jobsSource = jobs ? (await sourceSummary(jobs.id)).filter((s) => s.type === 'v3-action').map((s) => ({ id: s.id, name: s.name, records: s.records, keywords: s.inputs.job_title_keywords, excludeKeywords: s.inputs.job_title_exclude_keywords, days: s.inputs.max_num_days_since_posted, locations: s.inputs.locations, runSettings: s.runSettings, schedule: s.schedule })) : null;
    (jobsSource || []).forEach((s) => { if (s.records) warnings.push(`⚠ jobs source "${s.name}" already pulled ${s.records} records (${s.runSettings === 'scheduleV2' ? 'scheduled' : s.runSettings}): check its keywords fit this segment`); });
    return { workbookId, tables, models, routes, lookups, ab, addLead, jobsSource, warnings, external: lw.external,
      refScan: await refScan(tables.map((t) => t.id)),
      armDiff: base && chal ? await armDiff(base.id, chal.id) : 'baseline/challenger leads tables not identified by name: ask' };
  }

  async function backup(tableId, fieldIds) {
    const tb = await table(tableId); const out = [];
    for (const fid of fieldIds) {
      const f = tb.fields.find((x) => x.id === fid); if (!f) throw new Error(`no field ${fid} in ${tableId}`);
      const b = { tableId, fieldId: fid, name: f.name, type: f.type, configRevision: f.configRevision, takenAt: new Date().toISOString(), typeSettings: clone(f.typeSettings) };
      _backups[tableId + '/' + fid] = b; out.push(b);
    }
    return out;
  }

  // kind: 'action' | 'formula'. Action columns never on an auto-run table without allowAutoRun;
  // formula columns need allowFormulaOnAutoRun (they compute on every row immediately).
  async function guardAutoRun(tableId, kind, opts = {}) {
    const tb = await table(tableId);
    if (tb.tableSettings?.AUTO_RUN_ON) {
      if (kind === 'action' && !opts.allowAutoRun) throw new Error(`AUTO_RUN is ON for ${tb.name}: an action column could run. Ask Gaston to turn it off (or to confirm) first`);
      if (kind === 'formula' && !opts.allowFormulaOnAutoRun && !opts.allowAutoRun) throw new Error(`AUTO_RUN is ON for ${tb.name}: this formula would fill all rows at once (free). Get Gaston's OK naming this table, then pass {allowFormulaOnAutoRun:true}`);
    }
    return tb;
  }

  // Edit one field without running it. mutate(ts) changes a fresh copy of the live config.
  async function patch(tableId, fieldId, mutate, opts = {}) {
    const key = tableId + '/' + fieldId;
    if (!_backups[key] && !_created.has(key)) throw new Error(`back up ${fieldId} first (cb.backup) and log it`);
    const cur = (await table(tableId)).fields.find((x) => x.id === fieldId); if (!cur) throw new Error(`no field ${fieldId}`);
    const tb = await guardAutoRun(tableId, cur.type === 'action' ? 'action' : 'formula', opts);
    const f = tb.fields.find((x) => x.id === fieldId);
    if (_backups[key]?.configRevision && f.configRevision !== _backups[key].configRevision && !opts.allowRevisionChange) throw new Error(`${f.name} changed since the backup (revision ${f.configRevision}); re-read and back up again`);
    const before = clone(f.typeSettings); const ts = clone(f.typeSettings); mutate(ts);
    const body = { typeSettings: ts }; if (opts.name) body.name = opts.name;
    await j(`/workspaces/${WS}/tables/${tableId}/fields/${fieldId}?skipActionFieldRuns=true`, { method: 'PATCH', body: JSON.stringify(body) });
    await sleep(3000);
    const after = (await table(tableId)).fields.find((x) => x.id === fieldId);
    const fb = flat({ typeSettings: before, type: f.type }), fa = flat(after);
    const changed = Object.keys({ ...fb, ...fa }).filter((k) => fb[k] !== fa[k]);
    return { field: after.name, changed, savedAsIntended: JSON.stringify(after.typeSettings) === JSON.stringify(ts), runStatus: f.type === 'action' ? (await runStatus(tableId, [fieldId]))[after.name] : 'formula' };
  }

  async function addFormulaField(tableId, name, formulaText, opts = {}) {
    const tb = await guardAutoRun(tableId, 'formula', opts);
    if (tb.fields.some((f) => f.name === name)) throw new Error(`${name} already exists in ${tb.name}`);
    const r = await j(`/workspaces/${WS}/tables/${tableId}/fields`, { method: 'POST', body: JSON.stringify({ type: 'formula', name, typeSettings: { dataTypeSettings: { type: opts.dataType || 'text' }, formulaType: opts.dataType || 'text', formulaText, formulaPrompt: '' } }) });
    const id = r.field?.id || r.id || (await table(tableId)).fields.find((f) => f.name === name)?.id;
    _created.add(tableId + '/' + id);
    return { id };
  }

  async function refsTo(fieldId, tableIds) {
    const out = [];
    for (const tid of tableIds) { const tb = await table(tid); tb.fields.forEach((f) => { if (f.id !== fieldId && JSON.stringify(f.typeSettings || {}).includes(fieldId)) out.push(`${tb.name} / ${f.name}`); }); }
    return out;
  }

  // Columns in `tableId` not in `baselineIds` (the table's ORIGINAL field list, taken before any
  // route was created). Waits, because add-route-to-table creates them asynchronously.
  async function newColumnsSince(tableId, baselineIds, waitMs = 10000) {
    await sleep(waitMs);
    const base = new Set(baselineIds);
    return (await table(tableId)).fields.filter((f) => !base.has(f.id)).map((f) => ({ id: f.id, name: f.name, type: f.type,
      passThrough: f.type === 'formula' && PASS_THROUGH.test(f.typeSettings?.formulaText || ''), createdThisRun: _created.has(tableId + '/' + f.id) }));
  }

  // Create a route toward `dest` and copy `template` (a route's typeSettings) onto it.
  // destBaselineIds: the destination's field IDs BEFORE this run's first route (pass the same list
  // for every route into that table). label: [from, to] swaps `=== 'from'` → `=== 'to'`.
  async function createRoute({ workbookId, origin, dest, template, label, name, destBaselineIds, allowAutoRun = false }) {
    await guardAutoRun(origin, 'action', { allowAutoRun });
    const destTb = await table(dest);
    const baseIds = destBaselineIds || destTb.fields.map((f) => f.id);
    const r = await j(`/${WS}/workbooks/${workbookId}/add-route-to-table`, { method: 'POST', body: JSON.stringify({ originTableId: origin, destinationTableId: dest }) });
    const newId = r.routingField?.id; if (!newId) throw new Error('add-route-to-table returned no routingField: ' + JSON.stringify(r).slice(0, 300));
    _created.add(origin + '/' + newId);
    const ts = clone(template);
    setInput(ts, 'tableId', `"${dest}"`); ts.referencedTableId = dest;
    if (label) {
      const [from, to] = label; const cond = ts.conditionalRunFormulaText || '';
      if (!cond.includes(`=== '${from}'`)) throw new Error(`label '${from}' not in template condition; new column ${newId} is UNCONFIGURED (no run condition): report it now`);
      ts.conditionalRunFormulaText = cond.replace(`=== '${from}'`, `=== '${to}'`);
    }
    await j(`/workspaces/${WS}/tables/${origin}/fields/${newId}?skipActionFieldRuns=true`, { method: 'PATCH', body: JSON.stringify({ typeSettings: ts }) });
    let nameResult = 'Send table data';
    if (name) { try { await j(`/workspaces/${WS}/tables/${origin}/fields/${newId}?skipActionFieldRuns=true`, { method: 'PATCH', body: JSON.stringify({ name }) }); nameResult = name; } catch (e) { nameResult = `not renamed (${e.status}): the old column still holds "${name}"; rename after deleting it`; } }
    const extra = await newColumnsSince(dest, baseIds, 10000);
    const after = (await table(origin)).fields.find((f) => f.id === newId);
    const srcRes = await j('/sources?tableId=' + dest);
    return { newFieldId: newId, name: nameResult, identical: JSON.stringify(after.typeSettings) === JSON.stringify(ts),
      destAutoRun: destTb.tableSettings?.AUTO_RUN_ON, destSources: (srcRes.results || srcRes).map((s) => s.id),
      autoCreatedDestColumns: extra.filter((c) => c.passThrough), otherNewDestColumns: extra.filter((c) => !c.passThrough).map((c) => c.name),
      runStatus: (await runStatus(origin, [newId]))[after.name] };
  }

  // Guarded delete. Each field must be created this run, a pass-through auto-column, or listed in
  // opts.approvedIds; opts.approvedBy = Gaston's words for THIS batch; nothing may reference it.
  async function deleteFields(tableId, fieldIds, opts = {}) {
    if (!opts.approvedBy) throw new Error('deleteFields needs opts.approvedBy (Gaston\'s OK for this exact batch)');
    if (!opts.scanTables?.length) throw new Error('deleteFields needs opts.scanTables (every table that could reference these fields)');
    const tb = await table(tableId); const approved = new Set(opts.approvedIds || []); const res = [];
    for (const fid of fieldIds) {
      const f = tb.fields.find((x) => x.id === fid); if (!f) { res.push({ fid, skipped: 'not found' }); continue; }
      const pass = f.type === 'formula' && PASS_THROUGH.test(f.typeSettings?.formulaText || '');
      if (!(_created.has(tableId + '/' + fid) || pass || approved.has(fid))) { res.push({ fid, name: f.name, skipped: 'not created this run, not pass-through, not approved by ID' }); continue; }
      const refs = await refsTo(fid, opts.scanTables); if (refs.length) { res.push({ fid, name: f.name, skipped: 'referenced by ' + refs.join('; ') }); continue; }
      await j(`/workspaces/${WS}/tables/${tableId}/fields/${fid}`, { method: 'DELETE', body: '{}' });
      res.push({ fid, name: f.name, deleted: true });
    }
    return res;
  }

  // Lead-check export: one line per leads row with an email, "<campaignId>,<email>,<h1>,<h2>,…",
  // hashes = first 12 hex of SHA-256(trimmed text) of each var field, same as lead_check.py.
  async function leadHashes(map, emailFieldId, varFieldIds) {
    const h = async (s) => { const b = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(String(s ?? '').trim())); return [...new Uint8Array(b)].map((x) => x.toString(16).padStart(2, '0')).join('').slice(0, 12); };
    const lines = [];
    for (const [campaignId, tableId] of Object.entries(map)) {
      const v = await allRowsView(tableId); const ids = (await j(`/tables/${tableId}/views/${v}/records/ids`)).results;
      for (let i = 0; i < ids.length; i += 200) {
        const r = await j(`/tables/${tableId}/bulk-fetch-records`, { method: 'POST', body: JSON.stringify({ recordIds: ids.slice(i, i + 200) }) });
        for (const rec of r.results) { const e = String(rec.cells?.[emailFieldId]?.value || '').toLowerCase(); if (!e) continue;
          const hs = []; for (const fid of varFieldIds) hs.push(await h(rec.cells?.[fid]?.value)); lines.push([campaignId, e, ...hs].join(',')); }
      }
    }
    return lines.join('\n');
  }

  async function fullRecord(tableId, recordId) { return j(`/tables/${tableId}/records/${recordId}`); }

  // Big output → the harness saves it to a file; then `python3 scripts/save_dump.py <that file> …`.
  const dump = (obj) => JSON.stringify(obj) + '\n' + 'X'.repeat(95000);

  window.cb = { j, table, count, flat, setInput, inputs, allRowsView, runStatus, runTotals, refScan, sourceSummary, pathsOf, armDiff,
    schemaDiffByName, keysReadFrom, reuseCheck, linkWarnings, audit, backup, patch, addFormulaField, refsTo, newColumnsSince, createRoute,
    deleteFields, leadHashes, fullRecord, dump, _backups, _created };
  return 'cb loaded: ' + Object.keys(window.cb).join(', ');
})();
