// Clay daily control — read-only scan. Runs INSIDE the in-app browser on app.clay.com
// (mcp__Claude_Browser__javascript_tool), so every call uses Gaston's own Clay session.
// No writes: only GET /workbooks, /tables, /folders, /tables/{id}/count, /sources.
//
// Usage: paste this file, then on the last line call
//   await clayScan(["wb_...", "wb_..."])   // workbook IDs from references/active-workflows.md
// Returns { active: [...detailed...], candidates: [...], scannedAt }.
//   active     — registry workbooks with every table, row count, source and flag
//   candidates — non-registry workbooks under the Open Jobs folders whose sources moved in
//                the last 3 days and whose name isn't [Old]/[Paused]: possible new workflows
//                or new versions to add to the registry (ask Gaston first).

async function clayScan(activeIds, opts = {}) {
  const WS = 447061;
  const ROOTS = opts.roots || ['Open Jobs Campaigns', 'New Outbound Engine Open Jobs'];
  const WARN = 35000, CAP = 50000;
  const now = Date.now();
  const g = async (u) => {
    const r = await fetch('https://api.clay.com/v3' + u, { credentials: 'include' });
    if (r.status === 401) throw new Error('Clay session expired — Gaston must sign in again in the browser pane');
    return r.json();
  };

  const [wbs, tablesRes] = await Promise.all([g(`/workspaces/${WS}/workbooks`), g(`/workspaces/${WS}/tables`)]);
  const tables = tablesRes.results.filter(t => !t.deletedAt);
  const folders = {};
  const getF = async (id) => { if (!id || folders[id]) return; folders[id] = await g('/folders/' + id); await getF(folders[id].parentFolderId); };
  for (const w of wbs) await getF(w.parentFolderId);
  const path = (id) => { const p = []; while (id && folders[id]) { p.unshift(folders[id].name); id = folders[id].parentFolderId; } return p.join(' / '); };

  const inScope = wbs.filter(w => !w.deletedAt && ROOTS.some(r => path(w.parentFolderId).startsWith(r)));
  const hoursAgo = (iso) => iso ? Math.round((now - Date.parse(iso)) / 36e5) : null;

  const roleOf = (t, srcs) => {
    if (/exclusion lookup/i.test(t.name)) return 'exclusion';
    if (/compan(y|ies) table/i.test(t.name)) return 'companies';
    if (srcs.some(s => s.type === 'v3-action' || s.type === 'webhook')) return 'jobs';
    if (/lead/i.test(t.name)) return 'leads';
    return 'other';
  };

  const scanTable = async (t) => {
    const [c, s] = await Promise.all([g(`/tables/${t.id}/count`), g('/sources?tableId=' + t.id)]);
    const srcs = (Array.isArray(s) ? s : []).filter(x => !x.deletedAt).map(x => {
      const sch = x.typeSettings?.scheduleConfig?.schedule?.value;
      return {
        id: x.id, name: x.name, type: x.type,
        records: x.state?.numSourceRecords ?? null,
        limit: x.typeSettings?.sourceRecordLimit ?? CAP,
        lastActivityH: hoursAgo(x.recordSourceUpdatedAt),
        status: x.state?.action?.status ?? null,
        schedule: sch ? `${(sch.timesOfDay || []).join(',')} ${sch.timezone}` : null,
      };
    });
    const rows = c.tableTotalRecordsCount;
    const role = roleOf(t, srcs);
    const flags = [];
    if (rows >= WARN) flags.push({ jobs: 'A_ROW_CLEANUP', companies: 'C_NEW_COMPANY_TABLE', leads: 'LEADS_AT_LIMIT', exclusion: 'EXCLUSION_AT_LIMIT', other: 'ROWS_HIGH' }[role] + ` (${rows} rows)`);
    for (const x of srcs) {
      const live = x.lastActivityH !== null && x.lastActivityH <= 72;   // only feeds still in use
      if (x.type === 'v3-action' && x.records >= WARN) flags.push(`B_SOURCE_REFRESH "${x.name}" ${x.records}/${x.limit}`);
      if (x.type === 'manual' && live && x.records >= 40000) flags.push(`D_SEND_FEED_NEAR_CAP "${x.name}" ${x.records}/${CAP}`);
      if (x.schedule && x.lastActivityH > 26) flags.push(`SOURCE_NOT_RUN "${x.name}" last ${x.lastActivityH}h ago`);
      if (x.status && x.status !== 'SUCCESS') flags.push(`SOURCE_STATUS "${x.name}" ${x.status}`);
    }
    return { id: t.id, name: t.name, role, rows, sources: srcs, flags };
  };

  // A full Companies table whose feeds all went quiet while a sibling Companies table is
  // still receiving rows was already migrated (Table → Table 2 → Table 3): not an action item.
  const markMigrated = (ts) => {
    const isLive = (t) => t.sources.some(s => s.lastActivityH !== null && s.lastActivityH <= 72);
    const liveCompanies = ts.filter(t => t.role === 'companies' && isLive(t));
    for (const t of ts) {
      if (t.role !== 'companies' || isLive(t) || !liveCompanies.length) continue;
      t.flags = t.flags.map(f => f.startsWith('C_NEW_COMPANY_TABLE')
        ? `C_MIGRATED (${t.rows} rows, now feeding "${liveCompanies.map(x => x.name).join('", "')}")` : f);
    }
    return ts;
  };

  const active = await Promise.all(inScope.filter(w => activeIds.includes(w.id)).map(async w => ({
    id: w.id, name: w.name, path: path(w.parentFolderId),
    link: `https://app.clay.com/workspaces/${WS}/workbooks/${w.id}`,
    tables: markMigrated(await Promise.all(tables.filter(t => t.workbookId === w.id).map(scanTable))),
  })));
  const missing = activeIds.filter(id => !inScope.some(w => w.id === id));

  // Shared Exclusion Lookup lives outside any workflow but every workflow writes to it.
  const excl = tables.filter(t => /exclusion lookup/i.test(t.name));
  const shared = await Promise.all(excl.map(scanTable));

  const candidates = [];
  await Promise.all(inScope.filter(w => !activeIds.includes(w.id) && !/^\[(old|paused)\]/i.test(w.name)).map(async w => {
    const ts = tables.filter(t => t.workbookId === w.id);
    const srcLists = await Promise.all(ts.map(t => g('/sources?tableId=' + t.id)));
    const freshest = Math.min(...srcLists.flat().filter(x => x && !x.deletedAt && x.recordSourceUpdatedAt).map(x => hoursAgo(x.recordSourceUpdatedAt)), Infinity);
    if (freshest <= 72) candidates.push({ id: w.id, name: w.name, path: path(w.parentFolderId), lastActivityH: freshest, link: `https://app.clay.com/workspaces/${WS}/workbooks/${w.id}` });
  }));

  return { scannedAt: new Date().toISOString(), active, shared, missing, candidates };
}
