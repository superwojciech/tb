import hashlib
import json
from time import time


class Blockchain:
    def __init__(self, difficulty=4):
        self.chain = []
        self.current_transactions = []   # pula transakcji oczekujących
        self.difficulty = difficulty     # liczba wiodących zer skrótu
        self.create_genesis_block()

    def create_genesis_block(self):
        self.chain.append({
            "index": 1,
            "timestamp": 0,
            "transactions": [],
            "nonce": 0,
            "previous_hash": "0",
        })

    @staticmethod
    def hash(block):
        return hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            "sender": sender,
            "recipient": recipient,
            "amount": amount,
        })
        return self.last_block["index"] + 1

    def proof_of_work(self, block):
        block["nonce"] = 0
        computed_hash = self.hash(block)
        while not computed_hash.startswith("0" * self.difficulty):
            block["nonce"] += 1
            computed_hash = self.hash(block)
        return computed_hash

    def mine(self, miner_address):
        reward = {"sender": "0", "recipient": miner_address, "amount": 1}
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time(),
            "transactions": [reward] + self.current_transactions,
            "nonce": 0,
            "previous_hash": self.hash(self.last_block),
        }
        self.proof_of_work(block)
        self.current_transactions = []
        self.chain.append(block)
        return block

    def valid_chain(self, chain):
        if chain[0] != self.chain[0]:
            return False
        for i in range(1, len(chain)):
            previous, block = chain[i - 1], chain[i]
            if block["previous_hash"] != self.hash(previous):
                return False
            if not self.hash(block).startswith("0" * self.difficulty):
                return False
        return True


if __name__ == "__main__":
    bc = Blockchain(difficulty=4)

    bc.new_transaction("Alice", "Bob", 5)
    bc.new_transaction("Bob", "Carol", 2)
    bc.mine("miner-1")

    bc.new_transaction("Carol", "Dave", 1)
    bc.mine("miner-1")

    bc.new_transaction("Dave", "Eve", 3)
    bc.mine("miner-2")

    for b in bc.chain:
        h = bc.hash(b)
        print(f"Blok {b['index']}: nonce={b['nonce']}, hash={h}")
        for tx in b["transactions"]:
            print("   ", tx)
        if b["index"] > 1:
            print("    skrót zaczyna się od", bc.difficulty, "zer:", h.startswith("0" * bc.difficulty))

    print("Łańcuch poprawny:", bc.valid_chain(bc.chain))
