"""
Legacy / conceptual mainnet payment processor.

NOTE:
    This module is kept as a standalone demo for illustrating ideas like
    node connectivity and asset conversion. It is NOT wired into the
    `cryptopayments` API and is not used by the testnet BTCPay-style
    simulator.

    For dev/testing flows, use the Testnet* modules and the
    /api/crypto/testnet/* endpoints instead.
"""

import uuid
import time
import random

# In-memory store for invoices (for simplification)
invoices = {}

# Simulated blockchain status
_node_connected = False

class Invoice:
    def __init__(self, invoice_id, amount, currency):
        self.invoice_id = invoice_id
        self.amount = amount
        self.currency = currency
        self.payment_address = self._generate_payment_address()
        self.status = "pending"  # pending, paid, expired
        self.paid_amount = 0.0
        self.created_at = time.time()
        self.expires_at = self.created_at + 3600  # Invoice expires in 1 hour

    def _generate_payment_address(self):
        # In a real system, this would interact with a cryptocurrency wallet or node
        # to generate a new, unique address for the specific blockchain.
        # Here, we'll use a UUID as a placeholder.
        return f"{self.currency.lower()}_address_{str(uuid.uuid4())}"

    def to_dict(self):
        return {
            "invoice_id": self.invoice_id,
            "amount": self.amount,
            "currency": self.currency,
            "payment_address": self.payment_address,
            "status": self.status,
            "paid_amount": self.paid_amount,
            "created_at": self.created_at,
            "expires_at": self.expires_at
        }

def initialize_node_connection(node_url: str) -> bool:
    """
    Simulates connecting to a blockchain node.
    In a real system, this would involve establishing a connection to a specific
    blockchain's node (e.g., Bitcoin Core, Ethereum Geth) to interact with the network.
    """
    global _node_connected
    print(f"Attempting to connect to blockchain node at {node_url}...")
    # Simulate connection success/failure
    _node_connected = random.choice([True, False])
    if _node_connected:
        print(f"Successfully connected to node at {node_url}.")
    else:
        print(f"Failed to connect to node at {node_url}.")
    return _node_connected

def convert_blockchain_asset(from_currency: str, to_currency: str, amount: float) -> dict:
    """
    Simulates converting one cryptocurrency to another.
    In a real system, this would involve complex cross-chain protocols,
    atomic swaps, or exchange integrations.
    """
    if not _node_connected:
        return {"error": "Node not connected. Cannot convert assets."}

    print(f"Attempting to convert {amount} {from_currency} to {to_currency}...")
    # Simulate conversion rate and success
    if random.random() > 0.1: # 90% chance of success
        converted_amount = amount * random.uniform(0.95, 1.05) # Simulate some fluctuation
        print(f"Successfully converted {amount} {from_currency} to {converted_amount:.4f} {to_currency}.")
        return {"success": True, "converted_amount": converted_amount, "to_currency": to_currency}
    else:
        print(f"Failed to convert {from_currency} to {to_currency}.")
        return {"error": "Conversion failed"}

def create_invoice(amount: float, currency: str) -> dict:
    """
    Creates a new invoice for a cryptocurrency payment.
    Requires a node connection to generate a valid payment address in a real system.
    """
    if not _node_connected:
        return {"error": "Node not connected. Cannot create invoice."}

    invoice_id = str(uuid.uuid4())
    invoice = Invoice(invoice_id, amount, currency)
    invoices[invoice_id] = invoice
    print(f"Invoice created: {invoice.to_dict()}")
    return invoice.to_dict()

def simulate_payment(invoice_id: str, paid_amount: float) -> dict:
    """
    Simulates a payment being received on the blockchain.
    In a real system, this would involve monitoring the blockchain node for transactions
    to the generated payment address and confirming a certain number of block confirmations.
    Mining is the process by which these transactions are confirmed and added to the blockchain.
    """
    if not _node_connected:
        return {"error": "Node not connected. Cannot simulate payment."}

    invoice = invoices.get(invoice_id)
    if not invoice:
        return {"error": "Invoice not found"}

    if invoice.status == "paid":
        return {"error": "Invoice already paid"}

    if time.time() > invoice.expires_at:
        invoice.status = "expired"
        return {"error": "Invoice expired"}

    invoice.paid_amount += paid_amount
    if invoice.paid_amount >= invoice.amount:
        invoice.status = "paid"
        # In a real system, this would trigger a webhook to the e-commerce platform.
        print(f"Webhook triggered for invoice {invoice_id}: Payment received!")
    else:
        print(f"Partial payment received for invoice {invoice_id}. Remaining: {invoice.amount - invoice.paid_amount}")

    print(f"Invoice updated: {invoice.to_dict()}")
    return invoice.to_dict()

def get_invoice_status(invoice_id: str) -> dict:
    """
    Retrieves the current status of an invoice.
    """
    invoice = invoices.get(invoice_id)
    if not invoice:
        return {"error": "Invoice not found"}
    return invoice.to_dict()

def check_for_expired_invoices():
    """
    Checks for and marks expired invoices.
    """
    current_time = time.time()
    for invoice_id, invoice in invoices.items():
        if invoice.status == "pending" and current_time > invoice.expires_at:
            invoice.status = "expired"
            print(f"Invoice {invoice_id} has expired.")

# Example Usage with new conceptual functions:
if __name__ == "__main__":
    print("--- Initializing Node Connection ---")
    if not initialize_node_connection("https://simulated-node.com"):
        print("Exiting due to failed node connection.")
        exit()

    print("\n--- Creating an invoice ---")
    new_invoice = create_invoice(100.0, "BTC")
    if "error" in new_invoice:
        print(new_invoice["error"])
        invoice_id = None
    else:
        invoice_id = new_invoice["invoice_id"]
        print(f"Generated Invoice ID: {invoice_id}")

    if invoice_id:
        print("\n--- Checking invoice status ---")
        status = get_invoice_status(invoice_id)
        print(f"Current status: {status['status']}")

        print("\n--- Simulating a full payment ---")
        simulate_payment(invoice_id, 100.0)
        status = get_invoice_status(invoice_id)
        print(f"Status after payment: {status['status']}")

    print("\n--- Simulating a blockchain asset conversion ---")
    conversion_result = convert_blockchain_asset("BTC", "ETH", 0.5)
    print(conversion_result)

    print("\n--- Creating another invoice for partial payment test ---")
    new_invoice_2 = create_invoice(50.0, "ETH")
    if "error" in new_invoice_2:
        print(new_invoice_2["error"])
        invoice_id_2 = None
    else:
        invoice_id_2 = new_invoice_2["invoice_id"]
        print(f"Generated Invoice ID 2: {invoice_id_2}")

    if invoice_id_2:
        print("\n--- Simulating partial payment ---")
        simulate_payment(invoice_id_2, 20.0)
        status_2 = get_invoice_status(invoice_id_2)
        print(f"Status after partial payment: {status_2['status']}, Paid: {status_2['paid_amount']}")

        print("\n--- Simulating remaining payment ---")
        simulate_payment(invoice_id_2, 30.0)
        status_2 = get_invoice_status(invoice_id_2)
        print(f"Status after full payment: {status_2['status']}, Paid: {status_2['paid_amount']}")

    print("\n--- Checking for expired invoices (conceptual) ---")
    # In a real application, this would run periodically
    check_for_expired_invoices()
