from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import index, AddressViewSet, CouponViewSet, OrderViewSet, CartViewSet, ProductViewSet
from core.payments import create_payment_intent
from core.webhooks import stripe_webhook

app_name = "core"

# Create router and register viewsets
router = DefaultRouter()
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'coupons', CouponViewSet, basename='coupon')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path("", index),
    path("api/", include(router.urls)),
    path("api/create-payment-intent/", create_payment_intent),
    path("api/stripe-webhook/", stripe_webhook),
]