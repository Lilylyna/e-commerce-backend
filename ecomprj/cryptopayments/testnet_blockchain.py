import time
import uuid
import hashlib

class Block:
    def __init__(self, index, timestamp, transactions, previous_hash,  nonce=0):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = str(self.index) + str(self.timestamp) + str(self.transactions) + str(self.previous_hash) + str(self.nonce)
        return hashlib.sha256(block_string.encode()).hexdigest()

class Transaction:
    def __init__(self, sender, recipient, amount, tx_id=None, fee=0.0):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.fee = fee
        self.amount_with_fee = amount + fee
        self.timestamp = time.time()
        self.tx_id = tx_id if tx_id else str(uuid.uuid4())

    def to_dict(self):
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "fee": self.fee,
            "amount_with_fee": self.amount_with_fee,
            "timestamp": self.timestamp,
            "tx_id": self.tx_id
        }

class TestnetBlockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.create_genesis_block()
        self.balances = {}
        self.mempool = [] # For unconfirmed transactions

    def create_genesis_block(self):
        genesis_block = Block(0, time.time(), [], "0")
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        return self.chain[-1]

    def add_transaction(self, transaction: Transaction) -> bool:
        if transaction.amount <= 0:
            print("Transaction amount must be positive.")
            return False
        # Sender must have enough balance PLUS the fee
        fee = self.calculate_fee(transaction.amount) # Placeholder for transaction_size
        if transaction.sender != "network" and self.balances.get(transaction.sender, 0) < (transaction.amount + fee):
            print(f"Insufficient funds for {transaction.sender}. Balance: {self.balances.get(transaction.sender, 0)}, Needed: {transaction.amount + fee}")
            return False

        self.pending_transactions.append(transaction)
        self.mempool.append(transaction) # Add to mempool as unconfirmed
        print(f"Added transaction to pending and mempool: {transaction.to_dict()}")
        return True

    def mine_block(self) -> Block:
        if not self.pending_transactions:
            print("No pending transactions to mine.")
            return None

        # Include fees in transactions before mining
        transactions_to_mine = []
        for tx in self.pending_transactions:
            fee = self.calculate_fee(tx.amount) # Calculate fee for each transaction
            if tx.sender != "network":
                tx.amount_with_fee = tx.amount + fee
                # Deduct fee from sender, add to a miner (network) or burn (for simplicity, we'll let it be deducted)
            else:
                tx.amount_with_fee = tx.amount
            transactions_to_mine.append(tx)

        last_block_hash = self.last_block.hash
        new_block_index = len(self.chain)
        timestamp = time.time()

        new_block = Block(new_block_index, timestamp, transactions_to_mine, last_block_hash)

        self.chain.append(new_block)
        self._update_balances(new_block.transactions)
        self.pending_transactions = [] # Clear pending transactions after mining
        self.mempool = [tx for tx in self.mempool if tx not in transactions_to_mine] # Remove confirmed from mempool
        print(f"Block {new_block.index} mined with {len(new_block.transactions)} transactions.")
        return new_block

    def _update_balances(self, transactions):
        for tx in transactions:
            if tx.sender != "network": # 'network' is a special sender for faucet/rewards
                self.balances[tx.sender] = self.balances.get(tx.sender, 0) - tx.amount_with_fee # Deduct amount + fee
            self.balances[tx.recipient] = self.balances.get(tx.recipient, 0) + tx.amount

    def calculate_fee(self, transaction_size_bytes: float) -> float:
        """
        Simulates calculating a network fee based on transaction size.
        In a real system, this would depend on current network congestion and fee markets.
        """
        # Simulating a fixed sat/byte fee (e.g., 10 sat/byte for simplicity)
        # For more realism, transaction_size_bytes would be derived from the actual transaction structure.
        return transaction_size_bytes * 0.00001  # e.g., 1 sat = 0.00000001 BTC. So 0.00001 is 1000 sat

    def get_mempool_transactions(self):
        return self.mempool

    def get_balance(self, address: str) -> float:
        return self.balances.get(address, 0)

    def get_transactions_for_address(self, address: str):
        address_transactions = []
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender == address or tx.recipient == address:
                    address_transactions.append(tx.to_dict())
        return address_transactions

    def generate_payment_proof(self, tx_id: str) -> dict:
        """
        Simulates generating a payment proof (e.g., Merkle proof or transaction receipt).
        In a real blockchain, this would involve cryptographic proofs showing the transaction
        is included in a block.
        """
        for block in self.chain:
            for tx in block.transactions:
                if tx.tx_id == tx_id:
                    print(f"Generated simulated payment proof for transaction {tx_id} in block {block.index}.")
                    # In a real scenario, this would be a complex Merkle proof or signed receipt.
                    return {
                        "tx_id": tx.tx_id,
                        "block_hash": block.hash,
                        "block_index": block.index,
                        "confirmation_time": block.timestamp,
                        "simulated_merkle_proof": f"merkle_proof_for_tx_{tx_id}_in_block_{block.index}"
                    }
        print(f"Transaction {tx_id} not found on the blockchain.")
        return {"error": "Transaction not found"}

# Example Usage (for testing this module independently):
if __name__ == "__main__":
    print("--- Initializing Testnet Blockchain ---")
    test_blockchain = TestnetBlockchain()
    print(f"Genesis block hash: {test_blockchain.last_block.hash}")

    print("\n--- Creating and adding transactions ---")
    tx1 = Transaction("walletA", "walletB", 10.0)
    test_blockchain.add_transaction(tx1)
    tx2 = Transaction("walletB", "walletC", 5.0)
    test_blockchain.add_transaction(tx2)

    print("\n--- Mining a block ---")
    test_blockchain.mine_block()
    print(f"Chain length: {len(test_blockchain.chain)}")

    print("\n--- Checking balances ---")
    print(f"Balance of walletA: {test_blockchain.get_balance("walletA")}")
    print(f"Balance of walletB: {test_blockchain.get_balance("walletB")}")

    # Simulate faucet for walletA
    faucet_tx = Transaction("network", "walletA", 100.0)
    test_blockchain.add_transaction(faucet_tx)
    test_blockchain.mine_block()
    print(f"Balance of walletA after faucet: {test_blockchain.get_balance("walletA")}")

    print("\n--- Getting transactions for walletA ---")
    wallet_a_txs = test_blockchain.get_transactions_for_address("walletA")
    for tx in wallet_a_txs:
        print(tx)

    print("\n--- Trying to send with insufficient funds ---")
    insufficient_tx = Transaction("walletC", "walletA", 1000.0)
    test_blockchain.add_transaction(insufficient_tx)
    test_blockchain.mine_block()
    print(f"Balance of walletC: {test_blockchain.get_balance("walletC")}")
