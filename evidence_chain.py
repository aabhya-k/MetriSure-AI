from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class EvidenceRecord(BaseModel):
    evidence_id: str
    image_id: str
    declaration_type: str
    extracted_text: str
    confidence: float
    bbox: Optional[list[int]] = None

    rule_id: str
    status: str
    reason: str

    timestamp: str


def create_evidence_record(
    evidence_id,
    image_id,
    declaration_type,
    extracted_text,
    confidence,
    bbox,
    rule_id,
    status,
    reason
):
    return EvidenceRecord(
        evidence_id=evidence_id,
        image_id=image_id,
        declaration_type=declaration_type,
        extracted_text=extracted_text,
        confidence=confidence,
        bbox=bbox,
        rule_id=rule_id,
        status=status,
        reason=reason,
        timestamp=datetime.now().isoformat()
    )