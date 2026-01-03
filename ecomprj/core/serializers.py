from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Address, Coupon, Order, OrderItem, Cart, Product
)

User = get_user_model()


class AddressSerializer(serializers.ModelSerializer):
    """Serializer for Address model"""
    class Meta:
        model = Address
        fields = [
            'id', 'address_type', 'full_name', 'phone',
            'address_line_1', 'address_line_2', 'city',
            'state', 'country', 'zip_code', 'is_default', 'active', 'date'
        ]
        read_only_fields = ['id', 'date', 'active']  # active is managed by soft_delete
    
    def validate(self, data):
        """Ensure at least one default address per type"""
        user = self.context['request'].user
        address_type = data.get('address_type')
        is_default = data.get('is_default', False)
        
        if is_default:
            # If setting as default, unset other defaults of the same type (only active addresses)
            Address.objects.filter(
                user=user,
                address_type=address_type,
                is_default=True,
                active=True
            ).exclude(id=self.instance.id if self.instance else None).update(is_default=False)
        
        return data


class CouponSerializer(serializers.ModelSerializer):
    """Serializer for Coupon model"""
    is_valid = serializers.SerializerMethodField()
    
    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'discount_type', 'discount_value',
            'minimum_purchase', 'max_usage', 'used_count',
            'valid_from', 'valid_to', 'active', 'is_valid', 'date'
        ]
        read_only_fields = ['id', 'used_count', 'date']
    
    def get_is_valid(self, obj):
        """Check if coupon is currently valid"""
        return obj.is_valid()


class CouponValidateSerializer(serializers.Serializer):
    """Serializer for validating coupon codes"""
    code = serializers.CharField(max_length=50)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0)
    
    def validate_code(self, value):
        """Validate coupon code exists and is valid"""
        try:
            coupon = Coupon.objects.get(code=value.upper())
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Invalid coupon code.")
        
        if not coupon.is_valid():
            raise serializers.ValidationError("This coupon is no longer valid.")
        
        return value
    
    def validate(self, data):
        """Validate coupon can be applied to this order"""
        code = data.get('code')
        subtotal = data.get('subtotal', 0)
        
        try:
            coupon = Coupon.objects.get(code=code.upper())
            
            if subtotal < coupon.minimum_purchase:
                raise serializers.ValidationError(
                    f"Minimum purchase of ${coupon.minimum_purchase} required for this coupon."
                )
            
            data['coupon'] = coupon
        except Coupon.DoesNotExist:
            pass
        
        return data


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem model"""
    product_title = serializers.CharField(source='product.title', read_only=True)
    product_image = serializers.ImageField(source='product.image', read_only=True)
    item_subtotal = serializers.DecimalField(source='subtotal', max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_title', 'product_image',
            'quantity', 'price', 'item_subtotal', 'date'
        ]
        read_only_fields = ['id', 'date']


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model"""
    order_items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    shipping_address_data = AddressSerializer(source='shipping_address', read_only=True)
    billing_address_data = AddressSerializer(source='billing_address', read_only=True)
    coupon_code = serializers.CharField(source='coupon.code', read_only=True, allow_null=True)
    
    class Meta:
        model = Order
        fields = [
            'oid', 'user', 'user_email', 'user_username', 'order_status',
            'subtotal', 'shipping_fee', 'tax', 'discount_amount', 'total',
            'shipping_address', 'billing_address', 'shipping_address_data',
            'billing_address_data', 'coupon', 'coupon_code',
            'order_items', 'date', 'updated'
        ]
        read_only_fields = [
            'oid', 'user', 'subtotal', 'shipping_fee', 'tax',
            'discount_amount', 'total', 'date', 'updated'
        ]


class CheckoutSerializer(serializers.Serializer):
    """Serializer for checkout request"""
    shipping_address_id = serializers.IntegerField(required=True)
    billing_address_id = serializers.IntegerField(required=False, allow_null=True)
    coupon_code = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True)
    
    def validate_shipping_address_id(self, value):
        """Validate shipping address belongs to user"""
        user = self.context['request'].user
        try:
            address = Address.objects.get(id=value, user=user)
            if address.address_type != 'shipping':
                raise serializers.ValidationError("Selected address is not a shipping address.")
        except Address.DoesNotExist:
            raise serializers.ValidationError("Shipping address not found.")
        return value
    
    def validate_billing_address_id(self, value):
        """Validate billing address belongs to user"""
        if value is None:
            return value
        
        user = self.context['request'].user
        try:
            address = Address.objects.get(id=value, user=user)
            if address.address_type != 'billing':
                raise serializers.ValidationError("Selected address is not a billing address.")
        except Address.DoesNotExist:
            raise serializers.ValidationError("Billing address not found.")
        return value
    
    def validate_coupon_code(self, value):
        """Validate coupon code if provided"""
        if not value or value.strip() == '':
            return None
        
        try:
            coupon = Coupon.objects.get(code=value.upper())
            if not coupon.is_valid():
                raise serializers.ValidationError("This coupon is no longer valid.")
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Invalid coupon code.")
        
        return value.upper()
        
class CartSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.title', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = ['id', 'product', 'product_title', 'product_price', 'quantity', 'price', 'subtotal']

class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model"""
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'description', 'price', 'old_price', 'image',
            'status', 'stock_count', 'in_stock', 'date', 'is_discounted', 'discount_percentage'
        ]
        read_only_fields = ['id', 'date', 'is_discounted', 'discount_percentage']
