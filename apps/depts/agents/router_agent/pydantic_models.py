from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal
from apps.depts.choices import DepartmentCategory

class RouterDecision(BaseModel):
    """Router Agent output for request classification"""
    department: Literal[
        DepartmentCategory.POLICE, DepartmentCategory.FIRE_BRIGADE,
        DepartmentCategory.AMBULANCE, DepartmentCategory.HEALTH,
        DepartmentCategory.CYBERCRIME, DepartmentCategory.DISASTER_MGMT,
        DepartmentCategory.OTHER
    ]
    confidence: float = Field(..., description="Classification confidence 0.0-1.0", ge=0.0, le=1.0)
    urgency_indicators: List[str] = Field(default_factory=list, description="Emergency signals detected")
    reason: str = Field(..., description="Detailed reasoning for classification")
    keywords_detected: List[str] = Field(default_factory=list, description="Key phrases that influenced decision")
    degraded_mode_used: Optional[bool] = Field(default=False, description="Whether fallback rules were used")
    classification_source: Optional[str] = Field(default="llm", description="Source: llm or fallback")


class RouterInput(BaseModel):
    """Initial user request"""
    request_text: str = Field(..., description="User's emergency description")
    user_city: Optional[str] = Field(None, description="User's current city")
    user_location: Optional[Dict[str, float]] = Field(None, description="GPS coordinates {lat, lng}")