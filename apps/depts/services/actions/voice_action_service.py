"""
Voice Action Service - VAPI integration template
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

logger = logging.getLogger(__name__)

class VoiceActionService:
    """
    Voice call service using VAPI (Voice AI Platform)
    Template implementation - requires VAPI API key in settings
    """

    def __init__(self):
        # VAPI configuration - add to your .env file
        self.vapi_api_key = getattr(settings, 'VAPI_API_KEY', None)
        self.vapi_base_url = "https://api.vapi.ai"
        self.vapi_phone_number = getattr(settings, 'VAPI_PHONE_NUMBER', None)

    def execute_voice_action(self, voice_action) -> Dict[str, Any]:
        """
        Execute voice call action from TriggerOrchestrator

        Args:
            voice_action: VoiceCallAction object

        Returns:
            Dict with execution result
        """
        try:
            if not self.vapi_api_key:
                # Fallback to mock for testing
                return self._mock_voice_call(voice_action)

            # VAPI call configuration
            call_config = {
                "phoneNumber": voice_action.recipient_phone,
                "assistantId": self._get_emergency_assistant_id(),
                "metadata": {
                    "priority": voice_action.priority.value,
                    "title": voice_action.title,
                    "script": voice_action.call_script,
                    "max_duration": voice_action.max_duration_minutes
                }
            }

            # Make VAPI API call
            response = requests.post(
                f"{self.vapi_base_url}/call",
                headers={
                    "Authorization": f"Bearer {self.vapi_api_key}",
                    "Content-Type": "application/json"
                },
                json=call_config,
                timeout=30
            )

            if response.status_code == 200:
                call_data = response.json()
                return {
                    "success": True,
                    "status": "initiated",
                    "action_type": voice_action.action_type.value,
                    "recipient": voice_action.recipient_phone,
                    "call_id": call_data.get("id"),
                    "estimated_duration": f"{voice_action.max_duration_minutes} minutes",
                    "script_preview": voice_action.call_script[:100] + "..."
                }
            else:
                return {
                    "success": False,
                    "status": "failed",
                    "action_type": voice_action.action_type.value,
                    "recipient": voice_action.recipient_phone,
                    "error": f"VAPI error: {response.status_code} - {response.text}"
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
        Check status of ongoing call
        """
        try:
            if not self.vapi_api_key or call_id.startswith("mock_"):
                return {
                    "success": True,
                    "call_id": call_id,
                    "status": "mock_completed",
                    "duration": "2 minutes",
                    "note": "Mock call status"
                }

            response = requests.get(
                f"{self.vapi_base_url}/call/{call_id}",
                headers={
                    "Authorization": f"Bearer {self.vapi_api_key}"
                },
                timeout=15
            )

            if response.status_code == 200:
                call_data = response.json()
                return {
                    "success": True,
                    "call_id": call_id,
                    "status": call_data.get("status"),
                    "duration": call_data.get("duration"),
                    "started_at": call_data.get("startedAt"),
                    "ended_at": call_data.get("endedAt")
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to get call status: {response.status_code}"
                }

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