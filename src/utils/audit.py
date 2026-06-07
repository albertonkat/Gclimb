"""
HIPAA-compliant audit logging for PHI access and extraction events.

Every extraction job, validation step, approval, and EMR write is logged
with a structured JSON record (no PHI in the log — only identifiers,
timestamps, model version, and outcome).
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

AUDIT_LOG_PATH = os.getenv("AUDIT_LOG_PATH", "/tmp/gclimb_audit.jsonl")


class AuditLogger:
    """
    Append-only structured audit log for HIPAA access tracking.
    Records contain no PHI — only document IDs, job IDs, user IDs,
    action codes, and confidence metrics.
    """

    EVENTS = {
        "DOCUMENT_INGESTED": "A document was received and queued for extraction",
        "EXTRACTION_STARTED": "Claude API extraction job began",
        "EXTRACTION_COMPLETED": "Extraction completed successfully",
        "EXTRACTION_FAILED": "Extraction failed with error",
        "VALIDATION_PASSED": "Data validation passed all checks",
        "VALIDATION_FAILED": "Data validation found errors — requires review",
        "REVIEW_APPROVED": "Human reviewer approved extracted data",
        "REVIEW_REJECTED": "Human reviewer rejected extracted data",
        "NYMBLE_PUSH_STARTED": "Pushing data to Nymble EMR",
        "NYMBLE_PUSH_COMPLETED": "Data successfully written to Nymble EMR",
        "NYMBLE_PUSH_FAILED": "Failed to push data to Nymble EMR",
        "EZCLAIM_PUSH_STARTED": "Pushing claim to EzClaim",
        "EZCLAIM_PUSH_COMPLETED": "Claim successfully created in EzClaim",
        "EZCLAIM_PUSH_FAILED": "Failed to push claim to EzClaim",
        "NPI_VALIDATED": "Provider NPI verified against NPPES registry",
    }

    def __init__(self, log_path: Optional[str] = None) -> None:
        self._path = Path(log_path or AUDIT_LOG_PATH)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        event: str,
        job_id: str,
        document_id: Optional[str] = None,
        user_id: Optional[str] = None,
        model_version: Optional[str] = None,
        confidence: Optional[float] = None,
        extra: Optional[dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> None:
        record = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "event": event,
            "job_id": job_id,
            "document_id": document_id,
            "user_id": user_id,
            "model_version": model_version,
            "confidence": confidence,
            "error": error,
        }
        if extra:
            record.update(extra)

        record = {k: v for k, v in record.items() if v is not None}

        try:
            with self._path.open("a") as f:
                f.write(json.dumps(record) + "\n")
        except OSError as exc:
            logger.error("Failed to write audit log: %s", exc)


# Module-level singleton
_audit = AuditLogger()


def audit(event: str, **kwargs: Any) -> None:
    _audit.log(event, **kwargs)
