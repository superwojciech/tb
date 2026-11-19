import hashlib
import json

block_a = {"index": 2, "timestamp": 1727251200, "transactions": ["Alice -> Bob: 5"],
           "nonce": 0, "previous_hash": "0" * 64}
# te same dane, odwrócona kolejność kluczy
block_b = dict(reversed(list(block_a.items())))

print("Kolejność kluczy A:", list(block_a))
print("Kolejność kluczy B:", list(block_b))
print("Te same dane:", block_a == block_b)

print("\nZ sort_keys=True:")
print("A:", hashlib.sha256(json.dumps(block_a, sort_keys=True).encode()).hexdigest())
print("B:", hashlib.sha256(json.dumps(block_b, sort_keys=True).encode()).hexdigest())

print("\nBez sort_keys:")
print("A:", hashlib.sha256(json.dumps(block_a).encode()).hexdigest())
print("B:", hashlib.sha256(json.dumps(block_b).encode()).hexdigest())