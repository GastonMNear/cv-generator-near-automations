# Task extraction rules

Read this during Step 4. It defines what becomes a task, what the task file looks like, and how
timing is handled.

## Contents
- [What qualifies as a task](#what-qualifies-as-a-task)
- [Owner attribution](#owner-attribution)
- [The task file](#the-task-file)
- [Priority](#priority)
- [Deadlines](#deadlines)
- [Worked examples](#worked-examples)

---

## What qualifies as a task

Every candidate must pass **both gates** from SKILL.md Step 4 before it becomes a file. They are
restated here because this is the file you're reading while extracting.

### Gate 1 — Ownership

**Passes when:**
- Gaston explicitly commits — "I'll do X", "I'll have that by Wednesday", "déjame eso a mí"
- Someone assigns him something and he doesn't decline (silence on a direct assignment is acceptance)
- He says he'll follow up / send / check / build something

**Fails when:**
- Nobody named him. Work that merely sits in his domain is not his until someone says so — the
  inference "he owns campaigns, this is a campaign, therefore his" is what fills the board with
  tasks he never agreed to.
- He agreed the work *should happen* without taking it — "sí", "dale", "exacto" endorse a plan;
  they don't claim it. Ask who would actually do it.
- It's a status question, not work — *"I think the routine is done, I have to check."* → meeting
  note's Open Questions.
- It's owned by someone else → **waiting-on** lane, and only if it blocks him.

### Gate 2 — Concreteness

State the physical action and the done-condition in **one line, from the transcript alone**. No
inference about what it probably means. If you can't, the transcript held a mention, not a task.

Good: *"Send Sara the session recordings + CEOs 11–200 template + Apollo CSV via Slack; done when
she has the pack."*
Fails: *"Ship the soft technical landing deploy"* — the only evidence is Daniel asking "we're doing
it this week, right?" and Gaston saying "Sí." Nobody said what shipping it involves.

**Hedging in your own draft is the tell.** If you're writing *"scope is thin in the transcript"*,
*"if the scope isn't obvious, the deck slide is the reference"*, or *"check first — it may already
exist"*, you are documenting the gate failure rather than acting on it. Stop and surface it instead.

That line you wrote is also what Step 5 matches on, so this gate is load-bearing twice: a task too
vague to state crisply is a task the next run can't recognise, which is how twins get created.

### Also discard

- **Same-day / in-call actions** — done during the call or immediately after ("ahora yo le
  contesto"). Done or moot by the time he reads the report. If real multi-day work merely *starts*
  with a message, write the work, not the message.
- Hypotheticals with no commitment — "we could maybe look at..."
- Things already completed during the call
- Vague aspirations with no actionable verb — "we should be more data-driven"

**Nothing discarded is silent.** Every failed candidate goes to the report's Judgment Calls section
with its quote, timestamp, and the gate it failed, so Gaston can reverse the call in a sentence.

The test behind both gates: could Gaston open this task in three weeks and know what to actually
*do*, and would he agree it was ever his? If not, it's context (→ meeting note) or an open question
(→ meeting note's Open Questions).

## Owner attribution

From `wiki/context/team.md` — read it in Step 0 rather than trusting this copy, it's the source.

**`team.md` is known to be behind.** As of the Aug 10-19 run these people appear in meetings but
are not yet in it: **Ivan Valenzuela** (cold calling, started Aug 12), **Mairol Sontay** (LinkedIn),
**Felix** (reviews LinkedIn lead lists, Girdley-side), **Micaela Roel**, **Sebastian Torres**,
**Maria Paz Marengo** ("Paz"), **Krista Nelson**, **Leonardo Capita**. When you attribute work to
someone missing from `team.md`, **add them to it in the same run** — an owner you had to infer once
should not need inferring again.

| Person | Owns |
|---|---|
| **Samuel** (Chapaval) | Daily LinkedIn execution — connections, DMs, follow-ups |
| **Mairol** (Sontay) | LinkedIn outreach alongside Samuel |
| **Hector** (Melara) | Reply handling; owns Clay cleanup 3x/week (Mon/Wed/Fri) since Aug 10 |
| **Ivan** (Valenzuela) | Cold calling; owns JustCall configuration |
| **Franco** | Reporting |
| **Hayden**, **Camila** (Bagnati) | Outreach team — tooling/workflow support |
| **Daniel** (Ardila), **Andres** (Bahamon) | Campaign decisions |
| **Felix** | Girdley-side; reviews the LinkedIn lead lists |
| **Maria Paz Marengo** ("Paz") | BigQuery / billing access alongside Andrés |
| **Micaela Roel**, **Sebastian Torres**, **Krista Nelson**, **Leonardo Capita** | Seen in team calls — confirm role before attributing |

Gaston: `gaston.murillo@hirewithnear.com`. Fathom's `action_items[].assigned to` is a useful
cross-check for attribution, and its items assigned to *others* are good candidates for the
waiting-on lane — but see the diarization warning in SKILL.md Step 3: labels drift on long calls,
so ground ownership in who owns the *system* being discussed.

Names appear inconsistently across sources (Fathom shows emails, the vault shows first names).
Match on the person, not the string.

## The task file

`wiki/tasks/YYYY-MM-DD-{slug}.md` — filename date is the **meeting date**, not today's.

```markdown
---
type: task
title: "{Task Title}"
created: YYYY-MM-DD
updated: YYYY-MM-DD
priority: high|medium|low
deadline: YYYY-MM-DD                  # ONLY if stated outright — omit the key otherwise
status: open
from-meeting: "[[wiki/meetings/YYYY-MM-DD-slug]]"
related: ["[[...]]"]                  # omit the key entirely if empty
sources: ["[[bibliography/...]]"]     # omit the key entirely if empty
---

# {Task title}

{1-3 lines: what it is and why it matters — business context, not a transcript restatement.}

**Why:** {who asked, what it unblocks, what "done" looks like}
**Timing:** {verbatim phrase — only when no hard date was given}

> {≤2 lines of verbatim quote — MAX}

**Source:** [[wiki/meetings/YYYY-MM-DD-slug]] · [Fathom @12:34](https://fathom.video/calls/N?timestamp=754)
```

**Frontmatter rules (trimmed 2026-08-19 — do not undo):**
- **No `tags:`** — redundant with `type` + `status` + `priority`
- **No empty `related: []` / `sources: []`** — omit the key entirely
- Frontmatter wikilinks must be quoted

**Aim for ~250 tokens, but this is a guideline, not a hard cap.** The point is to keep task files
from bloating, not to hit a number — real files land around 250-375 tok and that's fine. Frontmatter
wikilinks alone cost ~80-110 tok before a word of body, and Spanish quotes tokenize ~1.5x English.

Never strip established frontmatter (`sources:`, `from-meeting:`) to save tokens — that trades real
provenance for a trivial gain. If a task genuinely needs several hundred tokens of *explanation*,
that's the signal it's a project: write a `wiki/` page and link to it.

If you do want a real count (`chars/4` undercounts markdown badly):

```bash
python3 -c "import tiktoken;print(len(tiktoken.get_encoding('cl100k_base').encode(open('FILE').read())))"
```

**`**Why:**` is the point of this skill.** `task-manager`'s EXPLAIN operation answers "what did I
mean by this?" from the task body first, and only falls back to refetching the transcript if the
body is thin. A good `**Why:**` saves that round trip. Write it for a reader who has forgotten the
meeting entirely — name who asked and what it unblocks, don't restate the title.

Bad: `**Why:** Daniel asked for it in the weekly check.`
Good: `**Why:** Daniel needs the LinkedIn slides for Tuesday's leadership review; LinkedIn booked
only 1 call last week and he wants the targeting fix visible. Done = slides sent with headline
metrics.`

## Priority (frontmatter) and horizon (index)

These are two different fields — don't collapse them.

**`priority:` in frontmatter**, per `task-manager`:
- `urgent` / `ASAP` / `today` / `tomorrow`, or a deadline under 3 days → **high**
- `whenever` / `no rush` / `low priority` → **low**
- default → **medium**

Blocking someone else's work is also a high signal — if Samuel can't run LinkedIn until Gaston
ships the list, that's high regardless of phrasing. Note the blocker inline on the index line too
(`| **blocks Samuel**`) — it's the first thing worth seeing in a section.

**Index section = time horizon**, not priority: `## This Week (<dates>)` · `## Next Week (<dates>)` ·
`## Backlog`. Derive it from the deadline (or from what was actually said in the meeting), and default
to **Backlog** when the meeting gave no timing — then list those in the report's Needs-Your-Call
section so Gaston places them. A high-priority task with no date still starts in Backlog; priority
decides what gets dropped from an overloaded week, not which section it lands in.

## Deadlines

**Explicit date or day** → set `deadline:`. Resolve relative days against the **meeting date**:
"by Thursday" in a Friday Aug 14 meeting means Aug 20, not Aug 21.

**Vague** → omit `deadline:` entirely, record the phrase in `**Timing:**`, and list it in the
report's Needs-Your-Call section.

Phrases that are **not** dates, no matter how confident they sound:
- "soon", "when you get a chance", "next sprint", "ASAP" (urgency ≠ a date — set priority high,
  leave deadline empty)
- "first thing when I'm back" — not a date unless his return date is independently known
- "before the next call" — only a date if the next call's date was actually stated

A guessed date in `deadline:` looks authoritative and silently misleads; an empty one prompts a
question. Ask, don't interpolate.

## Worked examples

**1 — Clear commitment with a real date**

> Transcript: *Daniel:* "Necesito las slides de LinkedIn antes del martes." *Gaston:* "Sí, te las
> mando el lunes."

Meeting date 2026-08-14 (Friday) → "el lunes" = 2026-08-17.

```markdown
priority: high
deadline: 2026-08-17
```
```markdown
# Send Daniel the LinkedIn slides with headline metrics

LinkedIn slides for Tuesday's leadership review, including the headline metrics Daniel flagged.

**Why:** Daniel presents these Tuesday; LinkedIn booked only 1 call last week and the targeting
fix needs to be visible to leadership. Done = slides sent to Daniel with metrics filled in.

> "Sí, te las mando el lunes." (I'll send them Monday.)

**Source:** [[wiki/meetings/2026-08-14-weekly-check]] · [Fathom @07:01](https://fathom.video/calls/783947351?timestamp=421)
```

**2 — Commitment with vague timing → no deadline key**

> *Daniel:* "Y cuando puedas, extendé la secuencia de email." *Gaston:* "Dale."

```markdown
priority: medium
# NO deadline key at all
```
```markdown
**Why:** Daniel wants more touches in the sequence; no date given and nothing downstream blocks on it.
**Timing:** "cuando puedas" ("when you can") — genuinely open-ended, no date given.
```
→ and it appears in the report under **Needs Your Call**.

**3 — Assigned to someone else, but blocks Gaston → waiting-on**

> *Gaston:* "No puedo lanzar el experimento hasta que Daniel apruebe la copy."

Not a task file. It goes in the report's **Waiting On Others** lane and as a line in the meeting
note, flagged as blocking the launch task.

**4 — Not a task**

> *Andres:* "Deberíamos ser más data-driven con los experimentos."

No actionable verb, no owner, no commitment. Meeting note context at most.

**5 — Confirmed in passing → fails Gate 2** *(real: this one got written and shouldn't have)*

> *Daniel:* "Solved in soft technical lending deploy. Que lo vamos a hacer esta semana, ¿cierto?"
> *Gaston:* "Sí."

A deck line item confirmed in a single exchange. The date is real ("esta semana") and Gaston did
agree — Gate 1 passes. But nothing in the transcript says what deploying it involves, so the
done-condition can't be written without inventing it. → **Judgment Calls**, quoting both lines:

```
[J1] "Soft technical landing deploy" — Gate 2 (no scope)
     Daniel: "que lo vamos a hacer esta semana, ¿cierto?" — you: "Sí."  [Fathom @51:23]
     Confirmed for that week, but the call never says what shipping it means.
     → Want this as a task? Tell me the deliverable and I'll write it.
```

**6 — Status question → fails Gate 1**

> *Gaston:* "I think the routine is done. I have to check." / "I don't know if I have that active yet."

Reads like work because it names a deliverable, but he's describing uncertainty about existing
state, not taking on a build. If checking reveals it's missing, *that* is the task — and it'll be
said in a later meeting. → Open Questions in the meeting note, plus Judgment Calls.

**7 — Same-day action → discard**

> *Gaston:* "Daniel me preguntó por los follow-ups — ahora yo le contesto."

A Slack reply he sends within the hour. By the time the report reaches him it's done. Writing it
produces a task that can only ever be closed, never worked.

*Counter-case worth distinguishing:* if the reply requires assembling something first — a week of
numbers, a decision from Andrés — then the work is the assembly and the message is just its last
step. Write the assembly, with the message as the done-condition.
