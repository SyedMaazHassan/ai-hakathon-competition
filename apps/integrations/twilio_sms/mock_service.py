"""
Mock SMS Service - For testing without real Twilio credentials
"""
import logging
import time
import random

logger = logging.getLogger(__name__)

class MockTwilioSMSService:
    """Mock service that simulates SMS sending for testing"""

    def __init__(self):
        self.sent_messages = []  # Store sent messages for debugging

    def send_sms(self, to_number, message, from_number=None):
        """Mock SMS sending"""
        try:
            # Simulate some processing time
            time.sleep(0.1)

            # Generate fake message ID
            message_id = f"SM{random.randint(10000000, 99999999)}"

            # Store message for debugging
            sent_message = {
                "sid": message_id,
                "to": to_number,
                "from": from_number or "+1234567890",
                "body": message,
                "status": "queued",
                "timestamp": time.time()
            }
            self.sent_messages.append(sent_message)

            # Log the mock SMS
            logger.info(f"[MOCK SMS] To: {to_number}")
            logger.info(f"[MOCK SMS] Message: {message[:100]}...")
            logger.info(f"[MOCK SMS] Message ID: {message_id}")

            # Simulate 95% success rate
            if random.random() < 0.95:
                return {
                    "success": True,
                    "data": {
                        "sid": message_id,
                        "status": "queued",
                        "to": to_number,
                        "from_": from_number or "+1234567890",
                        "body": message,
                        "date_created": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                }
            else:
                # Simulate occasional failure
                return {
                    "success": False,
                    "error": "Mock SMS delivery failed (simulated 5% failure rate)"
                }

        except Exception as e:
            logger.error(f"[MOCK SMS] Error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def send_alert_sms(self, to_number, alert_type, message, from_number=None):
        """Mock alert SMS with priority formatting"""
        alert_emojis = {
            "emergency": "🚨",
            "warning": "⚠️",
            "info": "📢"
        }

        emoji = alert_emojis.get(alert_type, "📢")
        formatted_message = f"{emoji} {alert_type.upper()}: {message}"

        return self.send_sms(to_number, formatted_message, from_number)

    def check_message_status(self, message_id):
        """Mock message status check"""
        # Find message in our sent list
        for msg in self.sent_messages:
            if msg["sid"] == message_id:
                return {
                    "success": True,
                    "data": {
                        "sid": message_id,
                        "status": "delivered",  # Always successful in mock
                        "to": msg["to"],
                        "from_": msg["from"],
                        "body": msg["body"]
                    }
                }

        return {
            "success": False,
            "error": "Message ID not found"
        }

    def get_sent_messages_count(self):
        """Get count of sent messages (for debugging)"""
        return len(self.sent_messages)

    def get_last_sent_message(self):
        """Get last sent message (for debugging)"""
        return self.sent_messages[-1] if self.sent_messages else None

# Create global instance
MOCK_SMS_SERVICE = MockTwilioSMSService()