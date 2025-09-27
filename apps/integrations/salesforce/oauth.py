import os
import base64
import hashlib
import urllib.parse
import logging
import requests
from django.core import signing

from apps.integrations.models import SalesforceCredential
from apps.integrations.salesforce.constants import (
    SALESFORCE_CLIENT_ID, SALESFORCE_CLIENT_SECRET, SALESFORCE_REDIRECT_URI,
    SALESFORCE_AUTH_URL, SALESFORCE_TOKEN_URL, DEFAULT_SCOPE
)
from apps.integrations.utils.crypto import TokenEncryptor

logger = logging.getLogger(__name__)


class SalesforceBaseConfig:
    def __init__(self, user=None, session=None, scope=None):
        self.user = user
        self.session = session
        self.scope = scope or DEFAULT_SCOPE

        self.client_id = SALESFORCE_CLIENT_ID
        self.client_secret = SALESFORCE_CLIENT_SECRET
        self.redirect_uri = SALESFORCE_REDIRECT_URI
        self.auth_url = SALESFORCE_AUTH_URL
        self.token_url = SALESFORCE_TOKEN_URL
        self._token_data = None

    @property
    def token_data(self):
        if not self._token_data:
            try:
                self._token_data = SalesforceCredential.objects.get(user=self.user)
            except SalesforceCredential.DoesNotExist:
                raise Exception("Salesforce tokens not found for user.")
        return self._token_data



class SalesforceOAuth(SalesforceBaseConfig):
    def get_authorization_url(self, prompt_consent=False):
        code_verifier = self._generate_code_verifier()
        code_challenge = self._generate_code_challenge(code_verifier)
        self._store_verifier(code_verifier)

        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": self.scope,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "state": signing.dumps(code_verifier),
        }
        if prompt_consent:
            params["prompt"] = "consent"

        return f"{self.auth_url}?{urllib.parse.urlencode(params)}"

    def fetch_token(self, code, state):
        if not state:
            raise ValueError("Missing 'state' from OAuth callback.")
        code_verifier = signing.loads(state)

        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "code_verifier": code_verifier,
        }

        return self._post_token_request(payload, context="Token Exchange")

    def refresh_access_token(self, refresh_token):
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        return self._post_token_request(payload, context="Token Refresh")

    def _post_token_request(self, data, context="Token Request"):
        try:
            response = requests.post(self.token_url, data=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.exception(f"{context} failed for user: {self.user}")
            raise Exception(f"{context} failed.") from e

    def _generate_code_verifier(self):
        return base64.urlsafe_b64encode(os.urandom(40)).rstrip(b'=').decode()

    def _generate_code_challenge(self, verifier):
        digest = hashlib.sha256(verifier.encode()).digest()
        return base64.urlsafe_b64encode(digest).rstrip(b'=').decode()

    def _store_verifier(self, verifier):
        if self.session:
            self.session['sf_code_verifier'] = verifier
            self.session.modified = True
            self.session.save()

    def _get_headers(self):
        access_token = TokenEncryptor.decrypt(self.token_data.access_token)
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    def _refresh_access_token(self):
        refresh_token = TokenEncryptor.decrypt(self.token_data.refresh_token)
        try:
            token_response = self.refresh_access_token(refresh_token)
        except requests.HTTPError as e:
            if e.response.json().get("error") == "invalid_grant":
                logger.warning(f"Refresh token expired for user {self.user}. Re-auth required.")
                raise Exception("Refresh token expired. Please reconnect Salesforce.")
            raise

        self._update_token_data(token_response)

    def _update_token_data(self, token_response):
        self.token_data.access_token = TokenEncryptor.encrypt(token_response.get("access_token"))
        if "refresh_token" in token_response:
            self.token_data.refresh_token = TokenEncryptor.encrypt(token_response["refresh_token"])
        self.token_data.instance_url = token_response.get("instance_url", self.token_data.instance_url)
        self.token_data.token_type = token_response.get("token_type", self.token_data.token_type)
        self.token_data.scope = token_response.get("scope", self.token_data.scope)
        self.token_data.issued_at = int(token_response.get("issued_at", self.token_data.issued_at))
        self.token_data.save()
