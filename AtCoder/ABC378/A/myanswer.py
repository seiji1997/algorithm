# This is the myanswer.py for problem A in ABC378
from collections import Counter


def max_pair_removal():
    nums = list(map(int, input().split()))
    count = Counter(nums)
    return sum(v // 2 for v in count.values())


print(max_pair_removal())
