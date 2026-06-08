---
created: 2026-06-08
tags: [meta, agent-guide, navigation]
---

# Agent Navigation Guide

Master reference for Claude (ruflo) and Hermes. Read this when you need to find, write, or route anything in this second brain.

---

## Where to find things

| What you're looking for | Where to look |
|---|---|
| Project status, open tasks | `[[01-Projects/gclimb - Healthcare IoT Hub]]` |
| Healthcare IoT overview, device categories | `[[02-Areas/Healthcare-IoT/Overview]]` |
| SmartThings dev context, active repos | `[[02-Areas/SmartThings-Dev/Overview]]` |
| Z-Wave protocol reference | `[[03-Resources/Z-Wave Protocol]]` |
| Zigbee protocol reference | `[[03-Resources/Zigbee Protocol]]` |
| Z-Wave healthcare devices list | `[[03-Resources/Z-Wave Healthcare Devices]]` |
| Zigbee healthcare devices list | `[[03-Resources/Zigbee Healthcare Devices]]` |
| SmartThings platform reference | `[[03-Resources/SmartThings Platform]]` |
| ruflo agent reference | `[[03-Resources/ruflo]]` |
| Hermes config & shared memory setup | `[[03-Resources/hermes-config]]` |
| obsidian-brain + MCP setup | `[[03-Resources/brain-integration-setup]]` |
| Past session summaries | `[[06-Sessions/]]` |
| Distilled insights | `[[08-Insights/]]` |
| All healthcare content | `[[07-MOCs/Healthcare IoT MOC]]` |
| All resources index | `[[07-MOCs/Resources MOC]]` |
| Shared persistent memory | `MEMORY.md` (repo root) |
| How to write agent memories | `[[00-Inbox/agent-memory-protocol]]` |

---

## Where to write things

| Content type | Destination |
|---|---|
| Quick capture, unsorted | `00-Inbox/` — file as `YYYY-MM-DD-[agent]-[slug].md` |
| Session summary (end of every session) | `06-Sessions/YYYY-MM-DD-[agent]-[topic].md` |
| Distilled insight (from 3+ sessions) | `08-Insights/YYYY-MM-DD-[topic].md` |
| Project update or task status change | Edit `01-Projects/gclimb - Healthcare IoT Hub.md` in place |
| New protocol or tool reference | `03-Resources/[name].md` |
| Device handler notes, Groovy patterns | `02-Areas/SmartThings-Dev/` |
| Healthcare domain knowledge | `02-Areas/Healthcare-IoT/` |
| Any persistent learning | Append to `MEMORY.md` using format: `- [YYYY-MM-DD] [agent] learning — context` |

---

## Session protocol (mandatory)

### At the start of every session
1. Read `MEMORY.md` in full
2. Read the last 3 files in `06-Sessions/` (sort by filename descending)
3. Search brain for any topic directly relevant to today's task

### During a session
- When you discover something worth keeping: append to `MEMORY.md` immediately
- When you answer a domain question: search brain first (`brain_search`), don't guess

### At the end of every session
1. Write a session summary to `06-Sessions/YYYY-MM-DD-[agent]-[topic].md` using the `[[05-Templates/session-capture]]` template
2. Append key learnings to `MEMORY.md`
3. If a topic now has 3+ session notes: consider writing an `[[08-Insights/]]` note

---

## Search before writing

Always use `brain_search` before creating a new note. If something close exists, update or cross-reference it instead of creating a duplicate.

---

## Templates available

| Template | Use for |
|---|---|
| `[[05-Templates/agent-memory]]` | Structured memory notes in `00-Inbox/` |
| `[[05-Templates/session-capture]]` | End-of-session summaries in `06-Sessions/` |
| `[[05-Templates/insight]]` | Distilled insights in `08-Insights/` |

---

## MEMORY.md format

```
- [YYYY-MM-DD] [agent] learning or fact — source/context
```

Sections in the file:
- `## Project` — Gclimb repo context
- `## Agent Stack` — ruflo, Hermes, MCP config
- `## Second Brain` — vault structure notes
- `## Protocols & Standards` — HL7 FHIR, IEEE 11073, Z-Wave, Zigbee
- `## Device Handlers` — specific devices, fingerprints, quirks
- `## SmartThings Platform` — Groovy DSL, API, hub firmware

Always append to the most relevant section.
