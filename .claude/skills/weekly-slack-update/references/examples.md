# Weekly Slack update — examples

Read before drafting. These are messages Gaston actually sent, so they set the length, structure and voice.

## Gold-standard example (sent Fri Oct 9)

```
Hey Andrés, quick wrap-up of where things stand this week. One decision needed from you (#6), everything else is just closing the loops.

1. Clay maintenance → Sara (done)
Sara now owns workflow maintenance. She has the checklist covering everything that could break our sending cadence: truncated formulas, broken enrichments, table/source limits, etc. On my side, the next step is adding AI to the maintenance process to make it faster and more robust, but ownership is hers now.

2. Clay onboarding → Paz & Alexia (in progress)

* Paz: full walkthrough + Sara's trainings. We built EXP-013 together, so she's seen the whole process. The plan is to work hands on in some workflows with her next week
* Alexia: walkthrough of how we use Clay + some ideas on what she could automate or apply AI to. She's picking it up fast and has the trainings plus a condensed learning doc.
* Working sessions with both on Tuesday. I'll be hands-on next week, then over the following 1–2 weeks probably supporting as they build, and after that once they are fully onboarded they can take full care of that.

3. EXP-013 (launching Monday)
HR-only campaign. The workflow is built, the only pending item is adjuting some other Open Jobs / No-HM workflows to exclude HR leads, so all of them route to EXP-013. Plan is to start sending Monday.

4. Smartlead → Lila (starts next week)
Lila is fully onboarded and takes over recruiter inbox maintenance next week, on top of all the maintenance from outbound too. We also aligned on cameras always on for meetings.

5. Positive reply qualification (next steps with Lila)
Lila is drafting a prompt for Claude Code to build a skill: so that every new positive reply gets run through it and flagged qualified / semi-qualified / unqualified. The plan is to invoke the skill manually in the beginning before replying.
To scale it, I think we trigger the skill automatically (Seeing if there's an automatic Claude trigger or we can also test with Viktor) and post the verdict under the Slack positive-reply alert, so unqualified positions get discarded before we reply and anyone books a call.

6. Cold calling pickup rates (need your call on ownership)
Pickup rates are low for two main reasons:

* Spam tags: Felix confirmed most of our numbers are flagged as "likely spam". Charlie and Felix are on it, I can share updates as I get them.
* Wrong cities: we bought numbers in the right states but didn't target specific cities. Felix's tests show many calls go out from small cities, which hurts pickup. We should be calling from the largest city in each state.

We should remove the old numbers and buy new ones in the target cities. Charlie asked me to handle it - It's a straightforward process that I can get done, but also probably Ivan could be the owner of that (he or Dani bought the original numbers, I already asked him if it was him or not). If he hasn't done it before, I can walk him through it too. I've never done it but I already looked it up and it's super simple.
If you're ok with it, I can hand that over to Ivan.

7. Cold calling metrics & reporting
Aiming to finish today/monday so we start next week fully set up. Once we drop in the raw call data, the weekly tab and the rest of the reporting will update automatically.

8. Clay column limit + new DMU structure (in progress)
I'm working with Clay on the column limit. In parallel, I ran the full workflow through an AI review to find inefficiencies as you suggested, and I now need to go through the findings to design the new workflow. I'll keep working on it next week and share an update once it's set up.

Let me know if everything's clear!
```

What makes it work:
- The opening line says how many decisions are needed and points to the item number, so Andrés knows what needs him before reading the rest.
- One numbered item per workstream. Each header reads `Topic → Owner (status)`, with status values like done, in progress, launching Monday, starts next week, or need your call.
- 2–4 sentences per item: what changed, what is pending, the next step and when.
- The decision item explains the problem, gives the options with a recommendation, and ends with a yes/no question ("If you're ok with it, I can hand that over to Ivan.").
- Each item closes a loop from the previous 1:1 or update, such as EXP-013, cold-calling metrics or the column limit.
- There is no metrics block. Numbers appear only when they explain something.
- It closes with "Let me know if everything's clear!"
