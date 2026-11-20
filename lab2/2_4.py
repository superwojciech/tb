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
        # walidacja danych
        if isinstance(amount, bool) or not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("Kwota musi być liczbą dodatnią")
        if not isinstance(sender, str) or not sender.strip():
            raise ValueError("Nadawca musi być niepustym ciągiem znaków")
        if not isinstance(recipient, str) or not recipient.strip():
            raise ValueError("Odbiorca musi być niepustym ciągiem znaków")
        if sender == recipient:
            raise ValueError("Nadawca i odbiorca nie mogą być tacy sami")
        # sprawdzenie środków (nadawca "0" = coinbase, nie sprawdzamy)
        if sender != "0" and self.get_balance(sender) < amount:
            raise ValueError(f"Brak środków: saldo {sender} = {self.get_balance(sender)}, "
                             f"kwota = {amount}")
        self.current_transactions.append({
            "sender": sender,
            "recipient": recipient,
            "amount": amount,
        })
        return self.last_block["index"] + 1

    def get_balance(self, address):
        """Saldo adresu ze wszystkich transakcji w łańcuchu i w puli oczekujących."""
        balance = 0
        transactions = [tx for block in self.chain for tx in block["transactions"]]
        transactions += self.current_transactions
        for tx in transactions:
            if tx["recipient"] == address:
                balance += tx["amount"]
            if tx["sender"] == address:
                balance -= tx["amount"]
        return balance

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


def try_tx(bc, sender, recipient, amount):
    try:
        bc.new_transaction(sender, recipient, amount)
        print(f"OK     {sender!r} -> {recipient!r}: {amount!r}")
    except ValueError as e:
        print(f"ODRZ.  {sender!r} -> {recipient!r}: {amount!r}  ({e})")


if __name__ == "__main__":
    bc = Blockchain(difficulty=3)

    print("--- walidacja danych ---")
    try_tx(bc, "Alice", "Bob", -5)       # kwota ujemna
    try_tx(bc, "Alice", "Bob", 0)        # kwota zerowa
    try_tx(bc, "Alice", "Bob", "10")     # kwota nie jest liczbą
    try_tx(bc, "", "Bob", 1)             # pusty nadawca
    try_tx(bc, "Alice", "  ", 1)         # pusty odbiorca
    try_tx(bc, "Bob", "Bob", 1)          # nadawca = odbiorca

    print("\n--- saldo i brak środków ---")
    try_tx(bc, "Alice", "Bob", 1)        # Alice nie ma środków
    bc.mine("Alice")                     # Alice dostaje nagrodę 1
    bc.mine("Alice")                     # i kolejną: saldo 2
    print("Saldo Alice:", bc.get_balance("Alice"))
    try_tx(bc, "Alice", "Bob", 1.5)      # OK, saldo w puli spada do 0.5
    print("Saldo Alice (z pulą):", bc.get_balance("Alice"))

    print("\n--- próba double spending ---")
    try_tx(bc, "Alice", "Carol", 1.5)    # te same środki drugi raz -> odrzucone
    bc.mine("miner-1")
    print("Saldo Alice:", bc.get_balance("Alice"), "| Bob:", bc.get_balance("Bob"),
          "| Carol:", bc.get_balance("Carol"))
    print("Łańcuch poprawny:", bc.valid_chain(bc.chain))
