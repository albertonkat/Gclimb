---
created: 2026-06-08
tags: [setup, hermes, config]
---

# Hermes Config — Brain Integration

Hermes config snippets for connecting to the RuVector Brain and writing memories to this vault.

## MCP connection

Run once:
```bash
hermes mcp add ruvector-brain --url http://127.0.0.1:9876/sse
```

Or add to `~/.hermes/config.yaml`:
```yaml
mcp:
  servers:
    ruvector-brain:
      url: http://127.0.0.1:9876/sse
      type: sse
      description: "Gclimb second-brain vault"
```

## Context file

Create `~/.hermes/context/gclimb.md` so Hermes knows about the project:

```markdown
# Gclimb project context

Working on: SmartThings Groovy device handlers for healthcare IoT.
Devices: vital sign monitors, glucose monitors, fall detectors, sleep trackers, medication dispensers.
Standards: HL7 FHIR, IEEE 11073, Continua Health Alliance.
Repo: https://github.com/albertonkat/Gclimb

## Second brain
My knowledge vault is at: [path to your local Obsidian vault]/second-brain/
The vault is synced to the Gclimb GitHub repo.
When you learn something relevant, write it to second-brain/00-Inbox/ following the agent memory protocol in 00-Inbox/agent-memory-protocol.md.

## Memory write path
second-brain/00-Inbox/YYYY-MM-DD-hermes-[slug].md

## Key notes to know about
- second-brain/01-Projects/gclimb - Healthcare IoT Hub.md
- second-brain/02-Areas/Healthcare-IoT/Overview.md
- second-brain/03-Resources/Z-Wave Protocol.md
- second-brain/03-Resources/Zigbee Protocol.md
```

Activate in a session:
```
/context gclimb
```

Or set as default in `~/.hermes/config.yaml`:
```yaml
context:
  default_files:
    - ~/.hermes/context/gclimb.md
```

## Skill for memory write-back

Create `~/.hermes/skills/save-to-second-brain.md`:

```markdown
---
name: save-to-second-brain
description: Save the current learning or insight as a memory in the Gclimb second-brain vault
---

Write a memory note to the second-brain following this protocol:

1. File: [vault path]/second-brain/00-Inbox/{{date}}-hermes-{{slug}}.md
2. Frontmatter: created, agent: hermes, tags: [memory, agent-generated, <topic>], confidence
3. Sections: Context, Learning, Cross-references, Source
4. Use wikilinks to existing notes where relevant
5. Search brain_search first to avoid duplicates
```

Invoke with:
```
/save-to-second-brain
```
