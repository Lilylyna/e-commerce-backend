import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    """FilterSet for Product model"""
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    category = django_filters.NumberFilter(field_name='category__id')
    vendor = django_filters.NumberFilter(field_name='vendor__id')
    
    class Meta:
        model = Product
        fields = ['min_price', 'max_price', 'category', 'vendor']