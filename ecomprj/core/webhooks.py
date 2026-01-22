# core/webhook.py
import stripe
import logging
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .email_utils import send_order_confirmation
from .models import Order
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view

stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger("stripe")


@csrf_exempt
@require_POST
@api_view(["POST"])
@extend_schema(
    description="Stripe webhook to handle payment events",
    responses={200: None, 400: None}
)
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    if not sig_header:
        logger.error("Missing Stripe signature")
        return HttpResponse(status=400)

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        logger.error("Invalid Stripe signature")
        return HttpResponse(status=400)
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return HttpResponse(status=400)

    event_type = event["type"]
    intent = event["data"]["object"]
    intent_id = intent["id"]

    # Find order
    try:
        order = Order.objects.get(stripe_payment_intent=intent_id)
    except Order.DoesNotExist:
        logger.warning(f"No order found for intent {intent_id}")
        return HttpResponse(status=200)  # Important: respond 200 anyway

    # Handle successful payment
    if event_type == "payment_intent.succeeded":

        # Idempotency: skip if already paid
        if order.status == "paid":
            logger.info(f"Order {order.id} already marked as paid")
            return HttpResponse(status=200)

        # Amount verification (Stripe uses cents)
        expected_amount = int(order.amount * 100)
        if intent.amount_received != expected_amount:
            logger.error(
                f"Amount mismatch for order {order.id}: "
                f"expected {expected_amount}, got {intent.amount_received}"
            )
            return HttpResponse(status=400)

        # Mark order as paid
        order.status = "paid"
        order.save()
        logger.info(f"Payment succeeded for {intent_id}")

        # Send confirmation email safely
        try:
            send_order_confirmation(order)
            logger.info(f"Order confirmation email sent for order {order.id}")
        except Exception as e:
            logger.error(f"Failed to send email for order {order.id}: {str(e)}")

    # Handle failed payment
    elif event_type == "payment_intent.payment_failed":
        order.status = "failed"
        order.save()
        logger.info(f"Payment failed for {intent_id}")

    return HttpResponse(status=200)
