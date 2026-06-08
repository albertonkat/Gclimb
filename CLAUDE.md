# Gclimb — Healthcare IoT Hub

## Memory (MANDATORY — do this before anything else)

**Session start:**
1. Read `MEMORY.md` in full
2. Read the last 3 files in `second-brain/06-Sessions/` (sort by filename, most recent first)
3. If the task involves a domain topic (Z-Wave, Zigbee, FHIR, SmartThings), search the brain: `brain_search "<topic>"`

**During the session:**
When you discover something worth keeping — a device quirk, a decision, a pattern, a fact — append it to `MEMORY.md` immediately:
```
- [YYYY-MM-DD] [claude] what you learned — context
```

**Session end (mandatory):**
Write a session summary to `second-brain/06-Sessions/YYYY-MM-DD-claude-[topic-slug].md` using the template at `second-brain/05-Templates/session-capture.md`.

**Rules:**
- Never delete entries from `MEMORY.md`. It is append-only.
- Always search the brain before writing a new note — avoid duplicates.
- Both Claude and Hermes read this file. It is the single source of truth.

---

## Project

SmartThings Groovy device handlers and SmartApps for healthcare IoT devices: vital signs, glucose monitors, fall detectors, sleep trackers, medication dispensers. Targeting HL7 FHIR, IEEE 11073, and Continua Health Alliance standards.

---

## Second Brain (Obsidian vault at `second-brain/`)

### Navigation

See `second-brain/03-Resources/agent-guide.md` for the complete navigation map. Quick reference:

| What | Where |
|---|---|
| Project tasks and status | `01-Projects/gclimb - Healthcare IoT Hub.md` |
| Healthcare IoT overview | `02-Areas/Healthcare-IoT/Overview.md` |
| Z-Wave protocol reference | `03-Resources/Z-Wave Protocol.md` |
| Zigbee protocol reference | `03-Resources/Zigbee Protocol.md` |
| Z-Wave healthcare devices | `03-Resources/Z-Wave Healthcare Devices.md` |
| Zigbee healthcare devices | `03-Resources/Zigbee Healthcare Devices.md` |
| Agent session summaries | `06-Sessions/` |
| Distilled insights | `08-Insights/` |

### PARA Structure
```
second-brain/
  00-Inbox/       ← raw captures and agent memories
  01-Projects/    ← active work with a deadline
  02-Areas/       ← ongoing responsibilities
  03-Resources/   ← reference material
  04-Archive/     ← completed / paused
  05-Templates/   ← reusable note templates
  06-Daily-Notes/ ← daily captures
  06-Sessions/    ← agent session summaries (one per conversation)
  07-MOCs/        ← maps of content (index notes)
  08-Insights/    ← distilled knowledge from session clusters
```

### How to write memories back

1. **Persistent learning** → append to `MEMORY.md`
2. **Session summary** → write to `06-Sessions/YYYY-MM-DD-claude-[slug].md`
3. **New reference doc** → write to `03-Resources/[name].md`
4. **Device handler notes** → write to `02-Areas/SmartThings-Dev/`
5. **Inbox capture** → write to `00-Inbox/YYYY-MM-DD-claude-[slug].md`

Always use frontmatter:
```yaml
---
created: YYYY-MM-DD
agent: claude
tags: [memory, agent-generated, <topic>]
confidence: high
---
```

### MCP: RuVector Brain
Endpoint: `http://127.0.0.1:9876/sse` (local only — runs on the user's machine).

Tools:
- `brain_search` — semantic search across the vault
- `brain_query` — Q&A grounded in vault contents
- `brain_store` — write a memory into the brain index

Always run `brain_search` before writing a new note.

---

## Codebase layout
```
/                   ← repo root (Groovy device handlers go here, flat structure)
second-brain/       ← Obsidian knowledge vault
scripts/            ← setup and utility scripts
hermes/             ← Hermes agent config snippets
```

## Current open tasks
- [ ] Write first official SmartThings device handler (vital sign monitor or glucose monitor)
- [ ] Write first healthcare SmartApp
- [ ] Configure Artifactory secrets in GitHub repo settings

## Standards to follow
- HL7 FHIR for health data interoperability
- IEEE 11073 for personal health devices
- Continua Health Alliance guidelines
- Flat file structure (no `.src`-nested directories)
- GitHub Actions CI: compile + CodeNarc Groovy lint on every PR
