#core/payments.py
import json
import stripe
from decimal import Decimal
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Order
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from shortuuid import ShortUUID
import logging

logger = logging.getLogger(__name__)

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
            logger.info("BTCPay client initialized successfully")
        except Exception as e:
            logger.error(f"BTCPay client init error: {e}")
    else:
        logger.warning("BTCPay Server URL or API Key not configured. BTCPay payments will not work.")
except ImportError:
    logger.warning("BTCPay library not installed. Run 'pip install btcpay' to enable BTCPay payments.")

# -------------------------------
# Stripe Payment Intent
# -------------------------------
@csrf_exempt
@require_POST
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@extend_schema(
    description="Create a Stripe Payment Intent for checkout",
    request=inline_serializer(
        name='CreatePaymentIntentRequest',
        fields={
            'email': serializers.EmailField(required=True),
            'amount': serializers.DecimalField(max_digits=10, decimal_places=2, required=True),
            'currency': serializers.CharField(default='usd', required=False),
        }
    ),
    responses={
        200: inline_serializer(
            name='CreatePaymentIntentResponse',
            fields={
                'client_secret': serializers.CharField(),
                'order_id': serializers.IntegerField(),
                'payment_intent_id': serializers.CharField(),
                'publishable_key': serializers.CharField(),
                'amount': serializers.DecimalField(max_digits=10, decimal_places=2),
                'currency': serializers.CharField(),
            }
        ),
        400: inline_serializer(
            name='ErrorResponse',
            fields={'error': serializers.CharField()}
        ),
    },
)
def create_payment_intent(request):
    try:
        email = request.data.get("email")
        amount = request.data.get("amount")
        currency = request.data.get("currency", "usd")

        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not amount:
            return Response({"error": "Amount is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount_decimal = Decimal(str(amount))
            if amount_decimal <= 0:
                return Response({"error": "Amount must be greater than 0"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"error": "Invalid amount format"}, status=status.HTTP_400_BAD_REQUEST)

        # Convert dollars → cents for Stripe
        amount_cents = int(amount_decimal * 100)

        # Create Stripe PaymentIntent
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                receipt_email=email,
                automatic_payment_methods={"enabled": True},
                metadata={
                    'user_id': str(request.user.id),
                    'user_email': request.user.email,
                }
            )
        except stripe.error.StripeError as e:
            return Response({"error": f"Stripe error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # Generate unique order ID
        order_id = ShortUUID().random(10)

        order = Order.objects.create(
            user=request.user,
            email=email,
            stripe_payment_intent=intent.id,
            amount=amount_decimal,
            currency=currency,
            status="pending",
            order_status="pending",
            oid=order_id,
            subtotal=amount_decimal,
            shipping_fee=Decimal("0.00"),
            tax=Decimal("0.00"),
            discount_amount=Decimal("0.00"),
            total=amount_decimal,
        )

        return Response({
            "client_secret": intent.client_secret,
            "order_id": order.id,
            "payment_intent_id": intent.id,
            "publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
            "amount": str(amount_decimal),
            "currency": currency,
            "message": "Payment intent created successfully"
        }, status=status.HTTP_200_OK)

    except json.JSONDecodeError:
        return Response({"error": "Invalid JSON in request body"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Unexpected error in create_payment_intent: {str(e)}")
        return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# -------------------------------
# BTCPay Invoice
# -------------------------------
@csrf_exempt
@require_POST
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@extend_schema(
    description="Create a BTCPay Server Invoice for checkout",
    request=inline_serializer(
        name='CreateBTCPayInvoiceRequest',
        fields={
            'email': serializers.EmailField(required=True),
            'amount': serializers.DecimalField(max_digits=10, decimal_places=2, required=True),
            'currency': serializers.CharField(default='usd', required=False),
            'redirect_url': serializers.URLField(required=False),
        }
    ),
    responses={
        200: inline_serializer(
            name='CreateBTCPayInvoiceResponse',
            fields={
                'invoice_id': serializers.CharField(),
                'checkout_url': serializers.URLField(),
                'order_id': serializers.IntegerField(),
                'amount': serializers.DecimalField(max_digits=10, decimal_places=2),
                'currency': serializers.CharField(),
            }
        ),
        400: inline_serializer(
            name='ErrorResponse',
            fields={'error': serializers.CharField()}
        ),
        500: inline_serializer(
            name='ServerErrorResponse',
            fields={'error': serializers.CharField()}
        ),
    },
)
def create_btcpay_invoice(request):
    if not btcpay_client:
        return Response(
            {"error": "BTCPay Server is not configured or btcpay library is not installed. Run 'pip install btcpay'."}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    try:
        email = request.data.get("email")
        amount = request.data.get("amount")
        currency = request.data.get("currency", "usd")
        redirect_url = request.data.get("redirect_url", getattr(settings, "FRONTEND_URL", None))

        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not amount:
            return Response({"error": "Amount is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount_decimal = Decimal(str(amount))
            if amount_decimal <= 0:
                return Response({"error": "Amount must be greater than 0"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"error": "Invalid amount format"}, status=status.HTTP_400_BAD_REQUEST)

        order_id = ShortUUID().random(10)

        invoice_data = {
            "currency": currency,
            "amount": str(amount_decimal),
            "checkout": {
                "speedPolicy": "MediumSpeed",
                "redirectURL": redirect_url,
                "defaultPaymentMethod": "BTC",
            },
            "metadata": {
                "orderId": order_id,
                "user_id": str(request.user.id),
                "user_email": request.user.email,
            },
            "receipt": {"enabled": True},
            "buyer": {"email": email},
        }

        invoice = btcpay_client.create_invoice(getattr(settings, "BTCPAY_STORE_ID"), invoice_data)

        order = Order.objects.create(
            user=request.user,
            email=email,
            btcpay_invoice_id=invoice['id'],
            btcpay_checkout_url=invoice['checkoutLink'],
            amount=amount_decimal,
            currency=currency,
            status="pending",
            order_status="pending",
            oid=order_id,
            subtotal=amount_decimal,
            shipping_fee=Decimal("0.00"),
            tax=Decimal("0.00"),
            discount_amount=Decimal("0.00"),
            total=amount_decimal,
        )

        return Response({
            "invoice_id": invoice['id'],
            "checkout_url": invoice['checkoutLink'],
            "order_id": order.id,
            "amount": str(amount_decimal),
            "currency": currency,
            "message": "BTCPay Server invoice created successfully"
        }, status=status.HTTP_200_OK)

    except json.JSONDecodeError:
        return Response({"error": "Invalid JSON in request body"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Unexpected error in create_btcpay_invoice: {str(e)}")
        return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)