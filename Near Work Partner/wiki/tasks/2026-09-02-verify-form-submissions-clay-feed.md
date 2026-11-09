---
type: task
title: "Verify the form-submissions → Clay feed isn't broken"
created: 2026-09-02
updated: 2026-09-02
priority: high
status: open
related: ["[[wiki/tasks/2026-09-01-rb2b-integration-monitoring]]", "[[wiki/tasks/done/2026-09-01-forms-and-visitors-to-calling-list]]", "[[wiki/tools/clay]]"]
---

# Confirm form submissions are still reaching Clay

Daniel reported that Ivan is seeing Slack notifications in the **form follow-up** channel but not
receiving leads. Last lead landed in Clay on **Aug 30**. Determine whether there were genuinely zero
submissions Aug 31–Sep 1, or whether the pipe is broken.

**Why:** Same silent-failure class as RB2B — [[wiki/tasks/2026-09-01-rb2b-integration-monitoring]] —
which went two weeks unnoticed. Form submissions are the **warmest** inbound source, so a dead feed
costs more per lead than any cold segment. Gaston's read on the call was that the Clay workflow itself
looks fine, which makes "no submissions" the likely answer — but that was inference, not verification.

**Done =** either confirmed zero submissions in the window, or the break is found and fixed.

**Note:** Daniel's initial theory was that Clay couldn't find phone numbers; the notification-vs-lead
gap suggests the failure is upstream of enrichment instead.

**Source:** Huddle 2026-09-01 (Daniel + Gaston), ~[29:00]
