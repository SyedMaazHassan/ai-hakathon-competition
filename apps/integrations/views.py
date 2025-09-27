from apps.integrations.models import ZoomCredential
from apps.integrations.zoom.oauth import ZoomOAuth
from django.http import HttpResponseBadRequest
from django.shortcuts import render
from apps.integrations.models import SalesforceCredential
from apps.integrations.salesforce.oauth import SalesforceOAuth
import requests
from django.contrib.auth.mixins import LoginRequiredMixin
import logging
from django.contrib import messages
from .salesforce.service import SalesforceService
from .utils.crypto import TokenEncryptor
from apps.integrations.google_drive.oauth import GoogleDriveOAuth
from apps.integrations.google_drive.service import GoogleDriveService
from apps.integrations.google_calendar.oauth import GoogleCalendarOAuth
from apps.integrations.google_calendar.service import GoogleCalendarService
from apps.integrations.google_maps.service import GoogleMapsService
from apps.integrations.twilio_sms.service import TwilioSMSService
logger = logging.getLogger(__name__)
from django.utils import timezone
from django.views import View
from django.http import JsonResponse
from django.shortcuts import redirect
from apps.integrations.zoom.service import ZoomService


class ZoomMeetingsTranscriptsView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)

        if not request.user.zoom_token.exists():
            messages.warning(request, "Please connect your Zoom account first.")
            return redirect("profile")

        try:
            service = ZoomService(user=request.user)
        
            saved_transcripts = service.fetch_and_save_transcripts()
            messages.success(request, f"Successfully saved {len(saved_transcripts)} transcript(s).")
        except Exception as e:
            return JsonResponse({"error": f"Failed to fetch transcripts: {str(e)}"}, status=500)

        return redirect("transcripts_list")



class ZoomLoginView(View):
    """
    Redirects user to Zoom's OAuth authorization URL.
    """
    def get(self, request, *args, **kwargs):
        zoom_oauth = ZoomOAuth()
        auth_url = zoom_oauth.get_authorization_url()
        return redirect(auth_url)

class ZoomCallbackView(LoginRequiredMixin, View):
    """
    Handles Zoom OAuth callback and stores tokens in the DB.
    """
    def get(self, request, *args, **kwargs):
        code = request.GET.get("code")

        if not code:
            return JsonResponse({"error": "Authorization code not found"}, status=400)

        zoom_oauth = ZoomOAuth()
        try:
            token_data = zoom_oauth.get_access_token(code)

            ZoomCredential.objects.update_or_create(
                user=request.user,
                defaults={
                    "access_token": TokenEncryptor.encrypt(token_data["access_token"]),
                    "refresh_token": TokenEncryptor.encrypt(token_data["refresh_token"]),
                    "expires_in": token_data["expires_in"],
                    "created_at": timezone.now(),
                }
            )
            messages.success(request, "Zoom connected successfully!")
            return redirect("profile")

        except Exception as e:
            return JsonResponse({"error": f"Failed to authenticate with Zoom: {str(e)}"}, status=500)


class ConnectSalesforceView(LoginRequiredMixin, View):
    """
    Views for Connecting The SalesForce Account
    """
    def get(self, request, *args, **kwargs):
        oauth = SalesforceOAuth(user=request.user, session=request.session)
        auth_url = oauth.get_authorization_url(prompt_consent=True)
        return redirect(auth_url)

# room_views.py

class GoogleDriveConnectView(View):
    def get(self, request):
        oauth = GoogleDriveOAuth(user=request.user)
        auth_url, state = oauth.get_authorization_url()
        request.session['gd_state'] = state
        return redirect(auth_url)

class GoogleDriveCallbackView(View):
    def get(self, request):
        state = request.session.get('gd_state')
        if not state:
            messages.error(request, "OAuth state is missing. Please try connecting again.")
            return redirect('dashboard')

        oauth = GoogleDriveOAuth(user=request.user)
        try:
            oauth.exchange_code_for_token(request.build_absolute_uri())
            messages.success(request, "✅ Google Drive connected successfully!")
        except Exception as e:
            messages.error(request, f"❌ Failed to connect Google Drive: {str(e)}")

        return redirect('dashboard')



class GoogleDriveListFilesView(LoginRequiredMixin, View):
    def get(self, request):
        try:
            google_drive_service = GoogleDriveService(user=request.user)
            files_response = google_drive_service.list_user_files()

            # Extract files from the response
            if files_response.get('success'):
                files = files_response.get('data', {}).get('files', [])
            else:
                files = []

            context = {
                'drive_files': files,
                'success': files_response.get('success', False),
                'error': files_response.get('error', None) if not files_response.get('success') else None
            }

            return render(request, 'list_files.html', context)

        except Exception as e:
            context = {
                'drive_files': [],
                'success': False,
                'error': str(e)
            }
            return render(request, 'list_files.html', context)

class SalesforceCallbackView(LoginRequiredMixin, View):
    """
    OAuth Callback view for Salesforce
    """
    def get(self, request, *args, **kwargs):
        code = request.GET.get("code")
        if not code:
            return HttpResponseBadRequest("No authorization code provided.")

        state = request.GET.get("state")
        oauth = SalesforceOAuth(user=request.user, session=request.session)

        try:
            token_data = oauth.fetch_token(code, state=state)
        except requests.exceptions.RequestException as e:
            return HttpResponseBadRequest(f"Failed to fetch token: {str(e)}")

        salesforce_id_url = token_data.get("id", "")
        salesforce_id = salesforce_id_url.split("/")[-1] if salesforce_id_url else ""

        SalesforceCredential.objects.update_or_create(
            user=request.user,
            defaults={
                "access_token": TokenEncryptor.encrypt(token_data.get("access_token")),
                "refresh_token": TokenEncryptor.encrypt(token_data.get("refresh_token")),
                "signature": token_data.get("signature"),
                "scope": token_data.get("scope"),
                "instance_url": token_data.get("instance_url"),
                "salesforce_id": salesforce_id,
                "token_type": token_data.get("token_type"),
                "issued_at": int(token_data.get("issued_at")),
            }
        )

        return redirect("home")



class FetchSalesforceContactsView(LoginRequiredMixin, View):
    """
    View to fetch and import Salesforce contacts into local DB
    """
    def get(self, request, *args, **kwargs):
        service = SalesforceService(request.user)

        try:
            contacts = service.fetch_contacts()
            saved_data = service.import_contacts_to_db(request.user, contacts)

            messages.success(request, f"Successfully imported {len(saved_data)} Salesforce contact(s).")
        except Exception as e:
            messages.error(request, f"Salesforce import failed: {str(e)}")

        return redirect("deal_list")


# =============================================================================
# GOOGLE CALENDAR VIEWS
# =============================================================================

class GoogleCalendarConnectView(LoginRequiredMixin, View):
    def get(self, request):
        oauth = GoogleCalendarOAuth(user=request.user)
        auth_url, state = oauth.get_authorization_url()
        request.session['gc_state'] = state
        return redirect(auth_url)


class GoogleCalendarCallbackView(LoginRequiredMixin, View):
    def get(self, request):
        state = request.session.get('gc_state')
        if not state:
            messages.error(request, "OAuth state is missing. Please try connecting again.")
            return redirect('dashboard')

        oauth = GoogleCalendarOAuth(user=request.user)
        try:
            oauth.exchange_code_for_token(request.build_absolute_uri())
            messages.success(request, "✅ Google Calendar connected successfully!")
        except Exception as e:
            messages.error(request, f"❌ Failed to connect Google Calendar: {str(e)}")

        return redirect('dashboard')


class GoogleCalendarListView(LoginRequiredMixin, View):
    def get(self, request):
        try:
            calendar_service = GoogleCalendarService(user=request.user)
            calendars_response = calendar_service.list_user_calendars()

            if calendars_response.get('success'):
                calendars = calendars_response.get('data', {}).get('calendars', [])
            else:
                calendars = []

            return JsonResponse({
                'success': calendars_response.get('success', False),
                'calendars': calendars,
                'error': calendars_response.get('error', None) if not calendars_response.get('success') else None
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'calendars': [],
                'error': str(e)
            })


class GoogleCalendarEventsView(LoginRequiredMixin, View):
    def get(self, request):
        calendar_id = request.GET.get('calendar_id', 'primary')
        days_ahead = int(request.GET.get('days_ahead', 30))

        try:
            calendar_service = GoogleCalendarService(user=request.user)
            events_response = calendar_service.list_upcoming_events(calendar_id, days_ahead)

            if events_response.get('success'):
                events = events_response.get('data', {}).get('events', [])
            else:
                events = []

            return JsonResponse({
                'success': events_response.get('success', False),
                'events': events,
                'error': events_response.get('error', None) if not events_response.get('success') else None
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'events': [],
                'error': str(e)
            })


# =============================================================================
# GOOGLE MAPS VIEWS (Internal API - No OAuth)
# =============================================================================

class GoogleMapsGeocodeView(View):
    def get(self, request):
        address = request.GET.get('address')
        if not address:
            return JsonResponse({'success': False, 'error': 'Address parameter required'})

        try:
            maps_service = GoogleMapsService()
            result = maps_service.get_coordinates_from_address(address)
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


class GoogleMapsNearbyView(View):
    def get(self, request):
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        radius = request.GET.get('radius', 1000)
        place_type = request.GET.get('type')

        if not lat or not lng:
            return JsonResponse({'success': False, 'error': 'lat and lng parameters required'})

        try:
            maps_service = GoogleMapsService()
            result = maps_service.find_nearby_places(
                float(lat), float(lng), int(radius), place_type
            )
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


class GoogleMapsDirectionsView(View):
    def get(self, request):
        origin = request.GET.get('origin')
        destination = request.GET.get('destination')
        mode = request.GET.get('mode', 'driving')

        if not origin or not destination:
            return JsonResponse({'success': False, 'error': 'origin and destination parameters required'})

        try:
            maps_service = GoogleMapsService()
            result = maps_service.get_route_directions(origin, destination, mode)
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


# =============================================================================
# TWILIO SMS VIEWS (Internal API - No OAuth)
# =============================================================================

class TwilioSendSMSView(View):
    def post(self, request):
        to_number = request.POST.get('to_number')
        message = request.POST.get('message')
        message_type = request.POST.get('type', 'general')  # general, alert, notification, otp

        if not to_number or not message:
            return JsonResponse({'success': False, 'error': 'to_number and message parameters required'})

        try:
            sms_service = TwilioSMSService()

            if message_type == 'alert':
                alert_type = request.POST.get('alert_type', 'info')
                result = sms_service.send_alert_sms(to_number, alert_type, message)
            elif message_type == 'notification':
                title = request.POST.get('title', 'Notification')
                result = sms_service.send_notification_sms(to_number, title, message)
            elif message_type == 'otp':
                otp_code = request.POST.get('otp_code', message)
                app_name = request.POST.get('app_name', 'App')
                result = sms_service.send_otp_sms(to_number, otp_code, app_name)
            else:
                result = sms_service.send_sms(to_number, message)

            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


class TwilioSMSStatusView(View):
    def get(self, request, message_sid):
        try:
            sms_service = TwilioSMSService()
            result = sms_service.check_message_status(message_sid)
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


class TwilioSMSHistoryView(View):
    def get(self, request):
        phone_number = request.GET.get('phone_number')
        limit = int(request.GET.get('limit', 50))

        try:
            sms_service = TwilioSMSService()
            result = sms_service.get_message_history(phone_number, limit)
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

