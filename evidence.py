from pydantic import BaseModel
from typing import Optional


class Evidence(BaseModel):
    image_id: str
    declaration_type: str
    extracted_text: str
    bbox: Optional[list[int]] = None
    confidence: float
    rule_id: str
    reason: str