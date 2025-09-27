"""
Next-Steps Agent - Pydantic models for citizen communication
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from apps.depts.services.matcher_service import EntityInfo
from apps.depts.agents.department_orchestrator_agent.pydantic_models import DepartmentOrchestratorServiceOutput
from apps.depts.services.trigger_orchestrator_service import TriggerOrchestratorOutput

class NextStepsInput(BaseModel):
    """Input for Next-Steps Agent"""
    original_request: str
    department_output: DepartmentOrchestratorServiceOutput
    entity_info: EntityInfo
    trigger_output: TriggerOrchestratorOutput
    user_phone: Optional[str] = None
    user_email: Optional[str] = None
    preferred_language: str = "english"  # "english" or "urdu"

class CitizenInstruction(BaseModel):
    """Individual instruction for citizen"""
    step_number: int
    instruction: str
    timeline: str
    is_urgent: bool = False

class ContactInfo(BaseModel):
    """Contact information formatted for citizen"""
    primary_contact: str
    phone_number: str
    department_name: str
    address: Optional[str] = None
    alternative_contact: Optional[str] = None

class NextStepsOutput(BaseModel):
    """LLM-generated next steps for citizen communication"""
    citizen_message: str = Field(..., description="Main message for citizen in chosen language")
    immediate_instructions: List[CitizenInstruction] = Field(..., description="Steps citizen should take immediately")
    what_happens_next: str = Field(..., description="What the department will do")
    contact_info: ContactInfo = Field(..., description="Formatted contact information")
    reference_number: str = Field(..., description="Emergency reference for citizen")
    expected_response_time: str = Field(..., description="When citizen can expect help")
    safety_reminders: List[str] = Field(default_factory=list, description="Safety tips while waiting")

class NextStepsServiceOutput(BaseModel):
    """Complete service output with both LLM and programmatic fields"""
    citizen_message: str
    immediate_instructions: List[CitizenInstruction]
    what_happens_next: str
    contact_info: ContactInfo
    reference_number: str
    expected_response_time: str
    safety_reminders: List[str]
    # Programmatic fields
    language_used: str
    message_format: str  # "sms", "email", "voice"
    character_count: int
    success: bool = True
    error_message: Optional[str] = None