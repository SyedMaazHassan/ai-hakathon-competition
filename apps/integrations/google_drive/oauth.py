from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from django.utils import timezone
from apps.integrations.models import GoogleDriveCredential
from . import constants
from django.conf import settings
import datetime

class GoogleDriveOAuth:
    def __init__(self, user):
        self.user = user

    def get_authorization_url(self, state=None):
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_DRIVE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_DRIVE_CLIENT_SECRET,
                    "redirect_uris": [constants.REDIRECT_URI],
                    "auth_uri": constants.AUTH_URI,
                    "token_uri": constants.TOKEN_URI,
                }
            },
            scopes=constants.SCOPES,
            state=state
        )
        flow.redirect_uri = constants.REDIRECT_URI
        auth_url, new_state = flow.authorization_url(
            access_type="offline", 
            include_granted_scopes="true",
            prompt='consent'
        )
        return auth_url, new_state

    def exchange_code_for_token(self, authorization_response_url):
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_DRIVE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_DRIVE_CLIENT_SECRET,
                    "redirect_uris": [constants.REDIRECT_URI],
                    "auth_uri": constants.AUTH_URI,
                    "token_uri": constants.TOKEN_URI,
                }
            },
            scopes=constants.SCOPES
        )
        flow.redirect_uri = constants.REDIRECT_URI
        flow.fetch_token(authorization_response=authorization_response_url)
        creds = flow.credentials
        self._save_credentials(creds)
        return creds

    def get_valid_credentials(self):
        try:
            creds = GoogleDriveCredential.objects.get(user=self.user)
            credentials = Credentials(
                token=creds.access_token,
                refresh_token=creds.refresh_token,
                token_uri=creds.token_uri,
                client_id=settings.GOOGLE_DRIVE_CLIENT_ID,
                client_secret=settings.GOOGLE_DRIVE_CLIENT_SECRET,
                scopes=creds.scopes.split(','),
            )

            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                self._save_credentials(credentials)

            return credentials
        except GoogleDriveCredential.DoesNotExist:
            raise Exception("Google Drive not connected")

    def _save_credentials(self, creds):
        expiry = creds.expiry if creds.expiry else timezone.now() + datetime.timedelta(hours=1)
        
        GoogleDriveCredential.objects.update_or_create(
            user=self.user,
            defaults={
                "access_token": creds.token,
                "refresh_token": creds.refresh_token,
                "token_uri": creds.token_uri,
                "scopes": ",".join(creds.scopes),
                "expiry": expiry,
            }
        )
