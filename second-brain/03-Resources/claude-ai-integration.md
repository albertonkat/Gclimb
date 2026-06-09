---
created: 2026-06-09
tags: [setup, claude-ai, projects, memory, integration]
---

# Claude.ai Projects Integration

How to connect Claude.ai Projects (the web app) to this second brain so both surfaces share the same memory and knowledge.

---

## What You Can and Cannot Share

| Content | Claude Code | Claude.ai Projects |
|---|---|---|
| `MEMORY.md` | Auto-read every session | Upload manually as knowledge |
| Reference files (L-codes, ICD-10, LCD, payers) | Auto-read via brain_search | Upload manually as knowledge |
| Session summaries (`06-Sessions/`) | Auto-read | Upload latest files manually |
| SOAP notes, appeal letters (PHI) | Read/write to `~/GulfCoastLimb-PHI/` | **NEVER** — no HIPAA BAA |
| Templates (`05-Templates/`) | Direct access | Upload as knowledge (de-identified templates only) |

**HIPAA note:** Standard claude.ai does not have a HIPAA Business Associate Agreement (BAA). Do not upload, paste, or describe any patient-identifiable data in claude.ai Projects. Only de-identified content: `MEMORY.md`, reference files, blank templates.

---

## Step 1 — Create the Project

1. Go to **claude.ai → Projects → New project**
2. Name: **Gulf Coast Limb and Brace**
3. Description: `O&P practice knowledge system for Alberto Alvarez, CPO`

---

## Step 2 — Write the Project Instructions

In **Project Settings → Instructions**, paste the following (edit your NPI and address):

```
You are working with Alberto Alvarez, CPO, at Gulf Coast Limb and Brace, an orthotics and prosthetics practice.

## Before every response
Read the uploaded MEMORY.md in full — it is the shared persistent memory across all sessions. The reference files (HCPCS L-Codes, ICD-10 codes, Medicare LCD, Insurance Payers) are your primary clinical and billing references.

## PHI Rule — HARD STOP
This is a standard claude.ai session with no HIPAA protection.
- NEVER ask for or work with patient names, DOBs, insurance IDs, or any patient-identifiable data
- Work only with de-identified scenarios: "a K3 BK amputee with diabetes" — not a specific patient
- If I accidentally share PHI, stop and ask me to re-state without identifiers
- Real SOAP notes and appeal letters are written in Claude Code, saved locally — not here

## What this session is for
- Drafting and reviewing de-identified clinical documentation language
- Answering billing/coding questions using the reference files
- Planning appeal strategies (de-identified)
- Working on software projects
- Reviewing and improving templates

## Session end
At the end of our session, summarize:
- Topic covered
- Key decisions or learnings
- Any payer rules or clinical patterns discovered (de-identified)
I will copy this into the second brain.

## Domain context
- Primary billing: HCPCS Level II L-codes (L0100–L7499)
- Primary diagnosis coding: ICD-10-CM
- Dominant payer: Medicare Part B DMEPOS; LCDs govern coverage
- K-level classification is required for all lower limb prosthetics
- Standards: ABC credentialing (CPO), Medicare LCD compliance, HIPAA
```

---

## Step 3 — Upload Knowledge Files

Upload these files to the Project. They are all de-identified and safe for claude.ai.

**Upload every time they change (keep current):**
- `MEMORY.md` — the shared memory
- `CLAUDE.md` — session protocol and project context

**Upload once (update monthly or when content changes):**
- `second-brain/03-Resources/HCPCS L-Codes.md`
- `second-brain/03-Resources/ICD-10 O&P Codes.md`
- `second-brain/03-Resources/Medicare LCD Reference.md`
- `second-brain/03-Resources/Insurance Payers.md`
- `second-brain/03-Resources/CPO Scope of Practice.md`
- `second-brain/02-Areas/Clinical-Practice/Overview.md`
- `second-brain/02-Areas/Insurance-Billing/Overview.md`

**Upload before starting work on a topic (context boost):**
- Relevant files from `second-brain/06-Sessions/` (last 3–5 sessions)
- Relevant MOC: `07-MOCs/O&P Practice MOC.md`, `07-MOCs/Insurance Billing MOC.md`

**Templates (de-identified — blank, no patient data):**
- `second-brain/05-Templates/Insurance Appeal Letter.md`
- `second-brain/05-Templates/Prior Authorization.md`

**DO NOT UPLOAD (PHI / not safe for standard claude.ai):**
- Anything from `~/GulfCoastLimb-PHI/`
- Any file with real patient data

---

## Step 4 — Use the Project for All O&P Work

Instead of starting a new chat on claude.ai, always open **Projects → Gulf Coast Limb and Brace** first. Every conversation in the project has access to the uploaded knowledge.

Use claude.ai Projects for:
- Drafting appeal letter language (de-identified, then fill in patient details in Claude Code)
- Answering coding questions (HCPCS, ICD-10, LCD rules)
- Planning prior auth strategies
- Working on software projects
- Reviewing templates and improving language

Use Claude Code for:
- Writing actual SOAP notes and appeals with real patient data (saved to `~/GulfCoastLimb-PHI/`)
- Any task that requires reading/writing files in the repo

---

## Step 5 — Write-back After Each Projects Session

Claude.ai Projects cannot write to your files automatically. At the end of each session:

1. Ask Claude: *"Write a session summary with: date, topic, key decisions, clinical/billing patterns learned (de-identified), open items."*
2. Create a new file in the repo:
   `second-brain/06-Sessions/YYYY-MM-DD-claude-ai-[topic].md`
3. Add frontmatter:
   ```yaml
   ---
   created: YYYY-MM-DD
   agent: claude
   tags: [session, agent-generated, claude-ai]
   ---
   ```
4. Append key learnings to `MEMORY.md`
5. Git commit and push so Claude Code sees the update next session

---

## Keeping the Project Current

| When | Action |
|---|---|
| After Claude Code session that updates `MEMORY.md` | Re-upload `MEMORY.md` to the Project |
| After writing new session notes | Upload new files from `06-Sessions/` |
| Monthly | Re-upload all reference files |
| When you add a new resource note | Upload it to the Project |

---

## Quick Upload Script

Run this to see which files to re-upload (does not upload automatically — you do that in the browser):

```bash
#!/bin/bash
# Show files to re-upload to claude.ai Projects
REPO=/path/to/Gclimb
echo "=== Always re-upload (may have changed) ==="
echo "  $REPO/MEMORY.md"
echo "  $REPO/CLAUDE.md"
echo ""
echo "=== Recent sessions to upload ==="
ls -t $REPO/second-brain/06-Sessions/*.md | grep -v README | head -5
echo ""
echo "=== Reference files (upload monthly) ==="
ls $REPO/second-brain/03-Resources/*.md | grep -v agent-guide | grep -v claude-ai | grep -v past-data
```

---

## How the Full Memory Loop Works

```
Claude Code session
  → reads MEMORY.md + 06-Sessions/ at start
  → writes SOAP note → ~/GulfCoastLimb-PHI/ (PHI vault, not synced)
  → appends learning → MEMORY.md (de-identified)
  → writes session summary → 06-Sessions/
  → git push

You re-upload MEMORY.md to claude.ai Projects
  ↓
Claude.ai Projects session
  → reads uploaded MEMORY.md at start (same knowledge)
  → works on de-identified content only
  → produces session summary at end

You copy session summary → 06-Sessions/ → git commit
  ↓
Claude Code reads it next session — loop complete
```

---

## Cross-references
- [[03-Resources/agent-guide]] — PHI rules and navigation map
- [[03-Resources/past-data-import]] — import historical claude.ai chat history
- [[MEMORY]] — the shared memory file
