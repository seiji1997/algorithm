# This is the myanswer.py for problem C in ABC367
from itertools import product

def generate_sequences(N, K, R):
    results = []

    for seq in product(*(range(1, r + 1) for r in R)):
        if sum(seq) % K == 0:
            results.append(seq)
    
    for res in sorted(results):
        print(" ".join(map(str, res)))

N, K = map(int, input().split())
R = list(map(int, input().split()))

generate_sequences(N, K, R)