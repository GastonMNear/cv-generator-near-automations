---
name: ai-learnings
description: >
  Ingests AI articles, blog posts, newsletters, videos, or tweets into the Near Work Partner vault as structured learning notes. Extracts key insights and identifies actionable improvements for this agent, adding them to wiki/ai-learnings/improvement-backlog.md. Use this skill when given a URL, file, or pasted text about AI — agents, prompting, tools, architectures, LLMs, workflows. Trigger phrases: "ingest this article", "learn from this", "add this to AI learnings", "process this blog post". Output: bibliography entry + learning page + backlog update.
---

# ai-learnings

Ingests AI content and extracts actionable agent improvements.

## Input Modes

- **URL**: Fetch with `WebFetch`, extract content
- **File**: Read with filesystem Read tool
- **Paste**: Use text directly

---

## Processing Steps

### Step 1: Fetch & read content

For URLs: use `WebFetch` to pull the page. If content is minimal (JS-rendered page), note that in the note and work with what's available.

### Step 2: Extract key information

Identify:
- **Author / Source** (publication, person, company)
- **Date published** (if available)
- **Type**: article, newsletter, paper, tweet thread, video transcript, podcast notes
- **Category**: `prompting` | `tools` | `architecture` | `integrations` | `workflow` | `models` | `research`
- **Key claims** — the 3-7 most important specific claims or findings
- **Practical techniques** — concrete things that can be applied
- **Actionable improvements** — specific things to change about THIS agent

### Step 3: Create bibliography entry

File: `bibliography/YYYY-MM-DD - {Author} - {Short Title}.md`

```markdown
---
type: bibliography
source_type: article|newsletter|paper|video|tweet
title: "{Full Title}"
author: "{Author or Publication}"
date_published: YYYY-MM-DD
date_ingested: YYYY-MM-DD
url: "{URL if applicable}"
category: prompting|tools|architecture|integrations|workflow|models|research
topics: ["[[wiki/ai-learnings/filename]]"]
wiki_pages: ["[[wiki/ai-learnings/filename]]"]
---

{2-3 sentence summary: what this source is about and its main contribution.}
```

### Step 4: Create learning page

File: `wiki/ai-learnings/YYYY-MM-DD-{slug}.md`

```markdown
---
type: learning
title: "{Descriptive Title}"
created: YYYY-MM-DD
updated: YYYY-MM-DD
category: prompting|tools|architecture|integrations|workflow|models|research
actionable: true|false
tags: [type/learning, category/{category}]
status: mature
related: []
sources: ["[[bibliography/YYYY-MM-DD - Author - Title]]"]
---

# {Title}

## Summary
{2-3 sentence summary of the content}

## Key Insights
- **{Insight 1}**: {explanation}
- **{Insight 2}**: {explanation}
- **{Insight 3}**: {explanation}

## Practical Techniques
{Specific techniques, patterns, or methods described}

## Actionable Improvements for This Agent
{What specifically should change about the Near Work Partner agent based on this? Be concrete.}

- **[{category}]** {Specific improvement: what to change, where, why}
- **[{category}]** {Specific improvement}

*If no actionable improvements: "No direct improvements identified — useful for general awareness."*
```

### Step 5: Update improvement backlog

For each actionable improvement identified, add an entry to `wiki/ai-learnings/improvement-backlog.md`:

Prepend to the **Backlog** section:
```markdown
### [{date}] [{category}] {Short Title}
> From: [[wiki/ai-learnings/{learning-page}]]

{Specific thing to do}: {what to change, add, or remove in the agent}
```

Categories: `[prompting]` `[tools]` `[architecture]` `[integrations]` `[workflow]`

### Step 6: Update vault navigation

1. **`wiki/ai-learnings/_index.md`** — Add:
   ```
   - [[ai-learnings/YYYY-MM-DD-slug]] — {Title}. Category: {cat}. {1-sentence summary}
   ```

2. **`wiki/index.md`** — Add to AI Learnings section

3. **`wiki/hot.md`** — Update with the ingest

4. **`logs/ingest-log.md`** — Prepend:
   ```markdown
   ## YYYY-MM-DD | learning | {Title}
   - Source: [[bibliography/YYYY-MM-DD - Author - Title]]
   - Pages created: [[ai-learnings/slug]]
   - Improvements added: {N} to backlog
   - Key insight: {One sentence}
   ```

---

## Output to User

```
AI Learning ingested: {Title}
Source: {Author / Publication}
Category: {category}

Key Insights:
• {insight 1}
• {insight 2}
• {insight 3}

Actionable Improvements Added to Backlog ({N}):
• [{category}] {improvement 1}
• [{category}] {improvement 2}

Vault updated: wiki/ai-learnings/{filename}
```

---

## What Makes a Good Actionable Improvement

Good:
- "Add a step to the meeting-ingest skill to detect client sentiment and tag it"
- "Update obsidian-wiki hot.md format to include a 'blockers' section"
- "When processing Smartlead reply data, classify intent before escalating"

Bad:
- "Think more carefully about prompts" (too vague)
- "Use better tools" (not specific)
- "Improve agent" (meaningless)

The improvement must name a specific skill, workflow, or behavior to change.
