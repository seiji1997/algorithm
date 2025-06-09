# This is the myanswer.py for problem A in ABC395
import sys

data = sys.stdin.read().strip().split()
N = int(data[0])
A = list(map(int, data[1:]))

increasing = all(A[i] < A[i + 1] for i in range(N - 1))
if increasing:
    print("Yes")
else:
    print("No")
