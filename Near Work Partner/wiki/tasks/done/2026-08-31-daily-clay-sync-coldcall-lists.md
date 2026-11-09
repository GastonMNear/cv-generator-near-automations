---
type: task
title: "Enable the daily automatic Clay sync for both cold-calling lists"
created: 2026-08-31
updated: 2026-10-05
priority: medium
status: done
completed: 2026-10-05
from-meeting: "[[wiki/meetings/2026-08-31-cold-calling-lists]]"
related: ["[[wiki/tasks/2026-08-31-load-no-hm-ceos-to-parallel-dialer]]", "[[wiki/tasks/2026-08-26-automate-experiment-lead-adds]]"]
sources: ["[[bibliography/2026-08-31 - Listas Cold Calling - Meeting]]"]
---

# Make the cold-calling lists self-feeding

Finish configuring the Clay workflows so **both cold-calling campaigns receive leads automatically
every day**, removing manual list uploads after the Aug 31 setup.

**Why:** Daniel's stated goal — *"después de hoy Gasti ya no tenemos que subir nada más"*, nobody
should have to chase Gaston for a list again. **Manual uploads are the root cause of the No-HM list
sitting unloaded and Ivan running dry.** Fixing the instance without fixing the process means it
recurs next week.

**This is the durable half** of [[wiki/tasks/2026-08-31-load-no-hm-ceos-to-parallel-dialer]]: that
task loads the list once, this one makes it never need loading again.

**Done =** both campaigns receive their daily leads with no manual step.

**Timing:** No date. Gaston committed only *"en teoría sí"* — theory, not a promise, which is why this
is filed separately rather than assumed done with the upload. **Needs a date from Gaston.**

> "va a quedar automático, suba, que suba, que suba... suba diario. Sí, en teoría sí"
> *"it'll be automatic, uploading, uploading... uploading daily. Yes, in theory yes."*

> [!note] Distinct from [[wiki/tasks/2026-08-26-automate-experiment-lead-adds]] — that one covers
> **Smartlead experiment campaigns**, this one covers **JustCall cold-calling lists**. Different
> systems, different destinations. They may share a Clay pattern, so building either first likely
> makes the other cheaper.

**Source:** [[wiki/meetings/2026-08-31-cold-calling-lists]] · [Fathom @41:00](https://fathom.video/calls/805161647?timestamp=2460)

---

## Update 2026-09-28

**Rescoped: the destination is now CallTools, not JustCall.** The new dialer is live with manual CSV uploads (✅ Sep 28). The remaining half: *"tengo que configurar la API de Call Tools para mandar leads nuevos todos los días a esa herramienta y que no tengamos que estar cargando CSVs"* (I have to set up the CallTools API to send new leads every day so we stop uploading CSVs) [@53:00](https://fathom.video/calls/837061087?timestamp=3180). **Done =** a day's new leads arrive in CallTools without anyone uploading them. Still no date.

*From fathom-task-sync run 9 (Sep 14–25 meetings) + Gaston's Sep 28 status.*

## Update 2026-10-05

**Promised three times and given a date.** Sep 28: Daniel confirmed Gaston owns the Clay→CallTools upload and automation ([@10:34](https://fathom.video/calls/838137976?timestamp=634)). CallTools dialing went live on Thu Sep 24. Sep 29: *"En eso estoy… Hoy se va a llegar"* (on it, it lands today) ([@11:26](https://fathom.video/calls/840247722?timestamp=686)). Ivan also did a manual CSV load tagged `US Open Jobs Hiring Managers` that day. Sep 30: *"hoy voy a terminar 100% todo lo de Coldtools porque ya no quiero mandar más CSV… el API va a ese lado y el email forward, ida y vuelta"* ([@50:00](https://fathom.video/calls/844117752?timestamp=3000)). Daniel listed "CallTools perfect" as one of his top needs. **Self-set date: Sep 30, now past. Is it done?** It also gates the voicemail automation, and the FDNC block ([[tasks/2026-09-29-submit-calltools-fdnc-form]]) limits what the feed is worth until that is fixed.

*From fathom-task-sync run 10 (Sep 28 – Oct 1 meetings).*

## Closed 2026-10-05

Gaston (Oct 5, after run 10): CallTools API lead feed done.
