from django.conf import settings
from django.core.mail import send_mail

def send_order_confirmation(order):
    subject = f"Order Confirmation #{order.id}"
    message = (
        f"Hello,\n\n"
        f"Thank you for your order!\n\n"
        f"Order ID: {order.id}\n"
        f"Amount: {order.amount} {order.currency.upper()}\n"
        f"Status: {order.status}\n\n"
        f"We appreciate your business."
    )
    recipient_list = [order.email]

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=False,
    )