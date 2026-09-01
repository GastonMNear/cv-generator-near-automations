# Sheet layout — `Email Lead-Conversion-Timing-Analysis`

Spreadsheet **Outbound metrics** (`1Wklpdze9UReMsTxTtpYNs0dq6-xXYTeleHSn67te4wo`),
tab gid `1651055580`. Written by `scripts/write_to_sheet.py`.

| Col | Header | Content |
|---|---|---|
| A | `x` | marker, **first row of each week's block only** |
| B | Week | `Mon 8/24 → Sun 08/30/2026` |
| C | Start | real date — the idempotency key |
| D | End | real date (Sunday, inclusive) |
| E | Company | HubSpot contact's company |
| F | Contact | who booked, per HubSpot |
| G | Email | the **Smartlead** address we measured |
| H | Bucket (SAME/PREV) | the metric |
| I | Campaign | Smartlead campaign name(s), deduped |
| J | First reply (ET) | earliest REPLY across all campaigns — decides the bucket |
| K | Booked (ET) | `hs_createdate` — puts the row in this week |

Each block is: leads (counted first), then flagged rows, then a `WEEK TOTAL` row.
Rows are ordered counted-first, then SAME → PREV → UNRESOLVED, then by booking time.

The bucket cell reads `REVIEW – SAME` / `REVIEW – PREV` / `REVIEW – UNRESOLVED` for
meetings that are not confirmed Chili Piper bookings. They are written so no company
goes missing from the week, but they are excluded from the Slack headline and its
percentages until adjudicated — delete the row, or strip the `REVIEW – ` prefix to
keep it. The reason for each is named in the Slack message, and populates a `Note`
column automatically if you add that header.

## Columns are resolved by header name, not position

`write_to_sheet.py` finds the header row by locating `Week` in column B, then maps
each header label to a field through `ALIASES`. Reordering columns, inserting one, or
renaming within the alias set all keep working; an unrecognised header is left alone
and a field the sheet doesn't have is simply not written.

This is not defensive over-engineering — the layout already changed once during
development (columns reordered, `Match` dropped). Pinning positions would have
silently written buckets into the campaign column.

Header matching drops punctuation entirely, so `Bucket (SAME/PREV)` normalises to
`bucket same prev`. To add a column, give it a header in `ALIASES`; `match`, `total`,
`same`, `prev` and `same %` are already recognised and will populate if added.

## The `Totals` row

Each week's block ends with a totals row: `Totals` in column A, unique companies in
E, leads in F, and the split in H.

| A | E | F | H |
|---|---|---|---|
| `Totals` | `13` | `13` | `7 same (58%) \| 5 Prev (42%)` |

**These are formulas, not baked-in numbers**, and that is the point. The sheet is a
working document: `REVIEW – …` rows get kept or deleted by hand, and a booking
Smartlead could not match gets its bucket typed in. Cactus Audio is the standing
case — no Smartlead record, so it lands `REVIEW – UNRESOLVED`, and the moment `PREV`
is typed over it the split moves from 7/5 to 7/6 by itself. Static numbers would go
stale the first time the block was touched, which is worse than no totals at all.

```
E:  =COUNTUNIQUE(E7:E19)
F:  =COUNTA(F7:F19)
H:  =COUNTIF(H7:H19,"SAME")&" same ("&ROUND(…)&"%) | "&COUNTIF(H7:H19,"PREV")&…
```

`COUNTIF` matches the bucket exactly, so `REVIEW – SAME` is deliberately **not**
counted as SAME — a flagged row stays out of the split until it is adjudicated.
Deleting a row inside the block is safe; Sheets rewrites the ranges.

The row carries no Start date (B–D stay blank), so `--replace` finds it by the
`Totals` marker in column A immediately below the block rather than by date.

## Conventions## Conventions

**One blank row separates week blocks.** Readability choice with a cost: Sheets'
native filter and pivot auto-ranges stop at a blank row. Build those over an explicit
range (`A5:K996`) instead of letting Sheets guess.

**`valueInputOption=USER_ENTERED`** — dates land as real datetimes (verified: `SAME`
rows read back as serial `46258.378…`, displaying as `8/24/2026 9:05`), so the tab
stays sortable, chartable and formula-friendly.

**Appending the same week twice is refused** unless `--force`, compared on column C.
A routine that retries must not duplicate a week, and weeks are frozen once computed:
Smartlead category tags mutate, so recomputing history silently changes past numbers.

## Replacing a week already written

Appending a week twice is refused. To correct one in place:

```bash
python3 scripts/write_to_sheet.py --attribution attribution.json --replace
```

`--replace` clears the existing block and rewrites it at the same starting row. If
the new block is longer than the old one *and* another week sits below it, it refuses
rather than overwriting the week underneath — insert the rows first, then re-run.
`--force` appends a second copy instead, which is almost never what you want.

## Where the identity caveat went

There is no `Match` column, so a row where the person who booked is **not** the lead
we measured is called out in the Slack message instead:

> • HypeProxies: Awan Ali booked → measured Gunnar Catlett

That happens when a booking resolves by domain rather than by address and lands on a
colleague. The full match method per row is always in `attribution.json`
(`match`, `match_note`, `smartlead_name`) if you need to audit one. Adding a `Match`
header to the sheet turns the column back on with no code change.
