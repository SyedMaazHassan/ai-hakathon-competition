from django.conf import settings


ZOOM_AUTH_BASE_URL = "https://zoom.us/oauth/authorize"
ZOOM_TOKEN_URL = "https://zoom.us/oauth/token"
ZOOM_RECORDING_URL = "https://api.zoom.us/v2/users/me/recordings"

ZOOM_CLIENT_ID=settings.ZOOM_CLIENT_ID
ZOOM_CLIENT_SECRET=settings.ZOOM_CLIENT_SECRET
ZOOM_REDIRECT_URI=settings.ZOOM_REDIRECT_URI
ZOOM_WEBHOOK_SECRET=settings.ZOOM_WEBHOOK_SECRET