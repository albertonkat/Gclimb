"""Unit tests for extraction schemas and validation logic."""
import pytest
from datetime import date

from src.extraction.schemas import (
    DiagnosisCode,
    ExtractedPatientData,
    Gender,
    InsuranceInfo,
    PatientDemographics,
    ProviderInfo,
    ProviderRole,
    RelationshipToInsured,
)
from src.validation.patient_validator import PatientDataValidator


def make_minimal_patient() -> PatientDemographics:
    return PatientDemographics(
        first_name="Jane",
        last_name="Doe",
        date_of_birth=date(1985, 3, 15),
        gender=Gender.FEMALE,
    )


def make_minimal_data(**kwargs) -> ExtractedPatientData:
    defaults = dict(
        patient=make_minimal_patient(),
        overall_confidence=0.92,
        diagnoses=[DiagnosisCode(icd10_code="E11.65", is_primary=True)],
    )
    defaults.update(kwargs)
    return ExtractedPatientData(**defaults)


class TestDiagnosisCode:
    def test_code_normalization(self):
        dx = DiagnosisCode(icd10_code=" e11.65 ")
        assert dx.icd10_code == "E11.65"

    def test_code_removes_dash(self):
        dx = DiagnosisCode(icd10_code="E11-65")
        assert dx.icd10_code == "E1165"


class TestPatientDemographics:
    def test_ssn_last4_valid(self):
        p = PatientDemographics(first_name="A", last_name="B", ssn_last4="1234")
        assert p.ssn_last4 == "1234"

    def test_ssn_last4_invalid_raises(self):
        with pytest.raises(Exception):
            PatientDemographics(first_name="A", last_name="B", ssn_last4="12X4")

    def test_ssn_too_long_raises(self):
        with pytest.raises(Exception):
            PatientDemographics(first_name="A", last_name="B", ssn_last4="12345")


class TestPatientDataValidator:
    def setup_method(self):
        self.validator = PatientDataValidator()

    def test_passes_complete_record(self):
        data = make_minimal_data(
            primary_insurance=InsuranceInfo(
                payer_name="BlueCross",
                member_id="XYZ123",
            )
        )
        result = self.validator.validate(data)
        assert not result.validation_errors

    def test_flags_missing_insurance(self):
        data = make_minimal_data()
        result = self.validator.validate(data)
        assert any("primary_insurance" in e for e in result.validation_errors)
        assert result.requires_review

    def test_flags_missing_dob(self):
        patient = PatientDemographics(first_name="Jane", last_name="Doe")
        data = make_minimal_data(patient=patient)
        result = self.validator.validate(data)
        assert any("date_of_birth" in e for e in result.validation_errors)

    def test_flags_bad_icd10_format(self):
        data = make_minimal_data(
            diagnoses=[DiagnosisCode(icd10_code="BADCODE")],
            primary_insurance=InsuranceInfo(payer_name="Aetna", member_id="A1"),
        )
        result = self.validator.validate(data)
        assert any("icd10_code" in e for e in result.validation_errors)

    def test_auto_assigns_diagnosis_pointers(self):
        data = make_minimal_data(
            diagnoses=[
                DiagnosisCode(icd10_code="E11.65"),
                DiagnosisCode(icd10_code="I10"),
            ],
            primary_insurance=InsuranceInfo(payer_name="UHC", member_id="U99"),
        )
        result = self.validator.validate(data)
        assert result.diagnoses[0].pointer == 1
        assert result.diagnoses[1].pointer == 2

    def test_luhn_check_valid_npi(self):
        # NPI 1234567893 is a valid Luhn NPI
        assert PatientDataValidator._luhn_check_npi("1234567893")

    def test_luhn_check_invalid_npi(self):
        assert not PatientDataValidator._luhn_check_npi("1234567890")

    def test_flags_low_confidence(self):
        data = make_minimal_data(
            overall_confidence=0.60,
            primary_insurance=InsuranceInfo(payer_name="Cigna", member_id="C1"),
        )
        result = self.validator.validate(data)
        assert result.requires_review

    def test_primary_diagnosis_property(self):
        data = make_minimal_data(
            diagnoses=[
                DiagnosisCode(icd10_code="E11.65", is_primary=True),
                DiagnosisCode(icd10_code="I10"),
            ]
        )
        assert data.primary_diagnosis.icd10_code == "E11.65"
