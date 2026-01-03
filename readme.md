# E-Commerce Backend API

A comprehensive Django REST Framework backend for e-commerce operations, featuring JWT authentication, complete checkout flow, inventory management, and order processing.

## 🚀 Features Implemented

### ✅ **Authentication & Security**
- JWT Token Authentication (Access + Refresh tokens)
- User registration and login/logout
- Secure token verification and refresh endpoints
- Password hashing and user session management

### ✅ **Sales & Operations (Checkout Flow)**
- **Order Models**: Complete Order and OrderItem models with status tracking
- **Stock Validation**: Real-time inventory checking during checkout
- **Transaction Safety**: Database locking prevents overselling
- **Address Management**: Shipping and billing address support
- **Coupon System**: Percentage and fixed-amount discounts with usage limits
- **Order Processing**: Complete cart-to-order conversion
- **Email Notifications**: Automated order confirmations

### ✅ **Product & Inventory Management**
- Product catalog with categories and vendors
- Image upload support for products and categories
- Stock level tracking and availability status
- Product search and filtering capabilities

### ✅ **Shopping Cart System**
- Persistent cart storage per user
- Add/update/remove cart items
- Cart summary and total calculations
- Automatic price updates from product catalog

### ✅ **Admin & Vendor Management**
- Django admin interface for content management
- Vendor accounts with store management
- Product management per vendor
- Order status updates and tracking

## 🛠 Tech Stack

### Backend Framework
- **Django 5.2.7** - Web framework
- **Django REST Framework 3.16.1** - API framework
- **Django Simple JWT 5.5.1** - JWT authentication

### Database & Storage
- **SQLite** - Database (development)
- **Pillow 12.0.0** - Image processing
- **Django ShortUUIDField** - Unique ID generation

### Additional Libraries
- **Requests** - HTTP client for testing
- **Python-JWT** - JWT token handling
- **ShortUUID** - Compact unique identifiers

## 📋 API Endpoints

### Authentication
```
POST /api/token/              # Obtain access/refresh tokens
POST /api/token/verify/       # Verify JWT token validity
POST /api/token/refresh/      # Refresh access token
POST /api/accounts/login/     # Alternative login endpoint
```

### Address Management
```
GET  /api/addresses/          # List user addresses
POST /api/addresses/          # Create new address
GET  /api/addresses/{id}/     # Get specific address
PUT  /api/addresses/{id}/     # Update address
DELETE /api/addresses/{id}/   # Delete address (soft delete)
POST /api/addresses/{id}/set_default/  # Set as default
```

### Product Management
```
GET  /api/products/           # List published products
GET  /api/products/{id}/      # Get product details
```

### Shopping Cart
```
GET  /api/cart/               # List cart items
POST /api/cart/               # Add product to cart
PUT  /api/cart/{id}/          # Update cart item
DELETE /api/cart/{id}/        # Remove from cart
GET  /api/cart/summary/       # Get cart totals
```

### Coupon System
```
GET  /api/coupons/            # List active coupons
POST /api/coupons/validate/   # Validate coupon code
```

### Order Management (Sales & Operations Core)
```
GET  /api/orders/             # List user orders
GET  /api/orders/{id}/        # Get order details
POST /api/orders/checkout/    # Complete checkout process
POST /api/orders/{id}/cancel/ # Cancel pending order
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager
- Virtual environment (recommended)

### Installation

1. **Clone and Navigate**
   ```bash
   git clone <your-repository-url>
   cd e-commerce-backend
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install Dependencies**
   ```bash
   pip install django djangorestframework djangorestframework-simplejwt pillow django-shortuuidfield requests
   ```

4. **Setup Database**
   ```bash
   cd ecomprj
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create Test Data (Optional)**
   ```bash
   python manage.py create_test_data
   ```

6. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

   Server will start at: `http://127.0.0.1:8000/`

## 🧪 Testing

### Automated Test Suite
```bash
# From e-commerce-backend directory
python api_test_suite.py
```

This comprehensive test suite validates:
- JWT authentication flow
- Address management
- Cart operations
- Coupon validation
- Complete checkout process
- Order management
- Stock validation

### Manual Testing
```bash
# Run built-in API tests
cd ecomprj
python manage.py test_apis
```

## 📊 Database Models

### Core Models
- **User**: Django's built-in user model
- **Category**: Product categories
- **Vendor**: Store/vendor accounts
- **Product**: Product catalog with inventory
- **Cart**: Shopping cart items
- **Address**: User addresses (shipping/billing)
- **Coupon**: Discount codes with rules
- **Order**: Customer orders
- **OrderItem**: Individual order line items

### Key Relationships
- User → Addresses (1:many)
- User → Cart Items (1:many)
- User → Orders (1:many)
- Product → OrderItems (1:many)
- Order → OrderItems (1:many)
- Order → Addresses (shipping/billing)

## 🔒 Security Features

- JWT token-based authentication
- Password hashing with Django's auth system
- CSRF protection on forms
- SQL injection prevention via Django ORM
- Input validation and sanitization
- Soft deletes for data integrity

## 📧 Email Integration

- Automated order confirmation emails
- Configurable email templates
- SMTP server integration ready

## 🔄 API Response Format

All API responses follow REST standards:

**Success Response:**
```json
{
  "success": true,
  "message": "Operation completed",
  "data": { ... }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error description",
  "details": { ... }
}
```

## 🚀 Production Deployment

For production deployment:
1. Switch to PostgreSQL database
2. Configure environment variables
3. Set up proper SMTP server
4. Enable HTTPS/SSL
5. Configure static/media file serving
6. Set DEBUG=False
7. Use proper secret keys

## 📝 Development Notes

- Uses ShortUUID for readable IDs (e.g., `ordhc4133a14g`)
- Implements database transactions for data consistency
- Soft deletes preserve data integrity
- Comprehensive test coverage for all features

## 🤝 Contributing

1. Create feature branch from `main`
2. Implement changes with tests
3. Run full test suite
4. Submit pull request

---

**Built with Django REST Framework • JWT Authentication • PostgreSQL Ready**
