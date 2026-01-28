"""
Utility functions for the core app
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from .models import Order


def send_order_confirmation(order_id):
    """
    OBSERVER PATTERN INTEGRATION:
    This function is called by the EmailNotificationObserver when order status changes.
    The observer pattern allows this email functionality to be decoupled from the
    core order processing logic - the Order model doesn't need to know about emails,
    it just notifies observers when its state changes.
    """
    """
    Send order confirmation email to the customer.
    
    Args:
        order_id: The order ID (oid) to send confirmation for
    """
    try:
        # Get the order
        order = Order.objects.select_related('user', 'shipping_address', 'billing_address', 'coupon').prefetch_related(
            'order_items__product'
        ).get(oid=order_id)
        
        user = order.user
        order_items = order.order_items.all()
        
        # Prepare email context
        context = {
            'order': order,
            'user': user,
            'order_items': order_items,
            'shipping_address': order.shipping_address,
            'billing_address': order.billing_address,
            'site_name': getattr(settings, 'SITE_NAME', 'E-Commerce Store'),
        }
        
        # Render email templates (you can create these later)
        # For now, we'll use a simple text email
        subject = f'Order Confirmation - {order.oid}'
        
        # Create email body
        message = f"""
Hello {user.username or user.email},

Thank you for your order!

Order Details:
- Order ID: {order.oid}
- Order Status: {order.order_status.title()}
- Order Date: {order.date.strftime('%B %d, %Y at %I:%M %p')}

Order Items:
"""
        
        for item in order_items:
            message += f"\n- {item.product.title if item.product else 'Deleted Product'}"
            message += f"  Quantity: {item.quantity}"
            message += f"  Price: ${item.price:.2f}"
            message += f"  Subtotal: ${item.subtotal:.2f}"
        
        message += f"""

Pricing Summary:
- Subtotal: ${order.subtotal:.2f}
- Shipping Fee: ${order.shipping_fee:.2f}
- Tax: ${order.tax:.2f}
"""
        
        if order.discount_amount > 0:
            message += f"- Discount: -${order.discount_amount:.2f}\n"
            if order.coupon:
                message += f"  (Coupon: {order.coupon.code})\n"
        
        message += f"- Total: ${order.total:.2f}\n"
        
        if order.shipping_address:
            message += f"""

Shipping Address:
{order.shipping_address.full_name}
{order.shipping_address.address_line_1}
"""
            if order.shipping_address.address_line_2:
                message += f"{order.shipping_address.address_line_2}\n"
            message += f"{order.shipping_address.city}, {order.shipping_address.state} {order.shipping_address.zip_code}\n"
            message += f"{order.shipping_address.country}\n"
            message += f"Phone: {order.shipping_address.phone}\n"
        
        message += f"""

You can view your order details at: {getattr(settings, 'FRONTEND_URL', '')}/orders/{order.oid}

If you have any questions, please contact our support team.

Thank you for shopping with us!
"""
        
        # Get email from settings or use user email
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
        recipient_email = user.email
        
        if not recipient_email:
            # Log warning if user has no email
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"User {user.id} has no email address. Cannot send order confirmation.")
            return False
        
        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[recipient_email],
            fail_silently=False,  # Set to True in production if you want to handle errors gracefully
        )
        
        return True
        
    except Order.DoesNotExist:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Order {order_id} not found. Cannot send confirmation email.")
        return False
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to send order confirmation email for order {order_id}: {str(e)}")
        return False

