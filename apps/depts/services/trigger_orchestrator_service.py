"""
Trigger Orchestrator Service - Maps criticality to intelligent actions
This is the "wow factor" component that will impress judges
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from pydantic import BaseModel, Field
from typing import List, Optional, Union, Dict, Any
from enum import Enum
from apps.depts.agents.department_orchestrator_agent.pydantic_models import DepartmentOrchestratorServiceOutput
from apps.depts.services.matcher_service import EntityInfo
from apps.depts.agents.router_agent.pydantic_models import RouterDecision
from apps.depts.choices import ActionType, UrgencyLevel, CallStatus, AppointmentStatus
from apps.depts.services.actions.vapi_call_agent import EmergencyCallAgent

# =============================================================================
# TRIGGER-SPECIFIC ACTION TYPES (synced with database)
# =============================================================================

class TriggerActionType(str, Enum):
    """Available trigger action types for emergency response"""
    EMAIL = ActionType.EMAIL_SENT  # "email" from database
    SMS = ActionType.SMS_SENT      # "sms" from database
    VOICE_CALL = ActionType.EMERGENCY_CALL  # "call" from database
    EMERGENCY_BROADCAST = ActionType.EMERGENCY_BROADCAST  # "emergency_broadcast" from database
    FOLLOWUP_SCHEDULE = ActionType.FOLLOWUP_SCHEDULE      # "followup_schedule" from database

class ActionPriority(str, Enum):
    """Action execution priority - synced with UrgencyLevel"""
    IMMEDIATE = UrgencyLevel.CRITICAL    # "critical" from database
    URGENT = UrgencyLevel.HIGH           # "high" from database
    NORMAL = UrgencyLevel.MEDIUM         # "medium" from database
    SCHEDULED = UrgencyLevel.LOW         # "low" from database

class BaseAction(BaseModel):
    """Base action model"""
    action_type: TriggerActionType
    priority: ActionPriority
    title: str
    description: str
    estimated_duration: str
    requires_user_input: bool = False

class EmailAction(BaseAction):
    """Email notification action"""
    recipient_email: str
    subject: str
    body: str
    department_cc: Optional[str] = None
    action_type: TriggerActionType = TriggerActionType.EMAIL

class SMSAction(BaseAction):
    """SMS notification action"""
    recipient_phone: str
    message: str
    sender_name: str = "Emergency Services"
    action_type: TriggerActionType = TriggerActionType.SMS

class VoiceCallAction(BaseAction):
    """Voice call action using VAPI"""
    recipient_phone: str
    call_script: str
    max_duration_minutes: int = 5
    action_type: TriggerActionType = TriggerActionType.VOICE_CALL

# Maps and Calendar actions removed to simplify system

class EmergencyBroadcastAction(BaseAction):
    """Broadcast to multiple channels simultaneously"""
    broadcast_message: str
    channels: List[str]  # ["sms", "email", "push_notification"]
    target_contacts: List[str]
    action_type: TriggerActionType = TriggerActionType.EMERGENCY_BROADCAST

class FollowupScheduleAction(BaseAction):
    """Schedule automated follow-up"""
    followup_time_hours: int
    followup_message: str
    followup_method: str  # sms, email, call
    action_type: TriggerActionType = TriggerActionType.FOLLOWUP_SCHEDULE

# Union type for all actions
TriggerAction = Union[
    EmailAction, SMSAction, VoiceCallAction, EmergencyBroadcastAction,
    FollowupScheduleAction
]

class TriggerOrchestratorInput(BaseModel):
    """Input for Trigger Orchestrator"""
    department_output: DepartmentOrchestratorServiceOutput
    entity_info: EntityInfo
    router_decision: RouterDecision
    user_phone: Optional[str] = None
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    user_coordinates: Optional[Dict[str, float]] = None

class TriggerOrchestratorOutput(BaseModel):
    """Output with orchestrated actions"""
    triggered_actions: List[TriggerAction]
    execution_plan: str
    total_estimated_time: str
    success: bool = True
    error_message: Optional[str] = None

# =============================================================================
# TRIGGER ORCHESTRATOR SERVICE
# =============================================================================

class TriggerOrchestratorService:
    """
    Orchestrates intelligent actions based on criticality and context
    This creates the "wow factor" by showing smart emergency response
    """

    @staticmethod
    def determine_actions_by_criticality(
        criticality: str,
        department_output: DepartmentOrchestratorServiceOutput,
        entity_info: EntityInfo,
        router_decision: RouterDecision,
        user_phone: str = None,
        user_email: str = None,
        user_coordinates: Dict[str, float] = None,
        user_name: str = None
    ) -> List[TriggerAction]:
        """Map criticality to intelligent action combinations"""

        actions = []

        if criticality.lower() == "critical":
            # CRITICAL: Immediate multi-channel response

            # 1. Immediate voice call to entity
            if entity_info.phone:
                actions.append(VoiceCallAction(
                    priority=ActionPriority.IMMEDIATE,
                    title="Emergency Voice Alert",
                    description=f"Immediate call to {entity_info.name}",
                    estimated_duration="1-2 minutes",
                    recipient_phone=entity_info.phone,
                    call_script=f"CRITICAL EMERGENCY: {department_output.request_plan.incident_summary}. "
                               f"Location: {department_output.request_plan.location_details}. "
                               f"Immediate response required.",
                    max_duration_minutes=3
                ))

                call_agent = EmergencyCallAgent()

                # Make an emergency call
                call_result = call_agent.make_emergency_call(
                    phone_number=entity_info.phone,
                    call_reason=department_output.request_plan.incident_summary,
                    additional_context={
                        "case_code": department_output.request_plan.case_code,
                        "emergency_type": department_output.request_plan.incident_summary,
                        "location": department_output.request_plan.location_details,
                        "urgency_level": department_output.criticality,
                        "additional_notes": department_output.request_plan.additional_context
                    }
                )
                print(call_result)


            # 2. Emergency SMS to user
            if user_phone:
                user_greeting = f"Hello {user_name}, " if user_name else ""
                actions.append(SMSAction(
                    priority=ActionPriority.IMMEDIATE,
                    title="Citizen Emergency SMS",
                    description="Immediate confirmation and instructions",
                    estimated_duration="30 seconds",
                    recipient_phone=user_phone,
                    message=f"🚨 {user_greeting}EMERGENCY LOGGED: {entity_info.name} has been contacted immediately. "
                           f"Stay safe. Help is on the way. Ref: {entity_info.id[:8]}"
                ))

            # 3. Email alert to department for documentation
            if user_email:
                actions.append(EmailAction(
                    priority=ActionPriority.URGENT,
                    title="Emergency Documentation Email",
                    description=f"Detailed incident report to {entity_info.name}",
                    estimated_duration="30 seconds",
                    recipient_email=f"emergency@{entity_info.city.lower()}.gov",
                    subject=f"CRITICAL EMERGENCY - {department_output.request_plan.incident_summary}",
                    body=f"CRITICAL EMERGENCY REPORT\\n\\n"
                         f"Incident: {department_output.request_plan.incident_summary}\\n"
                         f"Location: {department_output.request_plan.location_details}\\n"
                         f"Contact: {user_name or 'Citizen'} - {user_phone or user_email}\\n"
                         f"Additional Context: {department_output.request_plan.additional_context}\\n"
                         f"Response Required: {department_output.request_plan.required_response}"
                ))

            # 3b. User alert email with action plan (CRITICAL level)
            if user_email:
                immediate_steps = "\\n".join([f"{step.step_number}. {step.action} - {step.timeline}"
                                            for step in department_output.action_plan.immediate_actions])
                follow_up_steps = "\\n".join([f"{step.step_number}. {step.action} - {step.timeline}"
                                            for step in department_output.action_plan.follow_up_actions])

                actions.append(EmailAction(
                    priority=ActionPriority.URGENT,
                    title="Critical Emergency Action Plan",
                    description=f"Action plan details for {user_name or 'Citizen'}",
                    estimated_duration="30 seconds",
                    recipient_email=user_email,
                    subject=f"🚨 CRITICAL EMERGENCY - Action Plan for Your Request",
                    body=f"Dear {user_name or 'Citizen'},\\n\\n"
                         f"🚨 CRITICAL EMERGENCY RESPONSE ACTIVATED\\n\\n"
                         f"Your emergency: {department_output.request_plan.incident_summary}\\n"
                         f"Location: {department_output.request_plan.location_details}\\n\\n"
                         f"IMMEDIATE ACTIONS BEING TAKEN:\\n{immediate_steps}\\n\\n"
                         f"FOLLOW-UP ACTIONS PLANNED:\\n{follow_up_steps}\\n\\n"
                         f"Estimated Resolution: {department_output.action_plan.estimated_resolution_time}\\n\\n"
                         f"Emergency services have been contacted immediately. Stay safe.\\n"
                         f"Reference: {entity_info.id[:8]}"
                ))

            # 4. Emergency broadcast to multiple contacts
            actions.append(EmergencyBroadcastAction(
                priority=ActionPriority.URGENT,
                title="Emergency Broadcast",
                description="Multi-channel emergency notification",
                estimated_duration="2 minutes",
                broadcast_message=f"CRITICAL: {department_output.request_plan.incident_summary}",
                channels=["sms", "email"],
                target_contacts=[entity_info.phone, user_phone] if user_phone else [entity_info.phone]
            ))

        elif criticality.lower() == "high":
            # HIGH: Fast response with smart assistance

            # 1. SMS to department
            actions.append(SMSAction(
                priority=ActionPriority.URGENT,
                title="Department Alert SMS",
                description=f"Urgent notification to {entity_info.name}",
                estimated_duration="30 seconds",
                recipient_phone=entity_info.phone,
                message=f"🚨 URGENT: {department_output.request_plan.incident_summary}. "
                       f"Location: {department_output.request_plan.location_details}. "
                       f"Contact: {user_phone or 'Not provided'}"
            ))

            # 2. Voice call to department for urgent response
            if entity_info.phone:
                actions.append(VoiceCallAction(
                    priority=ActionPriority.URGENT,
                    title="Urgent Voice Alert",
                    description=f"Voice call to {entity_info.name}",
                    estimated_duration="2-3 minutes",
                    recipient_phone=entity_info.phone,
                    call_script=f"URGENT EMERGENCY: {department_output.request_plan.incident_summary}. "
                               f"Location: {department_output.request_plan.location_details}. "
                               f"Please respond immediately.",
                    max_duration_minutes=3
                ))


                call_agent = EmergencyCallAgent()

                # Make an emergency call
                call_result = call_agent.make_emergency_call(
                    phone_number=entity_info.phone,
                    call_reason=department_output.request_plan.incident_summary,
                    additional_context={
                        "case_code": department_output.request_plan.case_code,
                        "emergency_type": department_output.request_plan.incident_summary,
                        "location": department_output.request_plan.location_details,
                        "urgency_level": department_output.criticality,
                        "additional_notes": department_output.request_plan.additional_context
                    }
                )

                print(call_result)


            # 3. User alert email with action plan (HIGH level)
            if user_email:
                immediate_steps = "\\n".join([f"{step.step_number}. {step.action} - {step.timeline}"
                                            for step in department_output.action_plan.immediate_actions])
                follow_up_steps = "\\n".join([f"{step.step_number}. {step.action} - {step.timeline}"
                                            for step in department_output.action_plan.follow_up_actions])

                actions.append(EmailAction(
                    priority=ActionPriority.URGENT,
                    title="Urgent Emergency Action Plan",
                    description=f"Action plan details for {user_name or 'Citizen'}",
                    estimated_duration="30 seconds",
                    recipient_email=user_email,
                    subject=f"🚨 URGENT RESPONSE - Action Plan for Your Emergency",
                    body=f"Dear {user_name or 'Citizen'},\\n\\n"
                         f"🚨 URGENT EMERGENCY RESPONSE INITIATED\\n\\n"
                         f"Your emergency: {department_output.request_plan.incident_summary}\\n"
                         f"Location: {department_output.request_plan.location_details}\\n\\n"
                         f"IMMEDIATE ACTIONS BEING TAKEN:\\n{immediate_steps}\\n\\n"
                         f"FOLLOW-UP ACTIONS PLANNED:\\n{follow_up_steps}\\n\\n"
                         f"Estimated Resolution: {department_output.action_plan.estimated_resolution_time}\\n\\n"
                         f"Emergency services are responding urgently to your situation.\\n"
                         f"Reference: {entity_info.id[:8]}"
                ))

            # 4. Follow-up scheduling
            actions.append(FollowupScheduleAction(
                priority=ActionPriority.NORMAL,
                title="Automated Follow-up",
                description="Schedule status check",
                estimated_duration="30 seconds",
                followup_time_hours=1,
                followup_message="Emergency status check: Has your situation been resolved?",
                followup_method="sms"
            ))

        elif criticality.lower() == "medium":
            # MEDIUM: Efficient digital communication

            # 1. Email to department
            if user_email:
                actions.append(EmailAction(
                    priority=ActionPriority.NORMAL,
                    title="Detailed Email Report",
                    description=f"Complete incident report to {entity_info.name}",
                    estimated_duration="1 minute",
                    recipient_email="department@example.com",  # Would be entity's email
                    subject=f"Incident Report: {department_output.request_plan.incident_summary}",
                    body=f"Incident Summary: {department_output.request_plan.incident_summary}\n\n"
                         f"Location: {department_output.request_plan.location_details}\n\n"
                         f"Additional Context: {department_output.request_plan.additional_context}\n\n"
                         f"Required Response: {department_output.request_plan.required_response}",
                    department_cc=entity_info.phone
                ))

            # 2. User alert email with action plan (MEDIUM level)
            if user_email:
                immediate_steps = "\\n".join([f"{step.step_number}. {step.action} - {step.timeline}"
                                            for step in department_output.action_plan.immediate_actions])
                follow_up_steps = "\\n".join([f"{step.step_number}. {step.action} - {step.timeline}"
                                            for step in department_output.action_plan.follow_up_actions])

                actions.append(EmailAction(
                    priority=ActionPriority.NORMAL,
                    title="Request Action Plan",
                    description=f"Action plan details for {user_name or 'Citizen'}",
                    estimated_duration="30 seconds",
                    recipient_email=user_email,
                    subject=f"Action Plan - {department_output.request_plan.incident_summary[:30]}...",
                    body=f"Dear {user_name or 'Citizen'},\\n\\n"
                         f"Thank you for your request. Here's our action plan:\\n\\n"
                         f"Your request: {department_output.request_plan.incident_summary}\\n"
                         f"Location: {department_output.request_plan.location_details}\\n\\n"
                         f"IMMEDIATE ACTIONS BEING TAKEN:\\n{immediate_steps}\\n\\n"
                         f"FOLLOW-UP ACTIONS PLANNED:\\n{follow_up_steps}\\n\\n"
                         f"Estimated Resolution: {department_output.action_plan.estimated_resolution_time}\\n\\n"
                         f"We will update you on progress. Reference: {entity_info.id[:8]}"
                ))

            # Calendar booking removed - using email for non-urgent follow-up
            if user_email:
                actions.append(EmailAction(
                    priority=ActionPriority.SCHEDULED,
                    title="Follow-up Information Email",
                    description="Detailed follow-up information and next steps",
                    estimated_duration="30 seconds",
                    recipient_email=user_email,
                    subject=f"Your Request - {department_output.request_plan.incident_summary[:30]}...",
                    body=f"Dear {user_name or 'Citizen'},\\n\\n"
                         f"Thank you for contacting us.\\n\\n"
                         f"Request: {department_output.request_plan.incident_summary}\\n"
                         f"Status: Processed and logged\\n"
                         f"Next Steps: {department_output.request_plan.required_response}\\n\\n"
                         f"We will contact you within the next business day if further action is needed."
                ))

        else:  # LOW criticality
            # LOW: Standard communication

            # 1. Simple email notification with action plan
            if user_email:
                immediate_steps = "\\n".join([f"{step.step_number}. {step.action} - {step.timeline}"
                                            for step in department_output.action_plan.immediate_actions])
                follow_up_steps = "\\n".join([f"{step.step_number}. {step.action} - {step.timeline}"
                                            for step in department_output.action_plan.follow_up_actions])

                actions.append(EmailAction(
                    priority=ActionPriority.NORMAL,
                    title="Service Request Action Plan",
                    description="Standard confirmation with action plan",
                    estimated_duration="30 seconds",
                    recipient_email=user_email,
                    subject="Service Request Received - Action Plan",
                    body=f"Dear {user_name or 'Citizen'},\\n\\n"
                         f"Thank you for your service request.\\n\\n"
                         f"Your request: {department_output.request_plan.incident_summary}\\n"
                         f"Location: {department_output.request_plan.location_details}\\n\\n"
                         f"ACTIONS PLANNED:\\n{immediate_steps}\\n\\n"
                         f"FOLLOW-UP ACTIONS:\\n{follow_up_steps}\\n\\n"
                         f"Estimated Processing Time: {department_output.action_plan.estimated_resolution_time}\\n\\n"
                         f"Your request has been forwarded to {entity_info.name}. "
                         f"They will contact you within 24-48 hours.\\n\\n"
                         f"Reference: {entity_info.id[:8]}"
                ))

        return actions

    @staticmethod
    def orchestrate_triggers(input_data: TriggerOrchestratorInput) -> TriggerOrchestratorOutput:
        """Main orchestration method"""
        try:
            actions = TriggerOrchestratorService.determine_actions_by_criticality(
                criticality=input_data.department_output.criticality,
                department_output=input_data.department_output,
                entity_info=input_data.entity_info,
                router_decision=input_data.router_decision,
                user_phone=input_data.user_phone,
                user_email=input_data.user_email,
                user_coordinates=input_data.user_coordinates,
                user_name=input_data.user_name
            )

            # Calculate total estimated time
            immediate_count = sum(1 for a in actions if a.priority == ActionPriority.IMMEDIATE)
            urgent_count = sum(1 for a in actions if a.priority == ActionPriority.URGENT)
            normal_count = sum(1 for a in actions if a.priority == ActionPriority.NORMAL)

            total_time = f"{immediate_count + urgent_count} immediate actions, {normal_count} background actions"

            # Create execution plan
            execution_plan = f"Orchestrated {len(actions)} intelligent actions based on {input_data.department_output.criticality} criticality"

            return TriggerOrchestratorOutput(
                triggered_actions=actions,
                execution_plan=execution_plan,
                total_estimated_time=total_time,
                success=True
            )

        except Exception as e:
            return TriggerOrchestratorOutput(
                triggered_actions=[],
                execution_plan="Failed to orchestrate actions",
                total_estimated_time="N/A",
                success=False,
                error_message=str(e)
            )

# =============================================================================
# ACTION SERVICE TEMPLATES (Simple implementations)
# =============================================================================

class EmailService:
    """Template for email service"""
    @staticmethod
    def send_email(action: EmailAction) -> Dict[str, Any]:
        return {
            "status": "queued",
            "action_type": "email",
            "recipient": action.recipient_email,
            "estimated_delivery": "30 seconds"
        }

class SMSService:
    """Template for SMS service"""
    @staticmethod
    def send_sms(action: SMSAction) -> Dict[str, Any]:
        return {
            "status": "sent",
            "action_type": "sms",
            "recipient": action.recipient_phone,
            "message_id": f"sms_{action.recipient_phone[-4:]}"
        }

class VAPICallService:
    """Template for VAPI voice call service"""
    @staticmethod
    def initiate_call(action: VoiceCallAction) -> Dict[str, Any]:
        return {
            "status": "calling",
            "action_type": "voice_call",
            "recipient": action.recipient_phone,
            "call_id": f"call_{action.recipient_phone[-4:]}"
        }

# GoogleCalendarService removed - using email for scheduling and follow-up

# NearbySearchService removed - focusing on core emergency actions

# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def trigger_emergency_actions(
    department_output: DepartmentOrchestratorServiceOutput,
    entity_info: EntityInfo,
    router_decision: RouterDecision,
    user_phone: str = None,
    user_email: str = None,
    user_coordinates: Dict[str, float] = None,
    user_name: str = None
) -> TriggerOrchestratorOutput:
    """Convenience function for triggering emergency actions"""

    input_data = TriggerOrchestratorInput(
        department_output=department_output,
        entity_info=entity_info,
        router_decision=router_decision,
        user_phone=user_phone,
        user_email=user_email,
        user_coordinates=user_coordinates,
        user_name=user_name
    )

    return TriggerOrchestratorService.orchestrate_triggers(input_data)