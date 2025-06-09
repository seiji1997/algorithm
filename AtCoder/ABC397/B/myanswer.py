import sys

S = sys.stdin.readline().strip()
n = len(S)

for k in range(1, 101):
    T = "io" * k
    j = 0
    for c in T:
        if j < n and c == S[j]:
            j += 1
        if j == n:
            break
    if j == n:
        print(2 * k - n)
        break
