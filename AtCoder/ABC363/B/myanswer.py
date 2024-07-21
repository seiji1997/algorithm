# This is the myanswer.py for problem B in ABC363
def day_count(N: int, T: int, P: int, L: list) -> int:
    count = sum(1 for length in L if length >= T)

    if count >= P:
        return 0
    
    days = 0

    while count < P:
        days += 1
        count = sum(1 for length in L if length + days >= T)
    
    return days

N, T, P = map(int, input().split())
L = list(map(int, input().split()))

result = day_count(N, T, P, L)
print(result)