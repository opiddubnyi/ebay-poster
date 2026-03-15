# tests/test_ebay_listing.py
import httpx
import respx
import pytest
from pathlib import Path
from poster.ebay import EbayClient
from poster.models import Listing
from poster.exceptions import ListingError


SANDBOX_BASE = "https://api.sandbox.ebay.com"
SANDBOX_MEDIA = "https://apim.sandbox.ebay.com"
SANDBOX_TOKEN_URL = f"{SANDBOX_BASE}/identity/v1/oauth2/token"


@pytest.fixture
def client():
    c = EbayClient({
        "client_id": "test_id",
        "client_secret": "test_secret",
        "refresh_token": "test_token",
        "ru_name": "test_runame",
        "environment": "sandbox",
    })
    c.access_token = "pre_set_token"
    c._token_expiry = 9999999999
    return c


@pytest.fixture
def listing(tmp_path):
    photo = tmp_path / "jersey.jpg"
    photo.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)
    return Listing(
        team="Brazil",
        year="1998",
        brand="Nike",
        size="XL",
        price=200.0,
        photos=[photo],
        type="Home",
        condition="USED_GOOD",
    )


def test_to_inventory_item(client, listing):
    payload = client._to_inventory_item(
        listing, image_urls=["https://i.ebayimg.com/test.jpg"]
    )
    assert payload["product"]["title"] == listing.title
    assert payload["condition"] == "USED_GOOD"
    assert payload["product"]["aspects"]["Brand"] == ["Nike"]
    assert payload["product"]["aspects"]["Team"] == ["Brazil"]
    assert payload["availability"]["shipToLocationAvailability"]["quantity"] == 1


def test_to_offer(client, listing):
    payload = client._to_offer(
        listing,
        sku="TEST-SKU",
        category_id="185099",
        policies={
            "fulfillment_policy_id": "fp1",
            "payment_policy_id": "pp1",
            "return_policy_id": "rp1",
        },
        location_key="my-warehouse",
    )
    assert payload["sku"] == "TEST-SKU"
    assert payload["pricingSummary"]["price"]["value"] == "200.00"
    assert payload["pricingSummary"]["price"]["currency"] == "USD"
    assert payload["categoryId"] == "185099"


@respx.mock
def test_create_inventory_item(client, listing):
    respx.put(f"{SANDBOX_BASE}/sell/inventory/v1/inventory_item/TEST-SKU").mock(
        return_value=httpx.Response(204)
    )
    client._create_inventory_item(
        sku="TEST-SKU",
        listing=listing,
        image_urls=["https://i.ebayimg.com/test.jpg"],
    )


@respx.mock
def test_create_offer(client, listing):
    respx.post(f"{SANDBOX_BASE}/sell/inventory/v1/offer").mock(
        return_value=httpx.Response(201, json={"offerId": "999"})
    )
    offer_id = client._create_offer(
        listing=listing,
        sku="TEST-SKU",
        category_id="185099",
        policies={
            "fulfillment_policy_id": "fp1",
            "payment_policy_id": "pp1",
            "return_policy_id": "rp1",
        },
        location_key="my-warehouse",
    )
    assert offer_id == "999"


@respx.mock
def test_publish_offer(client):
    respx.post(f"{SANDBOX_BASE}/sell/inventory/v1/offer/999/publish").mock(
        return_value=httpx.Response(200, json={"listingId": "123456789"})
    )
    listing_id = client._publish_offer("999")
    assert listing_id == "123456789"


@respx.mock
def test_publish_offer_failure(client):
    respx.post(f"{SANDBOX_BASE}/sell/inventory/v1/offer/999/publish").mock(
        return_value=httpx.Response(400, json={
            "errors": [{"message": "Missing required field"}]
        })
    )
    with pytest.raises(ListingError, match="Failed to publish"):
        client._publish_offer("999")


def test_generate_sku_no_spaces(client):
    listing = Listing(
        team="Manchester United",
        year="1999",
        brand="Umbro",
        size="L",
        price=300.0,
        photos=[Path("test.jpg")],
    )
    sku = client._generate_sku(listing)
    assert " " not in sku
    assert "MANCHESTER-UNITED" in sku
