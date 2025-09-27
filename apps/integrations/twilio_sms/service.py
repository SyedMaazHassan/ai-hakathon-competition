from .client import TwilioSMSClient
import re

class TwilioSMSService:
    def __init__(self):
        self.client = TwilioSMSClient()

    def send_sms(self, to_number, message, from_number=None):
        """Send SMS to a phone number"""
        # Validate phone number format
        if not self._is_valid_phone_number(to_number):
            return {"success": False, "error": "Invalid phone number format"}

        # Validate message length (SMS limit is 160 characters for single SMS)
        if len(message) > 1600:  # Allow up to 10 concatenated SMS
            return {"success": False, "error": "Message too long (max 1600 characters)"}

        return self.client.send_sms(to_number, message, from_number)

    def send_bulk_sms(self, phone_numbers, message, from_number=None):
        """Send SMS to multiple phone numbers"""
        results = []

        for phone in phone_numbers:
            result = self.send_sms(phone, message, from_number)
            results.append({
                "phone": phone,
                "success": result["success"],
                "message_sid": result.get("data", {}).get("sid") if result["success"] else None,
                "error": result.get("error") if not result["success"] else None
            })

        successful_sends = [r for r in results if r["success"]]

        return {
            "success": True,
            "data": {
                "total_sent": len(successful_sends),
                "total_failed": len(results) - len(successful_sends),
                "results": results
            }
        }

    def send_notification_sms(self, to_number, title, message, from_number=None):
        """Send formatted notification SMS"""
        formatted_message = f"🔔 {title}\n\n{message}"
        return self.send_sms(to_number, formatted_message, from_number)

    def send_alert_sms(self, to_number, alert_type, message, from_number=None):
        """Send alert SMS with priority formatting"""
        alert_emojis = {
            "emergency": "🚨",
            "warning": "⚠️",
            "info": "ℹ️",
            "success": "✅"
        }

        emoji = alert_emojis.get(alert_type.lower(), "📢")
        formatted_message = f"{emoji} {alert_type.upper()}: {message}"

        return self.send_sms(to_number, formatted_message, from_number)

    def check_message_status(self, message_sid):
        """Check the delivery status of a sent message"""
        return self.client.get_message_status(message_sid)

    def get_message_history(self, phone_number=None, limit=50):
        """Get SMS history with optional phone number filter"""
        return self.client.list_messages(to_number=phone_number, limit=limit)

    def send_otp_sms(self, to_number, otp_code, app_name="App", from_number=None):
        """Send OTP (One-Time Password) SMS"""
        message = f"Your {app_name} verification code is: {otp_code}\n\nThis code expires in 10 minutes. Do not share this code with anyone."
        return self.send_sms(to_number, message, from_number)

    def send_appointment_reminder(self, to_number, appointment_details, from_number=None):
        """Send appointment reminder SMS"""
        message = f"📅 Appointment Reminder\n\n"
        message += f"Date: {appointment_details.get('date', 'TBD')}\n"
        message += f"Time: {appointment_details.get('time', 'TBD')}\n"
        message += f"Location: {appointment_details.get('location', 'TBD')}\n"

        if appointment_details.get('notes'):
            message += f"Notes: {appointment_details['notes']}"

        return self.send_sms(to_number, message, from_number)

    def _is_valid_phone_number(self, phone_number):
        """Basic phone number validation"""
        # Remove any non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone_number)

        # Check if it's a valid international format
        # Should start with + and have 10-15 digits
        if re.match(r'^\+\d{10,15}$', cleaned):
            return True

        # Check if it's a valid US format without country code
        if re.match(r'^\d{10}$', cleaned):
            return True

        return False

    def format_phone_number(self, phone_number, country_code="+1"):
        """Format phone number to international format"""
        # Remove any non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone_number)

        # If already has country code, return as is
        if cleaned.startswith('+'):
            return cleaned

        # If 10 digits (US format), add country code
        if len(cleaned) == 10:
            return f"{country_code}{cleaned}"

        # If 11 digits starting with 1 (US format with 1), format properly
        if len(cleaned) == 11 and cleaned.startswith('1'):
            return f"+{cleaned}"

        return cleaned