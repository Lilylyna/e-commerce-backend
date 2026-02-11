from django.urls import path

from . import api

app_name = "cryptopayments"

urlpatterns = [
    # Core invoice lifecycle
    path("testnet/invoices/", api.create_testnet_invoice, name="create_testnet_invoice"),
    path(
        "testnet/invoices/<str:invoice_id>/",
        api.get_testnet_invoice_status,
        name="get_testnet_invoice_status",
    ),
    path(
        "testnet/invoices/<str:invoice_id>/simulate-payment/",
        api.simulate_testnet_payment,
        name="simulate_testnet_payment",
    ),
    path(
        "testnet/invoices/<str:invoice_id>/refund/",
        api.create_testnet_refund,
        name="create_testnet_refund",
    ),
    # Network-level helpers
    path(
        "testnet/mempool/<str:address>/",
        api.watch_testnet_mempool,
        name="watch_testnet_mempool",
    ),
    path(
        "testnet/proof/<str:tx_id>/",
        api.get_testnet_payment_proof,
        name="get_testnet_payment_proof",
    ),
]

