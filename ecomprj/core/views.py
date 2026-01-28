from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from .models import Address, Coupon, Order, OrderItem, Cart, Product
from .serializers import (
    AddressSerializer, CouponSerializer, CouponValidateSerializer,
    OrderSerializer, OrderItemSerializer, CheckoutSerializer, CartSerializer, ProductSerializer
)
from .utils import send_order_confirmation


class AddressViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user addresses"""
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return active addresses for the current user"""
        return Address.objects.filter(user=self.request.user, active=True)
    
    def perform_create(self, serializer):
        """Create address for current user"""
        serializer.save(user=self.request.user, active=True)
    
    def perform_destroy(self, instance):
        """Soft delete address instead of hard delete"""
        instance.soft_delete()
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set an address as default"""
        address = self.get_object()
        
        # Ensure address is active
        if not address.active:
            return Response(
                {'error': 'Cannot set a deleted address as default.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Unset other defaults of the same type (only active addresses)
        Address.objects.filter(
            user=request.user,
            address_type=address.address_type,
            is_default=True,
            active=True
        ).exclude(id=address.id).update(is_default=False)
        
        # Set this address as default
        address.is_default = True
        address.save()
        
        return Response({'message': 'Address set as default successfully.'})


class CouponViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing coupons (read-only for customers)"""
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated]
    queryset = Coupon.objects.filter(active=True)
    
    @action(detail=False, methods=['post'])
    def validate(self, request):
        """Validate a coupon code"""
        serializer = CouponValidateSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data['code']
            subtotal = serializer.validated_data.get('subtotal', 0)
            
            try:
                coupon = Coupon.objects.get(code=code.upper())
                
                if not coupon.is_valid():
                    return Response(
                        {'error': 'This coupon is no longer valid.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                if subtotal < coupon.minimum_purchase:
                    return Response(
                        {'error': f'Minimum purchase of ${coupon.minimum_purchase} required.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Calculate discount
                discount_amount = coupon.calculate_discount(subtotal)
                
                return Response({
                    'coupon': CouponSerializer(coupon).data,
                    'discount_amount': float(discount_amount),
                    'message': 'Coupon is valid.'
                })
            except Coupon.DoesNotExist:
                return Response(
                    {'error': 'Invalid coupon code.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing orders"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return orders for the current user"""
        return Order.objects.filter(user=self.request.user).prefetch_related('order_items__product')
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel an order if it's still pending.
        Restores product stock and changes order status to cancelled.
        """
        order = self.get_object()
        
        # Check if order belongs to user
        if order.user != request.user:
            return Response(
                {'error': 'You do not have permission to cancel this order.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if order can be cancelled (only pending orders)
        if order.order_status != 'pending':
            return Response(
                {'error': f'Order cannot be cancelled. Current status: {order.order_status}.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cancel order and restore stock within transaction
        try:
            with transaction.atomic():
                # Restore product stock
                for order_item in order.order_items.all():
                    if order_item.product:
                        # Lock product to prevent race conditions
                        product = Product.objects.select_for_update().get(id=order_item.product.id)
                        product.stock_count += order_item.quantity
                        product.save()
                
                # OBSERVER PATTERN: Update order status to cancelled
                # When order.save() is called, the observer pattern will be triggered
                # to notify observers (EmailNotificationObserver, InventoryObserver, AnalyticsObserver)
                # about the status change. Observers will handle email notifications,
                # inventory restoration, and analytics tracking automatically.
                order.order_status = 'cancelled'
                order.save()
                
                # Restore coupon usage if coupon was used
                if order.coupon:
                    order.coupon.used_count = max(0, order.coupon.used_count - 1)
                    order.coupon.save()
                
                return Response({
                    'message': 'Order cancelled successfully. Stock has been restored.',
                    'order': OrderSerializer(order).data
                }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': f'An error occurred while cancelling the order: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def checkout(self, request):
        """
        Checkout endpoint - converts cart to order
        
        Expected payload:
        {
            "shipping_address_id": 1,
            "billing_address_id": 1,  # optional, defaults to shipping
            "coupon_code": "SAVE10"    # optional
        }
        """
        serializer = CheckoutSerializer(data=request.data, context={'request': request})
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        
        # Get cart items
        cart_items = Cart.objects.filter(user=user).select_related('product')
        
        if not cart_items.exists():
            return Response(
                {'error': 'Your cart is empty.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate subtotal (initial calculation, will re-validate with locks)
        subtotal = 0
        items_to_order = []
        
        for cart_item in cart_items:
            # Calculate item subtotal
            item_subtotal = cart_item.price * cart_item.quantity
            subtotal += item_subtotal
            
            items_to_order.append({
                'product_id': cart_item.product.id,
                'product': cart_item.product,
                'quantity': cart_item.quantity,
                'price': cart_item.price
            })
        
        # Get addresses
        shipping_address_id = serializer.validated_data['shipping_address_id']
        billing_address_id = serializer.validated_data.get('billing_address_id')
        
        shipping_address = get_object_or_404(
            Address,
            id=shipping_address_id,
            user=user,
            address_type='shipping'
        )
        
        if billing_address_id:
            billing_address = get_object_or_404(
                Address,
                id=billing_address_id,
                user=user,
                address_type='billing'
            )
        else:
            # Use shipping address as billing if not provided
            billing_address = shipping_address
        
        # Handle coupon code (defer validation and usage increment to transaction)
        coupon = None
        discount_amount = Decimal('0.00')
        coupon_code = serializer.validated_data.get('coupon_code')
        
        # Calculate shipping fee (you can make this dynamic based on address, weight, etc.)
        shipping_fee = Decimal('10.00')  # Fixed shipping fee - can be made dynamic

        # Calculate tax (optional - 10% example)
        tax = (subtotal * Decimal('0.10')).quantize(Decimal('0.01'))

        # Calculate total (discount_amount will be applied after coupon validation)
        total = subtotal + shipping_fee + tax - discount_amount
        
        # Create order within transaction with database locking
        try:
            with transaction.atomic():
                # Validate stock with database locks (prevents race conditions)
                locked_products = {}
                for item_data in items_to_order:
                    # Lock the product row to prevent concurrent modifications
                    product = Product.objects.select_for_update().get(id=item_data['product_id'])
                    
                    # Check stock availability with locked product
                    if product.stock_count < item_data['quantity']:
                        return Response(
                            {
                                'error': f'Insufficient stock for {product.title}. '
                                        f'Available: {product.stock_count}, Requested: {item_data['quantity']}'
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    locked_products[item_data['product_id']] = product
                
                # If coupon code provided, lock coupon and validate usage inside transaction
                if coupon_code:
                    try:
                        coupon = Coupon.objects.select_for_update().get(code=coupon_code.upper())
                    except Coupon.DoesNotExist:
                        return Response({'error': 'Invalid coupon code.'}, status=status.HTTP_400_BAD_REQUEST)

                    if not coupon.is_valid():
                        return Response({'error': 'This coupon is no longer valid.'}, status=status.HTTP_400_BAD_REQUEST)

                    if subtotal < coupon.minimum_purchase:
                        return Response(
                            {'error': f'Minimum purchase of ${coupon.minimum_purchase} required for this coupon.'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    # Calculate discount and increment usage
                    discount_amount = coupon.calculate_discount(subtotal)
                    coupon.used_count += 1
                    coupon.save()

                    # Recalculate total with discount applied
                    total = subtotal + shipping_fee + tax - discount_amount

                # OBSERVER PATTERN: Create order (status will be 'pending' initially)
                # When the order is saved, the observer pattern will be triggered
                # to notify observers about the new order creation
                order = Order.objects.create(
                    user=user,
                    order_status='pending',
                    subtotal=subtotal,
                    shipping_fee=shipping_fee,
                    tax=tax,
                    discount_amount=discount_amount,
                    total=total,
                    shipping_address=shipping_address,
                    billing_address=billing_address,
                    coupon=coupon
                )
                
                # Create order items and reduce stock (using locked products)
                for item_data in items_to_order:
                    product = locked_products[item_data['product_id']]
                    
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=item_data['quantity'],
                        price=item_data['price']
                    )
                    
                    # OBSERVER PATTERN: Reduce product stock
                    # When product.save() is called, the observer pattern will be triggered
                    # to notify observers (ProductStockObserver) about stock changes.
                    # Observers will handle low stock alerts, out of stock notifications, etc.
                    product.stock_count -= item_data['quantity']
                    product.save()
                
                # Clear cart
                cart_items.delete()
                
                # Send order confirmation email (async - don't block response)
                try:
                    send_order_confirmation(order.oid)
                except Exception as email_error:
                    # Log error but don't fail the order
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Failed to send order confirmation email: {str(email_error)}")
                
                # Serialize and return order
                order_serializer = OrderSerializer(order)
                
                return Response({
                    'message': 'Order created successfully.',
                    'order': order_serializer.data
                }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response(
                {'error': f'An error occurred while creating the order: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Keep the original index view for backward compatibility
def index(request):
    return HttpResponse("welcome to our store!")

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user).select_related('product')

    def create(self, request, *args, **kwargs):
        """Create or update cart item if product already exists"""
        product_id = request.data.get('product')
        quantity = int(request.data.get('quantity', 1))
        user = request.user
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if product already exists in cart
        cart_item, created = Cart.objects.get_or_create(
            user=user,
            product=product,
            defaults={'quantity': quantity, 'price': product.price}
        )
        
        if not created:
            # Update quantity and price if item already exists
            cart_item.quantity += quantity
            cart_item.price = product.price  # Update to current price
            cart_item.save()
            serializer = self.get_serializer(cart_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Return the newly created item
            serializer = self.get_serializer(cart_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Returns the total price and item count for the cart"""
        cart_items = self.get_queryset()
        total = sum(item.subtotal for item in cart_items)
        count = cart_items.count()
        total_items = sum(item.quantity for item in cart_items)
        return Response({
            'total_price': float(total),
            'item_count': count,
            'total_quantity': total_items
        })

class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Handle the checkout process:
        - Validate the cart data sent in the request.
        - Check stock availability for each product.
        - Create an order and associated order items.
        - Deduct stock quantities and calculate the total price.
        - Return the created order details or appropriate error messages.
        """
        cart = request.data.get("cart")  # Assume cart is passed as a list of product IDs and quantities
        if not cart:
            return Response({"error": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        order = None
        try:
            with transaction.atomic():
                total_price = Decimal(0)
                order = Order.objects.create(user=request.user, total_price=0)  # Placeholder for total price

                for item in cart:
                    product_id = item.get("product_id")
                    quantity = item.get("quantity", 1)

                    product = get_object_or_404(Product, id=product_id)

                    if product.stock < quantity:
                        raise ValueError(f"Insufficient stock for product {product.name}.")

                    product.stock -= quantity
                    product.save()

                    order_item = OrderItem.objects.create(
                        order=order,
                        product=product.name,  # Replace with product instance if using FK
                        quantity=quantity,
                        price=product.price * quantity
                    )

                    total_price += order_item.price

                order.total_price = total_price
                order.save()

            # Optionally send confirmation email
            send_order_confirmation(order)

            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            if order:
                order.delete()
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing products"""
    serializer_class = ProductSerializer
    queryset = Product.objects.filter(status='published')
    permission_classes = [IsAuthenticated]