import base64
from datetime import timedelta
from urllib.parse import urlencode
from django.db import transaction
import requests
from django.utils import timezone
from django.conf import settings

from .constants import (
    ZOOM_AUTH_BASE_URL,
    ZOOM_TOKEN_URL,
    ZOOM_CLIENT_ID,
    ZOOM_CLIENT_SECRET,
    ZOOM_REDIRECT_URI
)
from ..models import ZoomCredential
from ..utils.crypto import TokenEncryptor


class ZoomOAuth:
    """
    Handles Zoom OAuth2.0 flow: authorization, token exchange, refresh, and token validation.
    """

    def __init__(self):
        self.client_id = ZOOM_CLIENT_ID
        self.client_secret = ZOOM_CLIENT_SECRET
        self.redirect_uri = ZOOM_REDIRECT_URI

    def get_authorization_url(self, state=None):
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
        }
        if state:
            params["state"] = state
        return f"{ZOOM_AUTH_BASE_URL}?{urlencode(params)}"

    def get_access_token(self, code):
        headers = self._get_auth_headers()
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
        }
        response = requests.post(ZOOM_TOKEN_URL, headers=headers, data=data)
        response.raise_for_status()

        return response.json()

    def refresh_token(self, refresh_token):
        headers = self._get_auth_headers()
        refresh_token = TokenEncryptor.decrypt(refresh_token)
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        response = requests.post(ZOOM_TOKEN_URL, headers=headers, data=data)
        if response.status_code != 200:
            return False, response.text
        return True, response.json()

    def is_token_expired(self, token):
        return timezone.now() >= token.created_at + timedelta(seconds=token.expires_in)

    def get_valid_access_token(self, user):
        """
        Validates and refreshes token if expired. Returns decrypted access token or error message.
        """
        try:
            token = ZoomCredential.objects.filter(user=user).first()
            if not token:
                return None, "Zoom tokens not found for user"

            if self.is_token_expired(token):
                with transaction.atomic():
                    refreshed, data = self.refresh_token(token.refresh_token)
                    if not refreshed:
                        return None, data

                    token.access_token = TokenEncryptor.encrypt(data.get("access_token"))
                    token.refresh_token = TokenEncryptor.encrypt(data.get("refresh_token"))
                    token.expires_in = data.get("expires_in", 3600)
                    token.created_at = timezone.now()
                    token.save()

            return TokenEncryptor.decrypt(token.access_token), None

        except ZoomCredential.DoesNotExist:
            return None, "Zoom credential not found in DB"
        except KeyError as e:
            return None, f"Missing key in token response: {str(e)}"
        except Exception as e:
            return None, f"Unexpected error while validating Zoom token: {str(e)}"

    def _get_auth_headers(self, access_token=None):
        """
        Basic Auth header using client_id and client_secret.
        """
        if access_token:
            return {
                "Authorization": f"Bearer {access_token}"
            }
        creds = f"{self.client_id}:{self.client_secret}"
        b64_creds = base64.b64encode(creds.encode()).decode()
        return {
            "Authorization": f"Basic {b64_creds}",
            "Content-Type": "application/x-www-form-urlencoded"
        }