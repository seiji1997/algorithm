# This is the myanswer.py for problem C in ABC384

from itertools import combinations
import sys


def solve():
    a, b, c, d, e = map(int, sys.stdin.readline().strip().split())
    values = {"A": a, "B": b, "C": c, "D": d, "E": e}
    chars = ["A", "B", "C", "D", "E"]

    all_patterns = []
    for r in range(1, 6):
        for comb in combinations(chars, r):
            name = "".join(comb)
            score = sum(values[ch] for ch in comb)
            all_patterns.append((score, name))

    all_patterns.sort(key=lambda x: (-x[0], x[1]))

    for _, name in all_patterns:
        print(name)


solve()
