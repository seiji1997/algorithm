# This is the myanswer.py for problem B in ABC388
import sys

input = sys.stdin.read().splitlines()
N, D = map(int, input[0].split())
heavy_snake = []
for i in range(1, N + 1):
    Ti, Li = map(int, input[i].split())
    heavy_snake.append((Ti, Li))

for k in range(1, D + 1):
    max_weight = -1
    for Ti, Li in heavy_snake:
        weight = Ti * (Li + k)
        if weight > max_weight:
            max_weight = weight
    print(max_weight)
