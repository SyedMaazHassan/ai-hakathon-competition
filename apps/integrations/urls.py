from django.urls import path
from .salesforce import service as salesforce_service
from . import views
from .zoom import webhook as zoom_webhook

urlpatterns = [
    #salesforce urls
    path("salesforce/connect/", views.ConnectSalesforceView.as_view(), name="connect_salesforce"),
    path("salesforce/callback/", views.SalesforceCallbackView.as_view(), name="salesforce_callback"),
    path('salesforce/sync-contacts/', views.FetchSalesforceContactsView.as_view(), name="fetch_user_contacts"),
    
    #zoom urls
    path("zoom/login/", views.ZoomLoginView.as_view(), name="zoom_login"),
    path("zoom/callback/", views.ZoomCallbackView.as_view(), name="zoom_callback"),
    path("zoom/meetings/", views.ZoomMeetingsTranscriptsView.as_view(), name="zoom_meetings"),
    path('zoom/webhook/', zoom_webhook.ZoomWebhookView.as_view(), name='zoom_webhook'),
    
    #google drive
    path("drive/connect/", views.GoogleDriveConnectView.as_view(), name="google_drive_connect"),
    path("drive/callback/", views.GoogleDriveCallbackView.as_view(), name="google_drive_callback"),
    path("drive/listfiles/", views.GoogleDriveListFilesView.as_view(), name="google_drive_list"),

    # Google Calendar URLs
    path("calendar/connect/", views.GoogleCalendarConnectView.as_view(), name="google_calendar_connect"),
    path("calendar/callback/", views.GoogleCalendarCallbackView.as_view(), name="google_calendar_callback"),
    path("calendar/list/", views.GoogleCalendarListView.as_view(), name="google_calendar_list"),
    path("calendar/events/", views.GoogleCalendarEventsView.as_view(), name="google_calendar_events"),

    # Google Maps URLs (Internal API)
    path("maps/geocode/", views.GoogleMapsGeocodeView.as_view(), name="google_maps_geocode"),
    path("maps/nearby/", views.GoogleMapsNearbyView.as_view(), name="google_maps_nearby"),
    path("maps/directions/", views.GoogleMapsDirectionsView.as_view(), name="google_maps_directions"),

    # Twilio SMS URLs (Internal API)
    path("sms/send/", views.TwilioSendSMSView.as_view(), name="twilio_send_sms"),
    path("sms/status/<str:message_sid>/", views.TwilioSMSStatusView.as_view(), name="twilio_sms_status"),
    path("sms/history/", views.TwilioSMSHistoryView.as_view(), name="twilio_sms_history"),

]