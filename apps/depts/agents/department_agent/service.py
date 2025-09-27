"""
Department Agent Service - Main Orchestrator
Task 7: Creates action plans and coordinates response
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from apps.depts.agents.router_agent.pydantic_models import RouterDecision
from apps.depts.services.matcher_service import match_entity, EntityInfo

# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class ActionStep(BaseModel):
    """Individual action step"""
    step_number: int
    action: str
    timeline: str
    responsible_party: str

class ActionPlan(BaseModel):
    """Complete action plan"""
    immediate_actions: List[ActionStep]
    follow_up_actions: List[ActionStep]
    estimated_resolution_time: str

class DepartmentAgentInput(BaseModel):
    """Input for Department Agent"""
    router_decision: RouterDecision
    user_city: Optional[str] = None
    user_location: Optional[Dict[str, float]] = None

class DepartmentAgentOutput(BaseModel):
    """Department Agent output with action plan"""
    urgency: str  # low, medium, high, critical
    assigned_entity: EntityInfo
    action_plan: ActionPlan
    rationale: str
    success: bool
    error_message: Optional[str] = None

# =============================================================================
# DEPARTMENT AGENT SERVICE
# =============================================================================

class DepartmentAgentService:

    @staticmethod
    def assess_urgency(router_decision: RouterDecision) -> str:
        """Assess urgency level based on router decision"""

        # Critical urgency keywords
        critical_keywords = [
            "chest pain", "heart attack", "breathing", "unconscious", "bleeding",
            "fire", "trapped", "explosion", "bomb", "terrorist", "armed",
            "shooting", "stabbing", "drowning", "cardiac arrest"
        ]

        # High urgency keywords
        high_keywords = [
            "accident", "injury", "pain", "emergency", "urgent", "robbery",
            "theft", "assault", "domestic violence", "gas leak", "electrical"
        ]

        # Check for critical indicators
        urgency_text = " ".join(router_decision.urgency_indicators + router_decision.keywords_detected).lower()

        if any(keyword in urgency_text for keyword in critical_keywords):
            return "critical"
        elif any(keyword in urgency_text for keyword in high_keywords):
            return "high"
        elif router_decision.confidence > 0.8:
            return "medium"
        else:
            return "low"

    @staticmethod
    def create_action_plan(urgency: str, department: str, entity: EntityInfo) -> ActionPlan:
        """Create action plan based on urgency and department"""

        # Action plans by department and urgency
        action_templates = {
            "health": {
                "critical": {
                    "immediate": [
                        {"step": 1, "action": f"Call {entity.name} immediately at {entity.phone}", "timeline": "0-2 minutes", "party": "Citizen"},
                        {"step": 2, "action": "Dispatch ambulance to location", "timeline": "2-5 minutes", "party": entity.name},
                        {"step": 3, "action": "Prepare emergency medical response", "timeline": "5-15 minutes", "party": entity.name}
                    ],
                    "follow_up": [
                        {"step": 1, "action": "Monitor patient status", "timeline": "15-30 minutes", "party": entity.name},
                        {"step": 2, "action": "Coordinate with hospital", "timeline": "30-60 minutes", "party": entity.name}
                    ],
                    "resolution": "15-30 minutes"
                }
            },
            "fire_brigade": {
                "critical": {
                    "immediate": [
                        {"step": 1, "action": f"Contact {entity.name} fire station at {entity.phone}", "timeline": "0-1 minute", "party": "Citizen"},
                        {"step": 2, "action": "Dispatch fire trucks and rescue team", "timeline": "1-3 minutes", "party": entity.name},
                        {"step": 3, "action": "Evacuate surrounding area if needed", "timeline": "3-10 minutes", "party": entity.name}
                    ],
                    "follow_up": [
                        {"step": 1, "action": "Investigate fire cause", "timeline": "1-2 hours", "party": entity.name},
                        {"step": 2, "action": "Submit incident report", "timeline": "2-24 hours", "party": entity.name}
                    ],
                    "resolution": "30-60 minutes"
                }
            },
            "police": {
                "high": {
                    "immediate": [
                        {"step": 1, "action": f"Call {entity.name} station at {entity.phone}", "timeline": "0-2 minutes", "party": "Citizen"},
                        {"step": 2, "action": "Dispatch patrol unit", "timeline": "2-10 minutes", "party": entity.name},
                        {"step": 3, "action": "Secure crime scene", "timeline": "10-20 minutes", "party": entity.name}
                    ],
                    "follow_up": [
                        {"step": 1, "action": "Record FIR and evidence", "timeline": "20-60 minutes", "party": entity.name},
                        {"step": 2, "action": "Begin investigation", "timeline": "1-24 hours", "party": entity.name}
                    ],
                    "resolution": "20-60 minutes"
                }
            }
        }

        # Get template or use default
        dept_templates = action_templates.get(department, {})
        urgency_template = dept_templates.get(urgency)

        if not urgency_template:
            # Default fallback plan
            immediate_actions = [
                ActionStep(
                    step_number=1,
                    action=f"Contact {entity.name} at {entity.phone}",
                    timeline="0-5 minutes",
                    responsible_party="Citizen"
                ),
                ActionStep(
                    step_number=2,
                    action="Explain situation and request assistance",
                    timeline="5-10 minutes",
                    responsible_party="Citizen"
                )
            ]
            follow_up_actions = [
                ActionStep(
                    step_number=1,
                    action="Follow department instructions",
                    timeline="10-30 minutes",
                    responsible_party="Citizen"
                )
            ]
            estimated_resolution = "30-60 minutes"
        else:
            immediate_actions = [
                ActionStep(
                    step_number=step["step"],
                    action=step["action"],
                    timeline=step["timeline"],
                    responsible_party=step["party"]
                ) for step in urgency_template["immediate"]
            ]
            follow_up_actions = [
                ActionStep(
                    step_number=step["step"],
                    action=step["action"],
                    timeline=step["timeline"],
                    responsible_party=step["party"]
                ) for step in urgency_template["follow_up"]
            ]
            estimated_resolution = urgency_template["resolution"]

        return ActionPlan(
            immediate_actions=immediate_actions,
            follow_up_actions=follow_up_actions,
            estimated_resolution_time=estimated_resolution
        )

    @staticmethod
    def process_request(input_data: DepartmentAgentInput) -> DepartmentAgentOutput:
        """Main orchestrator function - processes citizen request"""
        try:
            router_decision = input_data.router_decision

            # Step 1: Find best entity using Matcher Service
            matcher_result = match_entity(
                department_category=router_decision.department,
                user_city=input_data.user_city,
                user_location=input_data.user_location
            )

            if not matcher_result.success:
                return DepartmentAgentOutput(
                    urgency="unknown",
                    assigned_entity=None,
                    action_plan=None,
                    rationale=f"Could not find suitable entity: {matcher_result.error_message}",
                    success=False,
                    error_message=matcher_result.error_message
                )

            # Step 2: Assess urgency
            urgency = DepartmentAgentService.assess_urgency(router_decision)

            # Step 3: Create action plan
            action_plan = DepartmentAgentService.create_action_plan(
                urgency, router_decision.department, matcher_result.matched_entity
            )

            # Step 4: Generate rationale
            rationale = f"""
Request classified as {router_decision.department} with {router_decision.confidence:.2f} confidence.
Urgency assessed as {urgency} based on indicators: {', '.join(router_decision.urgency_indicators)}.
Assigned to {matcher_result.matched_entity.name} in {matcher_result.matched_entity.city}
using {matcher_result.match_strategy} strategy.
Expected resolution: {action_plan.estimated_resolution_time}.
            """.strip()

            return DepartmentAgentOutput(
                urgency=urgency,
                assigned_entity=matcher_result.matched_entity,
                action_plan=action_plan,
                rationale=rationale,
                success=True
            )

        except Exception as e:
            return DepartmentAgentOutput(
                urgency="unknown",
                assigned_entity=None,
                action_plan=None,
                rationale=f"Department Agent processing error: {str(e)}",
                success=False,
                error_message=str(e)
            )

# =============================================================================
# SIMPLE FUNCTION INTERFACE
# =============================================================================

def process_citizen_request(router_decision: RouterDecision,
                          user_city: str = None,
                          user_location: dict = None) -> DepartmentAgentOutput:
    """Simple function interface for processing citizen requests"""

    input_data = DepartmentAgentInput(
        router_decision=router_decision,
        user_city=user_city,
        user_location=user_location
    )

    return DepartmentAgentService.process_request(input_data)