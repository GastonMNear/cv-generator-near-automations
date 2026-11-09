# Social media & communities

XiaoHongShu, Twitter/X, Bilibili, V2EX, Reddit, Facebook, Instagram.

> ⚠️ **None of these are installed in this workspace.** Only the LinkedIn channel was installed
> (see [career.md](career.md)). `opencli`, `twitter-cli`, `bili-cli`, `rdt-cli`, and `xhs-cli` are
> all absent, so every command below fails until installed. V2EX is the sole exception — it is a
> public API reachable with plain `curl`.

## XiaoHongShu (multi-backend)

XiaoHongShu has three backends. **Run `agent-reach doctor --json` first** to see which
`active_backend` is serving xiaohongshu, then use the matching command group.

### Backend A: OpenCLI (preferred on desktop)

```bash
# Search notes
opencli xiaohongshu search "query" -f yaml

# Read note body + engagement (use the full URL from search results — it carries xsec_token)
opencli xiaohongshu note "NOTE_URL" -f yaml

# Comments (including nested replies)
opencli xiaohongshu comments NOTE_ID -f yaml

# Home recommendation feed
opencli xiaohongshu feed -f yaml

# A user's public notes
opencli xiaohongshu user USER_ID -f yaml
```

> Requires Chrome open with the OpenCLI extension installed. OpenCLI uses only a Chrome session the
> user already has and explicitly controls; Agent Reach does not log in for the user and does not
> read browser cookies. `agent-reach configure xhs-cookies` does not inject cookies into OpenCLI.
> If no session exists, do not automate a login — switch to backend B/C and follow the manual
> Cookie-Editor export flow.

### Backend B: xiaohongshu-mcp (server scenarios)

```bash
# Before authenticating, have the user export cookies manually with Cookie-Editor, then import
agent-reach configure xhs-cookies "exported Cookie header string"

# Read-only status check
mcporter call 'xiaohongshu.check_login_status()' --timeout 120000

# Search
mcporter call 'xiaohongshu.search_feeds(keyword: "query")' --timeout 120000

# Note detail + comments (feed_id and xsec_token come from search results)
mcporter call 'xiaohongshu.get_feed_detail(feed_id: "...", xsec_token: "...")' --timeout 120000
```

> The first call downloads a ~150MB headless browser — always pass `--timeout 120000`.
> Authentication goes through manual Cookie-Editor export only; after importing, run
> `check_login_status` first. That explicit command saves/imports the same-origin
> xiaohongshu.com cookie set the user supplied — the user should confirm the scope. Cookies from
> any domain other than xiaohongshu.com are ignored.

### Backend C: xhs-cli (legacy fallback, upstream unmaintained since 2026-03)

```bash
xhs search "query"          # search
xhs read NOTE_ID_OR_URL     # read a note (must use the URL/ID from search results, not a bare note_id)
xhs comments NOTE_ID_OR_URL # comments
xhs hot                     # trending
xhs feed                    # recommendations
```

> Known flaky: `xhs user` / `xhs user-posts` / `xhs favorites` may return API errors (upstream is
> unmaintained, nobody is fixing them). New users should go straight to backend A/B.

### General notes

> **Auth boundary:** Agent Reach must not perform a XiaoHongShu login for the user, and must not
> read browser cookies. OpenCLI may use only an existing Chrome session the user explicitly
> controls; xiaohongshu-mcp and the legacy tools use a manual Cookie-Editor export.
>
> **xsec_token constraint:** XiaoHongShu enforces an xsec_token mechanism, so **a bare note_id
> cannot be read directly**. Correct flow: search or pull the feed first, then read using the full
> URL/ID from those results. Same for all three backends.
>
> **Rate limiting:** high-frequency requests (bulk search, deep comment paging) trigger CAPTCHAs.
> This is a platform limit and cannot be worked around. Leave 2-3 seconds between operations.
>
> **Write operations (posting/commenting/liking):** stay read-only. xhs-cli v0.6.x write operations
> may return 406 due to request-signing problems.

## Twitter/X (twitter-cli)

### Auth prerequisites

Cookies saved by `agent-reach configure twitter-cookies "..."` are used only by `agent-reach doctor`
to check whether explicit credentials are present. `doctor` does not run upstream `twitter status`
and does not configure the current shell. Before running any `twitter` command below, you must
explicitly provide these in the same shell or the child-process environment:

```bash
export TWITTER_AUTH_TOKEN="..."
export TWITTER_CT0="..."
```

Never echo these values into logs or command output.

### Stable commands

```bash
# Home timeline (most reliable)
twitter feed -n 20

# Read a single tweet (with replies)
twitter tweet URL_OR_ID

# Read a long-form post / X Article
twitter article URL_OR_ID

# A user's timeline
twitter user-posts @username -n 20

# User profile
twitter user @username
```

### Commands that may be unstable

```bash
# Tweet search (Twitter changes GraphQL endpoints often — may 404)
twitter search "query" -n 10

# Likes (since 2024 you can only see your own — platform limit)
twitter likes
```

### Retry chain when search fails (in order, stop on success)

1. Just retry once — intermittent failures are common: `twitter search "query" -n 10`
2. Upgrade, then retry: `pipx upgrade twitter-cli && twitter search "query" -n 10`
3. Switch to the OpenCLI alternative (desktop, reuses the browser session):
   `opencli twitter search "query" -f yaml`
4. If none work, route around it with stable commands — `twitter feed` /
   `twitter user-posts @somebody`

### Important notes

> **Install:** `pipx install twitter-cli` (make sure it's v0.8.5+)
>
> **Auth:** manual Cookie-Editor export only, then set `TWITTER_AUTH_TOKEN` + `TWITTER_CT0`
> explicitly. Do not rely on automatic browser cookie reading.
>
> **IP risk:** do not call frequently from a VPS or datacenter IP, especially
> followers/following — there is a real account-ban risk. Use a residential connection or local
> environment.
>
> **OpenCLI alternative:** with OpenCLI installed on desktop, the full
> `opencli twitter search/article/user-posts -f yaml` set works using the browser session, with no
> cookie environment variables.
>
> **Output format:** prefer `--yaml` or `--json` for structured output — friendlier for an AI agent.

## Bilibili

> ⚠️ **Never use yt-dlp for Bilibili** (anti-abuse blocks it with 412 across the board; verified, no
> workaround). Use bili-cli / OpenCLI.

```bash
# Search / trending / video detail (bili-cli, read-only, no login)
bili search "query" --type video -n 5
bili hot -n 10
bili video BVxxx

# Subtitles (OpenCLI, needs desktop Chrome)
opencli bilibili subtitle BVxxx
```

> Full commands (audio transcription, direct API fallback) are in [video.md](video.md).

## V2EX (public API)

No auth needed — call the public API directly. **This one works here**, since it is plain `curl`.

### Trending topics

```bash
curl -s "https://www.v2ex.com/api/topics/hot.json" -H "User-Agent: agent-reach/1.0"
```

### Topics in a node

```bash
# node_name e.g.: python, tech, jobs, qna, programmers
curl -s "https://www.v2ex.com/api/topics/show.json?node_name=python&page=1" -H "User-Agent: agent-reach/1.0"
```

### Topic detail

```bash
# topic_id comes from the URL, e.g. https://www.v2ex.com/t/1234567
curl -s "https://www.v2ex.com/api/topics/show.json?id=TOPIC_ID" -H "User-Agent: agent-reach/1.0"
```

### Topic replies

```bash
curl -s "https://www.v2ex.com/api/replies/show.json?topic_id=TOPIC_ID&page=1" -H "User-Agent: agent-reach/1.0"
```

### User info

```bash
curl -s "https://www.v2ex.com/api/members/show.json?username=USERNAME" -H "User-Agent: agent-reach/1.0"
```

### Python usage example

```python
from agent_reach.channels.v2ex import V2EXChannel

ch = V2EXChannel()

# Trending posts
topics = ch.get_hot_topics(limit=10)
for t in topics:
    print(f"[{t['node_title']}] {t['title']} ({t['replies']} replies)")

# Posts in a node
node_topics = ch.get_node_topics("python", limit=5)

# Post detail + replies
topic = ch.get_topic(1234567)
print(topic["title"], "—", topic["author"])

# User info
user = ch.get_user("Livid")
```

> This import only works inside the `agent-reach` tool venv, not system Python. Prefer the `curl`
> calls above.
>
> **Node list:** https://www.v2ex.com/planes

## Reddit (multi-backend, login required)

**Reddit has no zero-config path.** The anonymous `.json` endpoints are blocked (403), and official
API access has been effectively closed to manual approval since 2025-11. Both backends depend on a
logged-in session — run `agent-reach doctor --json` first to see reddit's `active_backend`. Access
from mainland China needs a proxy.

### Backend A: OpenCLI (preferred on desktop, reuses the browser session)

```bash
# Search posts
opencli reddit search "query" -f yaml

# Read full post + comments
opencli reddit read POST_ID -f yaml

# Browse a subreddit / hot / popular
opencli reddit subreddit LocalLLaMA -f yaml
opencli reddit hot -f yaml
opencli reddit popular -f yaml

# Subreddit metadata (subscriber count, description)
opencli reddit subreddit-info LocalLLaMA -f yaml
```

> Requires Chrome open and logged into reddit.com.

### Backend B: rdt-cli (legacy / server fallback, upstream unmaintained since 2026-03)

```bash
rdt search "query" --limit 10   # search posts
rdt read POST_ID                # read full post + comments
rdt sub python --limit 20       # browse a subreddit
rdt popular --limit 10          # browse popular
rdt all --limit 10              # browse /r/all
```

> **Install:** `pipx install 'git+https://github.com/public-clis/rdt-cli.git'` (the PyPI release
> lags; needs v0.4.2+ from GitHub). Run `rdt login` before searching or reading (on a server with no
> browser, write the cookie manually — see the doctor hint).
>
> ⚠️ This installs unpinned from a third-party GitHub repo. Review it before running, or skip it.
>
> Prefer `--yaml` output — friendlier for an AI agent.

### Advanced: official API + PRAW (only for users who already have credentials)

Users who registered a Reddit script app before 2025-11 (holding client_id/client_secret) can use
PRAW against the official API (100 QPM free). New applications need manual approval and personal
projects are essentially never approved — **do not recommend this path to new users.**

## Facebook (OpenCLI, login required)

Facebook goes through OpenCLI, reusing the facebook.com session in the user's Chrome. Run
`agent-reach doctor --json` first to check facebook's `active_backend` — it should be `OpenCLI`. Do
not recommend Jina/Exa/Graph API as the default path.

```bash
# Search users / pages / posts
opencli facebook search "query" -f yaml

# User or page info
opencli facebook profile zuck -f yaml

# Current account's News Feed
opencli facebook feed --limit 10 -f yaml

# Groups visible to the current account, with recent activity
opencli facebook groups --limit 20 -f yaml
```

> Requires Chrome open with the OpenCLI extension installed and logged into facebook.com. Facebook
> Groups currently only promises the group list and recent activity visible to the current account —
> it does not promise an API for arbitrary group posts and comments.

## Instagram (OpenCLI, login required)

Instagram goes through OpenCLI, reusing the instagram.com session in the user's Chrome. Run
`agent-reach doctor --json` first to check instagram's `active_backend` — it should be `OpenCLI`. Do
not fall back to instaloader by default; it has a history of unstable cookies/401/429.

```bash
# Search users (not a site-wide post keyword search)
opencli instagram search "query" -f yaml

# User profile
opencli instagram profile nasa -f yaml

# A user's recent posts
opencli instagram user nasa --limit 12 -f yaml

# Explore / Discover
opencli instagram explore --limit 20 -f yaml

# Current account's saved posts
opencli instagram saved --limit 20 -f yaml
```

> Requires Chrome open with the OpenCLI extension installed and logged into instagram.com.
> `instagram search` searches users; to read posts, resolve the username first, then use
> `instagram user USERNAME`. On 429 / login-required errors, have the user re-login in Chrome and
> reduce request frequency.
