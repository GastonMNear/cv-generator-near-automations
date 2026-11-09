---
type: task
title: "Finish the /email-replies-workflow + clay-api skill refactor"
created: 2026-09-09
updated: 2026-09-11
priority: medium
status: done
from-meeting: "[[wiki/meetings/2026-09-09-smartlead-replies-working-session]]"
---

# The skill refactor was left mid-edit, and Lila is now running it daily

Gaston was actively editing `/email-replies-workflow` and `clay-api` when the Sep 9 session started:
lookup by **email + campaign only**, dropping the table/campaign-name requirement.

**Why it matters now:** **the skill failed during the live demo** (*"Failed to check skill"*), and it
has since been handed to Lila as her primary daily tool. She is the one who hits the breakage, and
she has the least context to diagnose it.

**Known operating constraint worth encoding in the skill itself:** the lookup key must be the email
the lead is **registered under in Smartlead** — the address email 1 was sent to — **never** the
address they replied from. Replies frequently arrive from a forwarded or alternate mailbox, and the
lookup fails silently. This is currently tribal knowledge taught verbally.

**Timing:** In progress during the call, no completion date given.

**Source:** [[wiki/meetings/2026-09-09-smartlead-replies-working-session]] · [Fathom @36:37](https://fathom.video/calls/817171205?timestamp=2197)

---

## Completed 2026-09-11

**Done — and the architecture changed.** The CV generation project no longer depends on Clay tables. **All lead data is now fetched from Smartlead**, chosen as the source of truth precisely because it is independent of new Clay tables and new campaigns.

**Why this matters beyond the refactor:** Clay tables change constantly — every new campaign or experiment spawned a table the skill had to know about, which is what made the old lookup brittle. Smartlead holds the lead regardless of which experiment or table it came from, so the skill stops breaking when the upstream changes shape.

*Reported done by Gaston, 2026-09-11 status sweep.*
