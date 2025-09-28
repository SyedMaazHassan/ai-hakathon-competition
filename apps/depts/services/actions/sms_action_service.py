"""
SMS Action Service - Twilio integration wrapper
Plug & play with TriggerOrchestrator SMSAction
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from apps.integrations.twilio_sms.service import TwilioSMSService
from apps.integrations.twilio_sms.mock_service import MOCK_SMS_SERVICE
from typing import Dict, List, Any
import logging
import os

logger = logging.getLogger(__name__)

class SMSActionService:
    """
    SMS service wrapper using existing Twilio integration or mock service
    """

    def __init__(self):
        # Check if Twilio credentials are available
        twilio_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        twilio_token = os.environ.get("TWILIO_AUTH_TOKEN")
        twilio_phone = os.environ.get("TWILIO_FROM_PHONE_NUMBER")

        if twilio_sid and twilio_token and twilio_phone:
            logger.info("Using real Twilio SMS service")
            self.twilio_service = TwilioSMSService()
            self.use_mock = False
        else:
            logger.info("Twilio credentials not found, using mock SMS service")
            self.twilio_service = MOCK_SMS_SERVICE
            self.use_mock = True

    def execute_sms_action(self, sms_action) -> Dict[str, Any]:
        """
        Execute SMS action from TriggerOrchestrator

        Args:
            sms_action: SMSAction object from TriggerOrchestrator

        Returns:
            Dict with execution result
        """
        try:
            # Determine alert type based on priority
            alert_type_mapping = {
                "critical": "emergency",
                "high": "warning",
                "medium": "info",
                "low": "info"
            }
            alert_type = alert_type_mapping.get(sms_action.priority.value, "info")

            # Format message with priority indicator
            if sms_action.priority.value == "critical":
                formatted_message = f"🚨 CRITICAL: {sms_action.message}"
            elif sms_action.priority.value == "high":
                formatted_message = f"⚠️ URGENT: {sms_action.message}"
            else:
                formatted_message = f"📢 {sms_action.message}"

            # Add Google Maps location link if coordinates are available
            if hasattr(sms_action, 'user_coordinates') and sms_action.user_coordinates:
                lat = sms_action.user_coordinates.get('lat') or sms_action.user_coordinates.get('latitude')
                lng = sms_action.user_coordinates.get('lng') or sms_action.user_coordinates.get('longitude')
                if lat and lng:
                    maps_link = f"https://maps.google.com/maps?q={lat},{lng}"
                    formatted_message += f"\n📍 Location: {maps_link}"

            # Add sender name if provided
            if hasattr(sms_action, 'sender_name') and sms_action.sender_name:
                formatted_message += f"\n- {sms_action.sender_name}"

            # Use Twilio service to send
            result = self.twilio_service.send_alert_sms(
                to_number=sms_action.recipient_phone,
                alert_type=alert_type,
                message=sms_action.message
            )

            if result["success"]:
                return {
                    "success": True,
                    "status": "sent",
                    "action_type": sms_action.action_type.value,
                    "recipient": sms_action.recipient_phone,
                    "message_id": result.get("data", {}).get("sid", "unknown"),
                    "estimated_delivery": sms_action.estimated_duration,
                    "message_preview": formatted_message[:50] + "...",
                    "service_type": "mock" if self.use_mock else "twilio"
                }
            else:
                return {
                    "success": False,
                    "status": "failed",
                    "action_type": sms_action.action_type.value,
                    "recipient": sms_action.recipient_phone,
                    "error": result.get("error", "Unknown SMS error")
                }

        except Exception as e:
            logger.error(f"Failed to send SMS: {str(e)}")
            return {
                "success": False,
                "status": "failed",
                "action_type": sms_action.action_type.value,
                "recipient": sms_action.recipient_phone,
                "error": str(e)
            }

    def send_emergency_sms(self, sms_action) -> Dict[str, Any]:
        """
        Send high-priority emergency SMS with special formatting
        """
        try:
            # Emergency SMS with maximum impact
            emergency_message = f"""🚨 EMERGENCY ALERT 🚨

{sms_action.message}

This is an automated emergency notification.
DO NOT REPLY to this number.

Ref: {hash(sms_action.recipient_phone) % 10000}"""

            result = self.twilio_service.send_sms(
                to_number=sms_action.recipient_phone,
                message=emergency_message
            )

            if result["success"]:
                return {
                    "success": True,
                    "status": "sent",
                    "action_type": sms_action.action_type.value,
                    "recipient": sms_action.recipient_phone,
                    "message_id": result.get("data", {}).get("sid"),
                    "priority": "emergency",
                    "estimated_delivery": "immediate"
                }
            else:
                return {
                    "success": False,
                    "status": "failed",
                    "action_type": sms_action.action_type.value,
                    "recipient": sms_action.recipient_phone,
                    "error": result.get("error")
                }

        except Exception as e:
            logger.error(f"Failed to send emergency SMS: {str(e)}")
            return {
                "success": False,
                "status": "failed",
                "error": str(e)
            }

    def send_bulk_sms(self, sms_actions: List) -> Dict[str, Any]:
        """
        Send multiple SMS messages efficiently
        """
        try:
            # Extract phone numbers and messages
            phone_numbers = []
            messages = {}

            for sms_action in sms_actions:
                phone = sms_action.recipient_phone
                phone_numbers.append(phone)

                # Format message based on priority
                if sms_action.priority.value == "critical":
                    messages[phone] = f"🚨 CRITICAL: {sms_action.message}"
                elif sms_action.priority.value == "high":
                    messages[phone] = f"⚠️ URGENT: {sms_action.message}"
                else:
                    messages[phone] = sms_action.message

            # For now, send individually (could be optimized with Twilio bulk API)
            results = []
            for phone in phone_numbers:
                try:
                    result = self.twilio_service.send_sms(phone, messages[phone])
                    results.append({
                        "phone": phone,
                        "success": result["success"],
                        "message_id": result.get("data", {}).get("sid") if result["success"] else None,
                        "error": result.get("error") if not result["success"] else None
                    })
                except Exception as e:
                    results.append({
                        "phone": phone,
                        "success": False,
                        "error": str(e)
                    })

            successful = len([r for r in results if r["success"]])
            failed = len(results) - successful

            return {
                "success": True,
                "total_sent": successful,
                "total_failed": failed,
                "results": results
            }

        except Exception as e:
            logger.error(f"Bulk SMS failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "total_sent": 0,
                "total_failed": len(sms_actions)
            }

    def get_sms_status(self, message_id: str) -> Dict[str, Any]:
        """
        Check delivery status of sent SMS
        """
        try:
            result = self.twilio_service.check_message_status(message_id)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Convenience function for TriggerOrchestrator
def execute_sms_action(sms_action) -> Dict[str, Any]:
    """
    Execute SMS action - main entry point
    """
    service = SMSActionService()
    return service.execute_sms_action(sms_action)