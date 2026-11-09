---
type: context
title: Email campaign insights (living)
created: 2026-10-27
updated: 2026-11-09
week: 2026-11-02
related: ["[[context/outbound-engine]]"]
---

# Email campaign insights

Rewritten each Monday by `outbound-campaign-review`, never appended. Numbers live in the
Outbound sheet, and history lives in `logs/campaign-reviews/`. Metric = calls per 1k emails
sent, comparing the last 4 wks with the 8 before.

## Standing (wk Nov 2–8)
- **Volume leader:** US OJ No HM, 12 calls / 4 wks at 0.49/1k on ~6.2k/wk (rate held while volume grew 4.2k → 7.8k/wk).
- **Performance at scale:** Latam OJ HMs 2.3/1k (~430/wk). US OJ HMs 1.5/1k on ~1.3k/wk, its Oct gain gone.
- **Structural:** HM = 15% of sends, 40% of calls (1.57 vs 0.44/1k). It was 52%, and the drop is HM calls/positive (0.22 → 0.17), not positives.
- **Biggest lever:** EXP006 Need Confirmation, 20 positives → 1 call. Base conversion = +1.2 calls/wk, no new leads.
- **Concentration:** top 2 campaigns = 47% of calls.
- **Data caveat:** CC 11 vs sheet 12. EXP014 and most HireBase sends have no campaign block yet.

## Watchlist
- EXP006 Need Confirmation conversion (1 call / 20 positives, p=0.02) — opened Nov 9 — Nov 9 Smartlead pull (B `3804833`, 14 positives since Oct 11): **the flow works** (manual reply ≤2h for 9/12, two weekend gaps of 48–53h; the 5-email FU ran). **The break is after the resume:** 0 of 9 "send the profile" leads replied again, vs Aug–Oct when the same reply + same resume template booked (Umer, Gabriel, Cobi, Matt replied with times). The only call came from a referral (Biohack). Recent repliers skew to recruiters/HR, plus a staffing firm (Softcom) and a C2C ask. Open: Nirali (Zingly) asked to reconnect after mid-Nov and cfleenor (Nov 4, Qualification Pending) have no reply from us in Smartlead — next: confirm resume delivery on one thread + title mix; re-read next Mon.
- HM-wide calls/positive 0.22 → 0.17 (p=0.13) — opened Nov 9 — next: does it recover once this wk's 24 HM positives book (lag)?
- RB2B family (3 campaigns, by design) — opened Oct 27 — Nov 9: 2 calls / 4.3k = 0.46/1k vs core base 3.4; Visitor+DMU 1.2k sent 0 calls, Individual 0.9k 1 call — next: ~2.5k each for a verdict.
- Oct 29 pause decisions not applied — opened Nov 9 — EXP008A still 523 sent/wk (0 calls in 6 wks), EXP009 +273 leads, EXP012 Mkt +92 — next: Gaston confirms intent.
- US CEOs from HM OJ (EXP-011 always-on?) — opened Nov 9 — 8 positives, 0 calls in 4 wks (p=0.17) — next: 2 more wks.
- New campaigns: EXP013 (2.1k, 0 calls, 1.4 pos/1k vs 2.2 US No HM), EXP014 (Nov 6, not in sheet) — opened Oct 27 — next: EXP013 ~4.8k sends; EXP014 needs a sheet block.

## Resolved
- US OJ No HM conversion leak (Oct 27 → Nov 9): calls/positive back to 0.22 (base 0.24). It was variance.
- Canada OJ HMs 0-calls (Oct 19 → Nov 9): 2 calls in 3 wks, 4.0/1k. It was variance.
- Canada OJ No HMs supply (Oct 27 → Nov 9): not out of leads (42 added/wk, ~170 sent/wk). It's small, and 0 calls in 11 wks is p=0.16.

## Campaign change log
- Hard follow-ups (all campaigns): subsequences rebuilt Sep 21–23. Chili Piper link added to ~200 subs on Oct 27 (Lila). US HMs' Oct gain didn't persist.
- RB2B: two variants live Oct 5 and replaced core `2311489` (Gaston, Oct 29). Core stays ACTIVE with no new leads. Judge the 3 combined.
- HubSpot Cold Accounts OJ (HMs + NO HMs): batched on/off (Gaston, Oct 29). Zero leads between batches is expected.
- EXP013: launched ~Oct 12 (HR leads moved out of EXP012).
- EXP014 Eng/Sales/Mkt: launched Nov 6 (6 campaigns, B inboxes); subsequences added Nov 7.
- Oct 29 decisions: EXP-011 always-on; pause EXP-009, EXP-012, EXP-008A (→ baseline).
- US OJ No HM: volume 4.2k → 7.8k/wk Oct 12 → Nov 2 (+2.5k leads added this wk).
