from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import index, ProductViewSet, CategoryViewSet, WishlistViewSet

app_name = "core"

# Create router and register viewsets
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'wishlist', WishlistViewSet, basename='wishlist')

urlpatterns = [
    path("", index),
    path("api/", include(router.urls)),
]