"""
Core PDF extraction pipeline using the Anthropic Claude API.
Supports base64 inline documents, the Files API for reuse, and
the Message Batches API for high-volume processing queues.
"""
from __future__ import annotations

import base64
import logging
import os
from pathlib import Path
from typing import Any, Optional

import anthropic

from .prompts import EXTRACTION_TOOL, SYSTEM_PROMPT, build_extraction_message
from .schemas import (
    DiagnosisCode,
    DocumentType,
    ExtractionJob,
    ExtractionStatus,
    ExtractedPatientData,
    FieldConfidence,
    InsuranceInfo,
    LabResult,
    Medication,
    PatientDemographics,
    ProcedureCode,
    ProviderInfo,
    ProviderRole,
    Address,
    Gender,
    RelationshipToInsured,
)

logger = logging.getLogger(__name__)

MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
MAX_TOKENS = 4096
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.85"))


class PDFExtractor:
    """
    Extracts structured patient data from PDFs and fax images using Claude.

    Usage:
        extractor = PDFExtractor()
        job = await extractor.extract_from_file(Path("referral.pdf"))
    """

    def __init__(self) -> None:
        self._client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def extract_from_file(self, path: Path, job: Optional[ExtractionJob] = None) -> ExtractionJob:
        """Read a PDF from disk and run extraction. Returns the updated job."""
        if job is None:
            job = ExtractionJob(source_path=str(path), source_type="pdf")

        job.status = ExtractionStatus.PROCESSING

        pdf_bytes = path.read_bytes()
        if len(pdf_bytes) > 32 * 1024 * 1024:
            job.status = ExtractionStatus.FAILED
            job.error_message = "PDF exceeds the 32 MB Claude API limit"
            return job

        try:
            result = self._run_extraction(pdf_bytes, path.name)
            result.source_filename = path.name
            job.result = result
            job.status = (
                ExtractionStatus.REVIEW_REQUIRED
                if result.requires_review
                else ExtractionStatus.EXTRACTED
            )
        except Exception as exc:
            logger.exception("Extraction failed for %s", path)
            job.status = ExtractionStatus.FAILED
            job.error_message = str(exc)

        return job

    def extract_from_bytes(
        self, pdf_bytes: bytes, filename: str, job: Optional[ExtractionJob] = None
    ) -> ExtractionJob:
        """Extract from raw bytes (e.g., from a fax webhook payload)."""
        if job is None:
            job = ExtractionJob(source_type="fax")

        job.status = ExtractionStatus.PROCESSING
        try:
            result = self._run_extraction(pdf_bytes, filename)
            result.source_filename = filename
            job.result = result
            job.status = (
                ExtractionStatus.REVIEW_REQUIRED
                if result.requires_review
                else ExtractionStatus.EXTRACTED
            )
        except Exception as exc:
            logger.exception("Extraction failed for %s", filename)
            job.status = ExtractionStatus.FAILED
            job.error_message = str(exc)

        return job

    # ------------------------------------------------------------------
    # Internal extraction logic
    # ------------------------------------------------------------------

    def _run_extraction(self, pdf_bytes: bytes, filename: str) -> ExtractedPatientData:
        """Send the PDF to Claude and parse the structured tool response."""
        encoded = base64.standard_b64encode(pdf_bytes).decode("utf-8")

        # Estimate page count from file size for the user prompt (rough heuristic)
        estimated_pages = max(1, len(pdf_bytes) // (50 * 1024))

        response = self._client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    # Cache the system prompt — it's identical for every document
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            tools=[EXTRACTION_TOOL],
            tool_choice={"type": "tool", "name": "extract_patient_data"},
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "document",
                            "source": {
                                "type": "base64",
                                "media_type": "application/pdf",
                                "data": encoded,
                            },
                            # Cache the document for follow-up queries (e.g., validation clarification)
                            "cache_control": {"type": "ephemeral"},
                        },
                        {
                            "type": "text",
                            "text": build_extraction_message(estimated_pages),
                        },
                    ],
                }
            ],
        )

        tool_use_block = next(
            (b for b in response.content if b.type == "tool_use"),
            None,
        )
        if tool_use_block is None:
            raise ValueError("Claude returned no tool_use block — unexpected response format")

        return self._parse_tool_result(tool_use_block.input)

    def _parse_tool_result(self, data: dict[str, Any]) -> ExtractedPatientData:
        """Convert the raw Claude tool-use JSON into validated Pydantic models."""
        patient = self._parse_patient(data.get("patient", {}))
        primary_ins = self._parse_insurance(data.get("primary_insurance"))
        secondary_ins = self._parse_insurance(data.get("secondary_insurance"))
        diagnoses = [self._parse_diagnosis(d) for d in data.get("diagnoses", [])]
        procedures = [self._parse_procedure(p) for p in data.get("procedures", [])]
        medications = [self._parse_medication(m) for m in data.get("medications", [])]
        lab_results = [self._parse_lab(l) for l in data.get("lab_results", [])]
        referring = self._parse_provider(data.get("referring_provider"), ProviderRole.REFERRING)
        rendering = self._parse_provider(data.get("rendering_provider"), ProviderRole.RENDERING)

        overall_confidence = float(data.get("overall_confidence", 0.5))
        low_confidence_fields = data.get("low_confidence_fields", [])

        extracted = ExtractedPatientData(
            document_type=DocumentType(data.get("document_type", "unknown")),
            patient=patient,
            primary_insurance=primary_ins,
            secondary_insurance=secondary_ins,
            diagnoses=diagnoses,
            procedures=procedures,
            medications=medications,
            lab_results=lab_results,
            allergies=data.get("allergies", []),
            referring_provider=referring,
            rendering_provider=rendering,
            facility_name=data.get("facility_name"),
            facility_npi=data.get("facility_npi"),
            service_date=self._parse_date(data.get("service_date")),
            service_date_end=self._parse_date(data.get("service_date_end")),
            prior_auth_number=data.get("prior_auth_number"),
            referral_number=data.get("referral_number"),
            place_of_service=data.get("place_of_service"),
            accident_related=data.get("accident_related", False),
            accident_date=self._parse_date(data.get("accident_date")),
            accident_state=data.get("accident_state"),
            chief_complaint=data.get("chief_complaint"),
            clinical_notes=data.get("clinical_notes"),
            reason_for_referral=data.get("reason_for_referral"),
            overall_confidence=overall_confidence,
            low_confidence_fields=low_confidence_fields,
            requires_review=(
                overall_confidence < CONFIDENCE_THRESHOLD or len(low_confidence_fields) > 0
            ),
        )

        return extracted

    # ------------------------------------------------------------------
    # Field parsers
    # ------------------------------------------------------------------

    def _parse_patient(self, d: dict) -> PatientDemographics:
        address = None
        if addr_data := d.get("address"):
            address = Address(**{k: v for k, v in addr_data.items() if v})

        return PatientDemographics(
            first_name=d.get("first_name", ""),
            last_name=d.get("last_name", ""),
            middle_name=d.get("middle_name"),
            date_of_birth=self._parse_date(d.get("date_of_birth")),
            gender=Gender(d.get("gender", "U")),
            ssn_last4=d.get("ssn_last4"),
            mrn=d.get("mrn"),
            phone=d.get("phone"),
            email=d.get("email"),
            address=address,
        )

    def _parse_insurance(self, d: Optional[dict]) -> Optional[InsuranceInfo]:
        if not d or not d.get("payer_name") or not d.get("member_id"):
            return None

        return InsuranceInfo(
            payer_name=d["payer_name"],
            payer_id=d.get("payer_id"),
            member_id=d["member_id"],
            group_number=d.get("group_number"),
            group_name=d.get("group_name"),
            plan_name=d.get("plan_name"),
            plan_type=d.get("plan_type"),
            relationship_to_insured=RelationshipToInsured(
                d.get("relationship_to_insured", "self")
            ),
            insured_name=d.get("insured_name"),
            insured_dob=self._parse_date(d.get("insured_dob")),
            effective_date=self._parse_date(d.get("effective_date")),
            termination_date=self._parse_date(d.get("termination_date")),
            copay=d.get("copay"),
            deductible=d.get("deductible"),
        )

    def _parse_diagnosis(self, d: dict) -> DiagnosisCode:
        return DiagnosisCode(
            icd10_code=d.get("icd10_code", ""),
            description=d.get("description"),
            is_primary=d.get("is_primary", False),
            pointer=d.get("pointer"),
            confidence=float(d.get("confidence", 1.0)),
        )

    def _parse_procedure(self, d: dict) -> ProcedureCode:
        return ProcedureCode(
            cpt_code=d.get("cpt_code", ""),
            modifier1=d.get("modifier1"),
            modifier2=d.get("modifier2"),
            description=d.get("description"),
            units=int(d.get("units", 1)),
            charge=d.get("charge"),
            service_date=self._parse_date(d.get("service_date")),
            place_of_service=d.get("place_of_service"),
            diagnosis_pointers=d.get("diagnosis_pointers", []),
            confidence=float(d.get("confidence", 1.0)),
        )

    def _parse_medication(self, d: dict) -> Medication:
        return Medication(
            name=d.get("name", ""),
            dosage=d.get("dosage"),
            frequency=d.get("frequency"),
            route=d.get("route"),
            is_current=d.get("is_current", True),
        )

    def _parse_lab(self, d: dict) -> LabResult:
        return LabResult(
            test_name=d.get("test_name", ""),
            result_value=d.get("result_value"),
            unit=d.get("unit"),
            reference_range=d.get("reference_range"),
            flag=d.get("flag"),
            collection_date=self._parse_date(d.get("collection_date")),
        )

    def _parse_provider(
        self, d: Optional[dict], role: ProviderRole
    ) -> Optional[ProviderInfo]:
        if not d or not d.get("name"):
            return None

        address = None
        if addr_data := d.get("address"):
            address = Address(**{k: v for k, v in addr_data.items() if v})

        return ProviderInfo(
            npi=d.get("npi"),
            name=d["name"],
            first_name=d.get("first_name"),
            last_name=d.get("last_name"),
            specialty=d.get("specialty"),
            address=address,
            phone=d.get("phone"),
            fax=d.get("fax"),
            role=role,
        )

    @staticmethod
    def _parse_date(value: Optional[str]):
        if not value:
            return None
        try:
            from datetime import date
            from dateutil import parser as dateparser
            parsed = dateparser.parse(str(value))
            return parsed.date() if parsed else None
        except Exception:
            return None
