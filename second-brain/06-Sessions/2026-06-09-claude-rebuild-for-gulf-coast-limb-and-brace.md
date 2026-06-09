---
created: 2026-06-09
agent: claude
tags: [session, agent-generated, rebuild, o&p, hipaa]
---

# Session: Rebuild Second Brain for Gulf Coast Limb and Brace

## Date
2026-06-09

## Agent
claude

## Topic / Goal
Reframe the entire Gclimb repo from a fictional healthcare IoT project to the real business: Gulf Coast Limb and Brace, an O&P practice owned by Alberto Alvarez, CPO. Remove all IoT/SmartThings content and rebuild the second brain around clinical documentation, insurance billing, and software development.

## Key Decisions
- **Two-tier HIPAA architecture**: GitHub repo for de-identified templates/knowledge, local `~/GulfCoastLimb-PHI/` vault for real patient documents (SOAP notes, appeals, prior auth) — never committed
- **Claude Code only** surface for now (not Claude.ai Projects or Hermes)
- **Delete all IoT content** — it was a wrong assumption from prior sessions
- SOAP notes and appeals go to `~/GulfCoastLimb-PHI/` exclusively, even when Claude Code generates them

## Actions Taken
- Deleted all IoT/SmartThings files (15 files removed via git rm)
- Rewrote `CLAUDE.md` — full O&P context, hard PHI rules, session protocol, workflow for SOAP notes and appeals
- Rewrote `MEMORY.md` — clean slate with real business context, O&P domain basics, HIPAA rules
- Updated `README.md` — accurately describes the repo
- Created `01-Projects/Gulf Coast Limb and Brace.md` — main practice project note
- Created `02-Areas/Clinical-Practice/Overview.md` — full SOAP note structure for O&P, documentation checklist
- Created `02-Areas/Insurance-Billing/Overview.md` — billing basics, denial strategy, appeal levels, ABN rules
- Created `02-Areas/Software-Dev/Overview.md` — code projects area
- Created `02-Areas/Business-Operations/Overview.md` — practice management area
- Created `03-Resources/HCPCS L-Codes.md` — comprehensive L-code reference (prosthetics + orthotics)
- Created `03-Resources/ICD-10 O&P Codes.md` — Z89 amputee codes, neurological, orthopedic, etiology
- Created `03-Resources/Medicare LCD Reference.md` — LCD rules by device category, K-level requirements, documentation checklist
- Created `03-Resources/Insurance Payers.md` — Medicare, Medicaid, BCBS, UHC, Aetna, Cigna, VA, Tricare, WC
- Created `03-Resources/CPO Scope of Practice.md` — ABC credentials, CE, Medicare enrollment requirements
- Created `05-Templates/SOAP Note - Lower Extremity Prosthetic.md` — full BK/AK SOAP template with K-level section
- Created `05-Templates/SOAP Note - AFO Orthotic.md` — AFO/KAFO template with LCD justification section
- Created `05-Templates/SOAP Note - Upper Extremity Prosthetic.md` — BE/AE/myoelectric template
- Created `05-Templates/Insurance Appeal Letter.md` — full appeal with all levels, denial-reason responses
- Created `05-Templates/Prior Authorization.md` — prior auth request template
- Created `07-MOCs/O&P Practice MOC.md`, `Clinical Documentation MOC.md`, `Insurance Billing MOC.md`, `Software Projects MOC.md`
- Updated `07-MOCs/Resources MOC.md` and `Home.md` for O&P context
- Rebuilt `03-Resources/agent-guide.md` — PHI routing rules front and center, O&P navigation map
- Created `scripts/setup-phi-vault.sh` — initializes `~/GulfCoastLimb-PHI/` with folder structure, local gitignore, README

## Open Items
- Alberto needs to run `bash scripts/setup-phi-vault.sh` on his local machine
- First actual SOAP note or appeal letter to be written (will go to PHI vault)
- Software projects section is empty — populate as projects start
- Payer-specific learned patterns in `Insurance Payers.md` are blank — will fill from experience
- Consider adding Clinical Guidelines resource (AOPA evidence base, ABC practice standards)

## Cross-references
- [[MEMORY]]
- [[03-Resources/agent-guide]]
- [[02-Areas/Clinical-Practice/Overview]]
- [[02-Areas/Insurance-Billing/Overview]]
- [[01-Projects/Gulf Coast Limb and Brace]]
