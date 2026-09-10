from pydantic import BaseModel
from typing import Optional


class Declaration(BaseModel):
    declaration_type: str
    value: str
    confidence: float
    bbox: Optional[list[int]] = None


class ComplianceResult(BaseModel):
    rule_id: str
    declaration_type: str
    status: str
    reason: str
    confidence: float 