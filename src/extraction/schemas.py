"""
Pydantic models for all patient data extracted from PDFs and faxes.
Fields align with CMS-1500/UB-04 claim forms, FHIR R4 resources,
Nymble EMR API, and EzClaim billing API.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class DocumentType(str, Enum):
    REFERRAL = "referral"
    PRIOR_AUTH = "prior_authorization"
    LAB_REPORT = "lab_report"
    DISCHARGE_SUMMARY = "discharge_summary"
    PROGRESS_NOTE = "progress_note"
    PRESCRIPTION = "prescription"
    INSURANCE_CARD = "insurance_card"
    UNKNOWN = "unknown"


class Gender(str, Enum):
    MALE = "M"
    FEMALE = "F"
    OTHER = "O"
    UNKNOWN = "U"


class RelationshipToInsured(str, Enum):
    SELF = "self"
    SPOUSE = "spouse"
    CHILD = "child"
    OTHER = "other"


class ProviderRole(str, Enum):
    REFERRING = "referring"
    RENDERING = "rendering"
    SUPERVISING = "supervising"
    ORDERING = "ordering"
    ATTENDING = "attending"
    FACILITY = "facility"


class ExtractionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    EXTRACTED = "extracted"
    REVIEW_REQUIRED = "review_required"
    APPROVED = "approved"
    REJECTED = "rejected"
    FAILED = "failed"


class Address(BaseModel):
    street1: Optional[str] = None
    street2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: str = "US"


class PatientDemographics(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Gender = Gender.UNKNOWN
    ssn_last4: Optional[str] = None
    address: Optional[Address] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    mrn: Optional[str] = None  # Medical Record Number

    @field_validator("ssn_last4")
    @classmethod
    def validate_ssn(cls, v: Optional[str]) -> Optional[str]:
        if v and (not v.isdigit() or len(v) != 4):
            raise ValueError("ssn_last4 must be exactly 4 digits")
        return v


class InsuranceInfo(BaseModel):
    payer_name: str
    payer_id: Optional[str] = None          # Electronic payer ID for EDI
    member_id: str
    group_number: Optional[str] = None
    group_name: Optional[str] = None
    plan_name: Optional[str] = None
    plan_type: Optional[str] = None         # HMO, PPO, Medicare, Medicaid, etc.
    relationship_to_insured: RelationshipToInsured = RelationshipToInsured.SELF
    insured_name: Optional[str] = None
    insured_dob: Optional[date] = None
    insured_id: Optional[str] = None
    copay: Optional[str] = None
    deductible: Optional[str] = None
    effective_date: Optional[date] = None
    termination_date: Optional[date] = None


class DiagnosisCode(BaseModel):
    icd10_code: str
    description: Optional[str] = None
    is_primary: bool = False
    pointer: Optional[int] = None           # CMS-1500 diagnosis pointer (1-12)
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)

    @field_validator("icd10_code")
    @classmethod
    def normalize_code(cls, v: str) -> str:
        return v.upper().replace(" ", "").replace("-", "")


class ProcedureCode(BaseModel):
    cpt_code: str
    modifier1: Optional[str] = None
    modifier2: Optional[str] = None
    description: Optional[str] = None
    units: int = 1
    charge: Optional[float] = None
    service_date: Optional[date] = None
    place_of_service: Optional[str] = None  # POS code (11=office, 21=inpatient, etc.)
    diagnosis_pointers: List[int] = Field(default_factory=list)  # links to DiagnosisCode.pointer
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)


class ProviderInfo(BaseModel):
    npi: Optional[str] = None
    tax_id: Optional[str] = None
    name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    specialty: Optional[str] = None
    address: Optional[Address] = None
    phone: Optional[str] = None
    fax: Optional[str] = None
    role: ProviderRole
    is_validated: bool = False              # set True after NPI registry lookup


class Medication(BaseModel):
    name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    route: Optional[str] = None
    is_current: bool = True


class LabResult(BaseModel):
    test_name: str
    result_value: Optional[str] = None
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    flag: Optional[str] = None             # H, L, HH, LL, N
    collection_date: Optional[date] = None


class FieldConfidence(BaseModel):
    field_name: str
    confidence: float = Field(ge=0.0, le=1.0)
    raw_value: Optional[str] = None        # what Claude saw before normalization


class ExtractedPatientData(BaseModel):
    """
    Root model for all data extracted from a single patient document.
    Maps to both Nymble EMR and EzClaim billing API targets.
    """
    document_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_filename: Optional[str] = None
    document_type: DocumentType = DocumentType.UNKNOWN
    extraction_timestamp: datetime = Field(default_factory=datetime.utcnow)
    model_version: str = "claude-sonnet-4-6"

    # Core clinical data
    patient: PatientDemographics
    primary_insurance: Optional[InsuranceInfo] = None
    secondary_insurance: Optional[InsuranceInfo] = None
    diagnoses: List[DiagnosisCode] = Field(default_factory=list)
    procedures: List[ProcedureCode] = Field(default_factory=list)
    medications: List[Medication] = Field(default_factory=list)
    lab_results: List[LabResult] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)

    # Providers
    referring_provider: Optional[ProviderInfo] = None
    rendering_provider: Optional[ProviderInfo] = None
    facility_name: Optional[str] = None
    facility_npi: Optional[str] = None

    # Administrative
    service_date: Optional[date] = None
    service_date_end: Optional[date] = None
    prior_auth_number: Optional[str] = None
    referral_number: Optional[str] = None
    place_of_service: Optional[str] = None
    accident_related: bool = False
    accident_date: Optional[date] = None
    accident_state: Optional[str] = None

    # Clinical narrative
    chief_complaint: Optional[str] = None
    clinical_notes: Optional[str] = None
    reason_for_referral: Optional[str] = None

    # Extraction quality
    overall_confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    field_confidences: List[FieldConfidence] = Field(default_factory=list)
    low_confidence_fields: List[str] = Field(default_factory=list)
    requires_review: bool = True
    validation_errors: List[str] = Field(default_factory=list)
    status: ExtractionStatus = ExtractionStatus.EXTRACTED

    def mark_review_required(self, reason: str) -> None:
        self.requires_review = True
        self.validation_errors.append(reason)
        self.status = ExtractionStatus.REVIEW_REQUIRED

    @property
    def primary_diagnosis(self) -> Optional[DiagnosisCode]:
        primaries = [d for d in self.diagnoses if d.is_primary]
        return primaries[0] if primaries else (self.diagnoses[0] if self.diagnoses else None)


class ExtractionJob(BaseModel):
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: ExtractionStatus = ExtractionStatus.PENDING
    source_type: str = "pdf"            # pdf | fax
    source_path: Optional[str] = None
    page_count: Optional[int] = None
    result: Optional[ExtractedPatientData] = None
    error_message: Optional[str] = None
    nymble_patient_id: Optional[str] = None
    ezclaim_claim_id: Optional[str] = None
