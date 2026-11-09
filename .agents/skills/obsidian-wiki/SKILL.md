---
name: obsidian-wiki
description: >
  Core vault operations for the Near Work Partner Obsidian vault. Use this skill whenever you need to read, write, search, or update the vault — meeting notes, tasks, AI learnings, context pages. Covers: discovery protocol (hot cache → index → pages), three query modes (quick/standard/deep), surgical write rules, filesystem tool usage, and session-end checklist. Always invoke this skill before touching the vault to ensure you're following the right operating procedures.
---

# obsidian-wiki

Vault operations router for the Near Work Partner vault. Read this before any vault operation.

## Vault Path

`/Users/gastonmurillo/Documents/Near Automations/Near-AI-Agent/Near Work Partner`

No MCP is configured for this vault. All operations go through direct filesystem access.

## Discovery Protocol

Always follow this order — stop when you have enough:

1. **Read `wiki/hot.md`** (~500 tokens) — recent context cache. Often answers the question immediately.
2. **Read `wiki/index.md`** (~1000 tokens) — master catalog. Find which pages to read next.
3. **Read relevant pages** (3-5 max for standard queries) — meetings, tasks, context, tools.
4. **Follow wikilinks** to depth-1 only for key entities.

Never read more than needed. Token discipline is critical.

## Query Modes

| Mode | When | What to Read |
|------|------|-------------|
| **Quick** | "When is X due?", "Who attended Y?", lookups | hot.md + index.md only |
| **Standard** | Most questions, summaries, current state | hot.md + index + 3-5 relevant pages |
| **Deep** | Synthesis, comparisons, gap analysis | Full relevant subfolder |

## Filesystem Operations

| Need | Do |
|------|----|
| Read a page | `Read <vault>/<path>` |
| Create a new page | `Write <vault>/<path>` — include full YAML frontmatter |
| Edit / append / prepend | `Read` first, then `Edit` (surgical) — don't rewrite the page |
| Move or rename | `mv "<vault>/<old>" "<vault>/<new>"` via Bash |
| Delete | `rm "<vault>/<path>"` via Bash (confirm first) |
| Search content | `rg -n "term" "<vault>"` |
| Add/remove tags | Tags are YAML frontmatter / `#tags` in text — `Edit` the file |

**Critical rule**: Always use filesystem tools (Read/Write/Edit/Bash). No MCP is configured for this vault.

## Write Rules

- **Surgical writes only** — add new sections, never rewrite existing content
- Preserve provenance — old content stays, new content appends as new section
- Use wikilinks `[[Page Name]]`, never markdown links `[text](path)`
- Dates always as `YYYY-MM-DD`
- Frontmatter links quoted: `"[[Page Name]]"`

## Session-End Checklist

After every ingest, task creation, or significant vault operation:

- [ ] Update `wiki/hot.md` — overwrite completely with latest context (~500 words max)
- [ ] Update `wiki/index.md` — add new pages, update existing entries
- [ ] Append to `logs/ingest-log.md` — new entry at TOP, never edit past entries
- [ ] Create task entries for any action items found in meetings

## Contradiction Handling

When new information conflicts with existing vault content:

```markdown
> [!contradiction] Conflict with [[Source]]
> [[Existing Page]] says X. [[New Source]] says Y.
> Needs resolution. Check dates and context.
```

Add on BOTH the existing page and the new source. Never silently overwrite.

## Hot Cache Format

```markdown
---
type: meta
title: Hot Cache
updated: YYYY-MM-DDTHH:MM:SS
---

# Recent Context

## Last Updated
[Date] — [What happened]

## Key Recent Facts
- [Most important thing]
- [Second most important]

## Recent Changes
- Created: [[New Page]]
- Updated: [[Existing Page]] (what changed)
- Tasks created: [[Task 1]]

## Open Threads
- [Unresolved items, follow-ups in flight]
```

## Error Recovery

- If a path isn't found → double-check the vault root is joined onto the relative path, and quote paths with spaces
- If search returns no results → try broader search terms, check spelling
