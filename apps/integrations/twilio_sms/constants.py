from django.conf import settings

# Twilio API configuration
ACCOUNT_SID = settings.TWILIO_ACCOUNT_SID
AUTH_TOKEN = settings.TWILIO_AUTH_TOKEN
FROM_PHONE_NUMBER = settings.TWILIO_FROM_PHONE_NUMBER

# Twilio API URLs
BASE_URL = f"https://api.twilio.com/2010-04-01/Accounts/{ACCOUNT_SID}"
MESSAGES_URL = f"{BASE_URL}/Messages.json"
SMS_URL = MESSAGES_URL

# Message status options
MESSAGE_STATUS_QUEUED = "queued"
MESSAGE_STATUS_SENDING = "sending"
MESSAGE_STATUS_SENT = "sent"
MESSAGE_STATUS_FAILED = "failed"
MESSAGE_STATUS_DELIVERED = "delivered"
MESSAGE_STATUS_UNDELIVERED = "undelivered"