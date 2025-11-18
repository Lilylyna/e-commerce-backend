# 🛍️ E-Commerce Backend - Complete Project Rundown

## 📁 Project Structure Overview

Your project is a **Django REST API** for an e-commerce platform with:
- ✅ User authentication (sign up, sign in, logout, password reset)
- ✅ Product management (categories, vendors, products)
- ✅ Shopping cart functionality
- ✅ Admin interface
- ✅ JWT token authentication
- ✅ Permission system ready for API

---

## 🗂️ File Structure & What Each Does

### **Root Level Files**

#### `manage.py`
- **What it does:** Django's command-line utility
- **Usage:** Run migrations, start server, create superuser, etc.
- **Example:** `python manage.py runserver`, `python manage.py migrate`

#### `db.sqlite3`
- **What it does:** SQLite database file (stores all your data)
- **Contains:** Users, products, categories, vendors, cart items, etc.

---

## 📦 Apps Breakdown

### **1. `ecomprj/` - Main Project Configuration**

#### `ecomprj/settings.py`
**What it handles:**
- Project-wide settings and configuration
- Installed apps (core, userauths, accounts, rest_framework)
- Database configuration (SQLite)
- REST Framework settings (JWT authentication)
- Email configuration (console backend for development)
- Security settings

**Key configurations:**
```python
INSTALLED_APPS = [
    'core',           # Main e-commerce app
    'userauths',      # User authentication
    'accounts',       # JWT login endpoint
    'rest_framework', # API framework
    'rest_framework_simplejwt',  # JWT tokens
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('JWTAuthentication',),
    'DEFAULT_PERMISSION_CLASSES': ('IsAuthenticated',),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': 30 minutes,
    'REFRESH_TOKEN_LIFETIME': 7 days,
}
```

#### `ecomprj/urls.py`
**What it handles:**
- Main URL routing for entire project
- Connects all app URLs together

**Routes:**
- `/admin/` - Django admin panel
- `/` - Core app routes (home page)
- `/sign-in/`, `/sign-up/`, `/sign-out/` - Userauths app
- `/api/accounts/` - Accounts app (JWT login)
- `/auth/` - Password reset (Django built-in)
- `/api/token/refresh/` - JWT token refresh

---

### **2. `core/` - Main E-Commerce App** ⭐

#### `core/models.py`
**What it handles:**
- **Database models** (the structure of your data)

**Models:**
1. **Category** - Product categories
   - Fields: `cid`, `title`, `image`
   
2. **Vendor** - Store/seller information
   - Fields: `cid`, `title`, `image`, `description`, `address`, `contact`, ratings, etc.
   - Linked to: User (one user can be a vendor)

3. **Product** - Products for sale
   - Fields: `pid`, `title`, `description`, `image`, `price`, `old_price`, `stock_count`, `sku`, `status`, `featured`
   - Linked to: Category, Vendor
   - Properties: `is_discounted`, `discount_percentage`

4. **Cart** - Shopping cart items
   - Fields: `user`, `product`, `quantity`, `price`, `date`
   - Properties: `subtotal`
   - Constraint: One entry per user per product

#### `core/admin.py`
**What it handles:**
- **Django admin interface** customization
- Makes models manageable through `/admin/` panel

**Features:**
- Image previews for Category, Vendor, Product
- Organized fieldsets
- Search and filtering
- Read-only fields (IDs, timestamps)

#### `core/permissions.py`
**What it handles:**
- **Custom permission classes** for API views
- Controls who can access what

**Permission Classes:**
- `IsAdminOrReadOnly` - Admins can edit, others read-only
- `IsVendorOrReadOnly` - Vendors can create/edit, others read-only
- `IsOwnerOrAdmin` - Users see only their data, admins see all
- `IsVendorOwnerOrAdmin` - Vendors see only their vendor data
- `IsAuthenticatedOrReadOnly` - Anyone can read, authenticated can write

#### `core/mixins.py`
**What it handles:**
- **Reusable mixins** for class-based views (non-API)
- Adds permission checks to regular Django views

**Mixins:**
- `StaffRequiredMixin` - Requires staff status
- `VendorRequiredMixin` - Requires vendor profile
- `OwnerOrStaffMixin` - Owner or staff can access
- `VendorOwnerOrStaffMixin` - Vendor owner or staff can access

#### `core/views.py`
**What it handles:**
- Simple home page view
- Currently just returns "welcome to our store!"

#### `core/urls.py`
**What it handles:**
- URL routing for core app
- Currently just home page route `/`

---

### **3. `userauths/` - User Authentication App**

#### `userauths/views.py`
**What it handles:**
- **User authentication views** (sign up, sign in, logout)
- Supports both **form submissions** and **JSON API** requests

**Views:**
1. **`sign_in_view`** - Login functionality
   - Accepts: `username`, `password`
   - Returns: JSON with user info or redirects
   - Creates session for user

2. **`sign_up_view`** - User registration
   - Accepts: `username`, `password1`, `password2`
   - Validates passwords match
   - Creates user account
   - Auto-logs in user after signup
   - Returns: JSON with user info or redirects

3. **`logout_view`** - Logout functionality
   - Ends user session
   - Returns: JSON success or redirects to sign-in

#### `userauths/urls.py`
**What it handles:**
- URL routing for authentication
- Routes:
  - `/sign-in/` - Login
  - `/sign-up/` - Registration
  - `/sign-out/` - Logout

#### `userauths/tests.py`
**What it handles:**
- **Automated tests** for authentication
- Tests sign-up, validation errors, logout

---

### **4. `accounts/` - JWT Token Authentication**

#### `accounts/views.py`
**What it handles:**
- **JWT token generation** for API authentication
- Login endpoint that returns JWT tokens

**View:**
- **`LoginView`** - API login endpoint
  - Accepts: `username`, `password` (via serializer)
  - Returns: `access_token`, `refresh_token`, `username`
  - Used for API authentication (not web sessions)

#### `accounts/urls.py`
**What it handles:**
- URL routing for accounts app
- Route: `/api/accounts/login/` - JWT token login

#### `accounts/serializers.py`
**What it handles:**
- **Data validation** for login requests
- Validates username/password

---

## 🔐 Authentication Systems

### **1. Session-Based Authentication** (Web)
- **Used by:** `userauths` app
- **How it works:** Django sessions (cookies)
- **Endpoints:** `/sign-in/`, `/sign-up/`, `/sign-out/`
- **Use case:** Web browsers, form submissions

### **2. JWT Token Authentication** (API)
- **Used by:** `accounts` app + REST Framework
- **How it works:** JSON Web Tokens
- **Endpoints:** `/api/accounts/login/`, `/api/token/refresh/`
- **Use case:** Mobile apps, API clients, frontend frameworks

### **3. Password Reset** (Django Built-in)
- **Endpoints:** `/auth/password_reset/`, `/auth/reset/<token>/`
- **How it works:** Email-based token system
- **Use case:** Users forgetting passwords

---

## 📊 Database Schema

### **Current Tables:**
1. **auth_user** - Django's built-in user table
2. **core_category** - Product categories
3. **core_vendor** - Vendors/sellers
4. **core_product** - Products
5. **core_cart** - Shopping cart items
6. **authtoken_token** - API tokens (if used)
7. **sessions** - User sessions

### **Relationships:**
```
User ──┐
       ├──> Vendor (one-to-one)
       └──> Cart (one-to-many)

Vendor ──> Product (one-to-many)
Category ──> Product (one-to-many)
Product ──> Cart (one-to-many)
```

---

## 🎯 Current Functionality

### ✅ **What Works Now:**

1. **User Management:**
   - ✅ Sign up (create account)
   - ✅ Sign in (login)
   - ✅ Sign out (logout)
   - ✅ Password reset (via email)
   - ✅ Admin user management

2. **Product Management:**
   - ✅ Create categories
   - ✅ Create vendors
   - ✅ Create products
   - ✅ Admin interface for all models

3. **Shopping Cart:**
   - ✅ Cart model ready
   - ✅ Database structure in place

4. **Authentication:**
   - ✅ Session-based (web)
   - ✅ JWT tokens (API)
   - ✅ Permission system ready

5. **Admin Panel:**
   - ✅ Full admin interface at `/admin/`
   - ✅ Manage users, categories, vendors, products, cart

---

## 🚀 What You Can Build Next

### **Phase 1: API Endpoints** (HIGH PRIORITY)

#### **Product API**
```python
# core/views.py or core/api_views.py
GET    /api/products/              # List all products
GET    /api/products/{id}/        # Product detail
POST   /api/products/             # Create product (vendor/admin)
PUT    /api/products/{id}/         # Update product (owner/admin)
DELETE /api/products/{id}/        # Delete product (owner/admin)
GET    /api/products/featured/    # Featured products
GET    /api/products/category/{id}/ # Products by category
```

**What you need:**
- Create `core/serializers.py` (DRF serializers)
- Create `core/api_views.py` or use ViewSets
- Add routes to `core/urls.py`
- Use `core/permissions.py` for access control

#### **Cart API**
```python
GET    /api/cart/                  # Get user's cart
POST   /api/cart/add/              # Add item to cart
PUT    /api/cart/{id}/             # Update quantity
DELETE /api/cart/{id}/              # Remove item
DELETE /api/cart/clear/             # Clear entire cart
GET    /api/cart/total/             # Get cart total
```

**What you need:**
- Cart serializers
- Cart views with authentication
- Calculate totals

#### **Category & Vendor API**
```python
GET    /api/categories/            # List categories
GET    /api/vendors/               # List vendors
GET    /api/vendors/{id}/products/  # Vendor's products
```

---

### **Phase 2: Order System** (HIGH PRIORITY)

#### **Create Order Models**
```python
# core/models.py
class CartOrder(models.Model):
    user = ForeignKey(User)
    price = DecimalField()
    paid_status = BooleanField()
    order_date = DateTimeField()
    product_status = CharField()  # processing, shipped, delivered

class CartOrderItems(models.Model):
    order = ForeignKey(CartOrder)
    product = ForeignKey(Product)
    quantity = IntegerField()
    price = DecimalField()
    total = DecimalField()
```

#### **Order API**
```python
POST   /api/orders/create/          # Create order from cart
GET    /api/orders/                # List user's orders
GET    /api/orders/{id}/            # Order detail
PUT    /api/orders/{id}/status/     # Update status (admin/vendor)
```

---

### **Phase 3: Advanced Features** (MEDIUM PRIORITY)

#### **1. Wishlist**
```python
# Add to core/models.py
class Wishlist(models.Model):
    user = ForeignKey(User)
    product = ForeignKey(Product)
    date = DateTimeField()

# API
GET    /api/wishlist/
POST   /api/wishlist/add/
DELETE /api/wishlist/{id}/
```

#### **2. Product Reviews**
```python
# Add to core/models.py
class ProductReview(models.Model):
    user = ForeignKey(User)
    product = ForeignKey(Product)
    review = TextField()
    rating = IntegerField()  # 1-5
    date = DateTimeField()

# API
GET    /api/products/{id}/reviews/
POST   /api/products/{id}/reviews/
PUT    /api/reviews/{id}/
DELETE /api/reviews/{id}/
```

#### **3. Search & Filtering**
```python
# Install: pip install django-filter
GET    /api/products/?search=laptop
GET    /api/products/?category=electronics
GET    /api/products/?min_price=100&max_price=500
GET    /api/products/?vendor=1
GET    /api/products/?ordering=price
```

#### **4. User Addresses**
```python
# Add to core/models.py
class Address(models.Model):
    user = ForeignKey(User)
    address = CharField()
    city = CharField()
    state = CharField()
    zip_code = CharField()
    country = CharField()
    status = BooleanField()  # default address

# API
GET    /api/addresses/
POST   /api/addresses/
PUT    /api/addresses/{id}/
DELETE /api/addresses/{id}/
```

---

### **Phase 4: Payment & Checkout** (LATER)

#### **Payment Integration**
- Stripe integration
- PayPal integration
- Order confirmation emails
- Invoice generation

#### **Checkout Process**
```python
POST   /api/checkout/
Body: {
    "address_id": 1,
    "payment_method": "stripe",
    "cart_items": [1, 2, 3]
}
```

---

### **Phase 5: Admin Dashboard** (LATER)

#### **Statistics & Analytics**
- Total sales
- Popular products
- User statistics
- Revenue charts
- Order status overview

---

## 🛠️ Technical Stack

### **Backend:**
- Django 5.2.7
- Django REST Framework
- JWT Authentication (djangorestframework-simplejwt)
- SQLite (development)

### **Database:**
- SQLite (current)
- Can migrate to PostgreSQL/MySQL for production

### **Authentication:**
- Session-based (web)
- JWT tokens (API)
- Password reset (email)

---

## 📝 Next Steps Checklist

### **Immediate (This Week):**
- [ ] Create Product API endpoints
- [ ] Create Cart API endpoints
- [ ] Test API with Postman/curl
- [ ] Add product images via admin

### **Short Term (This Month):**
- [ ] Create Order models
- [ ] Create Order API
- [ ] Add search/filtering
- [ ] Create Wishlist model & API

### **Medium Term (Next Month):**
- [ ] Product reviews
- [ ] User addresses
- [ ] Payment integration
- [ ] Email notifications

### **Long Term:**
- [ ] Admin dashboard
- [ ] Analytics
- [ ] Mobile app support
- [ ] Production deployment

---

## 🎓 Key Concepts to Understand

### **1. Models → Serializers → Views → URLs**
```
Model (database) 
  ↓
Serializer (data validation/formatting)
  ↓
View (business logic)
  ↓
URL (routing)
```

### **2. Authentication Flow**
```
User → Login → Get Token → Use Token in API Requests
```

### **3. Permission System**
```
Request → Check Permission → Allow/Deny → Return Response
```

---

## 💡 Pro Tips

1. **Use Admin Panel** - Great for testing and managing data
2. **Test APIs** - Use Postman or curl to test endpoints
3. **Check Permissions** - Make sure permissions work correctly
4. **Use Serializers** - Always validate data with serializers
5. **Add Logging** - Log important actions for debugging

---

## 📚 Documentation Files You Have

- `IMPLEMENTATION_RECOMMENDATIONS.md` - Detailed implementation guide
- `API_TESTING.md` - How to test APIs
- `TEST_AUTH_ENDPOINTS.md` - Authentication testing
- `TOKENS_EXPLAINED.md` - JWT tokens explained
- `PROJECT_RUNDOWN.md` - This file!

---

## 🎉 Summary

**You have a solid foundation!**

✅ Authentication system (sessions + JWT)  
✅ Database models (Category, Vendor, Product, Cart)  
✅ Admin interface  
✅ Permission system  
✅ Testing setup  

**Ready to build:**
- Product API
- Cart API
- Order system
- Advanced features

**Your codebase is well-organized and ready for expansion!** 🚀

