"""
Department Orchestrator Agent Service - Clean service for department-specific processing
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

import json
from typing import Optional
from .pydantic_models import (
    DepartmentOrchestratorInput, DepartmentOrchestratorOutput,
    DepartmentOrchestratorServiceOutput, ActionPlan, ActionStep, RequestPlan
)
from .agent import get_specialized_agent, is_department_supported

class DepartmentOrchestratorService:
    """
    Service for processing department-specific requests using specialized agents
    """

    @staticmethod
    def determine_communication_method(criticality: str) -> str:
        """Determine communication method based on criticality level"""
        communication_mapping = {
            "critical": "CALL",
            "high": "SMS",
            "medium": "EMAIL",
            "low": "EMAIL"
        }
        return communication_mapping.get(criticality.lower(), "EMAIL")

    @staticmethod
    def process_request(input_data: DepartmentOrchestratorInput) -> DepartmentOrchestratorServiceOutput:
        """
        Process citizen request using the appropriate specialized department agent

        Args:
            input_data: DepartmentOrchestratorInput with router decision and request details

        Returns:
            DepartmentOrchestratorServiceOutput with criticality, action plan, and programmatic fields
        """
        try:
            department_category = input_data.router_decision.department

            # Check if department category is OTHER (unsupported)
            from apps.depts.choices import DepartmentCategory
            if department_category == DepartmentCategory.OTHER:
                # Create a fallback action plan and request plan
                fallback_action_plan = ActionPlan(
                    immediate_actions=[
                        ActionStep(
                            step_number=1,
                            action="Contact general emergency services at 15 (Police) or 1122 (Rescue)",
                            timeline="0-5 minutes",
                            responsible_party="Citizen"
                        )
                    ],
                    follow_up_actions=[
                        ActionStep(
                            step_number=1,
                            action="Wait for system support for this department category",
                            timeline="Future updates",
                            responsible_party="System"
                        )
                    ],
                    estimated_resolution_time="Manual intervention required"
                )

                fallback_request_plan = RequestPlan(
                    incident_summary=f"Request for unsupported department category",
                    location_details=f"User City: {input_data.user_city or 'Not provided'}",
                    additional_context=f"Original request: {input_data.original_request}. Router reason: {input_data.router_decision.reason}",
                    required_response="Manual handling required - please direct to appropriate department"
                )

                return DepartmentOrchestratorOutput(
                    criticality="medium",
                    action_plan=fallback_action_plan,
                    request_plan=fallback_request_plan,
                    rationale=f"Department category '{department_category}' is not currently supported",
                    success=False,
                    error_message=f"Unsupported department category: {department_category}",
                    assigned_entity=None
                )

            # Get the specialized agent for this department
            specialized_agent = get_specialized_agent(department_category)
            if not specialized_agent:
                # Create a fallback action plan
                fallback_plan = ActionPlan(
                    immediate_actions=[
                        ActionStep(
                            step_number=1,
                            action="Contact general emergency services for assistance",
                            timeline="0-5 minutes",
                            responsible_party="Citizen"
                        )
                    ],
                    follow_up_actions=[],
                    estimated_resolution_time="Agent not available"
                )

                return DepartmentOrchestratorOutput(
                    criticality="medium",
                    action_plan=fallback_plan,
                    rationale=f"No specialized agent found for department: {department_category}",
                    success=False,
                    error_message=f"Agent not available for department: {department_category}",
                    assigned_entity=None
                )

            # Call the specialized agent with Pydantic input
            agent_result = specialized_agent.run(input=input_data)

            # Get the Pydantic output directly (no parsing needed)
            if hasattr(agent_result, 'content') and agent_result.content:
                agent_output = agent_result.content

                # Agent output is LLM-generated, add programmatic fields
                communication_method = DepartmentOrchestratorService.determine_communication_method(
                    agent_output.criticality
                )

                return DepartmentOrchestratorServiceOutput(
                    criticality=agent_output.criticality,
                    action_plan=agent_output.action_plan,
                    request_plan=agent_output.request_plan,
                    rationale=agent_output.rationale,
                    assigned_entity=None,  # Will be set by pipeline service
                    communication_method=communication_method,
                    success=True
                )
            else:
                # Create a fallback action plan for empty responses
                fallback_plan = ActionPlan(
                    immediate_actions=[
                        ActionStep(
                            step_number=1,
                            action="Contact emergency services directly",
                            timeline="0-5 minutes",
                            responsible_party="Citizen"
                        )
                    ],
                    follow_up_actions=[],
                    estimated_resolution_time="No agent response"
                )

                return DepartmentOrchestratorOutput(
                    criticality="medium",
                    action_plan=fallback_plan,
                    rationale="No response from specialized agent",
                    success=False,
                    error_message="Empty response from specialized agent",
                    assigned_entity=None
                )

        except Exception as e:
            # Create a fallback action plan for exceptions
            fallback_plan = ActionPlan(
                immediate_actions=[
                    ActionStep(
                        step_number=1,
                        action="Contact emergency services directly for immediate assistance",
                        timeline="0-5 minutes",
                        responsible_party="Citizen"
                    )
                ],
                follow_up_actions=[],
                estimated_resolution_time="System error occurred"
            )

            return DepartmentOrchestratorOutput(
                criticality="medium",
                action_plan=fallback_plan,
                rationale=f"Department orchestrator processing error: {str(e)}",
                success=False,
                error_message=str(e),
                assigned_entity=None
            )



# Convenience function for easy import
def process_department_request(
    original_request: str,
    router_decision,
    user_city: str = None,
    user_location: dict = None
) -> DepartmentOrchestratorOutput:
    """
    Convenience function to process department request

    Args:
        original_request: Original citizen request text
        router_decision: RouterDecision from router agent
        user_city: User's city name
        user_location: User's coordinates

    Returns:
        DepartmentOrchestratorOutput
    """
    input_data = DepartmentOrchestratorInput(
        original_request=original_request,
        router_decision=router_decision,
        user_city=user_city,
        user_location=user_location
    )

    return DepartmentOrchestratorService.process_request(input_data)