# Gclimb — Healthcare IoT Hub

## Project
SmartThings Groovy device handlers and SmartApps for healthcare IoT devices (vital signs, glucose monitors, fall detectors, sleep trackers, medication dispensers). Targeting HL7 FHIR, IEEE 11073, and Continua Health Alliance standards.

## Second Brain (Obsidian vault at `second-brain/`)

### Structure (PARA)
```
second-brain/
  00-Inbox/       ← dump raw captures and agent memories here first
  01-Projects/    ← active work with a deadline
  02-Areas/       ← ongoing responsibilities (Healthcare-IoT, SmartThings-Dev)
  03-Resources/   ← reference material (protocols, platforms, tools)
  04-Archive/     ← completed / paused
  05-Templates/   ← reusable note templates
  06-Daily-Notes/ ← daily captures
  07-MOCs/        ← maps of content (index notes)
```

### How to read the vault
The vault is indexed by the RuVector Brain MCP server (see MCP config below).
Use the `brain_search` or `brain_query` MCP tools to find relevant notes semantically before writing new content — this avoids duplication.

### How to write memories back
When you learn something, complete a task, or want to persist knowledge:

1. **Create a file** in `second-brain/00-Inbox/` named:
   `YYYY-MM-DD-[agent]-[slug].md`
   e.g. `2026-06-08-claude-smartthings-zwave-fingerprint-notes.md`

2. **Use this frontmatter**:
   ```yaml
   ---
   created: YYYY-MM-DD
   agent: claude  # or: hermes
   tags: [memory, agent-generated, <relevant-topic>]
   project: "[[01-Projects/gclimb - Healthcare IoT Hub]]"
   ---
   ```

3. **Use wikilinks** to cross-reference existing notes:
   `[[03-Resources/Z-Wave Protocol]]`, `[[02-Areas/Healthcare-IoT/Overview]]`, etc.

4. If the content clearly belongs in a specific folder (e.g. a new resource note), write it there directly instead of the inbox.

### Existing key notes
- `[[01-Projects/gclimb - Healthcare IoT Hub]]` — project tasks and status
- `[[02-Areas/Healthcare-IoT/Overview]]` — device categories, standards
- `[[02-Areas/SmartThings-Dev/Overview]]` — active repos, recurring tasks
- `[[03-Resources/SmartThings Platform]]` — platform reference
- `[[03-Resources/Z-Wave Protocol]]` — Z-Wave reference
- `[[03-Resources/Zigbee Protocol]]` — Zigbee reference
- `[[03-Resources/ruflo.md]]` — ruflo agent orchestration platform

## MCP: RuVector Brain
The second-brain is exposed as an MCP server via the obsidian-brain plugin.
Endpoint: `http://127.0.0.1:9876/sse` (local only — runs on the user's machine).

Available tools (once connected):
- `brain_search` — semantic search across the vault
- `brain_query` — Q&A grounded in vault contents
- `brain_store` — write a memory into the brain index

**Always search the brain before writing a new note** to avoid duplicates.

## Codebase layout
```
/                   ← repo root (Groovy device handlers go here, flat structure)
second-brain/       ← Obsidian knowledge vault (this document lives here conceptually)
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
