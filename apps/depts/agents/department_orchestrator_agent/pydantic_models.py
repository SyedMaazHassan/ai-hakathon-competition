from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal
from apps.depts.agents.router_agent.pydantic_models import RouterDecision
from apps.depts.services.matcher_service import EntityInfo
from apps.depts.choices import UrgencyLevel

class ActionStep(BaseModel):
    """Individual action step in the plan"""
    step_number: int
    action: str
    timeline: str
    responsible_party: str

class ActionPlan(BaseModel):
    """Complete action plan with immediate and follow-up steps"""
    immediate_actions: List[ActionStep]
    follow_up_actions: List[ActionStep]
    estimated_resolution_time: str

class RequestPlan(BaseModel):
    """Simplified request plan for department communication - LLM value-add only"""
    incident_summary: str
    location_details: str
    additional_context: str
    required_response: str

class DepartmentOrchestratorInput(BaseModel):
    """Input for Department Orchestrator Agent"""
    original_request: str
    user_city: Optional[str] = None
    user_location: Optional[Dict[str, float]] = None
    router_decision: RouterDecision

class DepartmentOrchestratorOutput(BaseModel):
    """Output from Department Orchestrator Agent - LLM generated fields only"""
    criticality: Literal[UrgencyLevel.CRITICAL, UrgencyLevel.HIGH, UrgencyLevel.MEDIUM, UrgencyLevel.LOW]

    action_plan: ActionPlan
    request_plan: RequestPlan
    rationale: str

class DepartmentOrchestratorServiceOutput(BaseModel):
    """Complete service output - combines LLM output with programmatic fields"""
    # LLM generated fields
    criticality: Literal[UrgencyLevel.CRITICAL, UrgencyLevel.HIGH, UrgencyLevel.MEDIUM, UrgencyLevel.LOW]
    action_plan: ActionPlan
    request_plan: RequestPlan
    rationale: str

    # Programmatically determined fields
    assigned_entity: Optional[EntityInfo] = None
    communication_method: str  # Determined by criticality
    success: bool = True
    error_message: Optional[str] = None