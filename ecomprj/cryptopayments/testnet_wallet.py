import uuid
from .testnet_blockchain import Transaction, TestnetBlockchain

class TestnetWallet:
    def __init__(self, blockchain: TestnetBlockchain, xpub: str = "xpub_simulated_master_key"):
        self.blockchain = blockchain
        self.xpub = xpub # Simulated extended public key
        self.address_counter = 0
        self.addresses = set() # Stores addresses managed by this wallet

    def generate_address(self) -> str:
        # In a real HD wallet, this would derive a new address from the xpub.
        # Here, we simulate deterministic generation using a counter and the xpub.
        derived_address = f"{self.xpub}_{self.address_counter}"
        self.address_counter += 1
        self.addresses.add(derived_address)
        print(f"Generated new testnet address (derived from xpub): {derived_address}")
        return derived_address

    def get_balance(self, address: str) -> float:
        if address not in self.addresses:
            print(f"Warning: Address {address} not managed by this wallet. Checking blockchain directly.")
        return self.blockchain.get_balance(address)

    def send_funds(self, sender_address: str, recipient_address: str, amount: float) -> bool:
        if sender_address not in self.addresses:
            print(f"Error: Sender address {sender_address} not managed by this wallet.")
            return False
        
        # Calculate fee and check for sufficient funds
        # Assuming a fixed transaction size for simplicity for fee calculation
        transaction_size_bytes = 250 # Example size in bytes
        fee = self.blockchain.calculate_fee(transaction_size_bytes)
        total_amount = amount + fee

        if self.get_balance(sender_address) < total_amount:
            print(f"Error: Insufficient funds in {sender_address} to send {amount} (including fee of {fee}). Needed: {total_amount}, Have: {self.get_balance(sender_address)}")
            return False

        tx = Transaction(sender_address, recipient_address, amount)
        tx.fee = fee # Store the calculated fee in the transaction object
        
        if self.blockchain.add_transaction(tx):
            print(f"Funds {amount} (plus fee {fee}) sent from {sender_address} to {recipient_address}. Waiting for block confirmation...")
            return True
        return False

    def faucet(self, address: str, amount: float):
        """
        Simulates a faucet providing testnet funds to an address.
        """
        if address not in self.addresses:
            self.addresses.add(address) # Add to wallet if not already there

        faucet_transaction = Transaction("network", address, amount)
        if self.blockchain.add_transaction(faucet_transaction):
            print(f"Faucet dispensed {amount} to {address}. Mining block to confirm...")
            # Mine a block immediately to confirm faucet transaction for simplicity
            self.blockchain.mine_block()
            print(f"New balance for {address}: {self.get_balance(address)}")
            return True
        return False

# Example Usage (for testing this module independently):
if __name__ == "__main__":
    print("--- Initializing Testnet Blockchain and Wallet ---")
    test_blockchain = TestnetBlockchain()
    test_wallet = TestnetWallet(test_blockchain)

    address1 = test_wallet.generate_address()
    address2 = test_wallet.generate_address()

    print(f"\nInitial balance of {address1}: {test_wallet.get_balance(address1)}")

    print("\n--- Using Faucet to get funds ---")
    test_wallet.faucet(address1, 50.0)
    print(f"Balance of {address1} after faucet: {test_wallet.get_balance(address1)}")

    print("\n--- Sending funds between addresses ---")
    test_wallet.send_funds(address1, address2, 15.0)
    test_blockchain.mine_block() # Mine to confirm transaction

    print(f"Balance of {address1} after sending: {test_wallet.get_balance(address1)}")
    print(f"Balance of {address2} after receiving: {test_wallet.get_balance(address2)}")

    print("\n--- Attempting to send more than balance ---")
    test_wallet.send_funds(address2, address1, 100.0)
    test_blockchain.mine_block() # Try to mine, but transaction should not have been added

    print("\n--- Getting transactions for address1 ---")
    txs = test_blockchain.get_transactions_for_address(address1)
    for tx in txs:
        print(tx)
