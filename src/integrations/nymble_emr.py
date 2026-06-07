"""
Nymble EMR API integration.

Maps ExtractedPatientData → Nymble patient/chart API payloads.
Nymble uses a REST API with FHIR R4-influenced resources.

Endpoints used:
  POST /patients             - create or upsert patient record
  POST /patients/{id}/charts - create chart note with clinical data
  POST /patients/{id}/insurance - add insurance coverage
  POST /patients/{id}/medications - add medication list
  POST /patients/{id}/diagnoses - add problem list entries

Configure via environment:
  NYMBLE_BASE_URL   - e.g. https://api.nymble.com/v1
  NYMBLE_API_KEY    - API key from Nymble developer portal
  NYMBLE_PRACTICE_ID - your practice identifier
"""
from __future__ import annotations

import logging
import os
from typing import Any, Optional

import httpx

from ..extraction.schemas import ExtractedPatientData, InsuranceInfo, ProviderInfo

logger = logging.getLogger(__name__)


class NymbleEMRClient:
    """
    Pushes extracted patient data into Nymble EMR.

    Usage:
        client = NymbleEMRClient()
        patient_id = client.upsert_patient(extracted_data)
        client.create_chart_entry(patient_id, extracted_data)
    """

    def __init__(self) -> None:
        self._base_url = os.environ["NYMBLE_BASE_URL"].rstrip("/")
        self._api_key = os.environ["NYMBLE_API_KEY"]
        self._practice_id = os.environ["NYMBLE_PRACTICE_ID"]
        self._http = httpx.Client(
            base_url=self._base_url,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "X-Practice-ID": self._practice_id,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=30,
        )

    def push_all(self, data: ExtractedPatientData) -> str:
        """
        Full push: upsert patient, add insurance, create chart entry.
        Returns the Nymble patient ID.
        """
        patient_id = self.upsert_patient(data)
        if data.primary_insurance:
            self.add_insurance(patient_id, data.primary_insurance, is_primary=True)
        if data.secondary_insurance:
            self.add_insurance(patient_id, data.secondary_insurance, is_primary=False)
        if data.medications:
            self.add_medications(patient_id, data)
        self.create_chart_entry(patient_id, data)
        return patient_id

    def upsert_patient(self, data: ExtractedPatientData) -> str:
        """
        Create or update a patient record. Nymble matches on (first_name, last_name, dob).
        Returns the Nymble patient ID.
        """
        p = data.patient
        payload: dict[str, Any] = {
            "firstName": p.first_name,
            "lastName": p.last_name,
            "middleName": p.middle_name,
            "dateOfBirth": p.date_of_birth.isoformat() if p.date_of_birth else None,
            "gender": p.gender.value,
            "mrn": p.mrn,
            "phone": p.phone,
            "email": p.email,
        }
        if p.address:
            payload["address"] = {
                "street1": p.address.street1,
                "street2": p.address.street2,
                "city": p.address.city,
                "state": p.address.state,
                "zipCode": p.address.zip_code,
                "country": p.address.country,
            }

        payload = {k: v for k, v in payload.items() if v is not None}

        resp = self._http.post("/patients/upsert", json=payload)
        resp.raise_for_status()
        return resp.json()["patientId"]

    def add_insurance(
        self, patient_id: str, insurance: InsuranceInfo, is_primary: bool
    ) -> None:
        payload: dict[str, Any] = {
            "payerName": insurance.payer_name,
            "payerId": insurance.payer_id,
            "memberId": insurance.member_id,
            "groupNumber": insurance.group_number,
            "groupName": insurance.group_name,
            "planName": insurance.plan_name,
            "planType": insurance.plan_type,
            "isPrimary": is_primary,
            "relationshipToInsured": insurance.relationship_to_insured.value,
            "insuredName": insurance.insured_name,
            "effectiveDate": (
                insurance.effective_date.isoformat() if insurance.effective_date else None
            ),
            "terminationDate": (
                insurance.termination_date.isoformat() if insurance.termination_date else None
            ),
        }
        payload = {k: v for k, v in payload.items() if v is not None}
        resp = self._http.post(f"/patients/{patient_id}/insurance", json=payload)
        resp.raise_for_status()

    def create_chart_entry(self, patient_id: str, data: ExtractedPatientData) -> str:
        """Create a clinical chart note with diagnoses, labs, referral info, and notes."""
        diagnoses_payload = [
            {
                "icd10Code": dx.icd10_code,
                "description": dx.description,
                "isPrimary": dx.is_primary,
            }
            for dx in data.diagnoses
        ]

        labs_payload = [
            {
                "testName": lab.test_name,
                "resultValue": lab.result_value,
                "unit": lab.unit,
                "referenceRange": lab.reference_range,
                "flag": lab.flag,
                "collectionDate": lab.collection_date.isoformat() if lab.collection_date else None,
            }
            for lab in data.lab_results
        ]

        payload: dict[str, Any] = {
            "documentType": data.document_type.value,
            "serviceDate": data.service_date.isoformat() if data.service_date else None,
            "chiefComplaint": data.chief_complaint,
            "reasonForReferral": data.reason_for_referral,
            "clinicalNotes": data.clinical_notes,
            "diagnoses": diagnoses_payload,
            "labResults": labs_payload,
            "allergies": data.allergies,
            "priorAuthNumber": data.prior_auth_number,
            "referralNumber": data.referral_number,
            "facilityName": data.facility_name,
            "sourceDocument": data.source_filename,
        }

        if data.referring_provider:
            payload["referringProvider"] = self._provider_payload(data.referring_provider)

        payload = {k: v for k, v in payload.items() if v is not None}

        resp = self._http.post(f"/patients/{patient_id}/charts", json=payload)
        resp.raise_for_status()
        return resp.json().get("chartId", "")

    def add_medications(self, patient_id: str, data: ExtractedPatientData) -> None:
        meds = [
            {
                "name": m.name,
                "dosage": m.dosage,
                "frequency": m.frequency,
                "route": m.route,
                "isCurrent": m.is_current,
            }
            for m in data.medications
        ]
        resp = self._http.post(f"/patients/{patient_id}/medications", json={"medications": meds})
        resp.raise_for_status()

    @staticmethod
    def _provider_payload(provider: ProviderInfo) -> dict:
        p: dict[str, Any] = {
            "npi": provider.npi,
            "name": provider.name,
            "firstName": provider.first_name,
            "lastName": provider.last_name,
            "specialty": provider.specialty,
            "phone": provider.phone,
            "fax": provider.fax,
        }
        if provider.address:
            p["address"] = {
                "street1": provider.address.street1,
                "city": provider.address.city,
                "state": provider.address.state,
                "zipCode": provider.address.zip_code,
            }
        return {k: v for k, v in p.items() if v is not None}
