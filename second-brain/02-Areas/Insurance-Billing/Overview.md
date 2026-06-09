---
created: 2026-06-09
tags: [area, insurance, billing, appeals, prior-auth]
---

# Insurance & Billing — Overview

---

## O&P Billing Basics

O&P is billed under **DMEPOS (Durable Medical Equipment, Prosthetics, Orthotics, and Supplies)** — Medicare Part B, not Part A or Part D.

**Claim type:** CMS-1500 (or electronic 837P)  
**Billing codes:** HCPCS Level II L-codes (prosthetics L5000–L7499, orthotics L0100–L4999)  
**Modifiers commonly used:**
- `LT` / `RT` — left / right
- `KX` — supplier attests documentation on file supports coverage criteria
- `GY` — item is not covered by Medicare (used for ABN situations)
- `GA` — ABN on file
- `KB` — beneficiary requested upgrade, must use with `-GK`

---

## Prior Authorization

Medicare requires prior authorization for certain high-cost lower limb prostheses (microprocessor knees, powered ankles). Most commercial payers require prior auth for prosthetics and custom orthotics.

**Required for prior auth (typical):**
- Physician order
- CPO evaluation / clinical notes
- K-level documentation
- Device specification with HCPCS codes and cost
- ICD-10 diagnosis codes
- Prior device history (for replacements)

See [[05-Templates/Prior Authorization]] for the request template.

---

## Denial Reasons and Response Strategy

| Denial reason | Response strategy |
|---|---|
| **Lacks medical necessity** | Submit clinical notes, K-level justification, functional limitations documentation |
| **Missing / unsigned order** | Obtain corrected/countersigned order; resubmit |
| **Incorrect K-level** | Submit CPO evaluation with detailed functional assessment, physician attestation |
| **Frequency limitation** | Document premature wear (clinical photos, measurement records), or patient weight/activity change |
| **Not covered — covered by Medicare Part A** | Check if patient is in a Part A stay; if not, appeal with Part B eligibility proof |
| **Bundled into other service** | Document separate and distinct medical necessity for each billed item |
| **Code not on LCD** | Appeal with clinical literature, cite CMS guidelines, request redetermination |
| **Duplicate claim** | Verify no prior payment; if truly different service, appeal with documentation |

---

## Medicare Appeal Levels

1. **Redetermination** — submit within 120 days of denial; decided by same MAC
2. **Reconsideration** — submit within 180 days; decided by Qualified Independent Contractor (QIC)
3. **ALJ Hearing** — Administrative Law Judge; requires ≥$180 in dispute (2024)
4. **Medicare Appeals Council** — Board-level review
5. **Federal District Court** — requires ≥$1,840 in dispute (2024)

**Win rate improves significantly at Level 2 (QIC) with strong clinical documentation.**

---

## ABN (Advance Beneficiary Notice)

Issue an ABN when Medicare may deny coverage but the patient wants the item. The ABN:
- Must be given before services are rendered
- Explains why Medicare may not pay
- Gives patient the option to accept financial responsibility or not receive the service
- Protects the provider from being held liable

---

## Key Payer Rules to Know

See [[03-Resources/Medicare LCD Reference]] for LCD details.  
See [[03-Resources/Insurance Payers]] for payer-specific rules and contacts.

---

## Cross-references
- [[03-Resources/Medicare LCD Reference]]
- [[03-Resources/HCPCS L-Codes]]
- [[03-Resources/ICD-10 O&P Codes]]
- [[03-Resources/Insurance Payers]]
- [[05-Templates/Insurance Appeal Letter]]
- [[05-Templates/Prior Authorization]]
- [[07-MOCs/Insurance Billing MOC]]
