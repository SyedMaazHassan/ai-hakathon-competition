"""
Next Steps Agent - Converts Department Agent action plans into actionable user steps
Takes department's technical response plan and converts to citizen-friendly actionable steps
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from pydantic import BaseModel, Field
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class NextStepsInput(BaseModel):
    """Input for Next Steps Agent"""
    user_request: str = Field(description="Original citizen request")
    department_response_plan: str = Field(description="Department's response plan from DepartmentAgent")
    required_user_actions: str = Field(description="Actions user needs to take from DepartmentAgent")
    criticality_level: str = Field(description="Critical, High, Medium, or Low")
    entity_name: str = Field(description="Assigned entity name")
    case_code: str = Field(description="Reference case code")
    incident_summary: str = Field(description="Incident summary from department")
    location_details: str = Field(description="Location information")

class NextStepsOutput(BaseModel):
    """Output from Next Steps Agent"""
    citizen_message: str = Field(description="Complete citizen-friendly message")
    actionable_steps: List[str] = Field(description="Clear actionable steps for citizen to take urgently")
    reference_number: str = Field(description="Case reference number")
    urgency_indicator: str = Field(description="Urgency level message")
    help_arriving_info: str = Field(description="Information about help being dispatched")
    success: bool = True
    error_message: Optional[str] = None

# =============================================================================
# NEXT STEPS AGENT SERVICE
# =============================================================================

class NextStepsAgentService:
    """
    Service to convert Department Agent technical outputs into actionable citizen steps
    """

    @staticmethod
    def generate_next_steps(input_data: NextStepsInput) -> NextStepsOutput:
        """Convert department response plan into actionable citizen steps"""
        try:
            # Parse department action plan and convert to citizen steps
            actionable_steps = NextStepsAgentService._extract_citizen_actions(
                input_data.required_user_actions,
                input_data.criticality_level
            )

            # Generate urgency indicator
            urgency_indicator = NextStepsAgentService._get_urgency_message(input_data.criticality_level)

            # Generate help arrival info
            help_info = NextStepsAgentService._get_help_arrival_info(
                input_data.criticality_level,
                input_data.entity_name
            )

            # Create comprehensive citizen message
            citizen_message = NextStepsAgentService._create_citizen_message(
                input_data,
                actionable_steps,
                urgency_indicator,
                help_info
            )

            return NextStepsOutput(
                citizen_message=citizen_message,
                actionable_steps=actionable_steps,
                reference_number=input_data.case_code,
                urgency_indicator=urgency_indicator,
                help_arriving_info=help_info,
                success=True
            )

        except Exception as e:
            logger.error(f"Next Steps Agent failed: {str(e)}")
            return NextStepsOutput(
                citizen_message=f"Emergency request processed. Reference: {input_data.case_code}. Help is being arranged.",
                actionable_steps=["Keep your phone available", "Stay at safe location", "Follow safety protocols"],
                reference_number=input_data.case_code,
                urgency_indicator="Request processed",
                help_arriving_info="Emergency services have been notified",
                success=False,
                error_message=str(e)
            )

    @staticmethod
    def _extract_citizen_actions(required_actions: str, criticality: str) -> List[str]:
        """Extract and format actionable steps from department's required actions"""

        # Parse department actions and convert to citizen-friendly format
        actions = []

        # Common actions based on criticality
        if criticality.lower() == "critical":
            actions.extend([
                "🚨 IMMEDIATE: Ensure your safety - move to secure location if threatened",
                "📞 Keep phone available - emergency responders will contact you",
                "⚠️ Do NOT leave the location unless unsafe - help is coming to you",
                "🆘 Call 1122 (Rescue) or 15 (Police) if situation worsens"
            ])
        elif criticality.lower() == "high":
            actions.extend([
                "📞 Keep your phone available - urgent response team will contact you",
                "📋 Prepare relevant documents or information if applicable",
                "🏠 Stay at reported location if safe to do so",
                "⏰ Response expected within 30 minutes"
            ])
        elif criticality.lower() == "medium":
            actions.extend([
                "📱 Keep phone available during business hours",
                "📄 Gather any supporting documents or evidence",
                "🕐 Expect contact within 2-4 hours during work hours"
            ])
        else:  # Low
            actions.extend([
                "📝 Keep your reference number safe",
                "📞 You'll be contacted during business hours",
                "🕐 Expect response within 24-48 hours"
            ])

        # Try to extract specific actions from department's required_actions text
        if "gather" in required_actions.lower() or "collect" in required_actions.lower():
            actions.append("📋 Gather all relevant documents and information")

        if "evidence" in required_actions.lower():
            actions.append("📸 Preserve any evidence (photos, documents, etc.)")

        if "witness" in required_actions.lower():
            actions.append("👥 Note contact details of any witnesses")

        if "medical" in required_actions.lower():
            actions.append("🏥 Seek immediate medical attention if injured")

        if "safe" in required_actions.lower():
            actions.append("🛡️ Prioritize your safety above all else")

        return actions[:6]  # Limit to 6 most important actions

    @staticmethod
    def _get_urgency_message(criticality: str) -> str:
        """Get urgency level message"""
        if criticality.lower() == "critical":
            return "🚨 CRITICAL EMERGENCY - Immediate action required"
        elif criticality.lower() == "high":
            return "⚠️ HIGH PRIORITY - Urgent response initiated"
        elif criticality.lower() == "medium":
            return "📋 MEDIUM PRIORITY - Processing during business hours"
        else:
            return "✅ LOW PRIORITY - Standard processing timeline"

    @staticmethod
    def _get_help_arrival_info(criticality: str, entity_name: str) -> str:
        """Get information about help being dispatched"""
        if criticality.lower() == "critical":
            return f"🚑 Emergency response from {entity_name} dispatched immediately"
        elif criticality.lower() == "high":
            return f"🚨 {entity_name} alerted for urgent response within 30 minutes"
        elif criticality.lower() == "medium":
            return f"📞 {entity_name} will contact you within 2-4 business hours"
        else:
            return f"📋 {entity_name} will process during regular business hours"

    @staticmethod
    def _create_citizen_message(input_data: NextStepsInput, actionable_steps: List[str],
                               urgency_indicator: str, help_info: str) -> str:
        """Create comprehensive citizen message"""

        message_parts = [
            f"📋 EMERGENCY REQUEST PROCESSED",
            f"Reference: {input_data.case_code}",
            "",
            f"🔍 YOUR REQUEST: {input_data.incident_summary}",
            f"📍 LOCATION: {input_data.location_details}",
            f"🏢 ASSIGNED TO: {input_data.entity_name}",
            "",
            urgency_indicator,
            help_info,
            "",
            "🎯 YOUR ACTIONABLE STEPS:",
        ]

        # Add numbered actionable steps
        for i, step in enumerate(actionable_steps, 1):
            message_parts.append(f"{i}. {step}")

        message_parts.extend([
            "",
            f"📞 Your case reference: {input_data.case_code}",
            "Keep this reference number for all communications."
        ])

        return "\n".join(message_parts)

# Convenience function
def generate_citizen_next_steps(
    user_request: str,
    department_response_plan: str,
    required_user_actions: str,
    criticality_level: str,
    entity_name: str,
    case_code: str,
    incident_summary: str,
    location_details: str
) -> NextStepsOutput:
    """Convenience function to generate next steps"""

    input_data = NextStepsInput(
        user_request=user_request,
        department_response_plan=department_response_plan,
        required_user_actions=required_user_actions,
        criticality_level=criticality_level,
        entity_name=entity_name,
        case_code=case_code,
        incident_summary=incident_summary,
        location_details=location_details
    )

    service = NextStepsAgentService()
    return service.generate_next_steps(input_data)