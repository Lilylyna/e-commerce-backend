from rest_framework import serializers
from .models import Product, Category, Wishlist, Vendor


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    class Meta:
        model = Category
        fields = ['cid', 'title', 'image']
        read_only_fields = ['cid']
    
    def to_representation(self, instance):
        """Ensure image is returned as full URL"""
        representation = super().to_representation(instance)
        if instance.image:
            request = self.context.get('request')
            if request:
                representation['image'] = request.build_absolute_uri(instance.image.url)
        return representation


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model"""
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False
    )
    vendor_title = serializers.CharField(source='vendor.title', read_only=True)
    vendor_id = serializers.PrimaryKeyRelatedField(
        queryset=Vendor.objects.all(),
        source='vendor',
        write_only=True,
        required=False
    )
    is_discounted = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'pid', 'vendor', 'vendor_id', 'vendor_title', 'category', 'category_id',
            'title', 'price', 'old_price', 'image', 'status', 'stock_count', 'date',
            'is_discounted', 'discount_percentage'
        ]
        read_only_fields = ['pid', 'date']
    
    def to_representation(self, instance):
        """Ensure image is returned as full URL"""
        representation = super().to_representation(instance)
        if instance.image:
            request = self.context.get('request')
            if request:
                representation['image'] = request.build_absolute_uri(instance.image.url)
        return representation


class WishlistSerializer(serializers.ModelSerializer):
    """Serializer for Wishlist model"""
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )
    
    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'product_id', 'date']
        read_only_fields = ['id', 'date']

