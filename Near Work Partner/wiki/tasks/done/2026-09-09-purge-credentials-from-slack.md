---
type: task
title: "Purge shared credentials from Slack and rotate the exposed API keys"
created: 2026-09-09
updated: 2026-09-11
priority: high
status: done
from-meeting: "[[wiki/meetings/2026-09-09-smartlead-cv-workflow-training]]"
related: ["[[wiki/tasks/2026-09-09-provision-lila-tool-access]]"]
---

# Credentials are sitting in Slack history in plaintext

During Lila's Sep 9 setup session, secrets were pasted into Slack so she could configure her machine.
Remove them and rotate what was exposed.

**⚠️ The exposure is wider than the commitment made on the call.** Gaston's stated cleanup was
*"después la vamos a eliminar de Slack"* — about the **Smartlead password**. But the session also
pasted the **entire `.env` bundle** into Slack for Lila to copy into Claude Code:

- **Smartlead API key**
- **Google Docs credentials**
- **Clay credentials**
- Lila's generated Smartlead password

**Rotating the Smartlead password and deleting that one message does not clear the API keys.** Treat
the `.env` paste as a separate, larger item.

**Why it matters:** these are live production credentials for the systems that hold the entire lead
database and the outbound sending infrastructure. Slack history is searchable, retained, and visible
to anyone later added to that conversation.

**Suggested order:**
1. Delete every Slack message containing the password or the `.env` contents.
2. Rotate the **Smartlead API key**, **Clay** credentials, and the **Google Docs** service
   credentials — deletion alone does not undo exposure.
3. Re-distribute via a secret manager. Gaston already recommended LastPass to Lila for storage.
4. Confirm Lila has rotated her own Smartlead password.

**Blocked on:** step 4 was gated on Lila rotating her password. Steps 1–3 are not blocked.

**Timing:** No date stated. Verbatim: *"si quieres guardatela en algún lado y después la vamos a
eliminar de Slack."* Treated as **high priority** on exposure grounds rather than on stated urgency.

**Source:** [[wiki/meetings/2026-09-09-smartlead-cv-workflow-training]] · [Fathom @07:33](https://fathom.video/calls/817374239?timestamp=453)

---

## Completed 2026-09-11

**Done.** Credentials removed from Slack and the exposed keys handled.

**For the record — what the exposure was:** Lila's Smartlead password plus the full `.env` bundle (Smartlead API key, Google Docs credentials, Clay credentials), pasted into Slack during the Sep 9 setup session so she could configure Claude Code. The task was deliberately written wider than the commitment made on the call, which covered only the password.

**Prevention for next time:** distribute secrets through a password manager rather than Slack — Gaston already recommended LastPass to Lila for her own storage.

*Reported done by Gaston, 2026-09-11 status sweep (second pass).*
