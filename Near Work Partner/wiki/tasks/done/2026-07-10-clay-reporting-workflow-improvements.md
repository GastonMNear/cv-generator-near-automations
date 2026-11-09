---
type: task
title: "Clay + reporting workflow improvements from July 09 walkthrough"
created: 2026-07-10
updated: 2026-08-19
priority: high
deadline:
status: done
owner: Gaston
related: ["[[meetings/2026-07-09-clay-workflow-walkthrough]]", "[[tools/clay]]", "[[tools/smartlead]]", "[[tools/linkedin]]"]
sources: ["[[bibliography/2026-07-09 - Clay Workflow Walkthrough - Meeting]]"]
---

# Clay + Reporting Workflow Improvements From July 09 Walkthrough

Grouped backlog from the July 09 Clay workflow walkthrough. Keep this as the working list until items are split into separate implementation tasks.

## Must Do

- [ ] Replicate the Experiment 5 Company Table pattern across Open Jobs workflows.
- [ ] Confirm canonical link, owner, cadence, and logs for Paz's SmartLead batch-fetch action.
- [ ] Add/verify `LeadSource` in Paz's SmartLead batch-fetch/reporting sync.
- [ ] Review and tighten the Role Qualification prompt so bad-fit roles do not pass too easily.
- [ ] Review Company Type / recruiting-company prompt and job-title exclusion list.

## Should Do

- [ ] Investigate Smartlead webhook or batch process for replied-then-ghosted leads into Calling Sequences.
- [ ] Implement and report a 7-day sending test on roughly 10% of Candidate Lead volume.
- [ ] Improve Email 2 and Email 3 personalization using existing Clay fields.
- [ ] Validate LinkedIn/Meta lookalike-audience required fields before using no-email leads for paid media.

## Experiment Ideas To Shape Later

- Hybrid Open Jobs workflow with its own qualification and copy.
- C-level role campaign for larger companies where remote/global executive hiring is plausible.
- CEO outreach to companies with 5+ active open roles and a savings-based message.
- Niche psychology/clinical role workflow only if compliance/licensing fit is clearly validated.

## Notes

- Do not use Clay imports to BigQuery for Smartlead lead sync. Use Paz's SmartLead batch-fetch action.
- Qualified no-email leads should route to LinkedIn/no-email sheets, not Smartlead.
- Company Table logic mainly reduces Clay credit waste. It may improve operations, but it should not be counted as guaranteed incremental lead volume.
