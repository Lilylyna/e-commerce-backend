# E-Commerce Backend Project

This is the backend for an e-commerce application, built with Django and Django REST Framework.

## Implemented Features

-   **User Authentication & Authorization**
    -   User registration and login.
    -   JWT (JSON Web Token) based authentication with refresh and verify endpoints.
    -   Password change functionality for authenticated users.
    -   Default permissions set to `IsAuthenticated` for most API endpoints.

-   **Product & Category Management**
    -   `Category` model for organizing products.
    -   `Vendor` model for sellers, linked to Django's `User` model.
    -   `Product` model with details like price, stock, status, and discount calculations.
    -   Publicly accessible API endpoints for listing and filtering products and categories.
    -   Product listings include filtering, searching, and cursor pagination.

-   **Shopping Cart & Order Processing**
    -   `Cart` model to store items for purchase.
    -   APIs for adding, updating, and removing items from the cart.
    -   Cart summary endpoint to get total price and item count.
    -   `Order` model to represent customer orders.
    -   Checkout process to convert cart items into an order, with stock validation and coupon application.
    -   Order cancellation functionality with stock restoration.
    -   `OrderItem` model to detail individual products within an order.

-   **Payment Integration (Stripe)**
    -   API endpoint to create Stripe Payment Intents for secure payment collection.
    -   Stripe webhook endpoint (`/api/stripe-webhook/`) to handle payment success/failure events.
    -   Order status updates (`pending`, `paid`, `failed`) based on Stripe webhook events.
    -   Email confirmation for successful orders.

-   **User Address & Profile Management**
    -   `Address` model for storing shipping and billing addresses.
    -   Soft deletion for addresses.
    -   Functionality to set default addresses.
    -   `Profile` model for extended user information (bio, phone, image).
    -   Authenticated API endpoint for viewing user profile.

-   **Coupons & Discounts**
    -   `Coupon` model with various discount types (percentage, fixed amount).
    -   Validation and application of coupons during checkout.

-   **Wishlist Functionality**
    -   `Wishlist` model to allow users to save products for later.
    -   APIs for adding and removing products from a user's wishlist.

-   **API Documentation (DRF Spectacular)**
    -   Integrated OpenAPI 3.0 schema generation.
    -   Interactive Swagger UI available at `/api/schema/docs/`.

-   **Observer Pattern**
    -   Implemented a simple observer pattern for `Product` stock changes and `Order` status changes.
    -   Observers (e.g., `EmailNotificationObserver`, `InventoryObserver`, `AnalyticsObserver`, `ProductStockObserver`) are notified on relevant model `save` operations.

## Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd e-commerce-backend
    ```

2.  **Create and activate a virtual environment (recommended):**

    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a `.env` file in the `ecomprj` directory (e.g., `ecomprj/.env`) with the following variables:

    ```env
    SECRET_KEY=your_django_secret_key_here
    DEBUG=True
    DB_ENGINE=django.db.backends.sqlite3
    DB_NAME=db.sqlite3

    # Stripe API Keys (replace with your actual keys)
    STRIPE_SECRET_KEY=sk_test_your_secret_key
    STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key
    STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

    # SendGrid Email Settings (replace with your actual API key and email)
    SENDGRID_API_KEY=SG.your_sendgrid_api_key
    EMAIL_FROM=noreply@example.com
    ```
    *Note: For production, set `DEBUG=False` and configure a more robust database.* 

5.  **Run database migrations:**

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6.  **Create a superuser (for Django Admin):**

    ```bash
    python manage.py createsuperuser
    ```

7.  **Run the development server:**

    ```bash
    python manage.py runserver
    ```

    The API will be available at `http://127.0.0.1:8000/`.
    Django Admin will be at `http://127.0.0.1:8000/admin/`.
    Swagger UI for API docs will be at `http://127.0.0.1:8000/api/schema/docs/`.

