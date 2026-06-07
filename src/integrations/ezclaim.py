"""
EzClaim billing integration.

Maps ExtractedPatientData → EzClaim claim/patient API payloads.
EzClaim handles CMS-1500 (professional) and UB-04 (institutional) claim forms.

Endpoints used:
  POST /patients             - create patient demographic record
  POST /claims               - create a new claim
  POST /claims/{id}/lines    - add service lines (procedures)

The output is also formatted as X12 837P EDI for direct clearinghouse submission
when EzClaim's EDI export is not available.

Configure via environment:
  EZCLAIM_BASE_URL    - e.g. https://api.ezclaim.com/v2
  EZCLAIM_API_KEY     - EzClaim API key
  EZCLAIM_ACCOUNT_ID  - Your EzClaim account ID
"""
from __future__ import annotations

import logging
import os
from datetime import date
from typing import Any, Optional

import httpx

from ..extraction.schemas import (
    DiagnosisCode,
    ExtractedPatientData,
    InsuranceInfo,
    ProcedureCode,
)

logger = logging.getLogger(__name__)


class EzClaimClient:
    """
    Pushes extracted patient and claim data into EzClaim billing software.

    Usage:
        client = EzClaimClient()
        patient_id = client.create_patient(data)
        claim_id = client.create_claim(patient_id, data)
    """

    def __init__(self) -> None:
        self._base_url = os.environ["EZCLAIM_BASE_URL"].rstrip("/")
        self._api_key = os.environ["EZCLAIM_API_KEY"]
        self._account_id = os.environ["EZCLAIM_ACCOUNT_ID"]
        self._http = httpx.Client(
            base_url=self._base_url,
            headers={
                "Authorization": f"ApiKey {self._api_key}",
                "X-Account-ID": self._account_id,
                "Content-Type": "application/json",
            },
            timeout=30,
        )

    def push_all(self, data: ExtractedPatientData) -> tuple[str, str]:
        """
        Full push: create patient + claim.
        Returns (ezclaim_patient_id, ezclaim_claim_id).
        """
        patient_id = self.create_patient(data)
        claim_id = self.create_claim(patient_id, data)
        return patient_id, claim_id

    def create_patient(self, data: ExtractedPatientData) -> str:
        """Create a patient demographic record in EzClaim. Returns patient ID."""
        p = data.patient
        payload: dict[str, Any] = {
            "firstName": p.first_name,
            "lastName": p.last_name,
            "middleName": p.middle_name or "",
            "dateOfBirth": p.date_of_birth.isoformat() if p.date_of_birth else "",
            "sex": _gender_to_ezclaim(p.gender.value),
            "ssn": f"***-**-{p.ssn_last4}" if p.ssn_last4 else "",
            "phone": p.phone or "",
            "email": p.email or "",
        }
        if p.address:
            payload.update(
                {
                    "address1": p.address.street1 or "",
                    "address2": p.address.street2 or "",
                    "city": p.address.city or "",
                    "state": p.address.state or "",
                    "zipCode": p.address.zip_code or "",
                }
            )
        resp = self._http.post("/patients", json=payload)
        resp.raise_for_status()
        return resp.json()["patientId"]

    def create_claim(self, patient_id: str, data: ExtractedPatientData) -> str:
        """
        Create a CMS-1500 professional claim. Returns claim ID.
        Insurance boxes 11-13 (primary), 9a-9d (secondary) are populated.
        Diagnosis pointers link service lines to diagnosis codes.
        """
        claim_payload: dict[str, Any] = {
            "patientId": patient_id,
            "claimType": "professional",    # CMS-1500
            "serviceDate": _fmt_date(data.service_date),
            "serviceDateEnd": _fmt_date(data.service_date_end),
            "placeOfService": data.place_of_service or "11",
            "facilityName": data.facility_name or "",
            "facilityNpi": data.facility_npi or "",
            "priorAuthNumber": data.prior_auth_number or "",
            "referralNumber": data.referral_number or "",
            "isAccidentRelated": data.accident_related,
            "accidentDate": _fmt_date(data.accident_date),
            "accidentState": data.accident_state or "",
        }

        # Primary insurance (Box 1-13)
        if data.primary_insurance:
            claim_payload["primaryInsurance"] = _insurance_payload(data.primary_insurance)

        # Secondary insurance (Box 9)
        if data.secondary_insurance:
            claim_payload["secondaryInsurance"] = _insurance_payload(data.secondary_insurance)

        # Diagnosis codes (Box 21, A-L, max 12)
        claim_payload["diagnosisCodes"] = [
            {
                "code": dx.icd10_code,
                "description": dx.description or "",
                "pointer": dx.pointer or (i + 1),
                "isPrimary": dx.is_primary,
            }
            for i, dx in enumerate(data.diagnoses[:12])
        ]

        # Referring provider (Box 17)
        if data.referring_provider:
            rp = data.referring_provider
            claim_payload["referringProvider"] = {
                "npi": rp.npi or "",
                "lastName": rp.last_name or rp.name,
                "firstName": rp.first_name or "",
                "qualifier": "DN",  # Referring provider
            }

        # Rendering provider (Box 31)
        if data.rendering_provider:
            ren = data.rendering_provider
            claim_payload["renderingProvider"] = {
                "npi": ren.npi or "",
                "lastName": ren.last_name or ren.name,
                "firstName": ren.first_name or "",
            }

        resp = self._http.post("/claims", json=claim_payload)
        resp.raise_for_status()
        claim_id = resp.json()["claimId"]

        # Add service lines (Box 24)
        if data.procedures:
            self._add_service_lines(claim_id, data.procedures)

        return claim_id

    def _add_service_lines(self, claim_id: str, procedures: list[ProcedureCode]) -> None:
        lines = [
            {
                "cptCode": proc.cpt_code,
                "modifier1": proc.modifier1 or "",
                "modifier2": proc.modifier2 or "",
                "description": proc.description or "",
                "units": proc.units,
                "charge": proc.charge or 0.0,
                "serviceDate": _fmt_date(proc.service_date),
                "placeOfService": proc.place_of_service or "11",
                "diagnosisPointers": proc.diagnosis_pointers or [1],
            }
            for proc in procedures
        ]
        resp = self._http.post(f"/claims/{claim_id}/lines", json={"lines": lines})
        resp.raise_for_status()

    def export_837p(self, data: ExtractedPatientData) -> str:
        """
        Generate an X12 837P EDI transaction set string for direct clearinghouse submission.
        This is useful when EzClaim's built-in EDI export is unavailable or for batch processing.

        Returns a minimal valid 837P string. For production, consider using
        a dedicated X12 library (e.g., pyx12) for full segment compliance.
        """
        p = data.patient
        today = date.today().strftime("%Y%m%d")
        dob = p.date_of_birth.strftime("%Y%m%d") if p.date_of_birth else ""
        dos = data.service_date.strftime("%Y%m%d") if data.service_date else today

        ins = data.primary_insurance
        payer_id = ins.payer_id if ins else "UNKNWN"
        member_id = ins.member_id if ins else ""

        rp = data.referring_provider
        rp_npi = rp.npi if rp and rp.npi else ""
        rp_last = rp.last_name if rp and rp.last_name else (rp.name if rp else "")
        rp_first = rp.first_name if rp and rp.first_name else ""

        dx_codes = "~".join(
            f"HI*ABK:{dx.icd10_code}" for dx in data.diagnoses[:12]
        )

        sv1_lines = "\n".join(
            f"SV1*HC:{proc.cpt_code}*{proc.charge or '0'}*UN*{proc.units}***"
            + ":".join(str(ptr) for ptr in (proc.diagnosis_pointers or [1]))
            for proc in data.procedures
        )

        edi = f"""ISA*00*          *00*          *ZZ*SUBMITTER       *ZZ*{payer_id:<15}*{today[:6]}*{today[6:]}*^*00501*000000001*0*P*:~
GS*HC*SUBMITTER*{payer_id}*{today}*{today[6:]}*1*X*005010X222A1~
ST*837*0001*005010X222A1~
BHT*0019*00*{data.document_id[:10]}*{today}*{today[6:]}*CH~
NM1*41*2*GCLIMB HEALTH*****XX*{rp_npi}~
PER*IC*EDI CONTACT*TE*0000000000~
NM1*40*2*{ins.payer_name if ins else 'PAYER'}*****XV*{payer_id}~
HL*1**20*1~
NM1*85*2*RENDERING PROVIDER*****XX*{rp_npi}~
HL*2*1*22*0~
SBR*P*18*{ins.group_number if ins else ''}**30***CI~
NM1*IL*1*{p.last_name}*{p.first_name}****MI*{member_id}~
DMG*D8*{dob}*{p.gender.value}~
NM1*PR*2*{ins.payer_name if ins else 'PAYER'}*****XV*{payer_id}~
CLM*{data.document_id[:15]}*0***{data.place_of_service or '11'}:B:1*Y*A*Y*I~
{dx_codes}
{sv1_lines}
SE*XX*0001~
GE*1*1~
IEA*1*000000001~"""
        return edi


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _fmt_date(d: Optional[date]) -> str:
    return d.isoformat() if d else ""


def _gender_to_ezclaim(gender: str) -> str:
    return {"M": "Male", "F": "Female", "O": "Unknown", "U": "Unknown"}.get(gender, "Unknown")


def _insurance_payload(ins: InsuranceInfo) -> dict:
    return {
        "payerName": ins.payer_name,
        "payerId": ins.payer_id or "",
        "memberId": ins.member_id,
        "groupNumber": ins.group_number or "",
        "groupName": ins.group_name or "",
        "planName": ins.plan_name or "",
        "planType": ins.plan_type or "",
        "relationshipToInsured": ins.relationship_to_insured.value,
        "insuredName": ins.insured_name or "",
        "effectiveDate": _fmt_date(ins.effective_date),
        "terminationDate": _fmt_date(ins.termination_date),
    }
