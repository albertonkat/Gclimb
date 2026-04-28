# Gclimb — Claude Code Guide

## What This Repo Is
A monorepo containing two things: the SmartThings + Healthcare IoT codebase, and a personal knowledge management vault (Obsidian/PARA) under `second-brain/`. Both are tracked here intentionally — `albertonkat/Second-brain` on GitHub is archived and no longer used. Single source of truth is this repo.

## Directory Structure

```
Gclimb/
├── second-brain/          # Obsidian vault (PARA method)
│   ├── 00-Inbox/          # Raw captures, process and move out
│   ├── 01-Projects/       # Active work with a deadline
│   ├── 02-Areas/          # Ongoing responsibilities (Healthcare-IoT, SmartThings-Dev)
│   ├── 03-Resources/      # Reference material (protocols, platforms)
│   ├── 05-Templates/      # Note templates — don't modify without reason
│   ├── 07-MOCs/           # Maps of Content — index/overview notes
│   └── Home.md            # Vault dashboard
└── README.md
```

## Second-Brain Conventions

**PARA structure:**
- `00-Inbox` — dump zone, always process items out (move to Projects/Areas/Resources)
- `01-Projects` — one note per project, uses `Project.md` template
- `02-Areas` — one subfolder per area of responsibility
- `03-Resources` — reference docs, protocol notes, platform docs
- `07-MOCs` — never add granular content here, only links/overviews

**Naming:** `Title Case.md` for all notes. Subfolder names use `PascalCase` (e.g. `Healthcare-IoT`).

**Frontmatter:** Every note should have `tags` and `created` (YYYY-MM-DD). Projects also need `status: active | paused | done`.

**Wikilinks:** Use `[[Note Name]]` format for internal links. Always link to MOCs when referencing a domain.

## Templates (in `05-Templates/`)

| Template | Use For |
|---|---|
| `Project.md` | New projects in `01-Projects/` |
| `Daily Note.md` | Daily entries in `06-Daily-Notes/` (not yet created) |
| `Meeting Note.md` | Meeting summaries |
| `Fleeting Note.md` | Quick captures before processing |
| `Healthcare Device.md` | New IoT device docs |
| `MOC.md` | New maps of content |

## Active Focus Areas

- **Healthcare IoT** — SmartThings device handlers for healthcare devices (Z-Wave, Zigbee). See `02-Areas/Healthcare-IoT/` and `07-MOCs/Healthcare IoT MOC.md`.
- **SmartThings Dev** — Platform integration, Groovy device handlers, SmartApps. See `02-Areas/SmartThings-Dev/`.

## Git Workflow

- **Branch:** Always develop on a feature branch (e.g. `claude/task-name-shortid`)
- **Commits:** Short imperative subject line, no period. Body optional.
- **Push:** Always push before session ends — stop hook enforces this.
- **Never force-push** to `main`/`master`.

## Common Tasks

**Add a new note:** Create in the correct PARA folder, apply the relevant template frontmatter, add a wikilink from the relevant MOC.

**Add a new project:** Create `01-Projects/<Project Name>.md` using the Project template, then link from `07-MOCs/Projects MOC.md`.

**Process inbox:** Move each item from `00-Inbox/` to its correct PARA destination, delete or archive the original inbox entry.

## What Not to Do

- Don't add files directly to vault root (except `Home.md`)
- Don't modify template files unless changing the template schema itself
- Don't create new top-level folders in the vault without updating `Home.md` and the relevant MOC
