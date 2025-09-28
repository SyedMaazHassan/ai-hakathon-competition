"""
Voice Action Service - VAPI integration with EmergencyCallAgent
Plug & play with TriggerOrchestrator VoiceCallAction
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

import requests
import json
from typing import Dict, List, Any
from django.conf import settings
import logging
from .vapi_call_agent import EmergencyCallAgent

logger = logging.getLogger(__name__)

class VoiceActionService:
    """
    Voice call service using VAPI (Voice AI Platform)
    Template implementation - requires VAPI API key in settings
    """

    def __init__(self):
        # Use your functional EmergencyCallAgent
        self.emergency_agent = EmergencyCallAgent()

    def execute_voice_action(self, voice_action) -> Dict[str, Any]:
        """
        Execute voice call action using functional EmergencyCallAgent

        Args:
            voice_action: VoiceCallAction object

        Returns:
            Dict with execution result
        """
        try:
            # Extract call reason from the script or title
            call_reason = self._determine_call_reason(voice_action.call_script)

            # Build context from the voice action
            additional_context = {
                "case_code": f"VA-{hash(voice_action.title) % 10000:04d}",
                "emergency_type": call_reason,
                "location": "Emergency location",  # Could be extracted from script
                "urgency_level": voice_action.priority.value.upper(),
                "additional_notes": voice_action.call_script
            }

            # Make the emergency call using your functional agent
            result = self.emergency_agent.make_emergency_call(
                phone_number=voice_action.recipient_phone,
                call_reason=call_reason,
                additional_context=additional_context
            )

            if result["success"]:
                return {
                    "success": True,
                    "status": "initiated",
                    "action_type": voice_action.action_type.value,
                    "recipient": voice_action.recipient_phone,
                    "call_id": result.get("call_id"),
                    "estimated_duration": f"{voice_action.max_duration_minutes} minutes",
                    "script_preview": voice_action.call_script[:100] + "...",
                    "service": "EmergencyCallAgent"
                }
            else:
                return {
                    "success": False,
                    "status": "failed",
                    "action_type": voice_action.action_type.value,
                    "recipient": voice_action.recipient_phone,
                    "error": result.get("error", "Unknown error")
                }

        except Exception as e:
            logger.error(f"Voice call failed: {str(e)}")
            return {
                "success": False,
                "status": "failed",
                "action_type": voice_action.action_type.value,
                "recipient": voice_action.recipient_phone,
                "error": str(e)
            }

    def _determine_call_reason(self, call_script: str) -> str:
        """Determine emergency type from call script"""
        script_lower = call_script.lower()

        if any(word in script_lower for word in ["fire", "burning", "smoke", "flame"]):
            return "fire"
        elif any(word in script_lower for word in ["medical", "heart", "injury", "accident", "hospital"]):
            return "medical"
        elif any(word in script_lower for word in ["police", "crime", "robbery", "theft", "danger"]):
            return "police"
        else:
            return "general"

    def _mock_voice_call(self, voice_action) -> Dict[str, Any]:
        """
        Mock voice call for testing/demo purposes
        """
        logger.info(f"MOCK VOICE CALL: {voice_action.recipient_phone}")
        logger.info(f"Script: {voice_action.call_script}")

        return {
            "success": True,
            "status": "mock_initiated",
            "action_type": voice_action.action_type.value,
            "recipient": voice_action.recipient_phone,
            "call_id": f"mock_call_{hash(voice_action.recipient_phone)}",
            "estimated_duration": f"{voice_action.max_duration_minutes} minutes",
            "script_preview": voice_action.call_script[:100] + "...",
            "note": "MOCK CALL - VAPI not configured"
        }

    def _get_emergency_assistant_id(self) -> str:
        """
        Get VAPI assistant ID for emergency calls
        In production, create specialized assistants for different emergency types
        """
        # Default emergency assistant - configure in VAPI dashboard
        return getattr(settings, 'VAPI_EMERGENCY_ASSISTANT_ID', 'default_assistant')

    def get_call_status(self, call_id: str) -> Dict[str, Any]:
        """
        Check status of ongoing call using EmergencyCallAgent
        """
        try:
            # Use your functional agent's get_call_status method
            return self.emergency_agent.get_call_status(call_id)
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def create_emergency_assistant(self) -> Dict[str, Any]:
        """
        Create specialized emergency assistant in VAPI
        This should be run once during setup
        """
        if not self.vapi_api_key:
            return {"success": False, "error": "VAPI API key not configured"}

        assistant_config = {
            "name": "Emergency Response Assistant",
            "model": {
                "provider": "openai",
                "model": "gpt-4",
                "temperature": 0.1
            },
            "voice": {
                "provider": "eleven-labs",
                "voiceId": "emergency_voice_id"
            },
            "firstMessage": "This is an emergency response call. Please confirm your location and describe the situation.",
            "systemMessage": """
You are an emergency response AI assistant. Your role is to:
1. Confirm the recipient is available and safe
2. Relay the emergency information clearly
3. Provide immediate safety instructions if needed
4. Confirm receipt of the emergency alert
5. Keep the call brief but thorough
6. Maintain a calm, professional tone

Do not provide medical advice beyond basic safety measures.
Always instruct to call local emergency services if immediate help is needed.
""",
            "recordingEnabled": True,
            "maxDurationSeconds": 300  # 5 minutes max
        }

        try:
            response = requests.post(
                f"{self.vapi_base_url}/assistant",
                headers={
                    "Authorization": f"Bearer {self.vapi_api_key}",
                    "Content-Type": "application/json"
                },
                json=assistant_config
            )

            if response.status_code == 200:
                assistant_data = response.json()
                return {
                    "success": True,
                    "assistant_id": assistant_data.get("id"),
                    "name": assistant_data.get("name")
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to create assistant: {response.text}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Convenience function for TriggerOrchestrator
def execute_voice_action(voice_action) -> Dict[str, Any]:
    """
    Execute voice call action - main entry point
    """
    service = VoiceActionService()
    return service.execute_voice_action(voice_action)