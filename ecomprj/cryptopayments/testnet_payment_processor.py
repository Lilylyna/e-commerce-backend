import time
import uuid
from typing import Dict
from .testnet_blockchain import TestnetBlockchain, Transaction
from .testnet_wallet import TestnetWallet
from .testnet_webhook_queue import WebhookQueue # Import the WebhookQueue

class TestnetInvoice:
    def __init__(self, invoice_id, amount, currency, payment_address):
        self.invoice_id = invoice_id
        self.amount = amount
        self.currency = currency
        self.payment_address = payment_address
        self.status = "pending"  # pending, paid, expired
        self.paid_amount = 0.0
        self.created_at = time.time()
        self.expires_at = self.created_at + 3600  # Invoice expires in 1 hour

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

class TestnetPaymentProcessor:
    def __init__(self, blockchain: TestnetBlockchain, wallet: TestnetWallet):
        self.blockchain = blockchain
        self.wallet = wallet
        self.invoices: Dict[str, TestnetInvoice] = {}
        self.webhook_queue = WebhookQueue() # Instantiate the WebhookQueue

    def create_invoice(self, amount: float, currency: str) -> dict:
        """
        Creates a new testnet invoice. It generates a new address from the testnet wallet
        to be used as the payment destination.
        """
        payment_address = self.wallet.generate_address()
        invoice_id = str(uuid.uuid4())
        invoice = TestnetInvoice(invoice_id, amount, currency, payment_address)
        self.invoices[invoice_id] = invoice
        print(f"Testnet Invoice created: {invoice.to_dict()}")
        return invoice.to_dict()

    def monitor_payments(self, invoice_id: str):
        """
        Monitors the simulated blockchain for payments to a specific invoice address.
        In a real system, this would involve polling a node or using webhooks for new transactions.
        """
        invoice = self.invoices.get(invoice_id)
        if not invoice:
            return {"error": "Invoice not found"}

        if invoice.status == "paid" or invoice.status == "expired":
            return invoice.to_dict()

        # Check for expired invoices during monitoring
        if time.time() > invoice.expires_at:
            invoice.status = "expired"
            print(f"Testnet Invoice {invoice_id} has expired during monitoring.")
            return invoice.to_dict()

        # Get transactions for the payment address
        address_transactions = self.blockchain.get_transactions_for_address(invoice.payment_address)
        current_paid_amount = 0.0
        for tx in address_transactions:
            if tx["recipient"] == invoice.payment_address:
                current_paid_amount += tx["amount"]

        if current_paid_amount > invoice.paid_amount:
            invoice.paid_amount = current_paid_amount
            print(f"Update: Invoice {invoice_id} now has {invoice.paid_amount} paid.")

        if invoice.paid_amount >= invoice.amount:
            invoice.status = "paid"
            print(f"Testnet Webhook triggered for invoice {invoice_id}: Payment received!")
            self.webhook_queue.add_webhook("http://your-ecommerce-backend.com/webhook", invoice.to_dict()) # Dispatch webhook

        return invoice.to_dict()

    def get_invoice_status(self, invoice_id: str) -> dict:
        """
        Retrieves the current status of a testnet invoice.
        """
        # Always monitor before returning status to get the latest payment info
        return self.monitor_payments(invoice_id)

    def watch_mempool(self, address: str) -> list:
        """
        Simulates watching the mempool for unconfirmed transactions related to an address.
        In a real system, this would involve subscribing to mempool events from a blockchain node.
        """
        mempool_transactions = []
        for tx in self.blockchain.get_mempool_transactions():
            if tx.recipient == address or tx.sender == address:
                mempool_transactions.append(tx.to_dict())
        if mempool_transactions:
            print(f"Mempool for {address}: {len(mempool_transactions)} unconfirmed transactions found.")
        return mempool_transactions

    def create_refund(self, invoice_id: str, refund_address: str, amount: float) -> dict:
        """
        Simulates creating a refund transaction for a given invoice.
        In a real system, this would involve sending funds from a merchant wallet to the customer's refund address.
        """
        invoice = self.invoices.get(invoice_id)
        if not invoice:
            return {"error": "Invoice not found"}

        if invoice.status != "paid":
            return {"error": "Cannot refund an unpaid or expired invoice."}

        if amount <= 0 or amount > invoice.paid_amount:
            return {"error": "Invalid refund amount."}

        # For simplicity, we'll assume the payment processor has a "merchant wallet" with sufficient funds
        # In a real system, the merchant would specify which wallet to use for refunds.
        merchant_address = self.wallet.generate_address() # Generate a temporary merchant address for refund source
        # Fund the merchant address for the refund (simulated)
        self.wallet.faucet(merchant_address, amount * 2) # Ensure enough funds for refund + fee

        if self.wallet.send_funds(merchant_address, refund_address, amount):
            print(f"Refund initiated for invoice {invoice_id}: {amount} {invoice.currency} to {refund_address}.")
            # Mark the invoice with refund status, or create a separate refund record
            # For simplicity, we just print and rely on blockchain to show the transaction
            return {"success": True, "invoice_id": invoice_id, "refund_address": refund_address, "amount": amount}
        else:
            print(f"Refund failed for invoice {invoice_id}.")
            return {"success": False, "error": "Failed to send refund transaction."}

    def check_for_expired_invoices(self):
        """
        Checks all pending invoices for expiration.
        """
        current_time = time.time()
        for invoice_id, invoice in self.invoices.items():
            if invoice.status == "pending" and current_time > invoice.expires_at:
                invoice.status = "expired"
                print(f"Testnet Invoice {invoice_id} has expired.")

# Example Usage:
if __name__ == "__main__":
    print("--- Testnet Payment Processor Demo ---")

    # 1. Initialize Testnet Blockchain and Wallet
    test_blockchain = TestnetBlockchain()
    test_wallet = TestnetWallet(test_blockchain)
    test_payment_processor = TestnetPaymentProcessor(test_blockchain, test_wallet)
    print("Testnet Blockchain and Wallet initialized.")

    # 2. Create an invoice
    print("\n--- Creating a Testnet Invoice ---")
    invoice_data = test_payment_processor.create_invoice(10.0, "TBTC") # TBTC for Testnet Bitcoin
    invoice_id = invoice_data["invoice_id"]
    payment_address = invoice_data["payment_address"]
    print(f"Generated Testnet Invoice ID: {invoice_id}")
    print(f"Payment Address: {payment_address}")

    # 3. Check initial invoice status
    print("\n--- Checking initial invoice status ---")
    status = test_payment_processor.get_invoice_status(invoice_id)
    print(f"Current status: {status['status']}, Paid: {status['paid_amount']}")

    # 4. Use the faucet to get funds to a sender wallet
    print("\n--- Fauceting funds to a sender wallet ---")
    sender_address = test_wallet.generate_address()
    test_wallet.faucet(sender_address, 20.0)
    print(f"Sender {sender_address} balance: {test_wallet.get_balance(sender_address)}")

    # 5. Simulate a payment from the sender wallet to the invoice address
    print("\n--- Simulating a payment ---")
    test_wallet.send_funds(sender_address, payment_address, 10.0)
    test_blockchain.mine_block() # Mine a block to confirm the transaction

    # 6. Check invoice status after payment
    print("\n--- Checking invoice status after payment ---")
    status = test_payment_processor.get_invoice_status(invoice_id)
    print(f"Status after payment: {status['status']}, Paid: {status['paid_amount']}")
    print(f"Balance of payment address ({payment_address}): {test_blockchain.get_balance(payment_address)}")

    # 7. Demonstrate partial payment and subsequent full payment
    print("\n--- Demonstrating Partial and Full Payment ---")
    invoice_data_2 = test_payment_processor.create_invoice(15.0, "TETH")
    invoice_id_2 = invoice_data_2["invoice_id"]
    payment_address_2 = invoice_data_2["payment_address"]
    sender_address_2 = test_wallet.generate_address()
    test_wallet.faucet(sender_address_2, 30.0)

    print(f"\nPartial Payment to {invoice_id_2}...")
    test_wallet.send_funds(sender_address_2, payment_address_2, 5.0)
    test_blockchain.mine_block()
    status_2 = test_payment_processor.get_invoice_status(invoice_id_2)
    print(f"Status: {status_2['status']}, Paid: {status_2['paid_amount']}")

    print(f"\nRemaining Payment to {invoice_id_2}...")
    test_wallet.send_funds(sender_address_2, payment_address_2, 10.0)
    test_blockchain.mine_block()
    status_2 = test_payment_processor.get_invoice_status(invoice_id_2)
    print(f"Status: {status_2['status']}, Paid: {status_2['paid_amount']}")

    print("\n--- Checking for expired invoices (conceptual) ---")
    # In a real application, this would run periodically, but here we just call it once
    test_payment_processor.check_for_expired_invoices()
