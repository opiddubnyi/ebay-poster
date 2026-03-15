# Poster

CLI tool to automate posting vintage soccer jersey listings to eBay.

## Features

- Post listings to eBay via the Inventory API (create item, offer, publish)
- Auto-generate eBay-optimized titles from jersey details (team, year, brand, size)
- Upload photos to eBay image hosting
- Dry-run mode to preview listings without posting
- Config-driven defaults to minimize repetitive input
- OAuth2 authentication with automatic token refresh

## Installation

```bash
git clone https://github.com/opiddubnyi/ebay-poster.git
cd ebay-poster
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

## Quick Start

### 1. Set up eBay credentials

```bash
poster setup
```

This walks you through connecting your eBay developer account. See [docs/ebay-setup.md](docs/ebay-setup.md) for detailed instructions.

### 2. Post a listing

```bash
poster post --team "Brazil" --year "1998" --type Home --brand Nike \
  --size XL --price 200 --best-offer --photos ./front.jpg ./back.jpg
```

### 3. Preview before posting

```bash
poster post --team "Brazil" --year "1998" --brand Nike --size XL \
  --price 200 --photos ./front.jpg --dry-run
```

## CLI Reference

### `poster post`

| Flag | Required | Description |
|---|---|---|
| `--team` | Yes | Team name (e.g., "Brazil") |
| `--year` | Yes | Year(s) (e.g., "1998" or "1998 1999 2000") |
| `--brand` | Yes | Brand (e.g., "Nike") |
| `--size` | Yes | Size (e.g., "XL") |
| `--price` | Yes | Price in USD |
| `--photos` | Yes | One or more photo file paths |
| `--player` | No | Player name (e.g., "Ronaldo") |
| `--type` | No | Home / Away / Third |
| `--condition` | No | eBay condition (default: USED_GOOD) |
| `--best-offer` | No | Accept Best Offer |
| `--description` | No | Listing description |
| `--custom-title` | No | Override auto-generated title |
| `--dry-run` | No | Preview without posting |

### `poster setup`

Interactive setup for eBay API credentials and OAuth2 authorization.

### `poster config show`

Display current configuration (credentials are masked).

## Configuration

Stored in `~/.poster/config.yaml`:

```yaml
ebay:
  client_id: "your_client_id"
  client_secret: "your_client_secret"
  refresh_token: "your_refresh_token"
  ru_name: "your_runame"
  environment: "sandbox"  # or "production"
  fulfillment_policy_id: "your_id"
  payment_policy_id: "your_id"
  return_policy_id: "your_id"
  location_key: "my-warehouse"

defaults:
  condition: "USED_GOOD"
  category_id: "185099"
  best_offer: true
```

## Running Tests

```bash
pytest -v
```

## License

MIT
