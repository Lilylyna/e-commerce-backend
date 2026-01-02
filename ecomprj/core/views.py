from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import logout
from rest_framework import viewsets, status, filters, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import CursorPagination
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Category, Wishlist
from .serializers import ProductSerializer, CategorySerializer, WishlistSerializer
from .filters import ProductFilter


# Simple index view for the root URL
def index(request):
    return HttpResponse("welcome to our store!")


class ProductCursorPagination(CursorPagination):
    """Cursor pagination for product listing"""
    page_size = 20
    ordering = '-date'


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Product listing with filtering, search, and pagination.
    Read-only to prevent modifications from this endpoint.
    """
    queryset = Product.objects.filter(status='published')
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]  # Public access for product listing
    pagination_class = ProductCursorPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ProductFilter
    search_fields = ['title']  # Search only on title (description field doesn't exist in Product model)
    
    def get_queryset(self):
        """Return published products only"""
        return Product.objects.filter(status='published').select_related('category', 'vendor')


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Category listing.
    Read-only to prevent modifications from this endpoint.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]  # Public access for category listing


class WishlistViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Wishlist management.
    Requires authentication - users can only manage their own wishlist.
    """
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only wishlist items for the current user"""
        return Wishlist.objects.filter(user=self.request.user).select_related('product', 'product__category', 'product__vendor')
    
    def perform_create(self, serializer):
        """Create wishlist item for the current user"""
        product = serializer.validated_data['product']
        user = self.request.user
        
        # Check if wishlist item already exists
        if Wishlist.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError("Product is already in your wishlist.")
        
        serializer.save(user=user)
    
    @action(detail=False, methods=['post'], url_path='add')
    def add(self, request):
        """Add a product to wishlist"""
        product_id = request.data.get('product_id')
        if not product_id:
            return Response(
                {'error': 'product_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if already in wishlist
        if Wishlist.objects.filter(user=request.user, product=product).exists():
            return Response(
                {'error': 'Product is already in your wishlist'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        wishlist_item = Wishlist.objects.create(user=request.user, product=product)
        serializer = self.get_serializer(wishlist_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['delete'], url_path='remove')
    def remove(self, request):
        """Remove a product from wishlist by product_id"""
        product_id = request.data.get('product_id')
        if not product_id:
            return Response(
                {'error': 'product_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = Product.objects.get(id=product_id)
            wishlist_item = Wishlist.objects.get(user=request.user, product=product)
            wishlist_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Wishlist.DoesNotExist:
            return Response(
                {'error': 'Product is not in your wishlist'},
                status=status.HTTP_404_NOT_FOUND
            )
