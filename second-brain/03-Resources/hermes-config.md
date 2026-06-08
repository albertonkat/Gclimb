---
created: 2026-06-08
tags: [setup, hermes, config, memory]
---

# Hermes Config — Shared Memory

Point Hermes at the shared `MEMORY.md` so it reads and writes the same memory as Claude/ruflo.

## Step 1 — Set memory file path

In `~/.hermes/config.yaml`, add:
```yaml
memory:
  file: /path/to/your/Gclimb/MEMORY.md
```

Replace `/path/to/your/Gclimb/` with the actual path where you cloned the repo.

Or set via CLI:
```bash
hermes config set memory.file /path/to/your/Gclimb/MEMORY.md
```

## Step 2 — Create a context file for the project

Create `~/.hermes/context/gclimb.md`:
```markdown
# Gclimb context

SmartThings Groovy device handlers for healthcare IoT.
Repo: /path/to/your/Gclimb/

## Memory (MANDATORY)
At the start of every session, read MEMORY.md at the repo root in full.
When you learn something new, append it immediately:
  - [YYYY-MM-DD] [hermes] what you learned — context
Never delete entries. This file is shared with Claude — it is the single source of truth.

## Second brain
Obsidian vault is at: /path/to/your/Gclimb/second-brain/
PARA structure: 00-Inbox, 01-Projects, 02-Areas, 03-Resources, 04-Archive

## Key notes
- second-brain/01-Projects/gclimb - Healthcare IoT Hub.md
- second-brain/02-Areas/Healthcare-IoT/Overview.md
- second-brain/03-Resources/Z-Wave Protocol.md
- second-brain/03-Resources/Zigbee Protocol.md
```

Activate in a session:
```bash
hermes
/context gclimb
```

Or set as default so it loads every time:
```yaml
context:
  default_files:
    - ~/.hermes/context/gclimb.md
```

## Step 3 — Create a save-memory skill

Create `~/.hermes/skills/remember.md`:
```markdown
---
name: remember
description: Append a new learning to the shared MEMORY.md
---

Append this to /path/to/your/Gclimb/MEMORY.md:
- [{{date}}] [hermes] {{learning}} — {{context}}

Read the file first to avoid duplicating something already there.
```

Use it during a session:
```
/remember Z-Wave fingerprint format uses 0x0104 for HA profile — discovered while writing device handler
```

## How it works with Claude

Both agents read the same `MEMORY.md` file. When Hermes learns something and appends it, Claude sees it on the next session start (because CLAUDE.md instructs Claude to read MEMORY.md first). Vice versa.

Nothing is lost between sessions. Nothing is siloed per agent.
