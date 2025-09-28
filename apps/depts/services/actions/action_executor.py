"""
Action Executor - Master orchestrator for all trigger actions
Simple, efficient execution of TriggerOrchestrator actions
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from typing import Dict, List, Any, Union
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

from .email_action_service import EmailActionService
from .sms_action_service import SMSActionService
from .voice_action_service import VoiceActionService
# Calendar and Maps services removed to simplify system

from apps.depts.services.trigger_orchestrator_service import (
    TriggerAction, EmailAction, SMSAction, VoiceCallAction,
    EmergencyBroadcastAction, FollowupScheduleAction, TriggerActionType
)

logger = logging.getLogger(__name__)

class ActionExecutor:
    """
    Master executor for all trigger actions
    Routes actions to appropriate services and handles execution
    """

    def __init__(self):
        self.email_service = EmailActionService()
        self.sms_service = SMSActionService()
        self.voice_service = VoiceActionService()
        # Calendar and Maps services removed to focus on core emergency actions

    def execute_single_action(self, action: TriggerAction) -> Dict[str, Any]:
        """
        Execute a single trigger action

        Args:
            action: TriggerAction object from TriggerOrchestrator

        Returns:
            Dict with execution result
        """
        try:
            # Route to appropriate service based on action type
            if action.action_type == TriggerActionType.EMAIL:
                return self.email_service.execute_email_action(action)

            elif action.action_type == TriggerActionType.SMS:
                return self.sms_service.execute_sms_action(action)

            elif action.action_type == TriggerActionType.VOICE_CALL:
                return self.voice_service.execute_voice_action(action)

            # Calendar and Maps actions removed to focus on core emergency services

            elif action.action_type == TriggerActionType.EMERGENCY_BROADCAST:
                return self._execute_broadcast_action(action)

            elif action.action_type == TriggerActionType.FOLLOWUP_SCHEDULE:
                return self._execute_followup_action(action)

            else:
                return {
                    "success": False,
                    "action_type": action.action_type.value,
                    "error": f"Unknown action type: {action.action_type}"
                }

        except Exception as e:
            logger.error(f"Action execution failed: {str(e)}")
            return {
                "success": False,
                "action_type": getattr(action, 'action_type', {}).get('value', 'unknown'),
                "error": str(e)
            }

    def execute_multiple_actions(self, actions: List[TriggerAction], parallel: bool = True) -> Dict[str, Any]:
        """
        Execute multiple trigger actions

        Args:
            actions: List of TriggerAction objects
            parallel: Whether to execute actions in parallel

        Returns:
            Dict with combined execution results
        """
        if not actions:
            return {
                "success": True,
                "total_actions": 0,
                "successful_actions": 0,
                "failed_actions": 0,
                "results": []
            }

        if parallel and len(actions) > 1:
            return self._execute_actions_parallel(actions)
        else:
            return self._execute_actions_sequential(actions)

    def _execute_actions_sequential(self, actions: List[TriggerAction]) -> Dict[str, Any]:
        """Execute actions one by one"""
        results = []
        successful = 0
        failed = 0

        for action in actions:
            result = self.execute_single_action(action)
            results.append(result)

            if result.get("success", False):
                successful += 1
            else:
                failed += 1

        return {
            "success": True,
            "total_actions": len(actions),
            "successful_actions": successful,
            "failed_actions": failed,
            "execution_mode": "sequential",
            "results": results
        }

    def _execute_actions_parallel(self, actions: List[TriggerAction]) -> Dict[str, Any]:
        """Execute actions in parallel for better performance"""
        results = []
        successful = 0
        failed = 0

        # Group actions by priority for execution order
        immediate_actions = [a for a in actions if a.priority.value == "critical"]
        urgent_actions = [a for a in actions if a.priority.value == "high"]
        normal_actions = [a for a in actions if a.priority.value in ["medium", "low"]]

        # Execute immediate actions first
        for action_group in [immediate_actions, urgent_actions, normal_actions]:
            if not action_group:
                continue

            with ThreadPoolExecutor(max_workers=min(len(action_group), 5)) as executor:
                # Submit all actions in the group
                future_to_action = {
                    executor.submit(self.execute_single_action, action): action
                    for action in action_group
                }

                # Collect results as they complete
                for future in as_completed(future_to_action):
                    result = future.result()
                    results.append(result)

                    if result.get("success", False):
                        successful += 1
                    else:
                        failed += 1

        return {
            "success": True,
            "total_actions": len(actions),
            "successful_actions": successful,
            "failed_actions": failed,
            "execution_mode": "parallel",
            "results": results
        }

    def _execute_broadcast_action(self, broadcast_action: EmergencyBroadcastAction) -> Dict[str, Any]:
        """
        Execute emergency broadcast to multiple channels
        """
        try:
            results = []
            channels = broadcast_action.channels
            message = broadcast_action.broadcast_message
            contacts = broadcast_action.target_contacts

            # Send via each channel
            if "sms" in channels and contacts:
                for contact in contacts:
                    if contact and contact.startswith('+'):  # Phone number
                        # Create SMS action and execute
                        sms_action = SMSAction(
                            priority=broadcast_action.priority,
                            title="Emergency Broadcast",
                            description="Broadcast SMS",
                            estimated_duration="30 seconds",
                            recipient_phone=contact,
                            message=message,
                            sender_name="Emergency Services"
                        )
                        sms_result = self.sms_service.execute_sms_action(sms_action)
                        results.append({"channel": "sms", "contact": contact, **sms_result})

            if "email" in channels and contacts:
                for contact in contacts:
                    if contact and "@" in contact:  # Email address
                        # Create Email action and execute
                        email_action = EmailAction(
                            priority=broadcast_action.priority,
                            title="Emergency Broadcast",
                            description="Broadcast Email",
                            estimated_duration="1 minute",
                            recipient_email=contact,
                            subject="Emergency Broadcast Alert",
                            body=message
                        )
                        email_result = self.email_service.execute_email_action(email_action)
                        results.append({"channel": "email", "contact": contact, **email_result})

            successful = len([r for r in results if r.get("success", False)])
            failed = len(results) - successful

            return {
                "success": True,
                "status": "broadcast_sent",
                "action_type": broadcast_action.action_type.value,
                "channels_used": channels,
                "total_sent": successful,
                "total_failed": failed,
                "target_contacts": len(contacts),
                "results": results
            }

        except Exception as e:
            logger.error(f"Broadcast action failed: {str(e)}")
            return {
                "success": False,
                "status": "failed",
                "action_type": broadcast_action.action_type.value,
                "error": str(e)
            }

    def _execute_followup_action(self, followup_action: FollowupScheduleAction) -> Dict[str, Any]:
        """
        Execute follow-up scheduling (mock implementation)
        """
        try:
            # In a real implementation, this would integrate with a task scheduler
            # like Celery, Django-RQ, or cloud functions

            logger.info(f"SCHEDULING FOLLOW-UP: {followup_action.followup_message}")
            logger.info(f"Method: {followup_action.followup_method}")
            logger.info(f"In {followup_action.followup_time_hours} hours")

            return {
                "success": True,
                "status": "scheduled",
                "action_type": followup_action.action_type.value,
                "followup_time_hours": followup_action.followup_time_hours,
                "followup_method": followup_action.followup_method,
                "followup_message": followup_action.followup_message,
                "schedule_id": f"followup_{hash(followup_action.followup_message)}",
                "note": "MOCK SCHEDULING - Task scheduler not configured"
            }

        except Exception as e:
            logger.error(f"Follow-up scheduling failed: {str(e)}")
            return {
                "success": False,
                "status": "failed",
                "action_type": followup_action.action_type.value,
                "error": str(e)
            }

    def get_action_status(self, action_type: str, action_id: str) -> Dict[str, Any]:
        """
        Get status of previously executed action
        """
        try:
            if action_type == "sms":
                return self.sms_service.get_sms_status(action_id)
            elif action_type == "voice_call":
                return self.voice_service.get_call_status(action_id)
            elif action_type == "calendar_booking":
                return self.calendar_service.get_booking_status(action_id)
            else:
                return {
                    "success": False,
                    "error": f"Status check not supported for action type: {action_type}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Global instance for easy access
ACTION_EXECUTOR = ActionExecutor()

# Convenience functions
def execute_trigger_actions(trigger_output) -> Dict[str, Any]:
    """
    Execute all actions from TriggerOrchestratorOutput

    Args:
        trigger_output: TriggerOrchestratorOutput object

    Returns:
        Combined execution results
    """
    if not trigger_output.success or not trigger_output.triggered_actions:
        return {
            "success": False,
            "error": trigger_output.error_message or "No actions to execute",
            "total_actions": 0
        }

    return ACTION_EXECUTOR.execute_multiple_actions(
        trigger_output.triggered_actions,
        parallel=True
    )