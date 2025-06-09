# This is the myanswer.py for problem B in ABC395
import sys

N = int(sys.stdin.readline().strip())

for r in range(N):
    row = []
    for c in range(N):
        layer = min(r, c, N - 1 - r, N - 1 - c)
        if layer % 2 == 0:
            row.append("#")
        else:
            row.append(".")
    print("".join(row))
