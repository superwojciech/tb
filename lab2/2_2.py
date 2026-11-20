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
        # Blok serializujemy raz; w pętli zmienia się tylko nonce.
        # Wynik jest identyczny z hash(block), więc valid_chain działa bez zmian.
        block["nonce"] = 0
        prefix, suffix = json.dumps(block, sort_keys=True).split('"nonce": 0', 1)
        target = "0" * self.difficulty
        nonce = 0
        while True:
            h = hashlib.sha256(f'{prefix}"nonce": {nonce}{suffix}'.encode()).hexdigest()
            if h.startswith(target):
                break
            nonce += 1
        block["nonce"] = nonce
        return h

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


# Aktualne dane sieci Bitcoin (listopad 2026, hashrateindex.com / mempool.space)
BTC_HASHRATE = 1000e18        # ~1000 EH/s
BTC_DIFFICULTY = 148.36e12    # trudność sieci


def measure(d, n_blocks):
    bc = Blockchain(difficulty=d)
    nonces, times = [], []
    for i in range(n_blocks):
        bc.new_transaction("Alice", "Bob", 1)
        start = time()
        block = bc.mine("miner-1")
        times.append(time() - start)
        nonces.append(block["nonce"])
        # print(f"   d={d}: blok {i + 1}/{n_blocks} gotowy w {times[-1]:.1f} s", flush=True)
    return sum(nonces) / n_blocks, sum(times) / n_blocks, sum(nonces) + n_blocks, sum(times)


if __name__ == "__main__":
    rows = []
    total_hashes = total_time = 0
    print(f"{'d':>2} {'16^d':>10} {'śr. nonce':>12} {'śr. czas [s]':>13} {'H/s':>10}")
    for d in range(1, 5):
        n = 5 if d < 6 else 1          # d=6 jest drogie, więc tylko 1 blok
        avg_nonce, avg_time, hashes, t = measure(d, n)
        total_hashes += hashes
        total_time += t
        rows.append((d, 16 ** d, avg_nonce, avg_time))
        print(f"{d:>2} {16**d:>10} {avg_nonce:>12.0f} {avg_time:>13.4f} {hashes / t:>10.0f}", flush=True)

    hps = total_hashes / total_time
    print(f"\nWydajność komputera: {hps:,.0f} H/s")

    # Szacunek dla Bitcoin: średnio difficulty * 2^32 skrótów na blok
    hashes_per_block = BTC_DIFFICULTY * 2 ** 32
    years = hashes_per_block / hps / (365.25 * 24 * 3600)
    print(f"Skrótów na 1 blok Bitcoin: {hashes_per_block:.2e}")
    print(f"Czas wydobycia 1 bloku Bitcoin na tym komputerze: {years:.2e} lat")
    print(f"(dla porównania cała sieć: {hashes_per_block / BTC_HASHRATE:.0f} s)")

    import matplotlib.pyplot as plt
    d = [r[0] for r in rows]
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    ax[0].semilogy(d, [r[1] for r in rows], "o--", label="teoretycznie 16^d")
    ax[0].semilogy(d, [r[2] + 1 for r in rows], "s-", label="zmierzona śr. liczba prób")
    ax[0].set(xlabel="trudność d", ylabel="liczba prób", title="Liczba prób vs trudność")
    ax[1].semilogy(d, [r[1] / hps for r in rows], "o--", label="teoretycznie 16^d / H/s")
    ax[1].semilogy(d, [r[3] for r in rows], "s-", label="zmierzony śr. czas")
    ax[1].set(xlabel="trudność d", ylabel="czas [s]", title="Czas wydobycia vs trudność")
    for a in ax:
        a.legend()
        a.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig("wykres_trudnosc.png", dpi=150)
    print("Zapisano wykres_trudnosc.png")