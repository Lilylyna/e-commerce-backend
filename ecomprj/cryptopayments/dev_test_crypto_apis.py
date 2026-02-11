"""
Small dev helper script to exercise the cryptopayments testnet API.

Run from the project root (where manage.py lives):

    python -m cryptopayments.dev_test_crypto_apis

It will:
    1) Create a testnet invoice
    2) Check its status
    3) Simulate a payment
    4) Check status again
    5) Create a refund
and print all responses to stdout.
"""

import json
import urllib.request


BASE_URL = "http://127.0.0.1:8000/api/crypto/testnet"


def _request(method: str, path: str, body: dict | None = None):
    url = f"{BASE_URL}{path}"
    data = None
    headers = {}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req) as resp:
        raw = resp.read().decode("utf-8")
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = raw
        print(f"\n=== {method} {path} -> {resp.status} ===")
        print(raw)
        return parsed


def main():
    # 1) Create invoice
    create_resp = _request(
        "POST",
        "/invoices/",
        {"amount": 10, "currency": "TBTC"},
    )
    invoice_id = create_resp.get("invoice_id")

    if not invoice_id:
        print("Failed to create invoice; aborting.")
        return

    # 2) Initial status
    _request("GET", f"/invoices/{invoice_id}/")

    # 3) Simulate payment
    _request(
        "POST",
        f"/invoices/{invoice_id}/simulate-payment/",
        {"amount": 10},
    )

    # 4) Status after payment
    _request("GET", f"/invoices/{invoice_id}/")

    # 5) Create a refund of 5 units to a dummy address
    _request(
        "POST",
        f"/invoices/{invoice_id}/refund/",
        {"refund_address": "customer_refund_address_1", "amount": 5},
    )


if __name__ == "__main__":
    main()

