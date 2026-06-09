# Gulf Coast Limb and Brace — Claude Code Config

**Practice:** Gulf Coast Limb and Brace  
**Owner/CPO:** Alberto Alvarez, CPO  
**Domain:** Orthotics and Prosthetics (O&P)

---

## Memory (MANDATORY — do this before anything else)

**Session start:**
1. Read `MEMORY.md` in full
2. Read the last 3 files in `second-brain/06-Sessions/` (sort by filename, most recent first)
3. If the task involves a clinical or billing topic, search the brain: `brain_search "<topic>"`

**During the session:**
When you learn something worth keeping — a payer rule, a denial pattern, a code pairing, a clinical guideline, a code pattern — append it to `MEMORY.md` immediately:
```
- [YYYY-MM-DD] [claude] what you learned — context
```

**Session end (mandatory):**
Write a de-identified session summary to `second-brain/06-Sessions/YYYY-MM-DD-claude-[topic-slug].md` using `second-brain/05-Templates/session-capture.md`.

**Rules:**
- Never delete entries from `MEMORY.md`. It is append-only.
- Search the brain before writing a new note — avoid duplicates.
- `MEMORY.md` is the single source of truth for persistent knowledge.

---

## PHI Rule — HARD STOP

**SOAP notes, appeal letters, prior auth requests, and anything with patient names, DOB, insurance IDs, or diagnosis tied to a specific person is PHI.**

- **NEVER write PHI to this repo** (`/home/user/Gclimb/` or anywhere under it)
- **NEVER commit PHI to git**
- PHI files go to the **local PHI vault only**: `~/GulfCoastLimb-PHI/`
- What CAN go in this repo: de-identified templates, payer rules, code patterns, clinical guidelines, learning summaries with no patient identifiers

When writing a SOAP note or appeal letter:
1. Use the template from `second-brain/05-Templates/`
2. Write the real (PHI) document to `~/GulfCoastLimb-PHI/soap-notes/` or `~/GulfCoastLimb-PHI/appeals/`
3. Append only de-identified learnings to `MEMORY.md`
   - OK: `"Medicare denied K3 microprocessor knee for diabetic amputee without physiatry note — added letter template"`
   - NOT OK: `"Medicare denied K3 knee for patient John Smith DOB 1952"`

Run `scripts/setup-phi-vault.sh` once to initialize the local PHI vault structure.

---

## About the Practice

Gulf Coast Limb and Brace provides custom orthotics and prosthetics. Alberto Alvarez is a Certified Prosthetist Orthotist (CPO) credentialed by ABC (American Board for Certification in Orthotics, Prosthetics and Pedorthics).

**Primary work types:**
1. **Clinical documentation** — SOAP notes, progress notes, delivery receipts
2. **Insurance** — prior authorization requests, appeal letters, Medicare LCD compliance
3. **Software projects** — tools Alberto builds for the practice or the O&P field

---

## Second Brain (Obsidian vault at `second-brain/`)

### Navigation

See `second-brain/03-Resources/agent-guide.md` for the complete map. Quick reference:

| What | Where |
|---|---|
| Practice project + open tasks | `01-Projects/Gulf Coast Limb and Brace.md` |
| Clinical documentation standards | `02-Areas/Clinical-Practice/Overview.md` |
| Insurance + billing knowledge | `02-Areas/Insurance-Billing/Overview.md` |
| Software projects | `02-Areas/Software-Dev/Overview.md` |
| HCPCS L-code reference | `03-Resources/HCPCS L-Codes.md` |
| ICD-10 O&P diagnosis codes | `03-Resources/ICD-10 O&P Codes.md` |
| Medicare LCD reference | `03-Resources/Medicare LCD Reference.md` |
| Payer contacts + denial patterns | `03-Resources/Insurance Payers.md` |
| CPO scope and credentials | `03-Resources/CPO Scope of Practice.md` |
| Agent session summaries | `06-Sessions/` |
| Distilled insights | `08-Insights/` |

### PARA Structure
```
second-brain/
  00-Inbox/           ← raw captures and agent notes
  01-Projects/        ← active work with a deadline
  02-Areas/           ← ongoing responsibilities
  03-Resources/       ← reference material (codes, payers, guidelines)
  04-Archive/         ← completed / paused
  05-Templates/       ← SOAP notes, appeal letters, prior auth
  06-Daily-Notes/     ← daily captures
  06-Sessions/        ← agent session summaries (one per conversation)
  07-MOCs/            ← maps of content (index notes)
  08-Insights/        ← distilled knowledge from session clusters
```

### How to write memories back

1. **Persistent learning (de-identified)** → append to `MEMORY.md`
2. **Session summary** → write to `06-Sessions/YYYY-MM-DD-claude-[slug].md`
3. **New reference doc** → write to `03-Resources/[name].md`
4. **Clinical or billing area update** → write to `02-Areas/`
5. **PHI documents** → write to `~/GulfCoastLimb-PHI/` ONLY

Always use frontmatter:
```yaml
---
created: YYYY-MM-DD
agent: claude
tags: [memory, agent-generated, <topic>]
confidence: high
---
```

### MCP: RuVector Brain
Endpoint: `http://127.0.0.1:9876/sse` (local only — runs on Alberto's machine).

Tools:
- `brain_search` — semantic search across the vault
- `brain_query` — Q&A grounded in vault contents
- `brain_store` — write a memory into the brain index

Always run `brain_search` before writing a new note.

---

## Working on SOAP Notes

1. Ask for: patient presentation, diagnosis, visit type, device
2. Use template: `second-brain/05-Templates/SOAP Note - [type].md`
3. Write completed note to: `~/GulfCoastLimb-PHI/soap-notes/YYYY-MM-DD-[patientID]-[visit].md`
4. Append to MEMORY.md: any reusable clinical language or billing insight (no PHI)

## Working on Insurance Appeals

1. Ask for: payer, denied code(s), denial reason, clinical context (de-identified as needed)
2. Reference: `03-Resources/Insurance Payers.md`, `03-Resources/Medicare LCD Reference.md`
3. Use template: `second-brain/05-Templates/Insurance Appeal Letter.md`
4. Write completed letter to: `~/GulfCoastLimb-PHI/appeals/YYYY-MM-DD-[patientID]-[payer]-[code].md`
5. Append to MEMORY.md: payer rule learned, argument that worked/failed (no PHI)

## Working on Code Projects

1. Track project in: `01-Projects/[project-name].md`
2. Store code in repo root or a named subdirectory
3. Append learnings and decisions to MEMORY.md
4. Write session summary to `06-Sessions/` at end

---

## Standards
- HCPCS Level II L-codes for O&P billing
- ICD-10-CM diagnosis coding
- Medicare LCD compliance (see `03-Resources/Medicare LCD Reference.md`)
- HIPAA minimum necessary standard for PHI handling
- ABC credentialing standards (CPO, CO, CP)
