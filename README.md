# Gulf Coast Limb and Brace — Knowledge System

Alberto Alvarez, CPO | Gulf Coast Limb and Brace

This repository is the second brain and code workspace for the practice. It contains:

- **`second-brain/`** — Obsidian vault (PARA structure): clinical reference, billing knowledge, templates, agent session summaries
- **`MEMORY.md`** — Shared persistent memory for Claude; append-only, de-identified
- **`CLAUDE.md`** — Claude Code configuration and session protocol
- **`scripts/`** — Utility scripts (PHI vault setup, etc.)

## PHI Notice

This repository contains **no patient data**. All PHI (SOAP notes, appeal letters, patient records) lives in a local-only vault at `~/GulfCoastLimb-PHI/` that is never committed or pushed.

## Getting started

```bash
# Initialize your local PHI vault (run once on each machine)
bash scripts/setup-phi-vault.sh
```
