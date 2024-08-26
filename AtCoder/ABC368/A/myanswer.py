# This is the myanswer.py for problem A in ABC368
def arange_cards(N, K, A):
    move_cards = A[-K:]
    remain_cards = A[:-K]

    result = move_cards + remain_cards

    return result


N, K = map(int, input().split())
A = list(map(int, input().split()))
result = arange_cards(N, K, A)
print(" ".join(map(str, result)))