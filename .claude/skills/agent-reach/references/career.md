# Career / Recruiting

LinkedIn.

## LinkedIn

Backend: `mcp-server-linkedin` (stickerdaniel/linkedin-mcp-server), registered with mcporter as
`linkedin-scraper`. Drives Gaston's own logged-in browser session via patchright (stealth Playwright).

> Signatures verified 2026-08-05 with `mcporter list linkedin-scraper`.
> Note: params are `linkedin_username` / `company_name` (**not** URLs), and keywords is `keywords` (**not** `keyword`).

```bash
# Person profile (username slug, not a full URL)
mcporter call 'linkedin-scraper.get_person_profile(linkedin_username: "williamhgates")'

# Person profile + specific sections (experience/education/skills/contact_info/posts, ...)
mcporter call 'linkedin-scraper.get_person_profile(linkedin_username: "williamhgates", sections: "experience,education")'

# People search (plural "keywords"; there is no limit param)
mcporter call 'linkedin-scraper.search_people(keywords: "AI engineer", location: "Remote")'

# Company profile (company slug, not a URL) — response references["about"] carries company_urn
mcporter call 'linkedin-scraper.get_company_profile(company_name: "microsoft")'

# Employees at a company (the common recruiting path)
mcporter call 'linkedin-scraper.get_company_employees(company_name: "microsoft", keywords: "recruiter")'

# Job search
mcporter call 'linkedin-scraper.search_jobs(keywords: "software engineer", location: "Remote", max_pages: 2)'

# Job details
mcporter call 'linkedin-scraper.get_job_details(job_id: "JOB_ID")'

# Full tool list (19 tools)
mcporter list linkedin-scraper
```

### Response shape (measured 2026-08-05)

**Not structured JSON.** Every tool returns:

```
{ "url": "...", "sections": { "<section>": "<big blob of page text>" }, "references": [ {kind, url, text, context}, ... ] }
```

- `sections.*` is scraped page text, newline-separated. You parse it yourself — there are no
  `title` / `company` fields.
- `references[]` is the machine-readable half: `kind` is `person` / `feed_post` / `company` / `job`,
  and `url` is a relative path (`/in/username/`, `/jobs/view/{id}`). **Use this array to pull profile
  URLs and job IDs — do not regex the `sections` text.**
- Parse before writing to Clay. Never dump a whole text blob into a field.

### `get_job_details` — work model / title / company (measured 2026-08-05)

`job_id` is the trailing numeric segment of a job URL: `/jobs/view/<slug>-4439299810` → `4439299810`.
The slug is optional; the numeric ID is what resolves.

`sections.job_posting`, split on newlines and stripped of blanks, starts:

```
line 1  Company Name          ← use to verify you have the right row
line 2  Job Title             ← use to verify you have the right row
line 3  Location · posted · applicants
line 4  Promoted by hirer · …          (may be absent)
        $165K/yr - $195K/yr            (salary — present only sometimes)
        Remote | Hybrid | On-site      ← THE WORK MODEL TAG
        Full-time | Part-time | Contract
```

**Do not parse the work model by line index** — an optional salary line and an optional promo line
shift it. Anchor instead: scan the first ~10 lines for an exact match against
`{Remote, Hybrid, On-site}`. LinkedIn emits exactly that casing.

Always cross-check line 1/line 2 against the company + title you already hold for the row before
writing anything back. This is the only guard against attributing one job's tag to another row.

Cold-start is ~30s; subsequent calls ~5-10s. Fetch sequentially, not in parallel — parallel calls
contend for the single browser session and raise restriction risk on Gaston's real account.

### Read-only vs write operations

These two act **outward on Gaston's real account** and fall under the agent-reach skill's own
declared NOT-for scope (`posting/commenting/liking`). Do not call either without his explicit
approval for that specific send:

- `connect_with_person` — send or accept a connection request
- `send_message` — send a DM (requires `confirm_send: true`)

When filtering `search_people` by `current_company`, only a numeric company URN works. A plain
company name is accepted by the URL but silently ignored by LinkedIn, returning the unfiltered
result set. Get the URN from `get_company_profile` first.

### Session / auth

A session must exist before the first call. Either command opens a browser window:

```bash
uvx mcp-server-linkedin@latest --login                  # sign in manually
uvx mcp-server-linkedin@latest --import-from-browser    # reuse a logged-in Chrome/Brave/Edge
```

Session is stored in `~/.linkedin-mcp/profile/`. Clear it with `--logout`.

First call after an idle period cold-starts Chromium (~10-30s). The server closes an idle browser
after 600s by default — a slow first call is not a hang.

### Rate / account risk

Session-based scraping runs on Gaston's real account, not an API key. `search_people` and
`get_company_employees` at volume are the likeliest triggers for a LinkedIn restriction. Prefer Clay
for bulk enrichment; use this for one-off and live lookups.

### Fallback

If the MCP is unavailable, Jina Reader gets the publicly visible portion only:

```bash
curl -s "https://r.jina.ai/https://linkedin.com/in/username"
```

> **2026-10-06:** every `get_person_profile` call returned "LinkedIn setup is not complete yet… downloading
> the Patchright Chromium browser" for 5+ minutes of retries. mcporter spawns a fresh stdio server per call, so
> the background download may never finish between calls. If this persists, ask Gaston to run one
> `mcporter call` interactively (or keep a daemon up) until the download completes. Don't install the browser yourself.
