---
name: offweek-outbound-update
description: >
  Drafts the off-week outbound update that Gaston posts in the #outbound-ripping Slack
  channel on the Tuesdays with no volume session (the huddle is bi-weekly since
  2026-10-13, so this goes out every other Tuesday: Oct 20, Nov 3, Nov 17…). It covers
  all three channels for the last full week: headlines, email metrics vs the week before
  with the why, plus Carlos's cold calling and Felix's LinkedIn updates pasted word for
  word. Email numbers come from the same sheets as the huddle deck. Use this whenever
  Gaston asks for "the off-week update", "the update for outbound-ripping", "the written
  update since there's no huddle", "the Tuesday update", or wants to combine the three
  channels' weekly numbers into one message, even if he doesn't say "off-week". Not the
  huddle deck (`weekly-volume-session`) and not the Friday wrap-up to Andrés
  (`weekly-slack-update`). Draft only: Gaston posts it himself, so never post to Slack.
---

# Off-week outbound update

Since 2026-10-13 the Outbound Volume Session runs every two weeks. On 2026-10-13 Franco
asked for a written update in the weeks between, and the team agreed: headlines,
metrics, the change vs the week before, and why. Andrés, Franco and Michael read it. It
goes in **#outbound-ripping** on the **Tuesday of the off-week**.

**Read [references/examples.md](references/examples.md) before drafting.** It holds the
real messages and Gaston's corrections, and the format comes from them.

## Dates

- **Off-week Tuesday** = the last session + 7 days. Sessions so far: Oct 13, then
  Oct 27 and every 14 days after. Off-weeks: Oct 20, Nov 3, Nov 17…
- If Gaston names the week (including a re-run of a past one), use it.
- Otherwise, the last session is the newest deck in the volume session folder **dated on
  or before today**. The next session's deck is often created days early, so the newest
  deck can be in the future. List them from the repo root:
  `python3 -c "import sys; sys.path.insert(0, '.claude/skills/weekly-volume-session/scripts'); from duplicate_deck import list_decks; from slides_lib import token; print([d['name'][:5] for d in list_decks(token())])"`
  (names start `MM-DD`). If today isn't in the off-week, or the gap looks wrong (a
  skipped or moved session), ask Gaston which week he means.
- **Reporting week** = the Mon–Sun before the off-week Tuesday (Oct 20 → Oct 12–18).
  It's compared with the week before it (Oct 5–11), which the last deck already showed.
- **Next session** = off-week Tuesday + 7 days. The intro line names it.

## Workflow

1. **Fetch the numbers.** From the repo root:
   ```
   python3 .claude/skills/weekly-volume-session/scripts/fetch_metrics.py --session-date <off-week Tuesday> --out <scratch>/metrics.json
   python3 .claude/skills/offweek-outbound-update/scripts/email_block.py <scratch>/metrics.json
   ```
   The first script is the huddle deck's, so both use the same source and the same
   weeks. The second prints the booked-calls headline and the Email bullets, already
   formatted. Use its lines as they are, so the numbers aren't retyped by hand. It
   also prints the warnings. Mention the ones that affect this message, such as a
   missing Time-to-reply column or a booked-calls mismatch. Skip the capacity-group
   ones, which only matter for the deck.
2. **Ask Gaston** for what the sheets can't give, in one message:
   - Carlos's cold calling update and Felix's LinkedIn update, as they sent them.
   - The email story: what explains the moves, and what the focus is until the next
     session. Write only what he gives this week. The example's specifics (HireBase plan,
     filters, decision dates) belong to Oct 20 and must not be copied into a new update.
   - Anything that must be in the headlines.
   
   Also look in the vault (`obsidian-wiki`: `wiki/hot.md` first, then meetings, tasks and
   `logs/` since the last session) for email work you can mention: experiments launched,
   tests and decisions. Offer what you found; don't put it in unasked.
3. **Draft** in the format below and show it to Gaston. Below the draft, list every
   `[WHY]` and anything you weren't sure about. Don't put that list in the message.
4. **Save** the version Gaston sends to
   `Near Work Partner/logs/weekly-updates/YYYY-MM-DD-offweek-outbound-update.md` (the
   Tuesday date), with the frontmatter the 2026-10-20 file uses. Until he confirms it
   was sent, mark it `Status: draft, not sent`. If he rewrote a lot, add the sent version
   and the lesson to `references/examples.md`.

## Format

```
Hey team! Since the volume session is now bi-weekly, here's the off-week update across the three channels for **<Oct 12–18>**. Next session is Tuesday <Oct 27>.

**Headlines**
• <booked-calls line from email_block.py>
• <one line per channel: the result that matters most, from its section below>

**📧 Email**
<metric bullets from email_block.py>

<1–2 short paragraphs: what explains the moves and what the focus is until the next session. Numbered points if there are several workstreams.>

**📞 Cold calling**
<Carlos's update, word for word>

**💼 LinkedIn**
<Felix's update, word for word>

Happy to go deeper on any of this, and the full breakdown is coming on the <27th>.
```

- **Headlines:** 3–5 bullets. The first is always booked calls (total, mix, last week).
  The others give each channel's main result in plain words, taken from that channel's
  section. Don't add a headline the sections don't support.
- **Email bullets:** add the reason after a bullet only when Gaston gave one. A big move
  with no reason (Oct 20: median reply time 8 → 25 min) gets `[WHY]` so he sees it. Never
  make one up.
- **Cold calling and LinkedIn are the owners' own words.** Paste them as sent: don't
  reword, shorten or reorder them. The only allowed change is replacing raw phone
  numbers with their cities. If something in their text is unclear or looks wrong (a
  number that disagrees with the sheets), tell Gaston separately; don't change it in the
  message.
- Slack formatting: `**bold**` section titles, `•` bullets, emoji on the three section
  titles as in the example. No vault links, Fathom timestamps or campaign IDs.
- Email numbers: `17.3K` (one decimal, capital K), change in whole percent (`−3%`), the
  others as `X (vs Y)`. This is not the deck format (`17.3k`). The script handles it.

## Sources

Same as the huddle deck (see `weekly-volume-session` → Sources): booked calls per channel
from the **Command Center** › `Weekly Data`, email metrics from **Outbound metrics** ›
`Email Campaign Metrics (Weekly)`, median reply time from `Email Time-to-reply tracker`.
If Gaston says the sheets were updated after you fetched, re-run both commands.
