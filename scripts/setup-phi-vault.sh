#!/bin/bash
# setup-phi-vault.sh
# Run once on each machine to initialize the local PHI vault.
# This directory is NEVER committed to git.

set -e

PHI_VAULT="${HOME}/GulfCoastLimb-PHI"

echo "Setting up Gulf Coast Limb and Brace PHI vault at: ${PHI_VAULT}"
echo ""
echo "⚠️  This directory will contain HIPAA-protected patient data."
echo "    It is local-only and must NEVER be committed to git."
echo ""

mkdir -p "${PHI_VAULT}/soap-notes"
mkdir -p "${PHI_VAULT}/appeals"
mkdir -p "${PHI_VAULT}/prior-auth"
mkdir -p "${PHI_VAULT}/cases"

# Create a local .gitignore inside the PHI vault as an extra safeguard
cat > "${PHI_VAULT}/.gitignore" << 'EOF'
# This entire directory contains PHI and must never be tracked by git.
*
EOF

# Create a README inside the PHI vault
cat > "${PHI_VAULT}/README.md" << 'EOF'
# GulfCoastLimb-PHI — Local PHI Vault

Gulf Coast Limb and Brace | Alberto Alvarez, CPO

This directory contains HIPAA-protected patient health information (PHI).

**This directory is LOCAL ONLY. Never commit or sync to any remote service.**

## Structure

```
soap-notes/    YYYY-MM-DD-[patientID]-[visit-type].md
appeals/       YYYY-MM-DD-[patientID]-[payer]-[code].md
prior-auth/    YYYY-MM-DD-[patientID]-[payer].md
cases/         [patientID].md  (longitudinal case file per patient)
```

## Patient ID convention
Use a consistent internal identifier — NOT the patient's full name in filenames.
Recommended: last 4 of SSN + DOB (e.g., 1234-19520315) or your EMR patient number.

## Backup
Back up this directory using an encrypted, HIPAA-compliant backup solution.
Do NOT use standard cloud sync (Dropbox, Google Drive, iCloud) without a signed BAA.
EOF

echo ""
echo "✅ PHI vault created at: ${PHI_VAULT}"
echo ""
echo "Folders:"
ls -la "${PHI_VAULT}"
echo ""
echo "Next steps:"
echo "  1. Add ${PHI_VAULT} to a HIPAA-compliant encrypted backup"
echo "  2. Set up your Obsidian vault to open second-brain/ in this repo"
echo "  3. Run 'bash scripts/setup-phi-vault.sh' again on any other machine you use"
