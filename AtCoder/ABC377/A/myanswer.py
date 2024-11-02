# This is the myanswer.py for problem A in ABC377

import sys
from itertools import permutations


def check_string(S):
    if "ABC" in map("".join, permutations(S)):
        return "Yes"
    else:
        return "No"


S = input().strip()
print(check_string(S))
