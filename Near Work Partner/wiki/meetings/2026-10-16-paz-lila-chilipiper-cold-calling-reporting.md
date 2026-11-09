---
type: meeting
title: "ChiliPiper links + Cold calling reporting: combined booking link wrap-up, cold-calling report handed to Paz"
created: 2026-10-19
updated: 2026-10-19
attendees: ["Gaston Murillo — Outbound", "María Paz Marengo (Paz) — Marketing Ops", "Lila Lemus — Email Replies (left at ~04:06)"]
meeting-type: internal
duration-min: 22
recording_id: 193492627
fathom-url: "https://fathom.video/calls/863650212"
tags: [type/meeting, meeting-type/internal]
status: mature
related: ["[[wiki/meetings/2026-10-08-paz-clay-onboarding-exp13-chilipiper]]", "[[wiki/tasks/done/2026-09-17-ask-paz-size-routed-booking-link]]", "[[wiki/tasks/2026-08-24-justcall-metrics-via-api]]", "[[wiki/tasks/2026-09-04-align-weekly-monthly-metric-conventions]]"]
sources: ["[[bibliography/2026-10-16 - ChiliPiper links + Cold calling reporting - Meeting]]"]
---

# ChiliPiper links + Cold calling reporting — 2026-10-16

*(Fathom title: "ChiliPiper links + Cold calling reporting". Conducted in Spanish. The recording starts at the tail of the Chili Piper part. Lila leaves at ~04:06, and the rest is Gaston and Paz. "Coltools" / "Call Calling" in the transcript = **CallTools** / **cold calling**.)*

## TLDR
- **Chili Piper combined link is close.** Paz built a router where the lead fills a form with Number of Employees and is sent the right AE calendar. It reuses the website's **distributions**, so routing rules stay in sync across website, email and any other router [@02:41](https://fathom.video/calls/863650212?timestamp=161). **Remaining:** Paz adds the form fields that are still missing (the Zapier → HubSpot contact/company automation should keep the same trigger), then a test that it all lands in HubSpot [@00:00](https://fathom.video/calls/863650212?timestamp=0). After that, Gaston adds it to the sequences [@00:59](https://fathom.video/calls/863650212?timestamp=59).
- **Gaston's idea: drop the per-AE links entirely.** One general form ties a lead to the availability of every AE in that headcount band rather than one AE, so more slots are offered [@03:01](https://fathom.video/calls/863650212?timestamp=181). Gaston and Lila will work out how to use it once it's live. Nothing was decided yet.
- **Paz's scope shifts from Clay toward reporting.** Franco told Gaston that Alexia is freeing up time and should get into Clay automation and maintenance. Gaston and Andrés agreed it makes little sense for both Alexia and Paz to be in Clay, so Paz gets lighter-load work, starting with reporting [@04:12](https://fathom.video/calls/863650212?timestamp=252).
- **New Paz project: automate the cold-calling report from the CallTools API.** Andrés asked for it because the sheet depends on Ivan entering dispositions by hand every day without mistakes [@06:14](https://fathom.video/calls/863650212?timestamp=374). Gaston wants a **per-campaign breakdown** (≤5 campaigns), with the general row being the sum. Likely build: a Claude routine. Calls Booked and Qualified may come from the Command Center import, since Ivan can't know qualification. No deadline: "sin deadline", for Paz to pick up next week as she has time.
- **Sheet structure stays as is** (days in columns on the Daily Raw Data tab), so the existing Weekly/Monthly formulas keep working [@18:48](https://fathom.video/calls/863650212?timestamp=1128). Gaston will delete the stale campaign blocks and add the real current campaigns [@18:53](https://fathom.video/calls/863650212?timestamp=1133).
- **Access:** Gaston will make Paz a CallTools admin (he believes admins aren't billed) and send the credentials over Slack with a password he generates. Paz said she only needs **API** access to see what data is collected [@20:09](https://fathom.video/calls/863650212?timestamp=1209). No credential was spoken in the call. See *Security note*.

## Key Decisions
- The Chili Piper email router shares the website's distributions. A change to a distribution applies to every router.
- The cold-calling report gets automated from the CallTools API, owned by Paz, with a per-campaign breakdown if the API supports it. If it doesn't, fall back to the general level and solve per-campaign later.
- Keep the current Daily → Weekly/Monthly sheet structure. Gaston had raised dates-in-rows (as in the email daily tab) vs dates-in-columns, and both agreed to keep columns. Per-campaign Weekly/Monthly can come once the daily import works.
- Paz gets CallTools admin rather than sharing Gaston's login, which needs an emailed code each time.

## Action Items
**Gaston**
- [ ] Delete the outdated campaign blocks in the cold-calling Daily (and Weekly/Monthly) tabs and add the current campaigns [@18:53](https://fathom.video/calls/863650212?timestamp=1133)
- [ ] *(same-day)* Create Paz's CallTools admin user and send credentials + the Daily Raw Data link via Slack [@20:45](https://fathom.video/calls/863650212?timestamp=1245). This gates Paz's API work.
- [ ] *(after Paz's test)* Add the combined Chili Piper link to the sequences [@00:59](https://fathom.video/calls/863650212?timestamp=59) (existing task)

**Paz**
- [ ] Add the missing fields to the Chili Piper form. Check the Zapier → HubSpot automation. Tell Gaston/Lila when it's ready, then test the HubSpot sync with them [@00:00](https://fathom.video/calls/863650212?timestamp=0)
- [ ] Explore the CallTools API and build the automated daily cold-calling import (dials, dispositions, per campaign). No deadline [@14:06](https://fathom.video/calls/863650212?timestamp=846)

**Lila**
- [ ] Once the link is live, brainstorm with Gaston how to fold it into the sequences [@03:53](https://fathom.video/calls/863650212?timestamp=233)

## Context: how the cold-calling sheet works today
- Three tabs: **Daily**, **Weekly**, **Monthly**. Ivan fills Daily by hand each day at the general level only: dials, Calls Booked (he marks them when he books), and counts per **disposition**.
- Dispositions drive the rates: human pickups (the three green categories are real conversations; silent call / no contact are not), positive conversation rate, and bad data (wrong number, do-not-call, non-US). Example shown: **32 dispositioned leads out of 1,169 dials**, 3 of them human pickups.
- Weekly/Monthly are built from Daily with date-matching IFs, plus weekly cost. Gaston didn't build this sheet and doesn't love its structure, but agreed to keep it.
- Gaston thinks CallTools' Analytics tab shows dials per day per campaign, so the API should expose it. He hasn't checked the docs in detail.

## Security note
- Plan: Gaston generates a random password for Paz's new CallTools admin account and sends it **in plain text over Slack** [@20:45](https://fathom.video/calls/863650212?timestamp=1245). No credential value was spoken or shown in the transcript.
- Exposure: an admin-level login to the dialer, sitting in a Slack DM. Paz said she only needs the API, so a scoped API key, or an invite email that lets her set her own password, would expose less. At minimum she should change the password on first login.
- This is the second shared-tool access shortcut in a week (2FA was disabled on a shared account on Oct 9 for Sara + Ale).

## Open Questions
- Does CallTools actually charge for admin seats? Gaston thinks not ("me parece que no nos cobran por los admins"). Paz: if they charge, don't create one.
- Does the CallTools API expose dispositions **per campaign**? Unverified. Also, JustCall's API overstated connection metrics. Validate CallTools against Ivan's numbers before retiring manual entry.
- Should Calls Booked / Qualified come from the Command Center import instead of Ivan's marks? Gaston leaned that way but didn't decide.
- Which fields are missing from the Chili Piper form? Not named in the recorded portion.
- Did the earlier Oct 13/14 session happen, or is this Oct 16 call that session? The recording starts mid-topic.

## Full Transcript
See Fathom: https://fathom.video/calls/863650212
