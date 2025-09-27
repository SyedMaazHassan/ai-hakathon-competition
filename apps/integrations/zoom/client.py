import requests
from apps.integrations.zoom.oauth import ZoomOAuth


class ZoomClient:
    """
    Thin HTTP client for Zoom API with token injection and auto-refresh.
    """

    def __init__(self, user):
        self.user = user
        self.oauth = ZoomOAuth()
        self.access_token, error = self.oauth.get_valid_access_token(user)
        if error:
            raise Exception(f"Zoom Auth failed: {error}")

    def request(self, method, url, params=None, data=None, headers=None, stream=False, retry=True):
        headers = headers or {}
        headers.update({"Authorization": f"Bearer {self.access_token}"})

        response = requests.request(
            method=method,
            url=url,
            params=params,
            data=data,
            headers=headers,
            stream=stream,
        )

        if response.status_code == 401 and retry:
            self.access_token, _ = self.oauth.get_valid_access_token(self.user)
            return self.request(method, url, params, data, headers, stream, retry=False)

        if stream or method.lower() in ["post", "put", "delete"]:
            return response
        response.raise_for_status()
        return response.json()
