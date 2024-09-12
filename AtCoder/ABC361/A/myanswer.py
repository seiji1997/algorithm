# This is the myanswer.py for problem A in ABC361

N, K, X = map(int, input().split())
A = list(map(int, input().split()))

# B = A[:K] + [X] + A[K:]

B = A.copy()
B.insert(K, X)

print(" ".join(map(str, B)))
