# This is the myanswer.py for problem A in ABC376
# Let's implement the solution based on the problem's description.


def count_candies(N, C, T):
    candies = 1
    last_time = T[0]

    for i in range(1, N):
        if T[i] - last_time >= C:
            candies += 1
            last_time = T[i]
    return candies


N, C = map(int, input().split())
T = list(map(int, input().split()))

print(count_candies(N, C, T))
