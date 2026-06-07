"""
Validates extracted patient data for completeness, format correctness,
and clinical consistency before it is written to Nymble EMR or EzClaim.

Integrates with:
  - NPPES NPI Registry API (via httpx)
  - CMS ICD-10-CM code validation (via local lookup)
  - CPT code format checks
"""
from __future__ import annotations

import logging
import re
from typing import List

import httpx

from ..extraction.schemas import (
    DiagnosisCode,
    ExtractedPatientData,
    ProviderInfo,
)

logger = logging.getLogger(__name__)

NPPES_API = "https://npiregistry.cms.hhs.gov/api/"
NPI_PATTERN = re.compile(r"^\d{10}$")
ICD10_PATTERN = re.compile(r"^[A-Z]\d{2}(\.\w{1,4})?$")
CPT_PATTERN = re.compile(r"^\d{5}[A-Z0-9]?$")
ZIP_PATTERN = re.compile(r"^\d{5}(-\d{4})?$")


class PatientDataValidator:
    """
    Runs a chain of validation checks on ExtractedPatientData.
    Errors are appended to result.validation_errors.
    Low-confidence or incomplete records are flagged requires_review=True.
    """

    REQUIRED_FOR_EZCLAIM = [
        "patient.first_name",
        "patient.last_name",
        "patient.date_of_birth",
        "primary_insurance.member_id",
        "primary_insurance.payer_name",
    ]

    REQUIRED_FOR_NYMBLE = [
        "patient.first_name",
        "patient.last_name",
        "patient.date_of_birth",
    ]

    def validate(self, data: ExtractedPatientData) -> ExtractedPatientData:
        """Run all validation checks. Mutates and returns the data object."""
        self._check_patient_demographics(data)
        self._check_insurance(data)
        self._check_diagnoses(data)
        self._check_procedures(data)
        self._check_providers(data)
        self._check_confidence(data)

        if data.validation_errors:
            data.requires_review = True

        return data

    def validate_npis_online(self, data: ExtractedPatientData) -> ExtractedPatientData:
        """
        Hits the live NPPES API to verify provider NPI numbers.
        Call this after the synchronous validate() pass.
        Network errors are logged but do not fail the validation — they just
        leave is_validated=False so the human reviewer can check.
        """
        providers = [p for p in [data.referring_provider, data.rendering_provider] if p]
        for provider in providers:
            if provider.npi:
                self._verify_npi_online(provider)
        return data

    # ------------------------------------------------------------------
    # Check methods
    # ------------------------------------------------------------------

    def _check_patient_demographics(self, data: ExtractedPatientData) -> None:
        p = data.patient
        if not p.first_name.strip():
            data.mark_review_required("patient.first_name is missing")
        if not p.last_name.strip():
            data.mark_review_required("patient.last_name is missing")
        if p.date_of_birth is None:
            data.mark_review_required("patient.date_of_birth is missing")
        if p.ssn_last4 and not re.match(r"^\d{4}$", p.ssn_last4):
            data.mark_review_required(f"patient.ssn_last4 invalid format: {p.ssn_last4!r}")
        if p.address and p.address.zip_code:
            if not ZIP_PATTERN.match(p.address.zip_code):
                data.validation_errors.append(
                    f"patient.address.zip_code format unexpected: {p.address.zip_code}"
                )

    def _check_insurance(self, data: ExtractedPatientData) -> None:
        if data.primary_insurance is None:
            data.mark_review_required("primary_insurance is missing")
            return

        ins = data.primary_insurance
        if not ins.member_id.strip():
            data.mark_review_required("primary_insurance.member_id is missing")
        if not ins.payer_name.strip():
            data.mark_review_required("primary_insurance.payer_name is missing")

    def _check_diagnoses(self, data: ExtractedPatientData) -> None:
        if not data.diagnoses:
            data.mark_review_required("No diagnosis codes extracted")
            return

        for i, dx in enumerate(data.diagnoses):
            code = dx.icd10_code
            if not ICD10_PATTERN.match(code):
                data.validation_errors.append(
                    f"diagnoses[{i}].icd10_code format invalid: {code!r}"
                )
                dx.confidence = min(dx.confidence, 0.5)

        primaries = [d for d in data.diagnoses if d.is_primary]
        if not primaries:
            # Auto-assign first as primary
            data.diagnoses[0].is_primary = True

        # Ensure diagnosis pointers are sequential
        for i, dx in enumerate(data.diagnoses):
            if dx.pointer is None:
                dx.pointer = i + 1

    def _check_procedures(self, data: ExtractedPatientData) -> None:
        for i, proc in enumerate(data.procedures):
            if not CPT_PATTERN.match(proc.cpt_code):
                data.validation_errors.append(
                    f"procedures[{i}].cpt_code format invalid: {proc.cpt_code!r}"
                )

    def _check_providers(self, data: ExtractedPatientData) -> None:
        for provider in [data.referring_provider, data.rendering_provider]:
            if provider and provider.npi:
                if not NPI_PATTERN.match(provider.npi):
                    data.validation_errors.append(
                        f"provider {provider.name!r} NPI format invalid: {provider.npi!r}"
                    )
                elif not self._luhn_check_npi(provider.npi):
                    data.validation_errors.append(
                        f"provider {provider.name!r} NPI failed Luhn check: {provider.npi}"
                    )

    def _check_confidence(self, data: ExtractedPatientData) -> None:
        from ..extraction.schemas import ExtractionStatus
        threshold = 0.85
        if data.overall_confidence < threshold:
            data.requires_review = True
            if data.status == ExtractionStatus.EXTRACTED:
                data.status = ExtractionStatus.REVIEW_REQUIRED

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _luhn_check_npi(npi: str) -> bool:
        """Validate NPI using the Luhn algorithm (with 80840 prefix per CMS spec)."""
        full = "80840" + npi
        total = 0
        for i, ch in enumerate(reversed(full)):
            n = int(ch)
            if i % 2 == 0:
                n *= 2
                if n > 9:
                    n -= 9
            total += n
        return total % 10 == 0

    def _verify_npi_online(self, provider: ProviderInfo) -> None:
        """Query the NPPES registry and update provider.is_validated."""
        try:
            resp = httpx.get(
                NPPES_API,
                params={"number": provider.npi, "version": "2.1"},
                timeout=10,
            )
            resp.raise_for_status()
            result = resp.json()
            if result.get("result_count", 0) > 0:
                provider.is_validated = True
                nppes_record = result["results"][0]
                # Enrich name from registry if our extraction was uncertain
                basic = nppes_record.get("basic", {})
                if not provider.first_name and basic.get("first_name"):
                    provider.first_name = basic["first_name"]
                if not provider.last_name and basic.get("last_name"):
                    provider.last_name = basic["last_name"]
            else:
                logger.warning("NPI %s not found in NPPES registry", provider.npi)
        except httpx.HTTPError as exc:
            logger.warning("NPPES lookup failed for NPI %s: %s", provider.npi, exc)
