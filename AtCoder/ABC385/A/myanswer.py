# This is the myanswer.py for problem A in ABC385
def solve():
    A, B, C = map(int, input().split())
    total = A + B + C
    half = total // 2

    if A == B == C:
        print("Yes")
        return
    if total % 2 == 1:
        print("No")
        return
    if (
        A == half
        or B == half
        or C == half
        or (A + B) == half
        or (B + C) == half
        or (A + C) == half
    ):
        print("Yes")
    else:
        print("No")


solve()
