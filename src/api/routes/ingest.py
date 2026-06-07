"""
Ingest routes: PDF upload and fax webhook endpoints.
All uploaded documents are stored temporarily and queued for extraction.
"""
from __future__ import annotations

import hashlib
import os
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import JSONResponse

from ...extraction.fax_processor import FaxPreprocessor, FaxWebhookHandler
from ...extraction.pdf_extractor import PDFExtractor
from ...extraction.schemas import ExtractionJob, ExtractionStatus
from ...utils.audit import audit

router = APIRouter(prefix="/ingest", tags=["ingest"])

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/tmp/gclimb_uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_SIZE_BYTES = int(os.getenv("MAX_PDF_SIZE_MB", "32")) * 1024 * 1024

# In-memory job store (replace with Redis/DB in production)
_jobs: dict[str, ExtractionJob] = {}

_extractor = PDFExtractor()
_fax_preprocessor = FaxPreprocessor()
_fax_handler = FaxWebhookHandler()


@router.post("/pdf", status_code=status.HTTP_202_ACCEPTED)
async def ingest_pdf(
    file: Annotated[UploadFile, File(description="PDF file to extract patient data from")],
) -> JSONResponse:
    """
    Upload a PDF (referral, fax, lab report, etc.) for patient data extraction.
    Returns a job ID to poll for results.
    """
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF files are accepted",
        )

    content = await file.read()
    if len(content) > MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {MAX_SIZE_BYTES // (1024*1024)} MB limit",
        )

    # Store with a content-addressed filename to deduplicate
    sha256 = hashlib.sha256(content).hexdigest()[:16]
    dest = UPLOAD_DIR / f"{sha256}_{file.filename}"
    dest.write_bytes(content)

    job = ExtractionJob(source_path=str(dest), source_type="pdf")
    _jobs[job.job_id] = job

    audit("DOCUMENT_INGESTED", job_id=job.job_id, extra={"filename": file.filename})

    # Run synchronously for now; swap for Celery task in production
    updated_job = _extractor.extract_from_file(dest, job)
    _jobs[updated_job.job_id] = updated_job

    audit(
        "EXTRACTION_COMPLETED" if updated_job.status != ExtractionStatus.FAILED else "EXTRACTION_FAILED",
        job_id=updated_job.job_id,
        confidence=updated_job.result.overall_confidence if updated_job.result else None,
        error=updated_job.error_message,
    )

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            "jobId": updated_job.job_id,
            "status": updated_job.status.value,
            "requiresReview": updated_job.result.requires_review if updated_job.result else True,
        },
    )


@router.post("/fax/documo", status_code=status.HTTP_200_OK)
async def ingest_fax_documo(request: Request) -> JSONResponse:
    """
    Webhook endpoint for Documo IDP fax delivery.
    Configure your Documo webhook to POST JSON to this endpoint.
    """
    payload = await request.json()
    filename, fax_bytes, content_type = _fax_handler.handle_documo(payload)
    return await _process_fax(filename, fax_bytes, content_type)


@router.post("/fax/twilio", status_code=status.HTTP_200_OK)
async def ingest_fax_twilio(request: Request) -> JSONResponse:
    """
    Webhook endpoint for Twilio Programmable Fax (receives TIFF images).
    Configure your Twilio Fax webhook to POST form data to this endpoint.
    """
    form = await request.form()
    form_dict = dict(form)
    filename, fax_bytes, content_type = _fax_handler.handle_twilio_fax(form_dict)
    return await _process_fax(filename, fax_bytes, content_type)


@router.post("/fax/generic", status_code=status.HTTP_202_ACCEPTED)
async def ingest_fax_generic(
    file: Annotated[UploadFile, File()],
) -> JSONResponse:
    """
    Generic fax file upload endpoint (TIFF, PDF, JPEG accepted).
    """
    content = await file.read()
    return await _process_fax(file.filename or "fax.pdf", content, file.content_type or "application/pdf")


async def _process_fax(filename: str, raw_bytes: bytes, content_type: str) -> JSONResponse:
    """Common fax processing path."""
    try:
        pdf_bytes = _fax_preprocessor.prepare_for_extraction(raw_bytes, content_type)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to process fax: {exc}",
        )

    job = ExtractionJob(source_type="fax")
    _jobs[job.job_id] = job

    audit("DOCUMENT_INGESTED", job_id=job.job_id, extra={"filename": filename, "source": "fax"})

    updated_job = _extractor.extract_from_bytes(pdf_bytes, filename, job)
    _jobs[updated_job.job_id] = updated_job

    audit(
        "EXTRACTION_COMPLETED" if updated_job.status != ExtractionStatus.FAILED else "EXTRACTION_FAILED",
        job_id=updated_job.job_id,
        confidence=updated_job.result.overall_confidence if updated_job.result else None,
    )

    return JSONResponse(
        content={
            "jobId": updated_job.job_id,
            "status": updated_job.status.value,
            "requiresReview": updated_job.result.requires_review if updated_job.result else True,
        }
    )


def get_job_store() -> dict[str, ExtractionJob]:
    """Expose the job store for use by other routes."""
    return _jobs
