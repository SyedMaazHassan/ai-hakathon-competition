import logging
import requests

from apps.integrations.salesforce.oauth import SalesforceBaseConfig, SalesforceOAuth
from apps.integrations.models import SalesforceCredential
from apps.integrations.utils.crypto import TokenEncryptor

logger = logging.getLogger(__name__)


class SalesforceClient(SalesforceBaseConfig):
    """
    Handles low-level HTTP interactions with Salesforce API.
    Automatically refreshes tokens if needed.
    """

    def __init__(self, user):
        super().__init__(user)
        self.oauth = SalesforceOAuth(user)

    def request(self, method, path, **kwargs):
        url = f"{self.token_data.instance_url}{path}"
        headers = self.oauth._get_headers()
        kwargs.setdefault("headers", headers)

        response = requests.request(method, url, **kwargs)

        if response.status_code == 401:
            self.oauth._refresh_access_token()
            headers = self.oauth._get_headers()
            kwargs["headers"] = headers
            response = requests.request(method, url, **kwargs)

        response.raise_for_status()
        return response
