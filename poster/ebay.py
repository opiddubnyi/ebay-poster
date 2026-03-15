# poster/ebay.py
import base64
import time
import uuid
from urllib.parse import urlencode

import httpx

from poster.exceptions import AuthError, ListingError
from poster.media import upload_photos
from poster.models import Listing


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

    def _generate_sku(self, listing: Listing) -> str:
        short_id = uuid.uuid4().hex[:8]
        return f"{listing.team}-{listing.year}-{short_id}".upper()

    def _to_inventory_item(self, listing: Listing, image_urls: list[str]) -> dict:
        aspects = {
            "Brand": [listing.brand],
            "Size": [listing.size],
            "Team": [listing.team],
        }
        if listing.type:
            aspects["Type"] = [listing.type]

        product = {
            "title": listing.title,
            "imageUrls": image_urls,
            "aspects": aspects,
            "brand": listing.brand,
        }
        if listing.description:
            product["description"] = listing.description

        return {
            "availability": {
                "shipToLocationAvailability": {"quantity": 1}
            },
            "condition": listing.condition,
            "product": product,
        }

    def _to_offer(
        self,
        listing: Listing,
        sku: str,
        category_id: str,
        policies: dict,
        location_key: str,
    ) -> dict:
        offer = {
            "sku": sku,
            "marketplaceId": "EBAY_US",
            "format": "FIXED_PRICE",
            "availableQuantity": 1,
            "categoryId": category_id,
            "listingDuration": "GTC",
            "listingPolicies": {
                "fulfillmentPolicyId": policies["fulfillment_policy_id"],
                "paymentPolicyId": policies["payment_policy_id"],
                "returnPolicyId": policies["return_policy_id"],
            },
            "merchantLocationKey": location_key,
            "pricingSummary": {
                "price": {
                    "currency": "USD",
                    "value": f"{listing.price:.2f}",
                },
            },
        }
        if listing.best_offer:
            offer["listingPolicies"]["bestOfferTerms"] = {"bestOfferEnabled": True}
        return offer

    def _create_inventory_item(
        self, sku: str, listing: Listing, image_urls: list[str]
    ) -> None:
        url = f"{self.api_base}/sell/inventory/v1/inventory_item/{sku}"
        payload = self._to_inventory_item(listing, image_urls)
        response = httpx.put(url, headers=self._auth_headers(), json=payload)
        if response.status_code not in (200, 204):
            raise ListingError(
                f"Failed to create inventory item: {response.text}"
            )

    def _create_offer(
        self,
        listing: Listing,
        sku: str,
        category_id: str,
        policies: dict,
        location_key: str,
    ) -> str:
        url = f"{self.api_base}/sell/inventory/v1/offer"
        payload = self._to_offer(listing, sku, category_id, policies, location_key)
        response = httpx.post(url, headers=self._auth_headers(), json=payload)
        if response.status_code not in (200, 201):
            raise ListingError(f"Failed to create offer: {response.text}")
        return response.json()["offerId"]

    def _publish_offer(self, offer_id: str) -> str:
        url = f"{self.api_base}/sell/inventory/v1/offer/{offer_id}/publish"
        response = httpx.post(url, headers=self._auth_headers())
        if response.status_code != 200:
            raise ListingError(f"Failed to publish offer: {response.text}")
        return response.json()["listingId"]

    def post_listing(
        self,
        listing: Listing,
        category_id: str,
        policies: dict,
        location_key: str,
        dry_run: bool = False,
    ) -> dict:
        sku = self._generate_sku(listing)

        # Upload photos
        image_urls = upload_photos(
            photos=listing.photos,
            access_token=self._ensure_token(),
            media_base=self._media_base,
        )

        if dry_run:
            return {
                "dry_run": True,
                "sku": sku,
                "title": listing.title,
                "price": listing.price,
                "image_count": len(image_urls),
                "inventory_payload": self._to_inventory_item(listing, image_urls),
                "offer_payload": self._to_offer(
                    listing, sku, category_id, policies, location_key
                ),
            }

        # Create inventory item
        self._create_inventory_item(sku, listing, image_urls)

        # Create offer
        offer_id = self._create_offer(
            listing, sku, category_id, policies, location_key
        )

        # Publish
        listing_id = self._publish_offer(offer_id)

        return {
            "listing_id": listing_id,
            "sku": sku,
            "offer_id": offer_id,
            "url": f"https://www.ebay.com/itm/{listing_id}",
        }
