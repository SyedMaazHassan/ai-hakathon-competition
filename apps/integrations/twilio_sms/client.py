from twilio.rest import Client
from twilio.base.exceptions import TwilioException
import logging
from . import constants

logger = logging.getLogger(__name__)

class TwilioSMSClient:
    def __init__(self):
        self.account_sid = constants.ACCOUNT_SID
        self.auth_token = constants.AUTH_TOKEN
        self.from_number = constants.FROM_PHONE_NUMBER

        if not all([self.account_sid, self.auth_token, self.from_number]):
            raise ValueError("Twilio credentials not properly configured")

        self.client = Client(self.account_sid, self.auth_token)

    def send_sms(self, to_number, message_body, from_number=None):
        """Send SMS message using Twilio SDK"""
        try:
            message = self.client.messages.create(
                body=message_body,
                from_=from_number or self.from_number,
                to=to_number
            )

            return {
                "success": True,
                "data": {
                    "sid": message.sid,
                    "status": message.status,
                    "to": message.to,
                    "from": message.from_,
                    "body": message.body,
                    "date_created": message.date_created.isoformat() if message.date_created else None
                }
            }
        except TwilioException as e:
            logger.error(f"[Twilio] SMS send failed: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"[Twilio] Unexpected error: {e}")
            return {"success": False, "error": str(e)}

    def get_message_status(self, message_sid):
        """Get status of a sent message"""
        try:
            message = self.client.messages(message_sid).fetch()

            return {
                "success": True,
                "data": {
                    "sid": message.sid,
                    "status": message.status,
                    "to": message.to,
                    "from": message.from_,
                    "body": message.body,
                    "error_code": message.error_code,
                    "error_message": message.error_message,
                    "date_created": message.date_created.isoformat() if message.date_created else None,
                    "date_sent": message.date_sent.isoformat() if message.date_sent else None,
                    "date_updated": message.date_updated.isoformat() if message.date_updated else None
                }
            }
        except TwilioException as e:
            logger.error(f"[Twilio] Get message status failed: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"[Twilio] Unexpected error: {e}")
            return {"success": False, "error": str(e)}

    def list_messages(self, to_number=None, from_number=None, date_sent=None, limit=50):
        """List messages with optional filtering"""
        try:
            filter_params = {'limit': limit}

            if to_number:
                filter_params['to'] = to_number
            if from_number:
                filter_params['from_'] = from_number
            if date_sent:
                filter_params['date_sent'] = date_sent

            messages = self.client.messages.list(**filter_params)

            messages_data = []
            for message in messages:
                messages_data.append({
                    "sid": message.sid,
                    "status": message.status,
                    "to": message.to,
                    "from": message.from_,
                    "body": message.body,
                    "date_created": message.date_created.isoformat() if message.date_created else None,
                    "date_sent": message.date_sent.isoformat() if message.date_sent else None
                })

            return {"success": True, "data": {"messages": messages_data}}

        except TwilioException as e:
            logger.error(f"[Twilio] List messages failed: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"[Twilio] Unexpected error: {e}")
            return {"success": False, "error": str(e)}