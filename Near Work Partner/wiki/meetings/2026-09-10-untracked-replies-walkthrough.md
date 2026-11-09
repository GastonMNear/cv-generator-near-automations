---
type: meeting
title: "Untracked Replies Walkthrough"
created: 2026-09-10
updated: 2026-09-11
attendees: ["Gaston Murillo — cold email lead", "Lila Lemus — email replies"]
meeting-type: internal
duration-min: 20
recording_id: 181996144
fathom-url: "https://fathom.video/calls/819011271"
tags: [type/meeting, meeting-type/internal, topic/smartlead, topic/email-replies]
status: mature
related: ["[[wiki/meetings/2026-09-10-lila-replies-and-reply-time]]", "[[wiki/tasks/2026-09-04-fix-smartlead-positive-reply-slack-alerts]]"]
sources: ["[[bibliography/2026-09-10 - Untracked Replies Walkthrough - Meeting]]"]
---

# Untracked Replies Walkthrough

> [!note] Fathom titles this **"Impromptu Google Meet Meeting"**. Cut short at ~19 min because Gaston
> had a sales call in 5 minutes; follow-ups and metrics moved to Sep 11.

## TLDR
- **Untracked Replies is a Smartlead inbox holding inbound mail that could not be associated to a
  campaign and lead — and it has no reply affordance.** You literally cannot answer from that view.
- **Most of it is noise from warm-up reputation traffic**: every sender account runs an automated
  warm-up exchanging simulated human email to keep the inbox out of spam. That traffic lands
  untracked. Plus out-of-office, bounces, phishing/marketing, and staffing companies mass-mailing
  Google Groups.
- **Roughly once a week a genuine positive reply lands there** and must be manually associated to
  the campaign and original lead, after which it surfaces in the Master Inbox and behaves normally.
- Daily review established: ~5–10 minutes, ideally end of day, marking everything read so the
  read/unread boundary is the bookmark.

## Why a Real Positive Reply Lands Untracked — Two Cases
1. **The lead *is* in the campaign and replied positively, but the association silently failed.**
   *"por alguna razón no quedó asociado a esa campaña y a ese lead."* **Gaston does not know the cause.**
2. **We never emailed that person** — a colleague forwarded them our email or CV and they wrote in
   fresh, so there is no lead record to match.

> [!important] **Possible partial explanation for the dead Slack alert — NOT confirmed.**
> A reply that never associates to a campaign/lead is never classified as a positive reply, so it
> would never fire the Slack alert. **This connection was not stated on the call** and must not be
> recorded as diagnosed. Note the tension worth reconciling: this call treats the Slack channel as
> live and expected to fire (Gaston tells Lila to add a notification sound to it), while
> [[wiki/tasks/2026-09-04-fix-smartlead-positive-reply-slack-alerts]] records it as dead.

## Manual Association Procedure (verified live)
1. Open a second Smartlead tab → search leads by the sender's company domain or name.
2. Find the colleague we originally emailed; note which campaign that lead is in.
3. Return to the untracked reply → associate to campaign by pasting the campaign name → select the
   original lead → **Save**.
4. It disappears from Untracked and surfaces in the **Master Inbox within a few minutes** (not
   instantly), threaded under the **original lead's** name with the new person's reply as the latest
   message. It can then be replied to normally.

## Key Decisions
- **Partnership offers escalate to Gaston or the Outbound Slack group** rather than auto-booking
  Franco. For this one instance only, book with an AE and add Franco manually — he personally
  approved it. **This is not the default.**
- **Objection standard for "we have no employees in that country":** tell the truth — LinkedIn lets
  anyone self-associate with a company without employer approval, which is why our signal can be
  wrong. Apologise for the confusion and pitch anyway.
- **China/offshore objections:** counter-pitch LATAM on cost versus US plus US time-zone alignment.
- **Review technique:** judge from the list view without opening; open-and-close only to flip to read.

## Action Items
- **Gaston** — run the follow-ups + metrics session with Lila → done Sep 11
- **Gaston** — decide per-case whether Franco joins future partnership meetings
- **Lila** — daily Untracked Replies review; Slack @-mention sound; book the partnership meeting

**Source:** [Fathom recording](https://fathom.video/calls/819011271) · `recording_id: 181996144`
