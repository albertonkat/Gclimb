---
created: 2026-06-08
agent: claude
tags: [session, agent-generated, second-brain, setup, ruflo, hermes]
---

# Session: Second Brain as Single Source of Truth

## Date
2026-06-08

## Agent
claude

## Topic / Goal
Make the Obsidian second brain (at `second-brain/` in the Gclimb repo) the single source of truth for all data — all agent sessions, past chats, business knowledge, and learnings — so both Claude (ruflo) and Hermes can read from it and write back to it, and nothing is ever forgotten.

## Key Decisions
- `MEMORY.md` in repo root is the shared append-only memory file for both Claude and Hermes (neutral format both agents already understand)
- Session summaries go into `06-Sessions/` (one file per conversation, named `YYYY-MM-DD-[agent]-[topic].md`)
- Distilled insights go into `08-Insights/` (created when 3+ sessions cover the same topic)
- obsidian-brain MCP server at `127.0.0.1:9876/sse` adds semantic search on top of raw file access
- Hermes connects to the same vault via `hermes config set memory.file` + `hermes mcp add ruvector-brain`
- ruflo-iot-cognitum IoT plugin requires Cognitum Seed hardware — NOT compatible with SmartThings/Z-Wave/Zigbee; user continues using SmartThings directly

## Learnings
- Ruflo (ruvnet/ruflo, 58k stars) and Hermes (NousResearch/hermes-agent, 185k stars) use incompatible memory systems by default; MEMORY.md is the bridge
- Hermes stores session history locally with FTS5 full-text search; `hermes insights --days 365` exports it
- obsidian-brain plugin (ruvnet/obsidian-brain) indexes vault notes as semantic vectors at `127.0.0.1:9876/sse`
- The Healthcare IoT MOC had two broken wikilinks: Z-Wave Healthcare Devices and Zigbee Healthcare Devices (now fixed)
- Vault was missing `04-Archive/`, `06-Daily-Notes/`, `06-Sessions/`, and `08-Insights/` folders (now created)

## Actions Taken
- Created `MEMORY.md` — shared persistent memory (repo root)
- Created/updated `CLAUDE.md` — mandatory session read/write rules, navigation table, session end requirement
- Created `second-brain/03-Resources/ruflo.md` — ruflo agent reference
- Created `second-brain/00-Inbox/agent-memory-protocol.md` — naming/frontmatter rules
- Created `second-brain/05-Templates/agent-memory.md` — template for agent memory notes
- Created `second-brain/05-Templates/session-capture.md` — template for session summaries
- Created `second-brain/05-Templates/insight.md` — template for distilled insights
- Created `second-brain/03-Resources/brain-integration-setup.md` — full MCP + obsidian-brain + Hermes setup guide
- Created `second-brain/03-Resources/hermes-config.md` — Hermes memory config + shared MEMORY.md
- Created `second-brain/03-Resources/agent-guide.md` — master navigation map for all agents
- Created `second-brain/03-Resources/past-data-import.md` — commands for importing Hermes + Claude.ai history
- Created `second-brain/03-Resources/Z-Wave Healthcare Devices.md` — fixed broken wikilink
- Created `second-brain/03-Resources/Zigbee Healthcare Devices.md` — fixed broken wikilink
- Created `second-brain/04-Archive/.gitkeep`, `06-Daily-Notes/.gitkeep`, `06-Sessions/README.md`, `08-Insights/README.md`
- Updated `second-brain/07-MOCs/Healthcare IoT MOC.md` — filled Open Questions, added Sessions link
- Updated `second-brain/07-MOCs/Resources MOC.md` — added Sessions, Insights, Agent Infrastructure sections
- Updated `second-brain/Home.md` — added Agent Memory panel with Sessions, Insights, Agent Guide

## Open Items
- User needs to locally run: `hermes config set memory.file /path/to/Gclimb/MEMORY.md`
- User needs to locally run: `hermes mcp add ruvector-brain --url http://127.0.0.1:9876/sse`
- User needs to install obsidian-brain plugin in Obsidian and run "Brain: Bulk-sync vault → brain"
- User needs to install Obsidian Git plugin (auto-pull 5 min, auto-push on commit)
- User needs to import past Hermes sessions: `hermes insights --days 365` → `06-Sessions/hermes-history-import.md`
- User needs to export Claude.ai chats from claude.ai → Settings → Data & Privacy
- `.claude/settings.json` with MCP endpoint config needs to be created by user locally (permission denied in this session)
- First device handler still open: vital sign monitor or glucose monitor

## Cross-references
- [[MEMORY]]
- [[03-Resources/agent-guide]]
- [[03-Resources/brain-integration-setup]]
- [[03-Resources/hermes-config]]
- [[03-Resources/past-data-import]]
- [[01-Projects/gclimb - Healthcare IoT Hub]]
