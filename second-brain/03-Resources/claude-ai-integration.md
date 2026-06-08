---
created: 2026-06-08
tags: [setup, claude-ai, projects, memory, integration]
---

# Claude.ai Integration

How to connect Claude.ai (the web app) — including its Projects workspace, built-in memory, and conversation history — to this second brain so nothing is siloed.

---

## Overview

Claude.ai has three data layers, all of which should feed into the second brain:

| Layer | What it holds | How to sync |
|---|---|---|
| **Claude.ai Memory** | Facts Claude remembers about you across all chats | Export → merge into `MEMORY.md` |
| **Claude.ai Projects** | Project instructions + uploaded knowledge + conversation history | Upload vault files as knowledge; export sessions → `06-Sessions/` |
| **Claude.ai chat history** | All past conversations | Export data → convert → `06-Sessions/` |

---

## Part 1 — Claude.ai Memory

Claude.ai automatically remembers facts about you across conversations (when Memory is enabled).

### Export your Claude.ai memories

1. Go to **claude.ai → Settings → Memory** (or **claude.ai/settings**)
2. Click **"Manage memories"** to see what Claude currently knows about you
3. To export: **Settings → Data & Privacy → Export data** — the archive includes a `memories.json` file
4. Extract and view:
   ```bash
   # memories.json contains an array of remembered facts
   jq '.[] | "- [imported] [claude-ai-memory] \(.content)"' ~/claude-export/memories.json
   ```

### Merge into MEMORY.md

Copy the relevant entries from `memories.json` into `MEMORY.md` under the appropriate section:

```bash
# Append all memories to MEMORY.md (edit to add correct date + section)
jq -r '.[] | "- [2026-06-08] [claude-ai-memory] \(.content)"' \
  ~/claude-export/memories.json >> /path/to/Gclimb/MEMORY.md
```

Then edit `MEMORY.md` to:
- Remove duplicates (anything already captured)
- Place each entry under the right section (Project, Protocols, etc.)
- Fix the date to when the memory was created (if known)

### Ongoing: curate Claude.ai memories manually

Claude.ai memory is automatic but imprecise. Periodically:
1. Open **claude.ai → Settings → Memory → Manage memories**
2. Delete irrelevant facts, correct wrong ones
3. Re-export and re-merge any new entries you want in `MEMORY.md`

The reverse direction also matters: if you add something to `MEMORY.md`, you can tell Claude.ai directly in chat: *"Please remember: [fact]"* to write it back into claude.ai memory.

---

## Part 2 — Claude.ai Projects (the main integration)

**Projects** in claude.ai is the persistent workspace: you upload files as knowledge, write project instructions, and all conversations within the project share that context. This is the primary way to make claude.ai aware of your second brain.

### Step 1 — Create the Gclimb project

1. Go to **claude.ai → Projects → New project**
2. Name it: **Gclimb — Healthcare IoT**
3. Description: `SmartThings Groovy device handlers for healthcare IoT. Second brain at github.com/albertonkat/Gclimb/second-brain/`

### Step 2 — Write the project instructions

In **Project Settings → Instructions**, paste:

```
You are working on Gclimb, a SmartThings Groovy repo for healthcare IoT device handlers.

## Memory (read first)
The uploaded MEMORY.md is the single source of truth for everything I've learned across all sessions (Claude Code, Claude.ai, and Hermes). Read it before responding.

## At session end
Summarize what we discussed and any key decisions or learnings. I will copy this into my second brain.

## Second brain structure
The vault uses PARA: 00-Inbox, 01-Projects, 02-Areas, 03-Resources, 04-Archive, 05-Templates, 06-Sessions, 07-MOCs, 08-Insights.

Key notes (uploaded):
- MEMORY.md — persistent memory
- agent-guide.md — navigation map
- Healthcare IoT MOC — all healthcare context
- Z-Wave Healthcare Devices — device fingerprints and CC reference
- Zigbee Healthcare Devices — cluster IDs and profile reference

## Domain context
- Target standards: HL7 FHIR, IEEE 11073, Continua Health Alliance
- Radio protocols: Z-Wave (908.42 MHz) and Zigbee (2.4 GHz, profile 0x0104)
- Device handlers are flat .groovy files in the repo root
- GitHub Actions CI: compile + CodeNarc lint on every PR

## When I ask a domain question
Search your uploaded knowledge before answering. If something is in MEMORY.md or the uploaded notes, ground your answer there.
```

### Step 3 — Upload knowledge files

Upload these files from your local Gclimb repo to the Project:

**Core context (upload every time they change):**
- `MEMORY.md` — the shared memory
- `CLAUDE.md` — project instructions and structure
- `second-brain/03-Resources/agent-guide.md` — navigation map

**Reference material (upload once, refresh when updated):**
- `second-brain/07-MOCs/Healthcare IoT MOC.md`
- `second-brain/03-Resources/Z-Wave Healthcare Devices.md`
- `second-brain/03-Resources/Zigbee Healthcare Devices.md`
- `second-brain/03-Resources/Z-Wave Protocol.md`
- `second-brain/03-Resources/Zigbee Protocol.md`
- `second-brain/02-Areas/Healthcare-IoT/Overview.md`
- `second-brain/01-Projects/gclimb - Healthcare IoT Hub.md`

**Session context (upload the last 3–5 sessions before starting work):**
- Latest files from `second-brain/06-Sessions/`

To upload: open the Project → click the **paperclip / attachment icon** → select files.

### Step 4 — Use the project for all Gclimb conversations

Instead of starting a new chat on claude.ai, always open **Projects → Gclimb** before starting a Gclimb conversation. This ensures every message has access to the uploaded knowledge.

### Step 5 — Export session back to the vault

At the end of every Claude.ai Projects session:

1. Ask Claude: *"Write a session summary using this format:"*
   ```
   ## Date: YYYY-MM-DD
   ## Topic: [topic]
   ## Key Decisions: ...
   ## Learnings: ...
   ## Actions Taken: ...
   ## Open Items: ...
   ```
2. Copy the summary into a new file:
   `second-brain/06-Sessions/YYYY-MM-DD-claude-ai-[topic].md`
3. Add the frontmatter:
   ```yaml
   ---
   created: YYYY-MM-DD
   agent: claude
   tags: [session, agent-generated, claude-ai]
   ---
   ```
4. Append key learnings to `MEMORY.md`
5. Git commit and push so Claude Code and Hermes see the updates

---

## Part 3 — Keeping the Project knowledge current

The Project's uploaded files go stale as the vault evolves. Refresh them on a schedule:

| Trigger | Action |
|---|---|
| After any session that changes MEMORY.md | Re-upload `MEMORY.md` to the Project |
| After writing a new session note | Upload the new session file to the Project |
| Weekly | Re-upload `agent-guide.md` and the Healthcare IoT MOC |
| Monthly | Re-upload all reference files |

**Quick re-upload script:**
```bash
#!/bin/bash
# Run this from your Gclimb repo root after sessions to prep files for re-upload
VAULT=./second-brain
echo "Files to re-upload to Claude.ai Projects:"
echo "  MEMORY.md"
echo "  CLAUDE.md"
echo "  $VAULT/03-Resources/agent-guide.md"
echo ""
echo "Latest session notes:"
ls -t $VAULT/06-Sessions/*.md | head -5
```

---

## Part 4 — Full data export (one-time historical import)

To pull all past Claude.ai conversations into the vault:

1. **claude.ai → Settings → Data & Privacy → Export data**
2. Request the export — you'll get an email with a download link within a few minutes
3. Extract the archive. You'll find:
   - `conversations/` — JSON files, one per chat
   - `memories.json` — your saved memories
   - `account.json` — account metadata
4. Convert conversations to markdown:
   ```bash
   mkdir -p /path/to/Gclimb/second-brain/06-Sessions/claude-ai-import/
   for f in ~/claude-export/conversations/*.json; do
     title=$(jq -r '.name // "untitled"' "$f")
     date=$(jq -r '.created_at // "2026-01-01"' "$f" | cut -c1-10)
     slug=$(echo "$title" | tr '[:upper:] ' '[:lower:]-' | tr -cd 'a-z0-9-' | cut -c1-40)
     outfile="/path/to/Gclimb/second-brain/06-Sessions/claude-ai-import/${date}-claude-ai-${slug}.md"
     {
       echo "---"
       echo "created: $date"
       echo "agent: claude"
       echo "tags: [session, imported, claude-ai]"
       echo "imported: true"
       echo "---"
       echo ""
       echo "# $title"
       echo ""
       jq -r '.chat_messages[] | "**\(.sender):** \(.text)\n"' "$f" 2>/dev/null || \
       jq -r '.messages[] | "**\(.role):** \(.content[0].text // .content // "")\n"' "$f" 2>/dev/null
     } > "$outfile"
   done
   ```
5. Run **Brain: Bulk-sync vault → brain** in Obsidian to index everything

---

## The complete bidirectional flow

```
claude.ai Projects
   │  ↑ Upload: MEMORY.md, key notes, recent sessions
   │  ↓ Export: session summaries → 06-Sessions/
   │
   ├── Claude.ai Memory ──→ export memories.json → merge into MEMORY.md
   │
   └── Chat history ──→ export data → convert → 06-Sessions/claude-ai-import/

Claude Code (this tool)
   ↓ Reads: MEMORY.md + 06-Sessions/ at session start
   ↓ Writes: session summary → 06-Sessions/, learnings → MEMORY.md

Hermes
   ↓ Reads: MEMORY.md (shared file), brain_search via MCP
   ↓ Writes: session summary → 06-Sessions/, learnings → MEMORY.md

All three agents → MEMORY.md (single source of truth)
All three agents → 06-Sessions/ (session history)
obsidian-brain MCP ← indexes everything → semantic search for all agents
```

---

## Cross-references
- [[03-Resources/agent-guide]] — where everything lives in the vault
- [[03-Resources/hermes-config]] — Hermes memory + MCP setup
- [[03-Resources/brain-integration-setup]] — obsidian-brain MCP setup
- [[03-Resources/past-data-import]] — historical import commands
- [[00-Inbox/agent-memory-protocol]] — naming and frontmatter rules
