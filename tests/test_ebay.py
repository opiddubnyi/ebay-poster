# tests/test_ebay.py
import httpx
import respx
import pytest
from poster.ebay import EbayClient
from poster.exceptions import AuthError


SANDBOX_TOKEN_URL = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"


@pytest.fixture
def credentials():
    return {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "refresh_token": "test_refresh_token",
        "ru_name": "test_runame",
        "environment": "sandbox",
    }


@respx.mock
def test_refresh_access_token(credentials):
    respx.post(SANDBOX_TOKEN_URL).mock(
        return_value=httpx.Response(200, json={
            "access_token": "new_access_token",
            "expires_in": 7200,
            "token_type": "User Access Token",
        })
    )
    client = EbayClient(credentials)
    token = client.refresh_access_token()
    assert token == "new_access_token"
    assert client.access_token == "new_access_token"


@respx.mock
def test_refresh_access_token_failure(credentials):
    respx.post(SANDBOX_TOKEN_URL).mock(
        return_value=httpx.Response(401, json={"error": "invalid_grant"})
    )
    client = EbayClient(credentials)
    with pytest.raises(AuthError, match="Failed to refresh"):
        client.refresh_access_token()


def test_api_base_url_sandbox(credentials):
    client = EbayClient(credentials)
    assert client.api_base == "https://api.sandbox.ebay.com"


def test_api_base_url_production(credentials):
    credentials["environment"] = "production"
    client = EbayClient(credentials)
    assert client.api_base == "https://api.ebay.com"


@respx.mock
def test_consent_url(credentials):
    client = EbayClient(credentials)
    url = client.get_consent_url()
    assert "auth.sandbox.ebay.com" in url
    assert "test_client_id" in url
    assert "test_runame" in url
    assert "sell.inventory" in url
