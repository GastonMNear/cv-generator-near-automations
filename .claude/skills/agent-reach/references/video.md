# Video / podcasts

Subtitles and transcription for YouTube, Bilibili, and Xiaoyuzhou podcasts.

> ⚠️ **Not installed in this workspace.** Only the LinkedIn channel was installed. `yt-dlp` exists
> only inside the `agent-reach` tool venv (not on PATH); `bili-cli`, `opencli`, and the Xiaoyuzhou
> transcribe script are absent. Everything below needs installing first.

## YouTube (yt-dlp)

### Video metadata

```bash
yt-dlp --dump-json "URL"
```

### Download subtitles

```bash
# Subtitles only, no video
yt-dlp --write-sub --write-auto-sub --sub-lang "zh-Hans,zh,en" --skip-download -o "/tmp/%(id)s" "URL"

# Then read the .vtt file
cat /tmp/VIDEO_ID.*.vtt
```

### Fetch comments

```bash
# Extract comments (best-effort, completeness not guaranteed)
yt-dlp --write-comments --skip-download --write-info-json \
  --extractor-args "youtube:max_comments=20" \
  -o "/tmp/%(id)s" "URL"
# Comments land in the `comments` field of the .info.json
```

### Search videos

```bash
yt-dlp --dump-json "ytsearch5:query"
```

> **Subtitles note:** manually uploaded subtitles extract reliably; auto-generated ones often have
> duplicated lines across rows and need post-processing.
> **Comments note:** `--write-comments` scrapes the web page (not the YouTube Data API), so some
> comments may be missing.

### Fallback when there are no subtitles: Whisper audio transcription

```bash
# No subtitles available: download audio and transcribe with Whisper (a free Groq key is enough)
agent-reach transcribe "https://www.youtube.com/watch?v=VIDEO_ID"
agent-reach transcribe ./local_audio.mp3 -o /tmp/transcript.txt
```

> ⚠️ **This uploads audio to a third-party API** (Groq, or OpenAI on fallback). Do not transcribe
> client calls or anything confidential this way — use Fathom for meetings.
>
> `agent-reach transcribe` accepts only public http(s) URLs or local audio files. When searching with
> `ytsearch5:`, pick a concrete video URL from the yt-dlp results first, then transcribe.
> Requires a key: `agent-reach configure groq-key gsk_xxx` (free, console.groq.com)
> or `agent-reach configure openai-key sk-xxx`. Default `auto` mode falls back from Groq to OpenAI.

## Bilibili (bili-cli primary, OpenCLI for subtitles)

> ⚠️ **Never use yt-dlp for Bilibili.** Bilibili's anti-abuse system now blocks yt-dlp with 412
> across the board (verified on latest version, direct and proxied, with and without cookies).
> yt-dlp is for YouTube only.

### Video details / search / trending / rankings (bili-cli, read-only, no login)

```bash
# Video detail (title / uploader / duration / view+engagement stats / subtitle availability)
bili video BVxxx

# Search videos
bili search "query" --type video -n 5

# Trending / leaderboard
bili hot -n 10
bili rank -n 10

# Download audio and split into ASR-ready WAV (pair with `agent-reach transcribe` when no subtitles)
bili audio BVxxx
```

### Subtitles (OpenCLI, needs desktop Chrome)

```bash
# Subtitles line by line with timestamps
opencli bilibili subtitle BVxxx

# OpenCLI can also search / read video metadata (alternative)
opencli bilibili search "query" -f yaml
opencli bilibili video BVxxx -f yaml
```

### Zero-config fallback: hit the search API directly

```bash
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
curl -s -c /tmp/bili_ck.txt -o /dev/null -A "$UA" "https://www.bilibili.com/"
curl -s -b /tmp/bili_ck.txt -A "$UA" -e "https://www.bilibili.com/" \
  "https://api.bilibili.com/x/web-interface/search/all/v2?keyword=QUERY&page=1"
```

> **Installing bili-cli:** `pipx install bilibili-cli` (upstream stopped updating as of 2026-03 but
> tests healthy; read-only needs no login — `bili login` scans a QR to unlock feed/favorites and
> other personal features).

## Xiaoyuzhou podcasts

### Transcribe one episode (optional `--polish` improves punctuation)

```bash
# Writes a Markdown file to /tmp/. --polish has Llama 3.3 70B add Chinese punctuation and paragraphs
~/.agent-reach/tools/xiaoyuzhou/transcribe.sh --polish "https://www.xiaoyuzhoufm.com/episode/EPISODE_ID"
```

> The transcription prompt already asks Whisper for Chinese punctuation. If punctuation is still
> poor, add `--polish` to use the free Llama 3.3 70B on Groq for punctuation and paragraph breaks
> (~7 extra seconds on a 9-minute podcast). Each run costs one more LLM call — use as needed.

### Prerequisites

1. **ffmpeg**: `brew install ffmpeg`
2. **Groq API key** (free): https://console.groq.com/keys
3. **Configure the key**: `agent-reach configure groq-key YOUR_KEY`
4. **First run**: `agent-reach install --env=auto` to install the tooling

### Check status

```bash
agent-reach doctor
```

> Output Markdown files default to `/tmp/`.

## Which to use

| Case | Recommended |
|-----|---------|
| YouTube subtitles | yt-dlp |
| Bilibili video detail / search | bili-cli |
| Bilibili subtitles | `opencli bilibili subtitle` |
| Podcast transcription | Xiaoyuzhou `transcribe.sh` |
| Audio/video with no subtitles | `agent-reach transcribe` (for Bilibili, `bili audio` first) |
