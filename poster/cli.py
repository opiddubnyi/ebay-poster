# poster/cli.py
import argparse
import sys
import webbrowser
from pathlib import Path

from poster.config import Config
from poster.ebay import EbayClient
from poster.exceptions import PosterError
from poster.models import Listing


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="poster",
        description="Post vintage soccer jersey listings to eBay",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # post command
    post = subparsers.add_parser("post", help="Create a new listing")
    post.add_argument("--team", required=True)
    post.add_argument("--year", required=True)
    post.add_argument("--brand", required=True)
    post.add_argument("--size", required=True)
    post.add_argument("--price", type=float, required=True)
    post.add_argument("--photos", nargs="+", required=True)
    post.add_argument("--player", default=None)
    post.add_argument("--type", default=None)
    post.add_argument("--condition", default=None)
    post.add_argument("--best-offer", action="store_true", default=None)
    post.add_argument("--description", default=None)
    post.add_argument("--custom-title", default=None)
    post.add_argument("--dry-run", action="store_true", default=False)

    # setup command
    subparsers.add_parser("setup", help="Configure eBay API credentials")

    # config command
    config_parser = subparsers.add_parser("config", help="View configuration")
    config_parser.add_argument("action", choices=["show"])

    return parser


def build_listing_from_args(args, config=None) -> Listing:
    condition = args.condition
    if condition is None and config:
        condition = config.get("defaults.condition", "USED_GOOD")
    elif condition is None:
        condition = "USED_GOOD"

    best_offer = args.best_offer
    if best_offer is None and config:
        best_offer = config.get("defaults.best_offer", True)
    elif best_offer is None:
        best_offer = True

    return Listing(
        team=args.team,
        year=args.year,
        brand=args.brand,
        size=args.size,
        price=args.price,
        photos=[Path(p) for p in args.photos],
        player=args.player,
        type=args.type,
        condition=condition,
        best_offer=best_offer,
        description=args.description,
        custom_title=args.custom_title,
    )


def cmd_post(args) -> None:
    config = Config()
    listing = build_listing_from_args(args, config)

    creds = config.ebay_credentials
    if not creds.get("client_id"):
        print("Error: eBay not configured. Run 'poster setup' first.")
        sys.exit(1)

    client = EbayClient(creds)

    category_id = config.get("defaults.category_id", "185099")
    location_key = config.get("ebay.location_key", "default")
    policies = {
        "fulfillment_policy_id": config.get("ebay.fulfillment_policy_id"),
        "payment_policy_id": config.get("ebay.payment_policy_id"),
        "return_policy_id": config.get("ebay.return_policy_id"),
    }

    if not all(policies.values()) and not args.dry_run:
        print("Error: Listing policies not configured. Run 'poster setup' first.")
        sys.exit(1)

    result = client.post_listing(
        listing=listing,
        category_id=category_id,
        policies=policies,
        location_key=location_key,
        dry_run=args.dry_run,
    )

    if args.dry_run:
        print("=== DRY RUN ===")
        print(f"Title: {result['title']}")
        print(f"SKU: {result['sku']}")
        print(f"Price: ${listing.price:.2f}")
        print(f"Images: {result['image_count']}")
        print("Listing would be created with the above details.")
    else:
        print(f"Listing created successfully!")
        print(f"  URL: {result['url']}")
        print(f"  Listing ID: {result['listing_id']}")
        print(f"  SKU: {result['sku']}")


def cmd_setup(args) -> None:
    config = Config()
    print("=== eBay API Setup ===")
    print("You need an eBay developer account. See docs/ebay-setup.md for details.\n")

    client_id = input("Client ID: ").strip()
    client_secret = input("Client Secret: ").strip()
    ru_name = input("RuName (redirect URI name): ").strip()

    env = input("Environment (sandbox/production) [sandbox]: ").strip() or "sandbox"

    config.set("ebay.client_id", client_id)
    config.set("ebay.client_secret", client_secret)
    config.set("ebay.ru_name", ru_name)
    config.set("ebay.environment", env)
    config.save()

    # Start OAuth flow
    client = EbayClient(config.ebay_credentials)
    consent_url = client.get_consent_url()
    print(f"\nOpening browser for eBay authorization...")
    webbrowser.open(consent_url)

    auth_code = input("\nPaste the authorization code from the redirect URL: ").strip()
    tokens = client.exchange_auth_code(auth_code)

    config.set("ebay.refresh_token", tokens["refresh_token"])
    config.save()

    print("\nSetup complete! Credentials saved to ~/.poster/config.yaml")


def cmd_config_show(args) -> None:
    config = Config()
    creds = config.ebay_credentials
    print("=== Configuration ===")
    print(f"  Environment: {creds.get('environment', 'not set')}")
    print(f"  Client ID: {'***' + creds['client_id'][-4:] if creds.get('client_id') else 'not set'}")
    print(f"  Refresh Token: {'set' if creds.get('refresh_token') else 'not set'}")
    print(f"  Category ID: {config.get('defaults.category_id', 'not set')}")
    print(f"  Location Key: {config.get('ebay.location_key', 'not set')}")


def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "post":
            cmd_post(args)
        elif args.command == "setup":
            cmd_setup(args)
        elif args.command == "config":
            cmd_config_show(args)
    except PosterError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
