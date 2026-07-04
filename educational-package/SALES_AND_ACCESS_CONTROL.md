# Sales and Access Control Implementation

## Checkout and payment
- Recommended provider: Stripe Checkout + customer portal.
- Product mapping:
  - `codealong_core_monthly`
  - `codealong_pro_monthly`

## Account creation
1. Buyer completes checkout.
2. Buyer account is created or linked by email.
3. Entitlement is stored in backend user profile.

## Entitlement model
Use these fields in user records:
- `subscription_active` (boolean)
- `subscription_tier` (`preview` | `core` | `pro`)
- `subscription_expires_at` (datetime)
- `license_status` (`active` | `trial` | `expired` | `canceled`)

## Gating strategy
- Keep free preview docs in public paths.
- Gate premium learning assets behind authenticated routes/pages.
- Enforce server-side checks before returning premium files.

## Existing repository alignment
This repository already enforces signed-in and active-subscription access for protected Streamlit areas. Reuse that entitlement pattern for premium package routes and APIs.

## Operational flow
1. Checkout webhook updates entitlement.
2. User logs in.
3. Server verifies entitlement on each premium request.
4. If inactive/expired, serve upgrade/paywall response.
