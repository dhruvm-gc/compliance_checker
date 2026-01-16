from pydantic import BaseModel
from typing import List

class ComplianceRequest(BaseModel):
    doc_name: str
    document_text: str
    top_k: int = 4

class ClauseResult(BaseModel):
    clause: str
    matched_rules: List[str]
    status: str
    explanation: str
    suggested_fix: str

class ComplianceResponse(BaseModel):
    doc_name: str
    results: List[ClauseResult]
