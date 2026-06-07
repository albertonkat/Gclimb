"""
Extraction management routes:
  GET  /extraction/{job_id}         - get job status + extracted data
  GET  /extraction/pending          - list jobs awaiting human review
  POST /extraction/{job_id}/approve - approve and push to Nymble + EzClaim
  POST /extraction/{job_id}/reject  - reject with reason
"""
from __future__ import annotations

import os
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ...extraction.schemas import ExtractionStatus
from ...integrations.ezclaim import EzClaimClient
from ...integrations.nymble_emr import NymbleEMRClient
from ...utils.audit import audit
from ...validation.patient_validator import PatientDataValidator
from .ingest import get_job_store

router = APIRouter(prefix="/extraction", tags=["extraction"])

_validator = PatientDataValidator()
ENABLE_HUMAN_REVIEW = os.getenv("ENABLE_HUMAN_REVIEW_QUEUE", "true").lower() == "true"


class ApproveRequest(BaseModel):
    push_to_nymble: bool = True
    push_to_ezclaim: bool = True
    reviewer_id: Optional[str] = None


class RejectRequest(BaseModel):
    reason: str
    reviewer_id: Optional[str] = None


@router.get("/{job_id}")
async def get_extraction(job_id: str) -> JSONResponse:
    """Return the current status and extracted data for a job."""
    jobs = get_job_store()
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    response: dict[str, Any] = {
        "jobId": job.job_id,
        "status": job.status.value,
        "sourceType": job.source_type,
        "createdAt": job.created_at.isoformat(),
    }

    if job.result:
        response["result"] = job.result.model_dump(mode="json")
    if job.error_message:
        response["error"] = job.error_message

    return JSONResponse(content=response)


@router.get("/pending")
async def list_pending() -> JSONResponse:
    """List all jobs waiting for human review."""
    jobs = get_job_store()
    pending = [
        {
            "jobId": j.job_id,
            "status": j.status.value,
            "sourceType": j.source_type,
            "createdAt": j.created_at.isoformat(),
            "confidence": j.result.overall_confidence if j.result else None,
            "validationErrors": j.result.validation_errors if j.result else [],
            "lowConfidenceFields": j.result.low_confidence_fields if j.result else [],
        }
        for j in jobs.values()
        if j.status == ExtractionStatus.REVIEW_REQUIRED
    ]
    return JSONResponse(content={"pending": pending, "count": len(pending)})


@router.post("/{job_id}/validate")
async def validate_extraction(job_id: str) -> JSONResponse:
    """Run validation checks on extracted data without pushing to EMR."""
    jobs = get_job_store()
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if not job.result:
        raise HTTPException(status_code=400, detail="Job has no extracted result yet")

    validated = _validator.validate(job.result)
    job.result = validated
    jobs[job_id] = job

    audit(
        "VALIDATION_PASSED" if not validated.validation_errors else "VALIDATION_FAILED",
        job_id=job_id,
        document_id=validated.document_id,
        confidence=validated.overall_confidence,
        extra={"errors": validated.validation_errors},
    )

    return JSONResponse(
        content={
            "jobId": job_id,
            "validationErrors": validated.validation_errors,
            "requiresReview": validated.requires_review,
            "lowConfidenceFields": validated.low_confidence_fields,
        }
    )


@router.post("/{job_id}/approve")
async def approve_extraction(job_id: str, body: ApproveRequest) -> JSONResponse:
    """
    Approve extracted data and push to Nymble EMR and/or EzClaim.
    Requires ENABLE_HUMAN_REVIEW_QUEUE=true to be configured.
    """
    jobs = get_job_store()
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if not job.result:
        raise HTTPException(status_code=400, detail="No extracted data to approve")

    data = job.result
    results: dict[str, Any] = {}

    if body.push_to_nymble:
        try:
            audit("NYMBLE_PUSH_STARTED", job_id=job_id, document_id=data.document_id)
            nymble = NymbleEMRClient()
            patient_id = nymble.push_all(data)
            job.nymble_patient_id = patient_id
            results["nymble"] = {"patientId": patient_id, "status": "success"}
            audit("NYMBLE_PUSH_COMPLETED", job_id=job_id, extra={"nymble_patient_id": patient_id})
        except Exception as exc:
            results["nymble"] = {"status": "failed", "error": str(exc)}
            audit("NYMBLE_PUSH_FAILED", job_id=job_id, error=str(exc))

    if body.push_to_ezclaim:
        try:
            audit("EZCLAIM_PUSH_STARTED", job_id=job_id, document_id=data.document_id)
            ezclaim = EzClaimClient()
            patient_id, claim_id = ezclaim.push_all(data)
            job.ezclaim_claim_id = claim_id
            results["ezclaim"] = {"patientId": patient_id, "claimId": claim_id, "status": "success"}
            audit("EZCLAIM_PUSH_COMPLETED", job_id=job_id, extra={"claim_id": claim_id})
        except Exception as exc:
            results["ezclaim"] = {"status": "failed", "error": str(exc)}
            audit("EZCLAIM_PUSH_FAILED", job_id=job_id, error=str(exc))

    job.result.status = ExtractionStatus.APPROVED
    job.status = ExtractionStatus.APPROVED
    jobs[job_id] = job

    audit(
        "REVIEW_APPROVED",
        job_id=job_id,
        user_id=body.reviewer_id,
        document_id=data.document_id,
    )

    return JSONResponse(content={"jobId": job_id, "status": "approved", "integrations": results})


@router.post("/{job_id}/reject")
async def reject_extraction(job_id: str, body: RejectRequest) -> JSONResponse:
    """Mark an extraction as rejected with a reason."""
    jobs = get_job_store()
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.status = ExtractionStatus.REJECTED
    if job.result:
        job.result.status = ExtractionStatus.REJECTED
    jobs[job_id] = job

    audit(
        "REVIEW_REJECTED",
        job_id=job_id,
        user_id=body.reviewer_id,
        extra={"reason": body.reason},
    )

    return JSONResponse(content={"jobId": job_id, "status": "rejected", "reason": body.reason})


@router.get("/{job_id}/edi")
async def export_837p(job_id: str) -> JSONResponse:
    """Export the extracted claim as an X12 837P EDI string for clearinghouse submission."""
    jobs = get_job_store()
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if not job.result:
        raise HTTPException(status_code=400, detail="No extracted data")

    ezclaim = EzClaimClient()
    edi_str = ezclaim.export_837p(job.result)
    return JSONResponse(content={"jobId": job_id, "edi837p": edi_str})
