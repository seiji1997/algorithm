# This is the myanswer.py for problem C in ABC388
import sys

input_data = sys.stdin.read().split()
N = int(input_data[0])
A = list(map(int, input_data[1 : N + 1]))
count = 0
pointer = 0
for j in range(N):
    threshold = A[j] // 2
    while pointer < j and A[pointer] <= threshold:
        pointer += 1
    count += pointer

print(count)
