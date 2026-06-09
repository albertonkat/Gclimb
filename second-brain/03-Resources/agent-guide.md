---
created: 2026-06-09
tags: [meta, agent-guide, navigation]
---

# Agent Navigation Guide — Gulf Coast Limb and Brace

Master reference for Claude Code. Read this when you need to find, write, or route anything.

---

## PHI Rule — Read This First

**PHI = any patient-identifiable data: names, DOB, insurance IDs, diagnoses tied to a specific person.**

| Content type | Where it goes |
|---|---|
| Raw SOAP notes | `~/GulfCoastLimb-PHI/soap-notes/` — LOCAL ONLY |
| Raw appeal letters | `~/GulfCoastLimb-PHI/appeals/` — LOCAL ONLY |
| Prior auth requests | `~/GulfCoastLimb-PHI/prior-auth/` — LOCAL ONLY |
| Patient case files | `~/GulfCoastLimb-PHI/cases/` — LOCAL ONLY |
| De-identified templates | `second-brain/05-Templates/` — repo OK |
| De-identified learnings | `MEMORY.md` — repo OK |
| Clinical/billing reference | `second-brain/03-Resources/` — repo OK |
| Session summaries (de-identified) | `second-brain/06-Sessions/` — repo OK |

**Never commit anything from `~/GulfCoastLimb-PHI/` to git.**

---

## Where to Find Things

| What | Where |
|---|---|
| Practice project + open tasks | `[[01-Projects/Gulf Coast Limb and Brace]]` |
| Clinical documentation standards | `[[02-Areas/Clinical-Practice/Overview]]` |
| Insurance + billing knowledge | `[[02-Areas/Insurance-Billing/Overview]]` |
| Software projects | `[[02-Areas/Software-Dev/Overview]]` |
| Business operations | `[[02-Areas/Business-Operations/Overview]]` |
| HCPCS L-code reference | `[[03-Resources/HCPCS L-Codes]]` |
| ICD-10 diagnosis codes | `[[03-Resources/ICD-10 O&P Codes]]` |
| Medicare LCD coverage rules | `[[03-Resources/Medicare LCD Reference]]` |
| Payer contacts + denial patterns | `[[03-Resources/Insurance Payers]]` |
| CPO credentials and scope | `[[03-Resources/CPO Scope of Practice]]` |
| Claude.ai Projects setup | `[[03-Resources/claude-ai-integration]]` |
| Past session summaries | `[[06-Sessions/]]` |
| Distilled insights | `[[08-Insights/]]` |
| Master O&P index | `[[07-MOCs/O&P Practice MOC]]` |
| Clinical doc index | `[[07-MOCs/Clinical Documentation MOC]]` |
| Billing/appeals index | `[[07-MOCs/Insurance Billing MOC]]` |
| Shared persistent memory | `MEMORY.md` (repo root) |

---

## Where to Write Things

| Content type | Destination |
|---|---|
| PHI documents (SOAP, appeals, prior auth) | `~/GulfCoastLimb-PHI/` — never this repo |
| Session summary (end of every session) | `06-Sessions/YYYY-MM-DD-claude-[topic].md` |
| De-identified learning | Append to `MEMORY.md` |
| Distilled insight (3+ sessions on same topic) | `08-Insights/YYYY-MM-DD-[topic].md` |
| Project status update | Edit `01-Projects/[project].md` in place |
| New payer rule learned | Append to `03-Resources/Insurance Payers.md` under "Learned Denial Patterns" |
| New clinical pattern | Append to `MEMORY.md` + optionally to `02-Areas/Clinical-Practice/Overview.md` |
| New code project | Create `01-Projects/[project-name].md` |
| Quick capture, unsorted | `00-Inbox/YYYY-MM-DD-claude-[slug].md` |

---

## Session Protocol (Mandatory)

### At session start
1. Read `MEMORY.md` in full
2. Read the last 3 files in `06-Sessions/` (sort by name, most recent first)
3. If task involves a clinical or billing topic, `brain_search` for it first

### During the session
- Found something worth keeping? → Append to `MEMORY.md` immediately (de-identified)
- Answering a domain question? → `brain_search` first, don't guess

### At session end
1. Write de-identified summary to `06-Sessions/YYYY-MM-DD-claude-[topic].md`
   Use template: `[[05-Templates/session-capture]]`
2. Append key learnings to `MEMORY.md`
3. If 3+ sessions now cover the same topic → write an `[[08-Insights/]]` note

---

## MEMORY.md Format

```
- [YYYY-MM-DD] [agent] learning or fact — source/context
```

Agent tags: `[claude]` (Claude Code), `[claude-ai]` (Claude.ai web/Projects)

Sections: `## Practice`, `## PHI & Compliance`, `## Agent Stack`, `## Clinical — O&P Domain`, `## Insurance & Billing`, `## Clinical Documentation`, `## Software Projects`

**Always de-identify**: OK to write `"Medicare denied K3 knee without physiatry note"` — NOT OK to write any patient name, DOB, or ID.

---

## PHI Vault Structure (`~/GulfCoastLimb-PHI/`)

```
~/GulfCoastLimb-PHI/
  soap-notes/     YYYY-MM-DD-[patientID]-[visit-type].md
  appeals/        YYYY-MM-DD-[patientID]-[payer]-[code].md
  prior-auth/     YYYY-MM-DD-[patientID]-[payer].md
  cases/          [patientID].md  (longitudinal case file)
```

Patient IDs: use a consistent internal ID (e.g., initials + DOB hash or your EMR number) — never the full name in filenames.

---

## Templates Available

| Template | Use for |
|---|---|
| `[[05-Templates/SOAP Note - Lower Extremity Prosthetic]]` | BK/AK/hip disarticulation visits |
| `[[05-Templates/SOAP Note - AFO Orthotic]]` | AFO/KAFO/KO visits |
| `[[05-Templates/SOAP Note - Upper Extremity Prosthetic]]` | BE/AE/shoulder disart visits |
| `[[05-Templates/Insurance Appeal Letter]]` | Any payer appeal |
| `[[05-Templates/Prior Authorization]]` | Prior auth requests |
| `[[05-Templates/session-capture]]` | End-of-session summaries |
| `[[05-Templates/insight]]` | Distilled insights |
| `[[05-Templates/agent-memory]]` | Inbox memory notes |
