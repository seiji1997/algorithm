# This is the myanswer.py for problem E in ABC388
import sys

input_data = sys.stdin.read().split()
N = int(input_data[0])
A = list(map(int, input_data[1 : N + 1]))
count = 0
i = 0
j = N // 2
while i < N // 2 and j < N:
    if A[i] * 2 <= A[j]:
        count += 1
        i += 1
        j += 1
    else:
        j += 1
print(count)
