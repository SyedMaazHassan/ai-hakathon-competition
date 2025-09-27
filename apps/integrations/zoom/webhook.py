import hmac
import hashlib
import json
import logging
import time

from django.conf import settings
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View

from apps.integrations.zoom.service import ZoomService
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)




@method_decorator(csrf_exempt, name='dispatch')
class ZoomWebhookView(View):
    """
    Handles Zoom Webhook events with enhanced security:
    - URL Validation (CRC)
    - Event: recording.transcript_completed
    - Proper signature verification using raw request body
    """

    def verify_zoom_signature(self, request, raw_body_bytes: bytes) -> bool:
        """
        Verify Zoom request signature using:
        - X-Zm-Signature header
        - X-Zm-Request-Timestamp header
        - Raw request body bytes
        - ZOOM_WEBHOOK_SECRET from settings
        """
        try:
            zoom_signature = request.headers.get("X-Zm-Signature")
            zoom_timestamp = request.headers.get("X-Zm-Request-Timestamp")

            if not zoom_signature or not zoom_timestamp:
                logger.error("🔴 Missing Zoom signature or timestamp headers")
                return False

            # Allow 10-min window for time drift (Zoom recommends 5 min but provides 10-min buffer)
            current_time = time.time()
            if abs(current_time - int(zoom_timestamp)) > 600:
                logger.error(f"🔴 Timestamp too old: {current_time} vs {zoom_timestamp}")
                return False

            # Construct message using BYTES
            message = f"v0:{zoom_timestamp}:".encode() + raw_body_bytes
            
            # Handle secret key whether stored as string or bytes
            secret = settings.ZOOM_WEBHOOK_SECRET
            if isinstance(secret, str):
                secret = secret.encode()

            # Generate HMAC-SHA256 hash
            hash_for_verify = hmac.new(
                secret,
                message,
                hashlib.sha256
            ).hexdigest()

            expected_signature = f"v0={hash_for_verify}"

            # Securely compare signatures
            result = hmac.compare_digest(zoom_signature, expected_signature)
            if not result:
                logger.error(f"🔴 Signature mismatch\n  Expected: {expected_signature}\n  Received: {zoom_signature}")
            return result
            
        except Exception as e:
            logger.exception(f"🔥 Signature verification error: {e}")
            return False

    def extract_meeting_data(self, payload):
        """Extract meeting data from webhook payload"""
        try:
            meeting = payload.get("payload", {}).get("object", {})
            return {
                "meeting_id": str(meeting.get("id")),
                "topic": meeting.get("topic", "No Topic"),
                "host_email": meeting.get("host_email"),
                "files": meeting.get("recording_files", []),
                "download_token": payload.get("download_token")
            }
        except Exception as e:
            logger.exception(f"🔥 Failed to extract meeting data: {e}")
            return None

    def handle_zoom_url_validation(self, payload):
        """Handle Zoom CRC (Certificate of Completion) validation"""
        logger.info("🟢 Handling URL validation request")
        plain_token = payload.get("payload", {}).get("plainToken")
        
        if not plain_token:
            logger.error("🔴 Missing plainToken in CRC payload")
            return JsonResponse({"error": "Missing plainToken"}, status=400)

        try:
            # Convert secret to bytes if needed
            secret = settings.ZOOM_WEBHOOK_SECRET
            if isinstance(secret, str):
                secret = secret.encode()
                
            encrypted_token = hmac.new(
                secret,
                plain_token.encode(),
                hashlib.sha256
            ).hexdigest()

            logger.info(f"🟢 Generated encrypted token for CRC: {encrypted_token}")
            output = {
                "plainToken": plain_token,
                "encryptedToken": encrypted_token
            }
            json_dumped_response = json.dumps(output, ensure_ascii=False)
            print("output:", json_dumped_response)
            return HttpResponse(json_dumped_response, content_type="application/json", status=200)
            return JsonResponse(output, status=200, content_type='application/json')

        except Exception as e:
            logger.exception(f"🔥 CRC token encryption failed: {e}")
            return JsonResponse({"error": "Token encryption failed"}, status=500)

    def post(self, request, *args, **kwargs):
        """Handle incoming Zoom webhook POST requests"""
        # Preserve original body bytes for signature verification
        raw_body_bytes = request.body
        raw_body_str = raw_body_bytes.decode('utf-8', errors='replace')  # For JSON parsing
        
        # Log incoming request details
        logger.info("📥 Incoming Zoom webhook request:")
        logger.info(f"  Headers: {dict(request.headers)}")
        logger.info(f"  Raw body: {raw_body_str[:500]}")  # Log first 500 chars

        try:
            # Parse JSON payload if exists
            payload = json.loads(raw_body_str) if raw_body_str else {}
        except json.JSONDecodeError:
            logger.error("🔴 Invalid JSON payload")
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        print("input", payload)
        event_type = payload.get("event")
        logger.info(f"🟢 Event type: {event_type}")

        # Handle URL validation (CRC) separately
        if event_type == "endpoint.url_validation":
            logger.info("🟢 Handling CRC validation request")
            return self.handle_zoom_url_validation(payload)

        # Verify signature for all other events
        if not self.verify_zoom_signature(request, raw_body_bytes):
            logger.error("🔴 Signature verification failed - rejecting request")
            return HttpResponseForbidden("Invalid Zoom signature")

        # Only process transcript_completed events
        if event_type != "recording.transcript_completed":
            logger.info(f"🟡 Ignoring unsupported event: {event_type}")
            return JsonResponse({"status": "Ignored event"}, status=200)

        # Extract meeting data from payload
        logger.info("🟢 Processing transcript_completed event")
        data = self.extract_meeting_data(payload)
        if not data:
            logger.error("🔴 Failed to extract meeting data from payload")
            return JsonResponse({"error": "Malformed payload"}, status=400)

        # Find user by host email
        host_email = data.get("host_email")
        if not host_email:
            logger.error("🔴 Missing host_email in payload")
            return JsonResponse({"error": "Missing host email"}, status=400)
            
        logger.info(f"🟢 Looking for host: {host_email}")
        user = User.objects.filter(email=host_email).first()
        if not user:
            logger.error(f"🔴 Host user not found: {host_email}")
            return JsonResponse({"error": "Host user not found"}, status=404)

        # Process transcript using ZoomService
        try:
            logger.info(f"🟢 Processing transcript for meeting: {data['meeting_id']}")
            ZoomService(user).process_transcript_from_webhook(
                {
                    "id": data["meeting_id"],
                    "topic": data["topic"],
                    "recording_files": data["files"],
                },
                data["download_token"]
            )
            logger.info("✅ Transcript processed successfully")
            return JsonResponse({"status": "Transcript processed"}, status=200)
            
        except Exception as e:
            logger.exception(f"🔥 Transcript processing failed: {e}")
            return JsonResponse({"error": "Internal server error"}, status=500)