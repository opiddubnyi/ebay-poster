# eBay Developer Account Setup

## 1. Create a Developer Account

1. Go to https://developer.ebay.com/
2. Click "Join" and sign up (free)
3. Once logged in, go to "Application Keys" in the dashboard

## 2. Create an Application

1. Click "Create a keyset" for the Sandbox environment
2. Note your **Client ID** (App ID) and **Client Secret** (Cert ID)
3. Repeat for Production when ready to go live

## 3. Configure a RuName (Redirect URI)

1. In Application Keys, click "User Tokens" next to your keyset
2. Under "Get a Token from eBay via Your Application", click "Add eBay Redirect URL"
3. Set:
   - **Auth Accepted URL**: `https://localhost:8080/callback` (or any URL you control)
   - **Auth Declined URL**: `https://localhost:8080/declined`
4. Save — note the generated **RuName** string (e.g., `YourName-YourName-TestAp-abcdefg`)

## 4. Run Poster Setup

```bash
poster setup
```

You'll be prompted for:
- Client ID
- Client Secret
- RuName
- Environment (sandbox/production)

The tool will then open your browser for eBay authorization. After approving, paste the auth code back into the terminal.

## 5. Configure Listing Policies (One-Time)

Before posting listings, you need fulfillment, payment, and return policies set up on your eBay account. These can be created via:
- eBay Seller Hub: https://www.ebay.com/sh/settings
- Or via the poster tool (coming soon)

Once created, add the policy IDs to `~/.poster/config.yaml`:

```yaml
ebay:
  fulfillment_policy_id: "your_fulfillment_id"
  payment_policy_id: "your_payment_id"
  return_policy_id: "your_return_id"
  location_key: "my-warehouse"
```

## 6. Set Defaults (Optional)

Add defaults to skip repetitive CLI flags:

```yaml
defaults:
  condition: "USED_GOOD"
  category_id: "185099"
  best_offer: true
```

## 7. Test with Dry Run

```bash
poster post --team "Brazil" --year "1998" --brand Nike --size XL \
  --price 200 --photos ./jersey_front.jpg --dry-run
```
