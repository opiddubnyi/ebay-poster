# poster/ebay.py
import base64
import time
from urllib.parse import urlencode

import httpx

from poster.exceptions import AuthError


EBAY_OAUTH_SCOPES = [
    "https://api.ebay.com/oauth/api_scope",
    "https://api.ebay.com/oauth/api_scope/sell.inventory",
    "https://api.ebay.com/oauth/api_scope/sell.account",
]


class EbayClient:
    def __init__(self, credentials: dict):
        self._client_id = credentials["client_id"]
        self._client_secret = credentials["client_secret"]
        self._refresh_token = credentials.get("refresh_token")
        self._ru_name = credentials.get("ru_name")
        self._environment = credentials.get("environment", "sandbox")
        self.access_token: str | None = None
        self._token_expiry: float = 0

    @property
    def api_base(self) -> str:
        if self._environment == "production":
            return "https://api.ebay.com"
        return "https://api.sandbox.ebay.com"

    @property
    def _media_base(self) -> str:
        if self._environment == "production":
            return "https://apim.ebay.com"
        return "https://apim.sandbox.ebay.com"

    @property
    def _auth_base(self) -> str:
        if self._environment == "production":
            return "https://auth.ebay.com"
        return "https://auth.sandbox.ebay.com"

    @property
    def _token_url(self) -> str:
        return f"{self.api_base}/identity/v1/oauth2/token"

    def _basic_auth_header(self) -> str:
        raw = f"{self._client_id}:{self._client_secret}"
        return base64.b64encode(raw.encode()).decode()

    def refresh_access_token(self) -> str:
        response = httpx.post(
            self._token_url,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {self._basic_auth_header()}",
            },
            data={
                "grant_type": "refresh_token",
                "refresh_token": self._refresh_token,
            },
        )
        if response.status_code != 200:
            raise AuthError(f"Failed to refresh access token: {response.text}")
        data = response.json()
        self.access_token = data["access_token"]
        self._token_expiry = time.time() + data.get("expires_in", 7200) - 60
        return self.access_token

    def _ensure_token(self) -> str:
        if not self.access_token or time.time() >= self._token_expiry:
            self.refresh_access_token()
        return self.access_token

    def _auth_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._ensure_token()}",
            "Content-Type": "application/json",
            "Content-Language": "en-US",
        }

    def get_consent_url(self) -> str:
        params = urlencode({
            "client_id": self._client_id,
            "redirect_uri": self._ru_name,
            "response_type": "code",
            "scope": " ".join(EBAY_OAUTH_SCOPES),
        })
        return f"{self._auth_base}/oauth2/authorize?{params}"

    def exchange_auth_code(self, auth_code: str) -> dict:
        response = httpx.post(
            self._token_url,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {self._basic_auth_header()}",
            },
            data={
                "grant_type": "authorization_code",
                "code": auth_code,
                "redirect_uri": self._ru_name,
            },
        )
        if response.status_code != 200:
            raise AuthError(f"Failed to exchange auth code: {response.text}")
        data = response.json()
        self.access_token = data["access_token"]
        self._token_expiry = time.time() + data.get("expires_in", 7200) - 60
        self._refresh_token = data["refresh_token"]
        return {
            "access_token": data["access_token"],
            "refresh_token": data["refresh_token"],
        }
