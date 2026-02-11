import time
from collections import defaultdict
from decimal import Decimal
from typing import Dict

from django.conf import settings
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .testnet_blockchain import TestnetBlockchain
from .testnet_wallet import TestnetWallet
from .testnet_payment_processor import TestnetPaymentProcessor


# ---------------------------------------------------------------------------
# Singleton-like testnet environment (simulates a BTCPay test server)
# ---------------------------------------------------------------------------

_BLOCKCHAIN = TestnetBlockchain()
_WALLET = TestnetWallet(
    _BLOCKCHAIN,
    xpub=getattr(settings, "TESTNET_XPUB", "xpub_simulated_master_key"),
)
_PROCESSOR = TestnetPaymentProcessor(_BLOCKCHAIN, _WALLET)


# ---------------------------------------------------------------------------
# Simple in-memory rate limiting (per IP) for invoice creation
# ---------------------------------------------------------------------------

_INVOICE_REQUEST_LOG: Dict[str, list[float]] = defaultdict(list)


def _get_client_key(request) -> str:
    # Very simple key based on IP; good enough for local testing.
    return request.META.get("REMOTE_ADDR", "unknown")


def _check_rate_limit(request, window_seconds: int = 60, max_requests: int = 10) -> bool:
    """
    Basic sliding-window rate limiter so you can't spam invoice creations.
    This is intentionally simple and in-memory for test usage.
    """
    key = _get_client_key(request)
    now = time.time()
    timestamps = _INVOICE_REQUEST_LOG[key]
    # Keep only timestamps within the current window
    timestamps = [t for t in timestamps if now - t < window_seconds]
    if len(timestamps) >= max_requests:
        _INVOICE_REQUEST_LOG[key] = timestamps
        return False
    timestamps.append(now)
    _INVOICE_REQUEST_LOG[key] = timestamps
    return True


def _expire_old_invoices() -> None:
    """
    Helper to run invoice expiration checks on each API call.
    This keeps the demo environment fresh without needing a background worker.
    """
    _PROCESSOR.check_for_expired_invoices()


# ---------------------------------------------------------------------------
# API Views
# ---------------------------------------------------------------------------


@csrf_exempt
@api_view(["POST"])
def create_testnet_invoice(request):
    """
    Create a new testnet invoice (BTCPay-style).

    Body:
    - amount (decimal or float, required)
    - currency (string, required, e.g. 'TBTC')
    - webhook_url (optional) override for where the simulated webhook is sent
    """
    _expire_old_invoices()

    if not _check_rate_limit(request):
        return Response(
            {"error": "Rate limit exceeded for invoice creation."},
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    amount = request.data.get("amount")
    currency = request.data.get("currency")
    webhook_url = request.data.get("webhook_url")

    if amount is None or currency is None:
        return Response(
            {"error": "Both 'amount' and 'currency' are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        amount_decimal = float(Decimal(str(amount)))
        if amount_decimal <= 0:
            raise ValueError
    except Exception:
        return Response(
            {"error": "Invalid 'amount' value."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    invoice = _PROCESSOR.create_invoice(amount_decimal, currency, webhook_url=webhook_url)
    return Response(invoice, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def get_testnet_invoice_status(request, invoice_id: str):
    """
    Retrieve the current status of a testnet invoice.
    This also triggers a scan of the chain, similar to BTCPay checking for payments.
    """
    _expire_old_invoices()

    if invoice_id not in _PROCESSOR.invoices:
        raise Http404("Invoice not found")
    status_data = _PROCESSOR.get_invoice_status(invoice_id)
    return Response(status_data, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(["POST"])
def simulate_testnet_payment(request, invoice_id: str):
    """
    Helper endpoint for tests: simulate a payer sending funds to the invoice address.

    Body:
    - amount (optional, defaults to full invoice amount)
    """
    _expire_old_invoices()

    invoice = _PROCESSOR.invoices.get(invoice_id)
    if not invoice:
        raise Http404("Invoice not found")

    try:
        amount_raw = request.data.get("amount", invoice.amount)
        amount = float(Decimal(str(amount_raw)))
        if amount <= 0:
            raise ValueError
    except Exception:
        return Response(
            {"error": "Invalid 'amount' value."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Create a fresh sender address, fund it via the faucet, and send funds.
    sender_address = _WALLET.generate_address()
    # Ensure enough funds including simulated fees; over-fund a bit.
    _WALLET.faucet(sender_address, amount * 2)
    sent = _WALLET.send_funds(sender_address, invoice.payment_address, amount)
    if not sent:
        return Response(
            {"error": "Failed to send simulated payment."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Confirm the transaction on-chain.
    _BLOCKCHAIN.mine_block()

    status_data = _PROCESSOR.get_invoice_status(invoice_id)
    return Response(status_data, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(["POST"])
def create_testnet_refund(request, invoice_id: str):
    """
    Create a simulated refund for a paid invoice.

    Body:
    - refund_address (string, required)
    - amount (decimal, required)
    """
    _expire_old_invoices()

    refund_address = request.data.get("refund_address")
    amount = request.data.get("amount")

    if not refund_address or amount is None:
        return Response(
            {"error": "'refund_address' and 'amount' are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        amount_decimal = float(Decimal(str(amount)))
        if amount_decimal <= 0:
            raise ValueError
    except Exception:
        return Response(
            {"error": "Invalid 'amount' value."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    result = _PROCESSOR.create_refund(invoice_id, refund_address, amount_decimal)
    http_status = status.HTTP_200_OK if result.get("success") else status.HTTP_400_BAD_REQUEST
    return Response(result, status=http_status)


@api_view(["GET"])
def watch_testnet_mempool(request, address: str):
    """
    Return all unconfirmed transactions related to a given address (mempool view).
    """
    mempool = _PROCESSOR.watch_mempool(address)
    return Response({"address": address, "mempool": mempool}, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_testnet_payment_proof(request, tx_id: str):
    """
    Return a simulated payment proof for a given transaction ID.
    """
    proof = _BLOCKCHAIN.generate_payment_proof(tx_id)
    status_code = status.HTTP_200_OK if "error" not in proof else status.HTTP_404_NOT_FOUND
    return Response(proof, status=status_code)

