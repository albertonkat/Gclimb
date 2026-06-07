"""Unit tests for EzClaim EDI export and payload generation."""
import pytest
from datetime import date

from src.extraction.schemas import (
    DiagnosisCode,
    ExtractedPatientData,
    Gender,
    InsuranceInfo,
    PatientDemographics,
    ProcedureCode,
    ProviderInfo,
    ProviderRole,
)
from src.integrations.ezclaim import EzClaimClient, _gender_to_ezclaim, _insurance_payload


def make_full_data() -> ExtractedPatientData:
    return ExtractedPatientData(
        patient=PatientDemographics(
            first_name="John",
            last_name="Smith",
            date_of_birth=date(1970, 6, 15),
            gender=Gender.MALE,
            ssn_last4="5678",
        ),
        primary_insurance=InsuranceInfo(
            payer_name="Medicare",
            payer_id="00111",
            member_id="1EG4-TE5-MK72",
            group_number="GRP001",
        ),
        diagnoses=[
            DiagnosisCode(icd10_code="E11.65", is_primary=True, pointer=1),
            DiagnosisCode(icd10_code="I10", pointer=2),
        ],
        procedures=[
            ProcedureCode(
                cpt_code="99213",
                modifier1="25",
                units=1,
                charge=150.00,
                service_date=date(2026, 1, 10),
                place_of_service="11",
                diagnosis_pointers=[1, 2],
            )
        ],
        service_date=date(2026, 1, 10),
        overall_confidence=0.95,
    )


class TestEzClaimHelpers:
    def test_gender_mapping(self):
        assert _gender_to_ezclaim("M") == "Male"
        assert _gender_to_ezclaim("F") == "Female"
        assert _gender_to_ezclaim("U") == "Unknown"

    def test_insurance_payload_keys(self):
        ins = InsuranceInfo(payer_name="Aetna", member_id="A123")
        payload = _insurance_payload(ins)
        assert payload["payerName"] == "Aetna"
        assert payload["memberId"] == "A123"


class TestEDIExport:
    def test_837p_contains_patient_name(self):
        data = make_full_data()
        # EzClaimClient requires env vars — patch them
        import os
        os.environ.setdefault("EZCLAIM_BASE_URL", "http://localhost")
        os.environ.setdefault("EZCLAIM_API_KEY", "test")
        os.environ.setdefault("EZCLAIM_ACCOUNT_ID", "test")

        client = EzClaimClient()
        edi = client.export_837p(data)
        assert "Smith" in edi
        assert "John" in edi

    def test_837p_contains_payer_id(self):
        data = make_full_data()
        import os
        os.environ.setdefault("EZCLAIM_BASE_URL", "http://localhost")
        os.environ.setdefault("EZCLAIM_API_KEY", "test")
        os.environ.setdefault("EZCLAIM_ACCOUNT_ID", "test")

        client = EzClaimClient()
        edi = client.export_837p(data)
        assert "00111" in edi

    def test_837p_contains_diagnosis_code(self):
        data = make_full_data()
        import os
        os.environ.setdefault("EZCLAIM_BASE_URL", "http://localhost")
        os.environ.setdefault("EZCLAIM_API_KEY", "test")
        os.environ.setdefault("EZCLAIM_ACCOUNT_ID", "test")

        client = EzClaimClient()
        edi = client.export_837p(data)
        assert "E1165" in edi or "E11.65" in edi
