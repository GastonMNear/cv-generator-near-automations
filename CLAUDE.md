# CLAUDE.md

Automation workspace for Gaston. Uses a skill-based system to automate recurring tasks across Clay, Smartlead, LinkedIn, Google Docs, and AI CV generation.

## Skills System

Skills live in `.claude/skills/<name>/SKILL.md` (project) or `~/.claude/skills/<name>/SKILL.md` (personal). Invoke with `/<skill-name>` or Claude auto-loads when relevant. Claude self-patches skills on error so failures don't repeat.

Supporting files (references, scripts, templates) live alongside SKILL.md — Claude loads them on demand.

## Available Skills

| Skill | Trigger |
|---|---|
| `email-replies-workflow` | Given a lead email + Clay table, runs the full CV generation pipeline |
| `clay-api` | Reading/writing Clay tables, fetching rows, listing workspace resources |
| `linkedin-job-extractor` | Given a LinkedIn job URL, extracts title, company, description |
| `latam-cv-generator` | Given job details, generates a LATAM candidate CV as a Google Doc |
| `skill-creator` | Creating or editing skills |

## Key Integrations

**Clay** — Internal API at `api.clay.com`. Session-cookie auth. Workspace: HireWithNear (447061). Known tables in `.claude/skills/clay-api/references/known-tables.md`.

**Smartlead** — API key auth. Webhooks for reply events. Maps campaign IDs → Clay workflows.

**LinkedIn** — Scrape job posts at `linkedin.com/jobs/view/{id}`. Extract title, company, requirements.

**Google Docs** — Create/fill docs via Google API. CVs saved to configured Drive folder.

**Claude API** — Used for CV generation and AI tasks. Default model: `claude-sonnet-4-6`.

## Environment Variables

```
SMARTLEAD_API_KEY
CLAY_API_KEY
CLAY_SESSION_COOKIE
ANTHROPIC_API_KEY
GOOGLE_SERVICE_ACCOUNT_JSON
CAMPAIGN_WORKFLOW_MAP   # JSON: { campaign_id: workflow_id }
```

## Self-Annealing

Skills and reference files are living documents. The system improves after **every run** — not just failures.

### On failure:
1. Read the error and stack trace
2. Fix it — **unless the fix requires paid tokens/credits, in which case ask first**
3. Test the fix
4. Update the skill with what was learned

### On success — proactive optimization:
After every successful workflow run, ask: *"What did I have to discover at runtime that I could cache for next time?"*

Examples of things worth documenting immediately after a run:
- **Field IDs** discovered for a Clay table (email field, URL field, name field, employee count field, view ID) → add to `known-tables.md` under that table's entry
- **API quirks** encountered (e.g., wrong field matched by pattern, pagination behavior, auth expiry timing)
- **Edge cases** hit (e.g., expired LinkedIn URLs, Unicode issues in Windows terminal, email found in unexpected field)
- **Shortcuts** that would eliminate retry loops next time

The goal: **each run makes the next one faster and more reliable.**

The loop: **run → observe → document → system is stronger.**

When you discover field mappings, API patterns, better approaches, or structural data → update the relevant reference file immediately, in the same session.

⚠️ Do not create or overwrite skills without asking, unless explicitly instructed.

## Conventions

- Prefer skills for recurring tasks — keep logic in skill files, not ad-hoc scripts
- Log each workflow stage with lead email, campaign ID, and timestamps
- Retry API calls with backoff on rate limits; log failures for debugging
- Validate external data (Clay rows, LinkedIn URLs) before downstream steps
- Passwords/cookies may contain `$` — use single quotes in curl `--data-raw`

