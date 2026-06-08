# Shared Memory

> Append-only. Never delete entries. Both Claude and Hermes read this at session start and write here when something is worth remembering.

## Format
```
- [YYYY-MM-DD] [agent] learning or fact — source/context
```

---

## Project
- [2026-06-08] [claude] Gclimb is a SmartThings Groovy repo for healthcare IoT device handlers — vital signs, glucose, fall detectors, sleep trackers, medication dispensers — HL7 FHIR / IEEE 11073 / Continua standards
- [2026-06-08] [claude] Repo has GitHub Actions CI + CodeNarc Groovy linting already set up; flat file structure (no .src nesting)
- [2026-06-08] [claude] Open tasks: first official device handler, first healthcare SmartApp, Artifactory secrets in GitHub settings
- [2026-06-08] [claude] Existing older repo: albertonkat/SmartThingsPublic — Gclimb is the improved replacement

## Agent Stack
- [2026-06-08] [claude] User runs Hermes (NousResearch/hermes-agent, 185k stars) as their primary agent alongside Claude/ruflo
- [2026-06-08] [claude] Ruflo (ruvnet/ruflo) is the Claude Code agent orchestration harness — multi-agent swarms, HNSW memory, IoT plugin (requires Cognitum Seed hardware)
- [2026-06-08] [claude] Hermes stores its own memory in ~/.hermes/MEMORY.md by default — this file replaces that for shared memory
- [2026-06-08] [claude] Claude.ai Projects (web app) should be set up with MEMORY.md + key vault files uploaded as knowledge; session summaries exported back to 06-Sessions/
- [2026-06-08] [claude] Claude.ai Memory (built-in auto-memory) can be exported via Settings → Data & Privacy → Export data → memories.json and merged into this file

## Second Brain
- [2026-06-08] [claude] Obsidian vault lives at second-brain/ in this repo — PARA structure (Inbox, Projects, Areas, Resources, Archive, Templates, MOCs)
- [2026-06-08] [claude] Key notes: gclimb Healthcare IoT Hub (project), Healthcare-IoT Overview (areas), SmartThings Platform / Z-Wave / Zigbee (resources)

## Protocols & Standards
<!-- Add learnings about HL7 FHIR, IEEE 11073, Z-Wave, Zigbee, SmartThings as they're discovered -->

## Device Handlers
<!-- Add learnings about specific devices, fingerprints, capabilities as they're discovered -->

## SmartThings Platform
<!-- Add learnings about Groovy DSL, SmartThings APIs, hub firmware quirks as discovered -->
