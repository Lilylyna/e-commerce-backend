import uuid
from .testnet_blockchain import Transaction, TestnetBlockchain

try:
    # Optional HD wallet support using python-bip32 if installed.
    # This keeps the simulator lightweight but lets you plug in a real xpub.
    from bip32 import BIP32  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    BIP32 = None


class TestnetWallet:
    def __init__(self, blockchain: TestnetBlockchain, xpub: str = "xpub_simulated_master_key"):
        self.blockchain = blockchain
        self.xpub = xpub  # Simulated extended public key (or real xpub if provided)
        self.address_counter = 0
        self.addresses = set()  # Stores addresses managed by this wallet

        # If a real xpub is provided and bip32 is available, prepare an HD wallet context.
        self._bip32 = None
        if BIP32 is not None and xpub and xpub != "xpub_simulated_master_key":
            try:
                self._bip32 = BIP32.from_xpub(xpub)
                print("HD wallet enabled for TestnetWallet using provided xpub.")
            except Exception as exc:  # pragma: no cover - defensive path
                # Fall back to simple deterministic scheme if xpub is invalid.
                print(f"Failed to initialize BIP32 from xpub, falling back to simulated addresses: {exc}")
                self._bip32 = None

    def _derive_hd_address(self) -> str:
        """
        Derive a pseudo-address from the xpub using BIP32 if available.

        For simulation purposes we treat the compressed public key (hex) as the address.
        This keeps things deterministic without needing full Bech32/Base58 encoding.
        """
        assert self._bip32 is not None
        # Use a simple path scheme m/0/{index} to simulate BTCPay-style derivation.
        path = f"m/0/{self.address_counter}"
        pubkey = self._bip32.get_pubkey_from_path(path)
        # Represent the pubkey bytes as a hex "address" for the simulator.
        return pubkey.hex()

    def generate_address(self) -> str:
        """
        Generate the next receive address for this wallet.

        - If BIP32 is available and a real xpub was supplied, derive from the xpub.
        - Otherwise, use a deterministic xpub+counter string as before.
        """
        if self._bip32 is not None:
            derived_address = self._derive_hd_address()
        else:
            # Simulated deterministic generation using a counter and the xpub.
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
