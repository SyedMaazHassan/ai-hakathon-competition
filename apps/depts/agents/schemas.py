"""
Pydantic schemas for agent input/output - Clean and simple!
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# =============================================================================
# INPUT SCHEMAS
# =============================================================================

class UserRequestInput(BaseModel):
    """Initial user request"""
    request_text: str = Field(..., description="User's emergency description")
    user_city: Optional[str] = Field(None, description="User's current city")
    user_location: Optional[Dict[str, float]] = Field(None, description="GPS coordinates {lat, lng}")

class RouterInput(BaseModel):
    """Input to Router Agent"""
    request_text: str
    user_city: Optional[str] = None

class DepartmentAgentInput(BaseModel):
    """Input to Department Agent"""
    category: str
    request_text: str
    user_location: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None

class GuidanceAgentInput(BaseModel):
    """Input to Guidance Agent"""
    urgency: str
    actions_taken: List[Dict[str, Any]]
    assigned_entity: Optional[Dict[str, Any]] = None

class FollowUpAgentInput(BaseModel):
    """Input to Follow-up Agent"""
    case_code: str
    expected_response_time: str
    max_retries: int = 3

# =============================================================================
# OUTPUT SCHEMAS
# =============================================================================

class RouterOutput(BaseModel):
    """Router Agent output"""
    category: str = Field(..., description="Department category")
    confidence: float = Field(..., description="Confidence score 0-1")
    rationale: str = Field(..., description="Why this category was chosen")
    degraded_mode_used: bool = Field(False, description="Whether fallback was used")

class EntityInfo(BaseModel):
    """Information about assigned entity"""
    name: str
    phone: str
    city: str
    address: Optional[str] = None

class ActionPlan(BaseModel):
    """Action plan from Department Agent"""
    primary_action: str  # call, sms, email, booking
    fallback_action: Optional[str] = None
    call_script: Optional[str] = None
    sms_body: Optional[str] = None
    email_subject: Optional[str] = None
    email_body: Optional[str] = None

class DepartmentAgentOutput(BaseModel):
    """Department Agent output"""
    urgency: str  # low, medium, high, critical
    assigned_entity: EntityInfo
    action_plan: ActionPlan
    rationale: str

class ActionResult(BaseModel):
    """Result of executing an action"""
    action: str
    success: bool
    timestamp: str
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class GuidanceAgentOutput(BaseModel):
    """Guidance Agent output"""
    message_en: str
    message_ur: str
    next_steps: List[str]

class FollowUpAgentOutput(BaseModel):
    """Follow-up Agent output"""
    status: str  # pending, completed, escalated
    attempts: int
    actions_taken: List[ActionResult]
    next_step: Optional[str] = None

# =============================================================================
# MAIN PIPELINE SCHEMAS
# =============================================================================

class PipelineResult(BaseModel):
    """Complete pipeline result"""
    case_code: str
    success: bool
    router_result: RouterOutput
    department_result: Optional[DepartmentAgentOutput] = None
    execution_results: List[ActionResult] = []
    guidance_result: Optional[GuidanceAgentOutput] = None
    error_message: Optional[str] = None
    degraded_mode_used: bool = False
    processing_time_seconds: Optional[float] = None