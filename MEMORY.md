# Shared Memory — Gulf Coast Limb and Brace

> Append-only. Never delete entries. Claude reads this at every session start and writes here when something is worth remembering. De-identified only — no patient names, DOBs, or identifiers ever go here.

## Format
```
- [YYYY-MM-DD] [agent] learning or fact — source/context
```

---

## Practice
- [2026-06-09] [claude] Gulf Coast Limb and Brace is an orthotics and prosthetics (O&P) practice owned by Alberto Alvarez, CPO
- [2026-06-09] [claude] Alberto is credentialed CPO by ABC (American Board for Certification in Orthotics, Prosthetics and Pedorthics)
- [2026-06-09] [claude] Primary work: SOAP notes, insurance appeals/prior auth, and software projects for the practice
- [2026-06-09] [claude] Gclimb repo = Gulf Coast Limb and Brace knowledge system — second brain + code projects, no PHI ever committed

## PHI & Compliance
- [2026-06-09] [claude] PHI rule: all patient-identifiable documents go to ~/GulfCoastLimb-PHI/ (local-only, never committed); only de-identified knowledge goes in this repo
- [2026-06-09] [claude] Two-tier architecture: GitHub repo = templates/knowledge/code; local PHI vault = real patient documents
- [2026-06-09] [claude] HIPAA minimum necessary: only include PHI needed for the specific task, never over-document

## Agent Stack
- [2026-06-09] [claude] Claude Code is the primary agent — reads/writes this repo + local PHI vault
- [2026-06-09] [claude] Second brain vault at second-brain/ — PARA structure, Obsidian-compatible markdown
- [2026-06-09] [claude] RuVector Brain MCP at 127.0.0.1:9876/sse provides semantic search over the vault (local only)

## Clinical — O&P Domain
- [2026-06-09] [claude] K-levels: K0=non-ambulatory, K1=limited household, K2=limited community, K3=community ambulator, K4=high activity/athlete — determines prosthetic componentry Medicare will cover
- [2026-06-09] [claude] Primary billing codes: HCPCS Level II L-codes (L0100-L8499) for orthotics/prosthetics; see 03-Resources/HCPCS L-Codes.md
- [2026-06-09] [claude] Primary diagnosis codes: ICD-10-CM Z89.xxx (acquired absence of limb), M21.xxx (deformities), G-codes (neurological); see 03-Resources/ICD-10 O&P Codes.md
- [2026-06-09] [claude] Medicare is the dominant payer for O&P — LCDs (Local Coverage Determinations) set functional and documentation requirements per device category

## Insurance & Billing
<!-- Append payer rules, denial patterns, appeal arguments as discovered -->

## Clinical Documentation
<!-- Append SOAP note patterns, medical necessity language, documentation tips as discovered -->

## Software Projects
<!-- Append code project learnings, decisions, tech choices as discovered -->
