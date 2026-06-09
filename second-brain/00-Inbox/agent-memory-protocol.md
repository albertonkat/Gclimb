---
created: 2026-06-08
tags: [protocol, agent-memory, meta]
---

# Agent Memory Protocol

Rules for how Claude (ruflo) and Hermes write memories into this vault.

## File naming
```
second-brain/00-Inbox/YYYY-MM-DD-[agent]-[slug].md
```
Examples:
- `2026-06-08-claude-zwave-fingerprint-discovery.md`
- `2026-06-08-hermes-fhir-r4-resource-mapping.md`

## Required frontmatter
```yaml
---
created: YYYY-MM-DD
agent: claude        # or: hermes
tags: [memory, agent-generated, <topic>]
confidence: high     # or: medium | low
---
```

## Body structure
```markdown
## Context
What triggered this memory (task, question, discovery).

## Learning
The actual knowledge to persist.

## Cross-references
[[03-Resources/relevant-note]], [[01-Projects/gclimb - Healthcare IoT Hub]]

## Source
URL, file, or conversation that produced this.
```

## Where to write
| Content type | Destination |
|---|---|
| Unsorted / uncertain | `00-Inbox/` |
| Project update or task change | `01-Projects/gclimb - Healthcare IoT Hub.md` (edit in place) |
| New reference doc (protocol, tool) | `03-Resources/[name].md` |
| Device handler notes | `02-Areas/SmartThings-Dev/` |
| Healthcare domain notes | `02-Areas/Healthcare-IoT/` |

## Before writing — always search first
Use `brain_search` to check if a note already covers the topic.
Only create a new note if nothing close exists.

## Read-back rule
After writing a memory, confirm the file exists and frontmatter parses correctly.
