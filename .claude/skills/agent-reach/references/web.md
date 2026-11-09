# Web reading

General web pages, RSS.

## General web pages (Jina Reader)

```bash
# Read any web page
curl -s "https://r.jina.ai/URL"

# Example
curl -s "https://r.jina.ai/https://example.com/article"
```

**When to use:** most web pages can be read directly through Jina Reader.

> ⚠️ **This sends the URL to Jina's servers.** Fine for public pages. Do not use it on internal,
> authenticated, or client-confidential URLs — use the `defuddle` skill or WebFetch instead.

## Web Reader (MCP)

> ⚠️ **Not configured here** — needs a `web-reader` MCP server registered with mcporter.
> Only `linkedin-scraper` is registered. Use Jina Reader or the `defuddle` skill instead.

```bash
# Read page content (Markdown)
mcporter call 'web-reader.webReader(url: "https://example.com")'

# Keep images
mcporter call 'web-reader.webReader(url: "https://example.com", retain_images: true)'

# Plain text
mcporter call 'web-reader.webReader(url: "https://example.com", return_format: "text")'
```

**When to use:** when you need finer control over output format.

## RSS (feedparser)

```python
python3 -c "
import feedparser
for e in feedparser.parse('FEED_URL').entries[:5]:
    print(f'{e.title} — {e.link}')
"
```

**When to use:** subscribing to blogs, news sources, podcasts, any RSS feed.

> `feedparser` ships inside the `agent-reach` tool venv, not system Python. If the import fails,
> run it via `uv run --with feedparser python3 -c "..."`.

## Which to use

| Case | Recommended |
|-----|---------|
| General web page | `defuddle` skill, or Jina Reader (`curl r.jina.ai`) |
| Internal / confidential URL | WebFetch or `defuddle` — never Jina |
| Need images / format control | web-reader MCP — *needs setup* |
| RSS feed | feedparser |
