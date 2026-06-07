"""
Claude prompts for patient data extraction.
All prompts are designed for tool-use (structured JSON output) mode.
"""

SYSTEM_PROMPT = """You are a highly accurate medical data extraction specialist for a HIPAA-compliant healthcare platform.

Your task is to extract structured patient and clinical data from healthcare documents including:
- Referral letters and forms
- Prior authorization requests
- Lab reports and diagnostic results
- Discharge summaries and progress notes
- Prescription and medication lists
- Insurance cards and EOBs
- Fax cover sheets with patient information

Extraction rules:
1. Extract ALL fields you can find. Do not leave required fields blank if data exists in the document.
2. For ICD-10 codes: always include the full code with decimal (e.g., E11.65, not E11). If you see a description but no code, extract the description and note code_unknown=true.
3. For CPT codes: include all modifiers (e.g., 99213-25).
4. For NPI numbers: they are exactly 10 digits. Validate the format.
5. For dates: normalize to ISO 8601 (YYYY-MM-DD). If only partial date is available (e.g., "03/2024"), use the first of the month.
6. For diagnosis ordering: the first listed diagnosis is typically primary. Mark it is_primary=true.
7. Assign a confidence score (0.0-1.0) for each extracted field based on how clearly it appeared in the document. Fax artifacts, handwriting, or ambiguous text should reduce confidence.
8. If a field is completely absent from the document, omit it rather than guessing.
9. Never fabricate data. If you are unsure, lower the confidence score and note the uncertainty.
10. Identify the document type (referral, prior_authorization, lab_report, discharge_summary, progress_note, prescription, insurance_card, or unknown).

HIPAA reminder: You are processing Protected Health Information (PHI) under a Business Associate Agreement. Handle all data with appropriate care."""


EXTRACTION_TOOL = {
    "name": "extract_patient_data",
    "description": "Extract all structured patient and clinical data from the healthcare document",
    "input_schema": {
        "type": "object",
        "properties": {
            "document_type": {
                "type": "string",
                "enum": ["referral", "prior_authorization", "lab_report", "discharge_summary",
                         "progress_note", "prescription", "insurance_card", "unknown"],
                "description": "The type of healthcare document"
            },
            "patient": {
                "type": "object",
                "description": "Patient demographic information",
                "properties": {
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "middle_name": {"type": "string"},
                    "date_of_birth": {"type": "string", "description": "ISO 8601 date YYYY-MM-DD"},
                    "gender": {"type": "string", "enum": ["M", "F", "O", "U"]},
                    "ssn_last4": {"type": "string", "description": "Last 4 digits of SSN only"},
                    "mrn": {"type": "string", "description": "Medical Record Number"},
                    "phone": {"type": "string"},
                    "email": {"type": "string"},
                    "address": {
                        "type": "object",
                        "properties": {
                            "street1": {"type": "string"},
                            "street2": {"type": "string"},
                            "city": {"type": "string"},
                            "state": {"type": "string", "description": "2-letter state code"},
                            "zip_code": {"type": "string"}
                        }
                    }
                },
                "required": ["first_name", "last_name"]
            },
            "primary_insurance": {
                "type": "object",
                "description": "Primary insurance/payer information",
                "properties": {
                    "payer_name": {"type": "string"},
                    "payer_id": {"type": "string", "description": "Electronic payer ID for EDI"},
                    "member_id": {"type": "string"},
                    "group_number": {"type": "string"},
                    "group_name": {"type": "string"},
                    "plan_name": {"type": "string"},
                    "plan_type": {"type": "string", "description": "HMO, PPO, Medicare, Medicaid, CHIP, etc."},
                    "relationship_to_insured": {"type": "string", "enum": ["self", "spouse", "child", "other"]},
                    "insured_name": {"type": "string"},
                    "insured_dob": {"type": "string"},
                    "effective_date": {"type": "string"},
                    "termination_date": {"type": "string"},
                    "copay": {"type": "string"},
                    "deductible": {"type": "string"}
                }
            },
            "secondary_insurance": {
                "type": "object",
                "description": "Secondary insurance if present",
                "properties": {
                    "payer_name": {"type": "string"},
                    "payer_id": {"type": "string"},
                    "member_id": {"type": "string"},
                    "group_number": {"type": "string"},
                    "relationship_to_insured": {"type": "string", "enum": ["self", "spouse", "child", "other"]}
                }
            },
            "diagnoses": {
                "type": "array",
                "description": "List of diagnosis codes. First item is primary diagnosis.",
                "items": {
                    "type": "object",
                    "properties": {
                        "icd10_code": {"type": "string", "description": "ICD-10-CM code with decimal (e.g., E11.65)"},
                        "description": {"type": "string"},
                        "is_primary": {"type": "boolean"},
                        "pointer": {"type": "integer", "description": "Diagnosis pointer 1-12 for CMS-1500"},
                        "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                    },
                    "required": ["icd10_code"]
                }
            },
            "procedures": {
                "type": "array",
                "description": "CPT/HCPCS procedure codes from the document",
                "items": {
                    "type": "object",
                    "properties": {
                        "cpt_code": {"type": "string"},
                        "modifier1": {"type": "string"},
                        "modifier2": {"type": "string"},
                        "description": {"type": "string"},
                        "units": {"type": "integer", "default": 1},
                        "charge": {"type": "number"},
                        "service_date": {"type": "string"},
                        "place_of_service": {"type": "string"},
                        "diagnosis_pointers": {
                            "type": "array",
                            "items": {"type": "integer"}
                        },
                        "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                    },
                    "required": ["cpt_code"]
                }
            },
            "medications": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "dosage": {"type": "string"},
                        "frequency": {"type": "string"},
                        "route": {"type": "string"},
                        "is_current": {"type": "boolean", "default": True}
                    },
                    "required": ["name"]
                }
            },
            "lab_results": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "test_name": {"type": "string"},
                        "result_value": {"type": "string"},
                        "unit": {"type": "string"},
                        "reference_range": {"type": "string"},
                        "flag": {"type": "string", "enum": ["H", "L", "HH", "LL", "N", "A"]},
                        "collection_date": {"type": "string"}
                    },
                    "required": ["test_name"]
                }
            },
            "allergies": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of patient allergies"
            },
            "referring_provider": {
                "type": "object",
                "properties": {
                    "npi": {"type": "string", "description": "10-digit NPI"},
                    "name": {"type": "string"},
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "specialty": {"type": "string"},
                    "phone": {"type": "string"},
                    "fax": {"type": "string"},
                    "address": {
                        "type": "object",
                        "properties": {
                            "street1": {"type": "string"},
                            "city": {"type": "string"},
                            "state": {"type": "string"},
                            "zip_code": {"type": "string"}
                        }
                    }
                },
                "required": ["name"]
            },
            "rendering_provider": {
                "type": "object",
                "properties": {
                    "npi": {"type": "string"},
                    "name": {"type": "string"},
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "specialty": {"type": "string"},
                    "phone": {"type": "string"}
                }
            },
            "facility_name": {"type": "string"},
            "facility_npi": {"type": "string"},
            "service_date": {"type": "string", "description": "ISO 8601 date of service"},
            "service_date_end": {"type": "string"},
            "prior_auth_number": {"type": "string"},
            "referral_number": {"type": "string"},
            "place_of_service": {"type": "string", "description": "CMS POS code"},
            "accident_related": {"type": "boolean", "default": False},
            "accident_date": {"type": "string"},
            "accident_state": {"type": "string"},
            "chief_complaint": {"type": "string"},
            "reason_for_referral": {"type": "string"},
            "clinical_notes": {"type": "string", "description": "Key clinical findings, summary of relevant notes"},
            "overall_confidence": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": "Overall confidence in the extraction (0=very uncertain, 1=highly confident)"
            },
            "low_confidence_fields": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Names of fields where confidence < 0.7"
            }
        },
        "required": ["document_type", "patient", "overall_confidence"]
    }
}


def build_extraction_message(page_count: int) -> str:
    return (
        f"This is a {page_count}-page healthcare document. "
        "Please extract all patient data using the extract_patient_data tool. "
        "Be thorough — capture every field visible in the document. "
        "For any field that is unclear or partially legible, include your best reading and lower the confidence score."
    )
