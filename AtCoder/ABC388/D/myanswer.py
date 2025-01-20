# This is the myanswer.py for problem D in ABC388
import sys


data = sys.stdin.read().split()
N = int(data[0])
A = list(map(int, data[1 : N + 1]))
diff = [0] * (N + 2)
Bi = [0] * (N + 1)
sum_diff = 0

for j in range(1, N + 1):
    sum_diff += diff[j]
    S_j = sum_diff
    t_j = min(N - j, A[j - 1] + S_j)
    Bi[j] = A[j - 1] + S_j - t_j
    if t_j > 0:
        l = j + 1
        r = j + t_j
        if l <= N:
            r = min(r, N)
            diff[l] += 1
            diff[r + 1] -= 1

print(" ".join(map(str, Bi[1:])))
