---
type: meeting
title: "Weekly 1:1 Gasti + Lila: 13 email calls reconciled, hard-follow-up CTA rewrite, add-only recruiter warm-up skill, inbound warm-email follow-up flow, HubSpot access for Lila"
created: 2026-11-03
updated: 2026-11-03
attendees: ["Gaston Murillo — Outbound", "Lila Lemus — Email Replies (Gaston's report)"]
meeting-type: internal
duration-min: 51
recording_id: 196362813
fathom-url: "https://fathom.video/calls/873652607"
tags: [type/meeting, meeting-type/internal]
status: mature
related: ["[[wiki/meetings/2026-10-19-lila-weekly-1on1]]", "[[wiki/tasks/2026-11-03-decide-warmup-4-nonstandard-inboxes]]", "[[wiki/outbound/lead-qualification-tracking]]"]
sources: ["[[bibliography/2026-10-26 - Weekly 1on1 Gasti Lila - Meeting]]"]
---

# Weekly 1:1 Gasti + Lila — 2026-10-26

*(Fathom title: "Weekly 1:1 Gasti + Lila". Conducted in Spanish. ~51 min. Diarization drifts in places, for example Gaston's HubSpot answers are partly labelled as Lila around @46:06. Ownership below is grounded in content.)*

## TLDR
- **Last week's email calls reconciled at 13.** AutoMetrics showed 10 and the Command Center 11. Going name by name (Indigo, Rampa, WorkStreet, Parkour, PointGuard, Apostle, DevSec, Sled AI, Oxxon, Luxury Collection, Spark Media, Roll Call, Poc Real Estate) they landed on 13. The gap is the **HubSpot → metrics-sheet export not having run yet**. Workforce Connection Group and Iluma (booked the 17th) don't count for that week [@06:03](https://fathom.video/calls/873652607?timestamp=363), [@12:06](https://fathom.video/calls/873652607?timestamp=726). **October stands at ~39 calls against a 49 target, so it needs at least one more 10-call week** [@03:42](https://fathom.video/calls/873652607?timestamp=222). Gaston fixed the weekly booked-calls skill after it returned 16, including one from LLMs, not email outreach.
- **Roll Call booked with no matching lead.** The only touchpoint is an August Experiment 8 contact. Gaston's rule: if a booker says they found us by email and no lead or same-company contact exists, flag it in the Sales channel. When there's one plausible touchpoint, assign the call to that campaign [@08:43](https://fathom.video/calls/873652607?timestamp=523), [@11:15](https://fathom.video/calls/873652607?timestamp=675).
- **Hard-follow-up CTA rewrite (copy unchanged, CTA only).** Meeting-request Email 1 shouldn't ask "are you open?" because they already asked for a call. Use "grab a time / book here", or "send me a few times and I'll send the invite". **No "this week"**, since automated sends can land on a Friday. CTA goes in its own paragraph. Drop filler like "I'll handle the rest". Email 5 (close the loop) gets a lighter, low-commitment ask ("if this or another search is still active and you want to explore options, feel free to book here"). Candidate Sent follows the same pattern [@15:13](https://fathom.video/calls/873652607?timestamp=913), [@16:39](https://fathom.video/calls/873652607?timestamp=999), [@21:00](https://fathom.video/calls/873652607?timestamp=1260).
- **Subsequence rollout rule.** Every variant of each subsequence must be identical across all campaigns, all active, with a **hyperlink rather than a bare URL**. AI can do the update, then Lila spot-checks a few campaigns by hand [@23:37](https://fathom.video/calls/873652607?timestamp=1417), [@49:07](https://fathom.video/calls/873652607?timestamp=2947).
- **Recruiter warm-up skill: build add-only now.** Paz isn't removing or tagging departed recruiters yet, so removal waits. The skill should still be told a status column (active/inactive) is coming, so it needs only a quick fix later. Test it on the new recruiter's 2 inboxes. Lila: *"Trabajo en eso hoy"* ("I'll work on it today") [@25:01](https://fathom.video/calls/873652607?timestamp=1501).
- **Qualification skill so far: 28.6% Qualified, 42.9% Semi, 28.6% Unqualified.** Gaston wants to know whether any Semi/Unqualified lead ends up booking, to judge whether the clarifying questions are worth it. These are a large share of positives, so handle them carefully to protect calls booked. Lila offered a Friday report on Qualified/Semi → booked conversion [@28:00](https://fathom.video/calls/873652607?timestamp=1680), [@29:22](https://fathom.video/calls/873652607?timestamp=1762). *(Delivered Oct 30, see [[outbound/lead-qualification-tracking]].)*
- **Inbox Efficiency is running well and reputation is improving.** The stricter rule is already in the skill: if an inbox drops below ~90, cut its volume right away (to 1–3/day) so it recovers within a week, instead of waiting until it's near 60 [@30:00](https://fathom.video/calls/873652607?timestamp=1800).
- **Inbound now flows through Lila's mailbox.** Gaston explained lead magnets (e.g. the Pre-Vetted Candidates form): people leave their email, get generic CVs by email, and replies land in Lila's own inbox. She should use **the new inbound booking link, saved separately from the six cold-email links** so attribution stays clean [@32:19](https://fathom.video/calls/873652607?timestamp=1939). Lila: nothing has reached her inbox yet [@36:11](https://fathom.video/calls/873652607?timestamp=2171). A morning meeting with other teammates had assumed Lila was already doing manual follow-ups on these, which nobody had asked her to do.
- **Warm-email follow-up skill.** Rather than manual follow-ups, Lila builds an AI skill that checks who replied, whether they booked in HubSpot, and suggests follow-up 1/2/3 drafts, trained on the Smartlead follow-up doc's tone. Pair it with **Gmail labels** mirroring Smartlead (follow-up, meeting booked, opportunity lost), kept in sync against HubSpot. Lila will check it by hand at first. Volume is small (~69 inbound so far, maybe 7–8 replies/wk) [@37:17](https://fathom.video/calls/873652607?timestamp=2237), [@42:56](https://fathom.video/calls/873652607?timestamp=2576).
- **Lila has no HubSpot access.** Gaston: *"Se lo voy a pedir a Paz"* ("I'll ask Paz for it"), with his own API key as a fallback [@45:55](https://fathom.video/calls/873652607?timestamp=2755). Her Claude project doesn't use HubSpot; CVs come from Smartlead.

## Key Decisions
- Last week's email calls = **13**. The dashboard gap is the pending HubSpot export, not misattribution.
- A booking with no traceable lead gets flagged in the Sales channel. If one plausible touchpoint exists (Roll Call → Experiment 8), assign it there.
- Hard follow-ups: change only the CTA. No time references, CTA in its own paragraph, hyperlink not URL, all variants identical and active in every campaign.
- Recruiter warm-up skill ships **add-only**. Removal waits for Paz's status column.
- Inbound replies use the dedicated inbound booking link, kept apart from cold-email links.
- Inbound follow-ups go through an AI-assisted skill plus Gmail labels, not ad-hoc manual work. Lila supervises it by hand at first.

## Action Items
**Gaston**
- [ ] Ask Paz to give Lila HubSpot access [@45:55](https://fathom.video/calls/873652607?timestamp=2755), [@47:00](https://fathom.video/calls/873652607?timestamp=2820)
- [ ] *(conditional fallback / in-call)* Share his HubSpot API key with Lila if access is slow [@45:55](https://fathom.video/calls/873652607?timestamp=2755)
- [x] Fixed the weekly booked-calls skill (returned 16 incl. an LLMs-sourced call) — done before the call [@12:06](https://fathom.video/calls/873652607?timestamp=726)

**Lila**
- [ ] Update hard-follow-up CTAs per the rules above, then spot-check several campaigns for hyperlinks and consistency with the doc [@23:37](https://fathom.video/calls/873652607?timestamp=1417), [@49:07](https://fathom.video/calls/873652607?timestamp=2947)
- [ ] Build the recruiter warm-up skill (add-only, aware of the future status column) and test on the 2 new inboxes [@25:01](https://fathom.video/calls/873652607?timestamp=1501)
- [ ] Friday report: Qualified/Semi/Unqualified → booked conversion [@29:22](https://fathom.video/calls/873652607?timestamp=1762) — ✅ delivered Oct 30
- [ ] Save the inbound booking link in a separate section from the cold-email links [@32:19](https://fathom.video/calls/873652607?timestamp=1939)
- [ ] Set up Gmail labels and build the warm-email follow-up skill (HubSpot booked check + suggested follow-ups) [@42:56](https://fathom.video/calls/873652607?timestamp=2576)
- [ ] Assign Roll Call to Experiment 8 in AutoMetrics [@11:15](https://fathom.video/calls/873652607?timestamp=675)

**Waiting on**
- **Paz** — HubSpot access for Lila (once Gaston asks). Gates the HubSpot booked-check in the warm-email follow-up skill.
- **Paz** — status column on the recruiters sheet. Gates the removal half of the warm-up skill.

## Context
- Supersedes the Oct 19 "don't start the warm-up skill yet". Per Lila's Nov 3 Slack update the skill is live (1st + 15th), with 25 inboxes to connect via OAuth.
- Per the Nov 3 update, 1,000 emails / 64 campaigns of hard follow-ups carry the Chili Piper link since 10/27, and Lila's inbox has had 0 inbound replies since 10/1, consistent with her "nothing has arrived" here.
- Lila's qualification-skill numbers here (~28/43/29%) are her early sample. The Oct 30 report covers 24 leads (Oct 9–29).
- The "ellas" in the morning meeting are not named in the transcript.

## Open Questions
- Did Gaston ask Paz for Lila's HubSpot access, and has it been granted? If he shared his API key instead, it should be revoked/rotated once she has her own access.
- Is inbound mail actually routed to Lila's inbox? 0 replies since 10/1 against ~69 inbound leads suggests a routing gap.
- Who expected Lila to be doing manual inbound follow-ups, and has that been cleared up?
- Is the HubSpot → metrics-sheet export now running, so AutoMetrics matches the Command Center?

## Full Transcript
See Fathom: https://fathom.video/calls/873652607
