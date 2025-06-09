# This is the myanswer.py for problem C in ABC395
import sys

input_data = sys.stdin.read().strip().split()
A = list(map(int, input_data[1:]))

last_pos = [-1] * (1000001)
min_length = float("inf")

for i, val in enumerate(A):
    if last_pos[val] != -1:
        length = i - last_pos[val] + 1
        if length < min_length:
            min_length = length
    last_pos[val] = i

if min_length == float("inf"):
    print(-1)
else:
    print(min_length)
