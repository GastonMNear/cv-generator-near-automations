# Search tools

Exa AI search engine.

> ⚠️ **Not configured in this workspace.** These calls need an `exa` MCP server registered with
> mcporter; only `linkedin-scraper` is registered. They will fail until Exa is set up.
> For web search here, prefer WebSearch / Jina Reader (see [web.md](web.md)).

## Exa AI search

High-quality AI search engine, strong on technical and code search.

```bash
mcporter call 'exa.web_search_exa(query: "query", numResults: 5)'
mcporter call 'exa.get_code_context_exa(query: "code question", tokensNum: 3000)'
```

### When to use what

| Case | Params |
|-----|------|
| Web search | `web_search_exa(query: "...", numResults: 5)` |
| Code search | `get_code_context_exa(query: "...", tokensNum: 3000)` |

### Characteristics

- Strong on English content and technical documentation
- Supports code-context search
- High result quality

## Compared with other search tools

| Tool | Source | Best for |
|-----|------|---------|
| Exa | agent-reach | English / technical / code search — *needs setup* |
| ~~Zhipu search~~ | ~~my-mcp-tools~~ | Chinese search — not configured here |
| GitHub search | agent-reach ([dev.md](dev.md)) | Repo / code search — **available** |
