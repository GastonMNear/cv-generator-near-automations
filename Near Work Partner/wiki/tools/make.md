---
type: tool
title: Make.com — Reference
created: 2026-06-10
updated: 2026-06-10
tags: [tool, make, automation]
status: active
related: ["[[tools/smartlead]]", "[[context/outbound-engine]]"]
---

# Make.com

Automation / orchestration between tools.

## Scenarios Built

- **Smartlead → Google Sheets metrics dashboard** — pulls daily campaign metrics via the Smartlead API into a Sheets dashboard.
- Lead-routing automations tied to Smartlead/Clay.

## Known Issues / Quirks

- **Expired Smartlead API keys** broke Make scenarios — check key validity when automations silently fail.
- **Race conditions caused duplicate rows** in a Google Sheet (WhatsApp leads sheet) — guard against concurrent writes.
- A make.com plan upgrade has been on the purchase list.
