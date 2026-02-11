## E‑Commerce Backend (Django + DRF)

This is a full‑featured e‑commerce backend built with Django and Django REST Framework.  
It includes classic commerce flows (auth, products, cart, orders, payments) plus a crypto
testnet sandbox that simulates BTCPay‑style invoice handling for local development.

---

## Implemented Features

- **User Authentication & Authorization**
  - JWT auth (obtain / refresh / verify / blacklist).
  - User registration, login, password change.
  - Most API endpoints require `IsAuthenticated`.

- **Product, Category & Vendor Management**
  - `Category`, `Vendor`, and `Product` models.
  - Product fields for pricing, discounts, stock, featured flags, etc.
  - Filter/search/paginate product listing APIs.

- **Shopping Cart & Orders**
  - `Cart` and `CartItem` models with add/update/remove endpoints.
  - Checkout flow that converts cart → `Order` + `OrderItem`s.
  - Stock validation and restoration on cancellation.
  - Basic order lifecycle statuses (`pending`, `processing`, `delivered`, `cancelled`).

- **Payments – Stripe**
  - API to create Stripe PaymentIntents (`/api/create-payment-intent/`).
  - Stripe webhook (`/api/stripe-webhook/`) with amount verification and idempotency.
  - Order status sync and email confirmation on successful payment.

- **Payments – BTCPay (real)**
  - BTCPay invoice creation endpoint in `core.payments` (uses `btcpay` client when configured).
  - BTCPay webhook handler in `core.webhooks` that verifies signatures and maps BTCPay statuses
    (`New`, `Processing`, `Settled`, `Expired`, `Invalid`) to internal order statuses.

- **Crypto Testnet / BTCPay‑style Simulator (`ecomprj/cryptopayments`)**
  - In‑memory `TestnetBlockchain` with:
    - Blocks, mempool, balances.
    - Size‑based fee simulation.
    - Payment proof generation for a `tx_id`.
  - `TestnetWallet`:
    - Deterministic address generation from an xpub (via optional `bip32`) or a fallback
      `xpub_counter` scheme.
    - Faucet for funding test addresses.
    - Fee‑aware `send_funds` using the blockchain’s fee calculator.
  - `TestnetPaymentProcessor`:
    - Invoice creation with unique payment address and expiry.
    - Status tracking for `pending`, `partial`, `paid`, `overpaid`, `expired`.
    - Overpayment tracking via `overpaid_amount`.
    - Refund simulation to arbitrary addresses.
    - Mempool watching for an address.
    - Periodic‑style expiry checks.
    - Async webhook queue integration (`WebhookQueue`) with retries.
  - DRF API (`cryptopayments.api`, wired under `api/crypto/`):
    - `POST /api/crypto/testnet/invoices/` – create testnet invoice.
    - `GET /api/crypto/testnet/invoices/<invoice_id>/` – get invoice status.
    - `POST /api/crypto/testnet/invoices/<invoice_id>/simulate-payment/` – simulate on‑chain payment.
    - `POST /api/crypto/testnet/invoices/<invoice_id>/refund/` – simulate a refund.
    - `GET /api/crypto/testnet/mempool/<address>/` – view mempool for an address.
    - `GET /api/crypto/testnet/proof/<tx_id>/` – get a simulated payment proof.
  - Dev helper script:
    - `python -m cryptopayments.dev_test_crypto_apis` runs an end‑to‑end dev flow:
      create invoice → check status → simulate payment → check status → create refund.

- **User Addresses & Profiles**
  - `Address` model (shipping/billing), soft delete, default flags.
  - `Profile` model with basic user metadata.

- **Coupons & Discounts**
  - `Coupon` model, validation and application during checkout.

- **Wishlist**
  - `Wishlist` model and APIs for adding/removing products.

- **Observer Pattern for Domain Events**
  - `Observer` / `Subject` base classes in `core.patterns`.
  - `EmailNotificationObserver`, `InventoryObserver`, `AnalyticsObserver`, `ProductStockObserver`
    wired to order status and stock changes.

- **API Documentation**
  - DRF Spectacular OpenAPI schema.
  - Swagger UI at `/api/schema/docs/`.

---

## Setup & Configuration

All commands below assume you are in the project root (`e-commerce-backend`).

### 1. Clone the repo

```bash
git clone <repository_url>
cd e-commerce-backend
```

### 2. Create and activate a virtualenv

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If you want HD‑wallet style xpub support in the crypto simulator, also install:

```bash
pip install bip32
```

### 4. Environment variables

Create `ecomprj/.env` with at least:

```env
SECRET_KEY=your_django_secret_key_here
DEBUG=True
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# Stripe (optional if you’re not using Stripe in dev)
STRIPE_SECRET_KEY=sk_test_your_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Email (SendGrid or any backend you configure)
SENDGRID_API_KEY=SG.your_sendgrid_api_key
EMAIL_FROM=noreply@example.com

# Optional: BTCPay and crypto testnet settings
BTCPAY_SERVER_URL=https://your-btcpay-url
BTCPAY_API_KEY=your_btcpay_api_key
BTCPAY_STORE_ID=your_btcpay_store_id
BTCPAY_WEBHOOK_SECRET=your_btcpay_webhook_secret

# Optional: testnet crypto simulator
TESTNET_XPUB=xpub_simulated_master_key
TESTNET_WEBHOOK_URL=http://127.0.0.1:8000/api/stripe-webhook/
```

For production, set `DEBUG=False` and use a real database/credentials.

### 5. Run migrations

```bash
cd ecomprj
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a superuser

```bash
python manage.py createsuperuser
```

### 7. Run the development server

```bash
python manage.py runserver
```

- Main API root: `http://127.0.0.1:8000/`
- Admin: `http://127.0.0.1:8000/admin/`
- API docs: `http://127.0.0.1:8000/api/schema/docs/`

---

### Important note for BTCPay

if u want to test the project's crypto payment with btcpay you'll need to clone btc pay repo in the main directory from :
https://github.com/btcpayserver/btcpayserver
and make sure to set it up following the steps from the documentation :
https://docs.btcpayserver.org/Development/LocalDevelopment/
