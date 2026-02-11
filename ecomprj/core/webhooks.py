import stripe
import logging
import json
import hmac
import hashlib
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .email_utils import send_order_confirmation
from .models import Order
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe_logger = logging.getLogger("stripe")
btcpay_logger = logging.getLogger("btcpay")

# BTCPay Client setup - with graceful fallback if library not installed
btcpay_client = None
try:
    from btcpay import BTCPayClient
    
    if getattr(settings, "BTCPAY_SERVER_URL", None) and getattr(settings, "BTCPAY_API_KEY", None):
        try:
            btcpay_client = BTCPayClient(
                host=settings.BTCPAY_SERVER_URL,
                pem=settings.BTCPAY_API_KEY
            )
            btcpay_logger.info("BTCPay client initialized successfully")
        except Exception as e:
            btcpay_logger.error(f"BTCPay client init error: {e}")
            btcpay_client = None
    else:
        btcpay_logger.warning("BTCPay Server URL or API Key is not configured. BTCPay webhooks will not be processed.")
except ImportError:
    btcpay_logger.warning("BTCPay library not installed. Run 'pip install btcpay' to enable BTCPay webhooks.")

@csrf_exempt
@require_POST
@api_view(["POST"])
@extend_schema(
    description="Stripe webhook to handle payment events",
    request=None,
    responses={
        200: {"description": "Webhook processed successfully"},
        400: {"description": "Bad request or invalid signature"},
        500: {"description": "Internal server error"}
    }
)
def stripe_webhook(request):
    """
    Handle Stripe webhook events.
    Supports both test events (DEBUG=True) and production events.
    """
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    
    stripe_logger.info(f"Webhook received. Signature: {sig_header[:50] if sig_header else 'None'}...")

    # For testing in debug mode, skip signature verification
    if settings.DEBUG and not sig_header:
        stripe_logger.warning("DEBUG mode: Skipping signature verification")
        try:
            event_data = json.loads(payload.decode('utf-8'))
            return handle_stripe_webhook_event_debug(event_data)
        except Exception as e:
            stripe_logger.error(f"Debug webhook error: {str(e)}")
            return HttpResponse(status=400)

    # Production: Verify signature
    if not sig_header:
        stripe_logger.error("Missing Stripe signature")
        return HttpResponse(status=400)

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError as e:
        stripe_logger.error(f"Invalid Stripe signature: {str(e)}")
        return HttpResponse(status=400)
    except ValueError as e:
        stripe_logger.error(f"Invalid payload: {str(e)}")
        return HttpResponse(status=400)
    except Exception as e:
        stripe_logger.error(f"Webhook error: {str(e)}")
        return HttpResponse(status=400)

    # Handle verified event
    return handle_stripe_webhook_event(event)

def handle_stripe_webhook_event_debug(event_data):
    """Handle webhook events in debug mode (no signature verification)"""
    event_type = event_data.get("type")
    intent = event_data.get("data", {}).get("object", {})
    intent_id = intent.get("id")
    
    stripe_logger.info(f"Debug mode: Processing {event_type} for intent {intent_id}")
    
    # Find order
    try:
        order = Order.objects.get(stripe_payment_intent=intent_id)
        stripe_logger.info(f"Found order {order.id} for intent {intent_id}")
    except Order.DoesNotExist:
        stripe_logger.warning(f"No order found for intent {intent_id}")
        # In debug mode, we can still return success
        return JsonResponse({
            "status": "warning",
            "message": f"No order found for intent {intent_id}",
            "debug": True
        }, status=200)

    # Handle successful payment
    if event_type == "payment_intent.succeeded":
        # Skip if already paid
        if order.status == "paid":
            stripe_logger.info(f"Order {order.id} already marked as paid")
            return JsonResponse({
                "status": "already_paid",
                "message": f"Order {order.id} already paid",
                "debug": True
            }, status=200)

        # In debug mode, skip amount verification or use safe check
        expected_amount = int(order.amount * 100)
        amount_received = intent.get("amount_received", intent.get("amount", expected_amount))
        
        if amount_received != expected_amount:
            stripe_logger.warning(
                f"Debug: Amount mismatch for order {order.id}: "
                f"expected {expected_amount}, got {amount_received}. Accepting anyway in debug mode."
            )
        
        # Mark order as paid
        order.status = "paid"
        order.order_status = "processing"
        order.save()
        stripe_logger.info(f"Debug: Order {order.id} marked as paid")

        # Send confirmation email
        try:
            send_order_confirmation(order)
            stripe_logger.info(f"Debug: Order confirmation email sent for order {order.id}")
        except Exception as e:
            stripe_logger.error(f"Debug: Failed to send email for order {order.id}: {str(e)}")

        return JsonResponse({
            "status": "success",
            "message": f"Order {order.id} processed successfully",
            "debug": True,
            "order_id": order.id,
            "amount": str(order.amount)
        }, status=200)

    # Handle failed payment
    elif event_type == "payment_intent.payment_failed":
        order.status = "failed"
        order.save()
        stripe_logger.info(f"Debug: Payment failed for {intent_id}")
        
        return JsonResponse({
            "status": "failed",
            "message": f"Payment failed for order {order.id}",
            "debug": True
        }, status=200)
    
    # Unknown event type
    else:
        stripe_logger.info(f"Debug: Unhandled event type {event_type}")
        return JsonResponse({
            "status": "unhandled",
            "message": f"Unhandled event type: {event_type}",
            "debug": True
        }, status=200)

def handle_stripe_webhook_event(event):
    """Handle verified Stripe webhook events (production)"""
    event_type = event["type"]
    intent = event["data"]["object"]
    intent_id = intent["id"]
    
    stripe_logger.info(f"Processing {event_type} for intent {intent_id}")

    # Find order
    try:
        order = Order.objects.get(stripe_payment_intent=intent_id)
    except Order.DoesNotExist:
        stripe_logger.warning(f"No order found for intent {intent_id}")
        return HttpResponse(status=200)  # Important: respond 200 anyway

    # Handle successful payment
    if event_type == "payment_intent.succeeded":
        # Idempotency: skip if already paid
        if order.status == "paid":
            stripe_logger.info(f"Order {order.id} already marked as paid")
            return HttpResponse(status=200)

        # Amount verification (Stripe uses cents)
        expected_amount = int(order.amount * 100)
        
        # Use safe access for amount_received
        amount_received = intent.get("amount_received", 0)
        
        if amount_received != expected_amount:
            stripe_logger.error(
                f"Amount mismatch for order {order.id}: "
                f"expected {expected_amount}, got {amount_received}"
            )
            return HttpResponse(status=400)

        # Mark order as paid
        order.status = "paid"
        order.order_status = "processing"
        order.save()
        stripe_logger.info(f"Payment succeeded for {intent_id}")

        # Send confirmation email
        try:
            send_order_confirmation(order)
            stripe_logger.info(f"Order confirmation email sent for order {order.id}")
        except Exception as e:
            stripe_logger.error(f"Failed to send email for order {order.id}: {str(e)}")

    # Handle failed payment
    elif event_type == "payment_intent.payment_failed":
        order.status = "failed"
        order.save()
        stripe_logger.info(f"Payment failed for {intent_id}")

    return HttpResponse(status=200)

#btcpay webhook
@csrf_exempt
@require_POST
@api_view(["POST"])
@extend_schema(
    description="BTCPay Server webhook to handle payment events",
    request=None,
    responses={
        200: {"description": "Webhook processed successfully"},
        400: {"description": "Bad request or invalid signature"},
        500: {"description": "Internal server error"}
    }
)
def btcpay_webhook(request):
    """
    Handle BTCPay Server webhook events.
    """
    if not btcpay_client:
        btcpay_logger.error("BTCPay Server is not configured or btcpay library is not installed.")
        return HttpResponse(status=500)

    payload = request.body
    signature = request.META.get('HTTP_BTCPAY_SIG')  # BTCPay-Sig header

    if not signature:
        btcpay_logger.error("Missing BTCPay Server signature")
        return HttpResponse(status=400)

    # Verify webhook signature
    webhook_secret = getattr(settings, 'BTCPAY_WEBHOOK_SECRET', None)
    if webhook_secret:
        try:
            # BTCPay uses HMAC-SHA256 for webhook signatures
            expected_signature = hmac.new(
                webhook_secret.encode('utf-8'),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures (use constant-time comparison)
            if not hmac.compare_digest(signature, f"sha256={expected_signature}"):
                btcpay_logger.error("BTCPay webhook signature verification failed")
                return HttpResponse(status=400)
        except Exception as e:
            btcpay_logger.error(f"BTCPay webhook signature verification error: {str(e)}")
            return HttpResponse(status=400)
    else:
        btcpay_logger.warning("BTCPAY_WEBHOOK_SECRET not configured. Skipping signature verification.")

    try:
        event = json.loads(payload.decode('utf-8'))
    except json.JSONDecodeError:
        btcpay_logger.error("Invalid JSON payload for BTCPay webhook.")
        return HttpResponse(status=400)

    invoice_id = event.get('invoiceId')
    event_type = event.get('type')
    new_status = event.get('status')

    if not invoice_id or not event_type:
        btcpay_logger.warning(f"Malformed BTCPay webhook event: {event}")
        return HttpResponse(status=400)
    
    btcpay_logger.info(f"BTCPay Webhook received for invoice {invoice_id} with status {new_status} (Event Type: {event_type})")

    try:
        order = Order.objects.get(btcpay_invoice_id=invoice_id)
    except Order.DoesNotExist:
        btcpay_logger.warning(f"Order not found for BTCPay invoice ID: {invoice_id}")
        return HttpResponse(status=200)  # Important: respond 200 anyway to prevent retries

    # Map BTCPay statuses to our internal order statuses
    # BTCPay statuses: New, Processing, Expired, Invalid, Settled
    if new_status in ['Settled', 'Processing']:
        if order.status != "paid":
            order.status = "paid"
            order.order_status = "processing"
            order.save()
            btcpay_logger.info(f"Order {order.id} for BTCPay invoice {invoice_id} marked as paid.")
            try:
                send_order_confirmation(order)
                btcpay_logger.info(f"Order confirmation email sent for order {order.id}")
            except Exception as e:
                btcpay_logger.error(f"Failed to send email for order {order.id}: {str(e)}")
    elif new_status == 'Invalid':
        if order.status != "failed":
            order.status = "failed"
            order.order_status = "cancelled"
            order.save()
            btcpay_logger.warning(f"Order {order.id} for BTCPay invoice {invoice_id} marked as failed.")
    elif new_status == 'Expired':
        if order.status not in ["paid", "failed"]:
            order.status = "failed"
            order.order_status = "cancelled"
            order.save()
            btcpay_logger.info(f"Order {order.id} for BTCPay invoice {invoice_id} expired.")
    else:
        btcpay_logger.info(f"Unhandled BTCPay invoice status for invoice {invoice_id}: {new_status}")

    return HttpResponse(status=200)