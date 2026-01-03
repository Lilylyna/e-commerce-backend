from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import index, AddressViewSet, CouponViewSet, OrderViewSet, CartViewSet, ProductViewSet

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
]