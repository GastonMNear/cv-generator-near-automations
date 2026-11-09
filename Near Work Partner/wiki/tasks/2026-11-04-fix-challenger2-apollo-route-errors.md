---
type: task
title: "Fix the 2 bad-request errors on the Challenger 2 'Send Apollo Leads' route"
created: 2026-11-04
updated: 2026-11-04
priority: low
status: open
related: ["[[tools/moltsets]]", "[[tools/clay]]"]
---

# Challenger 2 "Send Apollo Leads" route: 2 bad-request errors

Found during the MoltSets audit on 2026-11-04. In the US Open Jobs (generic) jobs table (`t_0thes7nB88VNvTTfFfU`), the original
**"[Challenger 2] Send Apollo Leads"** route (`f_0tk51baisRnFVxM2Byt`, sends to `t_0tk4z9dHSfP9UhTkGim`) shows
`ERROR_BAD_REQUEST` on 2 of today's rows, so those Apollo leads never reached Challenger 2. This route is **not** the
MoltSets route "(2)", and the error has nothing to do with the MoltSets setup.

- Open the 2 errored cells and read the error message.
- Fix the cause, then re-run the 2 cells.

**Done =** both rows route to Challenger 2 without errors.
