from pydantic import BaseModel, Field
from typing import List, Optional

from .choices import DepartmentCategory

class RouterDecision(BaseModel):
    """Router Agent output for request classification"""
    department: DepartmentCategory
    confidence: float = Field(..., description="Classification confidence 0.0-1.0", ge=0.0, le=1.0)
    urgency_indicators: List[str] = Field(default_factory=list, description="Emergency signals detected")
    reason: str = Field(..., description="Detailed reasoning for classification")
    keywords_detected: List[str] = Field(default_factory=list, description="Key phrases that influenced decision")
    degraded_mode_used: Optional[bool] = Field(default=False, description="Whether fallback rules were used")
    classification_source: Optional[str] = Field(default="llm", description="Source: llm or fallback")
