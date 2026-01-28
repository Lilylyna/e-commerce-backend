import json
import stripe
from decimal import Decimal

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Order
from drf_spectacular.utils import extend_schema

stripe.api_key = settings.STRIPE_SECRET_KEY

#  Backend-defined price
TOTAL_PRICE = Decimal("49.99")


@csrf_exempt
@require_POST
@extend_schema(
    description="Create a Stripe Payment Intent",
    request=None,  # no body required
    responses={
        200: {
            "type": "object",
            "properties": {
                "client_secret": {"type": "string"},
                "order_id": {"type": "integer"},
                "amount": {"type": "string"},
                "currency": {"type": "string"},
            },
        },
        400: {"type": "object", "properties": {"error": {"type": "string"}}},
    },
)
def create_payment_intent(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    email = data.get("email")
    currency = "usd"

    if not email:
        return JsonResponse({"error": "email is required"}, status=400)

    # Convert dollars → cents for Stripe
    amount_cents = int(TOTAL_PRICE * 100)

    # Create Stripe PaymentIntent
    intent = stripe.PaymentIntent.create(
        amount=amount_cents,
        currency=currency,
        receipt_email=email,
        automatic_payment_methods={"enabled": True},
    )

    # Create Order (store dollars)
    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        email=email,
        stripe_payment_intent=intent.id,
        amount=TOTAL_PRICE,
        currency=currency,
        status="pending",
    )

    return JsonResponse({
        "client_secret": intent.client_secret,
        "order_id": order.id,
        "amount": str(TOTAL_PRICE),
        "currency": currency,
    })