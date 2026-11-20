import hashlib
import json
from time import time


class Blockchain:
    def __init__(self, difficulty=4):
        self.chain = []
        self.current_transactions = []
        self.difficulty = difficulty
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


def build_chain(difficulty):
    """Łańcuch 5 bloków: geneza + 4 wykopane, w bloku nr 2 transakcja Alice -> Bob."""
    bc = Blockchain(difficulty=difficulty)
    bc.new_transaction("Alice", "Bob", 5)
    bc.mine("miner-1")                       # blok nr 2
    for i in range(3):                       # bloki nr 3-5
        bc.new_transaction("Bob", "Carol", i + 1)
        bc.mine("miner-1")
    return bc


def attack(bc, block_number):
    """Atakujący ponownie wydobywa zmodyfikowany blok i wszystkie kolejne."""
    start = time()
    for i in range(block_number - 1, len(bc.chain)):
        bc.chain[i]["previous_hash"] = bc.hash(bc.chain[i - 1])
        bc.proof_of_work(bc.chain[i])
    return time() - start


if __name__ == "__main__":
    for d in (4, 5):
        print(f"--- trudność {d} ---")
        bc = build_chain(d)
        print("Liczba bloków:", len(bc.chain))
        print("Łańcuch poprawny przed modyfikacją:", bc.valid_chain(bc.chain))

        tx = bc.chain[1]["transactions"][1]          # blok nr 2, transakcja Alice -> Bob
        print("Oryginalna transakcja:", tx)
        tx["amount"] = 500
        print("Zmieniona transakcja: ", tx)
        print("Łańcuch poprawny po modyfikacji:", bc.valid_chain(bc.chain))

        t = attack(bc, block_number=2)
        print(f"Atak (ponowne wydobycie bloków 2-5): {t:.2f} s")
        print("Łańcuch poprawny po ataku:", bc.valid_chain(bc.chain))
        print()
