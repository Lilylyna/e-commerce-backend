
from django.urls import path
from core.views import index
from core.payments import create_payment_intent
from core.webhooks import stripe_webhook

urlpatterns = [
    path("", index),
    path("api/create-payment-intent/", create_payment_intent),
    path("api/stripe-webhook/", stripe_webhook),
]


