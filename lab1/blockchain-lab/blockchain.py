import hashlib
import json
from time import time


class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis = {
            "index": 1,
            "timestamp": 0,
            "transactions": [],
            "nonce": 0,
            "previous_hash": "0" * 64,
        }
        self.chain.append(genesis)

    @staticmethod
    def hash(block):
        # sort_keys=True gwarantuje deterministyczną kolejność pól
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def add_block(self, transactions):
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time(),
            "transactions": transactions,
            "nonce": 0,
            "previous_hash": self.hash(self.last_block),
        }
        self.chain.append(block)
        return block

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            poprzedni = self.chain[i - 1]
            biezacy = self.chain[i]
            if biezacy["previous_hash"] != self.hash(poprzedni):
                return False, biezacy["index"]
        return True, None


if __name__ == "__main__":
    bc = Blockchain()
    bc.add_block(["Alice -> Bob: 5"])
    bc.add_block(["Bob -> Carol: 2"])
    bc.add_block(["Carol -> Dave: 1"])

    for block in bc.chain:
        print(json.dumps(block, indent=2, ensure_ascii=False))
        print("hash:", Blockchain.hash(block))
        print("-" * 70)

    print("=== Łańcuch nienaruszony ===")
    print("is_chain_valid():", bc.is_chain_valid())

    print("\n=== Modyfikacja bloku nr 2 ===")
    bc.chain[1]["transactions"][0] = "Alice -> Bob: 500"
    print("Blok 2 po zmianie:", bc.chain[1]["transactions"])
    print("is_chain_valid():", bc.is_chain_valid())

    print("\n=== Atakujący przelicza previous_hash ===")
    for i in range(2, len(bc.chain)):
        bc.chain[i]["previous_hash"] = Blockchain.hash(bc.chain[i - 1])
    print("is_chain_valid():", bc.is_chain_valid())

    print("\n=== Modyfikacja ostatniego bloku ===")
    bc2 = Blockchain()
    bc2.add_block(["Alice -> Bob: 5"])
    bc2.add_block(["Bob -> Carol: 2"])
    bc2.add_block(["Carol -> Dave: 1"])
    bc2.last_block["transactions"][0] = "Carol -> Dave: 1000"
    print("Ostatni blok po zmianie:", bc2.last_block["transactions"])
    print("is_chain_valid():", bc2.is_chain_valid())