"""
Next-Steps Agent Service - Citizen communication with language support
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from .pydantic_models import NextStepsInput, NextStepsServiceOutput, ContactInfo
from .agent import NEXTSTEPS_AGENT

class NextStepsService:
    """
    Service for generating citizen communication in Urdu/English
    """

    @staticmethod
    def determine_message_format(criticality: str, trigger_output) -> str:
        """Determine optimal message format based on criticality and triggered actions"""
        if criticality.lower() == "critical":
            # Check if voice call is triggered
            voice_actions = [a for a in trigger_output.triggered_actions if a.action_type.value == "voice_call"]
            if voice_actions:
                return "voice"
            return "sms"
        elif criticality.lower() == "high":
            return "sms"
        else:
            return "email"

    @staticmethod
    def format_contact_info(entity_info, department_output) -> ContactInfo:
        """Format contact information for citizen"""
        return ContactInfo(
            primary_contact=entity_info.name,
            phone_number=entity_info.phone or "15 (Police) / 1122 (Rescue)",
            department_name=entity_info.department,
            address=entity_info.address,
            alternative_contact="15 (Police) / 1122 (Rescue)" if entity_info.phone else None
        )

    @staticmethod
    def generate_reference_number(entity_info, department_output) -> str:
        """Generate emergency reference number"""
        dept_code = department_output.criticality[:1].upper()
        entity_code = entity_info.id[:8] if entity_info.id else "EMRG"
        return f"{dept_code}-{entity_code}"

    @staticmethod
    def count_characters(text: str) -> int:
        """Count characters for SMS/message limits"""
        return len(text)

    @staticmethod
    def process_next_steps(input_data: NextStepsInput) -> NextStepsServiceOutput:
        """
        Generate citizen communication with next steps

        Args:
            input_data: NextStepsInput with complete emergency processing results

        Returns:
            NextStepsServiceOutput with formatted citizen communication
        """
        try:
            # Format contact information
            contact_info = NextStepsService.format_contact_info(
                input_data.entity_info,
                input_data.department_output
            )

            # Generate reference number
            reference_number = NextStepsService.generate_reference_number(
                input_data.entity_info,
                input_data.department_output
            )

            # Determine message format
            message_format = NextStepsService.determine_message_format(
                input_data.department_output.criticality,
                input_data.trigger_output
            )

            # Prepare agent input with all context
            agent_input = f"""
Emergency Processing Complete - Generate Citizen Communication

ORIGINAL REQUEST: {input_data.original_request}
LANGUAGE: {input_data.preferred_language}
CRITICALITY: {input_data.department_output.criticality}

DEPARTMENT RESPONSE:
- Assigned Department: {input_data.entity_info.name}
- Department Type: {input_data.entity_info.department}
- Contact: {input_data.entity_info.phone}
- Address: {input_data.entity_info.address}
- City: {input_data.entity_info.city}

ACTION PLAN:
Resolution Time: {input_data.department_output.action_plan.estimated_resolution_time}

Immediate Actions ({len(input_data.department_output.action_plan.immediate_actions)}):
{chr(10).join([f"{i+1}. {action.action} - {action.timeline} ({action.responsible_party})"
               for i, action in enumerate(input_data.department_output.action_plan.immediate_actions)])}

Follow-up Actions ({len(input_data.department_output.action_plan.follow_up_actions)}):
{chr(10).join([f"{i+1}. {action.action} - {action.timeline} ({action.responsible_party})"
               for i, action in enumerate(input_data.department_output.action_plan.follow_up_actions)])}

TRIGGERED ACTIONS: {input_data.trigger_output.execution_plan}
ESTIMATED TIME: {input_data.trigger_output.total_estimated_time}

REFERENCE NUMBER: {reference_number}
MESSAGE FORMAT: {message_format}

Please generate appropriate citizen communication in {input_data.preferred_language}.
"""

            # Call the agent
            agent_result = NEXTSTEPS_AGENT.run(input=agent_input)

            if hasattr(agent_result, 'content') and agent_result.content:
                agent_output = agent_result.content

                # Calculate character count for the main message
                character_count = NextStepsService.count_characters(agent_output.citizen_message)

                return NextStepsServiceOutput(
                    citizen_message=agent_output.citizen_message,
                    immediate_instructions=agent_output.immediate_instructions,
                    what_happens_next=agent_output.what_happens_next,
                    contact_info=contact_info,  # Use our formatted version
                    reference_number=reference_number,  # Use our generated version
                    expected_response_time=agent_output.expected_response_time,
                    safety_reminders=agent_output.safety_reminders,
                    # Programmatic fields
                    language_used=input_data.preferred_language,
                    message_format=message_format,
                    character_count=character_count,
                    success=True
                )
            else:
                # Fallback communication
                fallback_message = "Emergency logged. Help dispatched. Reference: " + reference_number
                if input_data.preferred_language == "urdu":
                    fallback_message = f"ایمرجنسی رجسٹر ہو گئی۔ مدد بھیجی جا رہی ہے۔ ریفرنس: {reference_number}"

                return NextStepsServiceOutput(
                    citizen_message=fallback_message,
                    immediate_instructions=[],
                    what_happens_next="Department will contact you shortly",
                    contact_info=contact_info,
                    reference_number=reference_number,
                    expected_response_time="Within 30 minutes",
                    safety_reminders=[],
                    language_used=input_data.preferred_language,
                    message_format=message_format,
                    character_count=len(fallback_message),
                    success=False,
                    error_message="No response from next-steps agent"
                )

        except Exception as e:
            # Error fallback
            error_message = f"System error. Call 15 (Police) or 1122 (Rescue). Ref: {input_data.entity_info.id[:8] if input_data.entity_info.id else 'ERR'}"
            if input_data.preferred_language == "urdu":
                error_message = f"سسٹم ایرر۔ 15 (پولیس) یا 1122 (ریسکیو) کال کریں۔ ریف: {input_data.entity_info.id[:8] if input_data.entity_info.id else 'ERR'}"

            return NextStepsServiceOutput(
                citizen_message=error_message,
                immediate_instructions=[],
                what_happens_next="Direct emergency contact required",
                contact_info=ContactInfo(
                    primary_contact="Emergency Services",
                    phone_number="15 / 1122",
                    department_name="Emergency"
                ),
                reference_number="ERROR",
                expected_response_time="Immediate",
                safety_reminders=[],
                language_used=input_data.preferred_language,
                message_format="sms",
                character_count=len(error_message),
                success=False,
                error_message=str(e)
            )


# Convenience function
def generate_citizen_communication(
    original_request: str,
    department_output,
    entity_info,
    trigger_output,
    user_phone: str = None,
    user_email: str = None,
    preferred_language: str = "english"
) -> NextStepsServiceOutput:
    """
    Convenience function to generate citizen communication

    Args:
        original_request: Original citizen request
        department_output: DepartmentOrchestratorServiceOutput
        entity_info: EntityInfo from matcher
        trigger_output: TriggerOrchestratorOutput
        user_phone: User's phone number
        user_email: User's email
        preferred_language: "english" or "urdu"

    Returns:
        NextStepsServiceOutput with formatted communication
    """
    input_data = NextStepsInput(
        original_request=original_request,
        department_output=department_output,
        entity_info=entity_info,
        trigger_output=trigger_output,
        user_phone=user_phone,
        user_email=user_email,
        preferred_language=preferred_language
    )

    return NextStepsService.process_next_steps(input_data)